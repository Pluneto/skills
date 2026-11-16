"""Tests for compact_context.py, driven through its public seam: hook input JSON on
stdin, text or JSON on stdout. Run: python3 -m unittest discover -s plugins/t3code/hooks"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "compact_context.py"
SID = "11111111-1111-1111-1111-111111111111"
OTHER_SID = "22222222-2222-2222-2222-222222222222"
THREAD = "thread-abc"
CLEAN_ENV = {k: v for k, v in os.environ.items()
             if k not in ("T3_COMPACT_NUDGE_TOKENS", "T3CODE_THREAD_ID", "CLAUDE_CODE_SESSION_ID")}


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True).stdout.strip()


def make_repo(root):
    git(root, "init", "-q")
    git(root, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "--allow-empty", "-m", "init")
    return Path(root)


def live_state_dir(cwd):
    return Path(git(cwd, "rev-parse", "--absolute-git-dir")) / "live-state"


def write_state(cwd, sid, body, plan, updated="2026-11-16T10:00:00Z"):
    path = live_state_dir(cwd) / f"{sid}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"Updated: {updated}\nPlan: {plan}\n{body}", encoding="utf-8")
    return path


def write_plan(root, build_log_lines=None, name="plan.md"):
    text = "# Plan\n\n## Steps\n\n- [ ] M1\n"
    if build_log_lines is not None:
        text += "\n## Build log\n\n" + "\n".join(build_log_lines) + "\n"
    path = Path(root) / name
    path.write_text(text, encoding="utf-8")
    return path


def usage_line(total, sidechain=False):
    return json.dumps({"type": "assistant", "isSidechain": sidechain, "message": {"usage": {
        "input_tokens": 2, "cache_read_input_tokens": total - 2 - 10, "cache_creation_input_tokens": 10,
        "output_tokens": 5}}})


def write_transcript(path, lines):
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)


def run_hook(payload, *argv, env=None, raw_input=None):
    full_env = dict(CLEAN_ENV, **(env or {}))
    run = subprocess.run([sys.executable, str(SCRIPT), *argv],
                         input=raw_input if raw_input is not None else json.dumps(payload),
                         capture_output=True, text=True, env=full_env)
    return run.returncode, run.stdout


class HookCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        repo = Path(self.tmp.name) / "repo"
        repo.mkdir()
        self.repo = make_repo(repo)
        self.plan = write_plan(self.repo, ["- built M1", "- built M2"])

    def payload(self, event, **extra):
        return dict({"hook_event_name": event, "session_id": SID, "cwd": str(self.repo)}, **extra)

    def assertSilent(self, payload, *argv, env=None):
        code, out = run_hook(payload, *argv, env=env)
        self.assertEqual((code, out), (0, ""))


class NoOpTests(HookCase):
    EVENTS = ("PreCompact", "SessionStart", "Stop")

    def test_no_live_state_file(self):
        for event in self.EVENTS:
            self.assertSilent(self.payload(event, transcript_path="/nonexistent"))

    def test_agent_id_in_input_is_ignored(self):
        write_state(self.repo, SID, "Milestone: M1\n", self.plan)
        for event in self.EVENTS:
            self.assertSilent(self.payload(event, agent_id="agent-1"))

    def test_file_of_another_session_is_ignored(self):
        write_state(self.repo, OTHER_SID, "Milestone: M1\n", self.plan)
        for event in self.EVENTS:
            self.assertSilent(self.payload(event))

    def test_not_a_git_checkout(self):
        plain = Path(self.tmp.name) / "plain"
        plain.mkdir()
        for event in self.EVENTS:
            self.assertSilent(dict(self.payload(event), cwd=str(plain)))

    def test_garbage_input_never_fails(self):
        self.assertEqual(run_hook(None, "Stop", raw_input="not json {"), (0, ""))
        self.assertEqual(run_hook(None, raw_input=""), (0, ""))

    def test_session_id_cannot_escape_the_live_state_dir(self):
        write_state(self.repo, SID, "Milestone: M1\n", self.plan)
        self.assertSilent(dict(self.payload("PreCompact"), session_id="../live-state/" + SID))

    def test_unknown_event_is_silent(self):
        write_state(self.repo, SID, "Milestone: M1\n", self.plan)
        self.assertSilent(self.payload("PostCompact"))


class PreCompactTests(HookCase):
    def test_prints_summary_instructions(self):
        path = write_state(self.repo, SID, "Milestone: M1\n", self.plan)
        for trigger in ("manual", "auto"):
            code, out = run_hook(self.payload("PreCompact", trigger=trigger))
            self.assertEqual(code, 0)
            self.assertIn(str(path), out)
            self.assertIn("Updated", out)
            self.assertIn("newer", out)
            for kept in ("rules", "open questions", "running children"):
                self.assertIn(kept, out.lower())
            self.assertIn("drop", out.lower())

    def test_event_from_argument_when_input_has_none(self):
        write_state(self.repo, SID, "Milestone: M1\n", self.plan)
        payload = self.payload("PreCompact")
        del payload["hook_event_name"]
        code, out = run_hook(payload, "PreCompact")
        self.assertEqual(code, 0)
        self.assertIn("live-state", out)


class SessionStartTests(HookCase):
    def inject(self, **extra):
        code, out = run_hook(dict(self.payload("SessionStart", source="compact"), **extra))
        self.assertEqual(code, 0)
        body = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(body["hookEventName"], "SessionStart")
        return body["additionalContext"]

    def test_small_file_header_state_and_build_log_tail(self):
        log = [f"- build line {n}" for n in range(1, 8)]
        plan = write_plan(self.repo, log)
        path = write_state(self.repo, SID, "Milestone: M3 next action: review\n", plan)
        text = self.inject()
        self.assertTrue(text.startswith("Live state restored after compaction"), text[:80])
        header = text.split("\n\n", 1)[0]
        self.assertIn(str(path), header)
        self.assertIn(str(plan), header)
        self.assertIn("2026-11-16T10:00:00Z", header)
        self.assertIn("Milestone: M3 next action: review", text)
        for kept in range(3, 8):
            self.assertIn(f"- build line {kept}", text)
        for dropped in (1, 2):
            self.assertNotIn(f"- build line {dropped}\n", text + "\n")
        self.assertNotIn("Read ", header)  # nothing cut, no Read instruction

    def test_oversized_file_keeps_header_marks_cut_and_stays_under_10k(self):
        plan = write_plan(self.repo, ["- built M1"])
        path = write_state(self.repo, SID, "".join(f"Fact {n}: " + "x" * 80 + "\n" for n in range(400)), plan)
        text = self.inject()
        self.assertLess(len(text), 10000)
        header = text.split("\n\n", 1)[0]
        self.assertIn(str(path), header)
        self.assertIn(str(plan), header)
        self.assertIn("2026-11-16T10:00:00Z", header)
        self.assertIn("cut", header)
        self.assertIn("Read", header)
        self.assertIn("Fact 0:", text)
        self.assertNotIn("Fact 399:", text)

    def test_overlong_updated_line_cannot_push_the_injection_past_10k(self):
        plan = write_plan(self.repo, ["- built M1"])
        path = write_state(self.repo, SID, "Fact: kept\n", plan, updated="2026-11-16T10:00:00Z" + "x" * 12000)
        text = self.inject()
        self.assertLess(len(text), 10000)
        header = text.split("\n\n", 1)[0]
        self.assertIn(str(path), header)
        self.assertIn(str(plan), header)
        self.assertIn("2026-11-16T10:00:00Z", header)
        self.assertIn("Read", header)

    def test_build_log_line_starting_with_a_hash_does_not_end_the_section(self):
        plan = write_plan(self.repo, ["- M1 done", "#29 merged", "- M2 done", "- M3 done"])
        write_state(self.repo, SID, "Fact: kept\n", plan)
        text = self.inject()
        for line in ("- M1 done", "#29 merged", "- M2 done", "- M3 done"):
            self.assertIn(line, text)

    def test_non_ascii_is_not_escaped(self):
        plan = write_plan(self.repo, ["- built M1"])
        write_state(self.repo, SID, "Rules from the user: caf\u00e9 \u2014 always\n", plan)
        self.assertIn("caf\u00e9 \u2014 always", self.inject())

    def test_long_build_log_line_is_cut_to_300_chars_and_flagged(self):
        plan = write_plan(self.repo, ["- " + "y" * 600])
        write_state(self.repo, SID, "Milestone: M1\n", plan)
        text = self.inject()
        self.assertIn("y" * 290, text)
        self.assertNotIn("y" * 301, text)
        self.assertIn("Read", text.split("\n\n", 1)[0])

    def test_plan_without_build_log(self):
        plan = write_plan(self.repo, None)
        write_state(self.repo, SID, "Milestone: M1\n", plan)
        text = self.inject()
        self.assertIn("Milestone: M1", text)
        self.assertNotIn("Build log:", text)

    def test_missing_plan_file(self):
        missing = Path(self.tmp.name) / "gone.md"
        write_state(self.repo, SID, "Milestone: M1\n", missing)
        text = self.inject()
        self.assertIn(str(missing), text)
        self.assertIn("Milestone: M1", text)

    def test_file_without_plan_line(self):
        path = live_state_dir(self.repo) / f"{SID}.md"
        path.parent.mkdir(parents=True)
        path.write_text("Updated: 2026-11-16T10:00:00Z\nMilestone: M1\n", encoding="utf-8")
        self.assertIn("Milestone: M1", self.inject())

    def test_linked_worktree_uses_its_own_git_dir(self):
        linked = Path(self.tmp.name) / "linked"
        git(self.repo, "worktree", "add", "-q", "-b", "side", str(linked))
        self.assertNotEqual(live_state_dir(linked), linked / ".git" / "live-state")
        write_state(linked, SID, "Milestone: LINKED\n", self.plan)
        code, out = run_hook(dict(self.payload("SessionStart", source="compact"), cwd=str(linked)))
        self.assertIn("Milestone: LINKED", json.loads(out)["hookSpecificOutput"]["additionalContext"])
        # the main checkout has no file of its own
        self.assertSilent(self.payload("SessionStart", source="compact"))

    def test_clears_the_nudge_marker(self):
        write_state(self.repo, SID, "Milestone: M1\n", self.plan)
        marker = live_state_dir(self.repo) / f"{SID}.nudged"
        marker.write_text("1")
        self.inject()
        self.assertFalse(marker.exists())


class StopTests(HookCase):
    def setUp(self):
        super().setUp()
        self.state = write_state(self.repo, SID, "Milestone: M1\n", self.plan)
        self.marker = live_state_dir(self.repo) / f"{SID}.nudged"
        self.transcript = Path(self.tmp.name) / "t.jsonl"

    def stop(self, lines, env=None, **extra):
        write_transcript(self.transcript, lines)
        payload = self.payload("Stop", transcript_path=str(self.transcript), stop_hook_active=False, **extra)
        return run_hook(payload, env=dict({"T3CODE_THREAD_ID": THREAD}, **(env or {})))

    def test_below_threshold_is_silent(self):
        self.assertEqual(self.stop([usage_line(199999)]), (0, ""))
        self.assertFalse(self.marker.exists())

    def test_at_threshold_blocks_with_instructions(self):
        code, out = self.stop([usage_line(200000)])
        self.assertEqual(code, 0)
        decision = json.loads(out)
        self.assertEqual(decision["decision"], "block")
        reason = decision["reason"]
        for needed in (str(self.state), "t3_thread_send", THREAD, "queue", "/compact", "no further tool calls"):
            self.assertIn(needed, reason)
        self.assertTrue(self.marker.exists())

    def test_context_is_input_plus_cache_read_plus_cache_creation(self):
        line = json.dumps({"type": "assistant", "message": {"usage": {
            "input_tokens": 100000, "cache_read_input_tokens": 60000, "cache_creation_input_tokens": 40000}}})
        self.assertEqual(json.loads(self.stop([line])[1])["decision"], "block")
        self.marker.unlink()
        line = line.replace("60000", "59999")
        self.assertEqual(self.stop([line]), (0, ""))

    def test_uses_the_last_main_thread_assistant_line(self):
        lines = [usage_line(250000), usage_line(250000, sidechain=True), usage_line(50000),
                 usage_line(300000, sidechain=True), json.dumps({"type": "user", "message": {}})]
        self.assertEqual(self.stop(lines), (0, ""))

    def test_threshold_override_by_env(self):
        self.assertEqual(self.stop([usage_line(5000)], env={"T3_COMPACT_NUDGE_TOKENS": "6000"}), (0, ""))
        code, out = self.stop([usage_line(5000)], env={"T3_COMPACT_NUDGE_TOKENS": "4000"})
        self.assertEqual(json.loads(out)["decision"], "block")

    def test_stop_hook_active_is_silent(self):
        write_transcript(self.transcript, [usage_line(300000)])
        payload = self.payload("Stop", transcript_path=str(self.transcript), stop_hook_active=True)
        self.assertEqual(run_hook(payload, env={"T3CODE_THREAD_ID": THREAD}), (0, ""))

    def test_nudges_once_per_compaction(self):
        self.assertEqual(json.loads(self.stop([usage_line(300000)])[1])["decision"], "block")
        self.assertEqual(self.stop([usage_line(300000)]), (0, ""))
        # compaction ran: SessionStart(compact) clears the marker, a later big turn nudges again
        run_hook(self.payload("SessionStart", source="compact"))
        self.assertEqual(json.loads(self.stop([usage_line(300000)])[1])["decision"], "block")

    def test_delegated_task_thread_is_silent(self):
        env = {"T3CODE_THREAD_ID": "thread:delegated-task:command%3Amcp%3Aabc"}
        write_transcript(self.transcript, [usage_line(300000)])
        payload = self.payload("Stop", transcript_path=str(self.transcript), stop_hook_active=False)
        self.assertEqual(run_hook(payload, env=env), (0, ""))

    def test_without_thread_id_is_silent(self):
        write_transcript(self.transcript, [usage_line(300000)])
        payload = self.payload("Stop", transcript_path=str(self.transcript), stop_hook_active=False)
        self.assertEqual(run_hook(payload), (0, ""))

    def test_big_line_before_a_compact_boundary_does_not_count(self):
        boundary = json.dumps({"type": "system", "subtype": "compact_boundary"})
        self.assertEqual(self.stop([usage_line(300000), boundary]), (0, ""))
        self.assertEqual(self.stop([usage_line(300000), boundary, usage_line(30000)]), (0, ""))
        code, out = self.stop([usage_line(10000), boundary, usage_line(300000)])
        self.assertEqual(json.loads(out)["decision"], "block")

    def test_unreadable_or_missing_transcript_is_silent(self):
        payload = self.payload("Stop", transcript_path="/nonexistent/t.jsonl", stop_hook_active=False)
        self.assertEqual(run_hook(payload, env={"T3CODE_THREAD_ID": THREAD}), (0, ""))
        write_transcript(self.transcript, ["{broken", ""])
        self.assertEqual(self.stop(["{broken"]), (0, ""))

    def test_big_transcript_is_read_from_the_tail(self):
        filler = json.dumps({"type": "user", "message": {"content": "z" * 100000}})
        huge_last = json.loads(usage_line(250000))
        huge_last["message"]["content"] = "w" * 400000  # a last line bigger than the first tail chunk
        lines = [usage_line(10000)] + [filler] * 30 + [json.dumps(huge_last), json.dumps({"type": "user", "message": {}})]
        self.assertEqual(json.loads(self.stop(lines)[1])["decision"], "block")


if __name__ == "__main__":
    unittest.main()
