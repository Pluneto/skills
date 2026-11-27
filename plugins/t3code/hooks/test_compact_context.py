"""Tests for compact_context.py, driven through its public seam: hook input JSON on
stdin, text or JSON on stdout, for both hosts (`--host t3`, the default, and `--host cli`).
The same script is copied to plugins/cli-host/hooks (scripts/validate keeps the copies identical).
Run: python3 -m unittest discover -s plugins/t3code/hooks"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parent / "compact_context.py"
SID = "11111111-1111-1111-1111-111111111111"
OTHER_SID = "22222222-2222-2222-2222-222222222222"
THREAD = "thread-abc"
# GIT_* goes too: a git hook (the pre-commit run of scripts/validate) exports GIT_DIR and GIT_INDEX_FILE,
# which would point every git call here at the repository being committed instead of the temp repos.
# TMUX and TMUX_PANE go too, and every test finds a fake `tmux` first on PATH (HookCase), so no test can type
# into the pane of the session that runs it.
CLEAN_ENV = {k: v for k, v in os.environ.items()
             if k not in ("COMPACT_NUDGE_TOKENS", "T3CODE_THREAD_ID", "CLAUDE_CODE_SESSION_ID", "TMUX", "TMUX_PANE")
             and not k.startswith("GIT_")}
PANE = "%7"
# Records each call's argv in $FAKE_TMUX_LOG; display-message prints "$FAKE_PANE_PID $FAKE_PANE_IN_MODE" (mode 0 by
# default), capture-pane prints $FAKE_CAPTURE.
FAKE_TMUX = f"""#!{sys.executable}
import json, os, sys
args = sys.argv[1:]
with open(os.environ["FAKE_TMUX_LOG"], "a") as log:
    log.write(json.dumps(args) + "\\n")
if os.environ.get("FAKE_TMUX_DOWN"):
    sys.exit(1)
if args[0] == "display-message":
    print(os.environ.get("FAKE_PANE_PID", ""), os.environ.get("FAKE_PANE_IN_MODE", "0"))
elif args[0] == "capture-pane":
    sys.stdout.write(open(os.environ["FAKE_CAPTURE"], encoding="utf-8").read())
"""
# A parent process whose comm is `claude` (python run through a symlink of that name): it marks itself as the
# pane's process when none is marked yet, then runs its argv with stdin passed through.
CLAUDE_PARENT = """import os, subprocess, sys
os.environ.setdefault("FAKE_PANE_PID", str(os.getpid()))
sys.exit(subprocess.run(sys.argv[1:]).returncode)"""


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True,
                          env=CLEAN_ENV).stdout.strip()


def make_repo(root):
    git(root, "init", "-q")
    git(root, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "--allow-empty", "-m", "init")
    return Path(root)


def live_state_dir(cwd):
    return Path(git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")) / "live-state"


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


def run_hook(payload, *argv, env=None, raw_input=None, claude_parents=0):
    """Run the hook, under `claude_parents` nested claude-named parents (0: straight from the test)."""
    full_env = dict(CLEAN_ENV, **(env or {}))
    command = [sys.executable, str(SCRIPT), *argv]
    for _ in range(claude_parents):
        command = [CLEAN_ENV["FAKE_CLAUDE"], "-c", CLAUDE_PARENT] + command
    run = subprocess.run(command,
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
        self.home = Path(self.tmp.name) / "home"  # the CLI host's fallback folder lives under $HOME
        self.home.mkdir()
        bin_dir = Path(self.tmp.name) / "bin"
        bin_dir.mkdir()
        (bin_dir / "tmux").write_text(FAKE_TMUX)
        (bin_dir / "tmux").chmod(0o755)
        (bin_dir / "claude").symlink_to(sys.executable)
        self.tmux_log = Path(self.tmp.name) / "tmux.log"
        self.capture = Path(self.tmp.name) / "capture.txt"
        patcher = mock.patch.dict(CLEAN_ENV, {
            "HOME": str(self.home), "PATH": f"{bin_dir}{os.pathsep}{CLEAN_ENV.get('PATH', '')}",
            "FAKE_TMUX_LOG": str(self.tmux_log), "FAKE_CAPTURE": str(self.capture),
            "FAKE_CLAUDE": str(bin_dir / "claude")})
        patcher.start()
        self.addCleanup(patcher.stop)

    def payload(self, event, **extra):
        return dict({"hook_event_name": event, "session_id": SID, "cwd": str(self.repo)}, **extra)

    def assertSilent(self, payload, *argv, env=None):
        code, out = run_hook(payload, *argv, env=env)
        self.assertEqual((code, out), (0, ""))


class NoOpTests(HookCase):
    EVENTS = ("PreCompact", "SessionStart", "Stop")

    def test_no_live_state_file(self):
        transcript = write_transcript(Path(self.tmp.name) / "t.jsonl", [usage_line(300000)])
        for argv in ((), ("--host", "t3")):
            for event in self.EVENTS:
                self.assertSilent(self.payload(event, transcript_path=transcript, stop_hook_active=False),
                                  event, *argv, env={"T3CODE_THREAD_ID": THREAD})

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

    def linked_worktree(self):
        linked = Path(self.tmp.name) / "linked"
        git(self.repo, "worktree", "add", "-q", "-b", "side", str(linked))
        return linked

    def inject_from(self, cwd):
        code, out = run_hook(dict(self.payload("SessionStart", source="compact"), cwd=str(cwd)))
        return json.loads(out)["hookSpecificOutput"]["additionalContext"]

    def test_linked_worktree_keeps_its_file_in_the_common_git_dir(self):
        linked = self.linked_worktree()
        self.assertEqual(live_state_dir(linked), self.repo / ".git" / "live-state")
        write_state(linked, SID, "Milestone: LINKED\n", self.plan)
        self.assertIn("Milestone: LINKED", self.inject_from(linked))

    def test_file_survives_a_removed_and_recreated_worktree(self):
        linked = self.linked_worktree()
        write_state(linked, SID, "Milestone: KEPT\n", self.plan)
        git(self.repo, "worktree", "remove", "--force", str(linked))
        git(self.repo, "worktree", "add", "-q", str(linked), "side")
        self.assertIn("Milestone: KEPT", self.inject_from(linked))

    def test_file_in_the_worktrees_own_git_dir_is_still_found(self):
        linked = self.linked_worktree()
        old = Path(git(linked, "rev-parse", "--absolute-git-dir")) / "live-state" / f"{SID}.md"
        old.parent.mkdir(parents=True)
        old.write_text("Updated: 2026-11-16T10:00:00Z\nMilestone: OLD PLACE\n", encoding="utf-8")
        self.assertIn("Milestone: OLD PLACE", self.inject_from(linked))
        write_state(linked, SID, "Milestone: NEW PLACE\n", self.plan)
        self.assertIn("Milestone: NEW PLACE", self.inject_from(linked))

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
        self.assertEqual(self.stop([usage_line(249999)]), (0, ""))
        self.assertFalse(self.marker.exists())

    def test_at_threshold_blocks_with_instructions(self):
        code, out = self.stop([usage_line(250000)])
        self.assertEqual(code, 0)
        decision = json.loads(out)
        self.assertEqual(decision["decision"], "block")
        reason = decision["reason"]
        for needed in (str(self.state), "t3_thread_send", THREAD, "queue", "/compact", "no further tool calls"):
            self.assertIn(needed, reason)
        self.assertTrue(self.marker.exists())

    def test_context_is_input_plus_cache_read_plus_cache_creation(self):
        line = json.dumps({"type": "assistant", "message": {"usage": {
            "input_tokens": 150000, "cache_read_input_tokens": 60000, "cache_creation_input_tokens": 40000}}})
        self.assertEqual(json.loads(self.stop([line])[1])["decision"], "block")
        self.marker.unlink()
        line = line.replace("60000", "59999")
        self.assertEqual(self.stop([line]), (0, ""))

    def test_uses_the_last_main_thread_assistant_line(self):
        lines = [usage_line(250000), usage_line(250000, sidechain=True), usage_line(50000),
                 usage_line(300000, sidechain=True), json.dumps({"type": "user", "message": {}})]
        self.assertEqual(self.stop(lines), (0, ""))

    def test_threshold_override_by_env(self):
        self.assertEqual(self.stop([usage_line(5000)], env={"COMPACT_NUDGE_TOKENS": "6000"}), (0, ""))
        code, out = self.stop([usage_line(5000)], env={"COMPACT_NUDGE_TOKENS": "4000"})
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

    def test_without_thread_id_is_silent_on_t3_and_nudges_on_cli(self):
        write_transcript(self.transcript, [usage_line(300000)])
        payload = self.payload("Stop", transcript_path=str(self.transcript), stop_hook_active=False)
        self.assertEqual(run_hook(payload), (0, ""))
        self.assertEqual(run_hook(payload, "Stop", "--host", "t3"), (0, ""))
        code, out = run_hook(payload, "Stop", "--host", "cli")
        self.assertEqual(json.loads(out)["decision"], "block")

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


class CliTests(HookCase):
    """`--host cli`: plain Claude Code. Any main session in a git repo is nudged; the user types /compact."""

    def setUp(self):
        super().setUp()
        self.transcript = Path(self.tmp.name) / "t.jsonl"
        self.fallback = self.home / ".claude" / "live-state" / f"{SID}.md"

    def run_cli(self, event, **extra):
        return run_hook(self.payload(event, **extra), event, "--host", "cli")

    def stop(self, tokens=300000, **extra):
        write_transcript(self.transcript, [usage_line(tokens)])
        return self.run_cli("Stop", transcript_path=str(self.transcript), stop_hook_active=False, **extra)

    def test_without_a_file_nudges_and_names_the_home_fallback(self):
        code, out = self.stop()
        self.assertEqual(code, 0)
        decision = json.loads(out)
        self.assertEqual(decision["decision"], "block")
        reason = decision["reason"]
        for needed in (str(self.fallback), "Updated:", "Plan:", "/compact", "300000"):
            self.assertIn(needed, reason)
        self.assertNotIn("t3_thread_send", reason)
        self.assertIn("/compact", decision["systemMessage"])
        self.assertTrue(self.fallback.with_suffix(".nudged").exists())
        self.assertFalse(self.fallback.exists())  # the agent writes the file, not the hook

    def test_an_existing_file_in_the_git_dir_wins(self):
        state = write_state(self.repo, SID, "Milestone: M1\n", self.plan)
        reason = json.loads(self.stop()[1])["reason"]
        self.assertIn(str(state), reason)
        self.assertNotIn(str(self.fallback), reason)
        self.assertTrue(state.with_suffix(".nudged").exists())

    def test_thread_id_is_not_needed_and_its_send_step_is_absent(self):
        write_transcript(self.transcript, [usage_line(300000)])
        payload = self.payload("Stop", transcript_path=str(self.transcript), stop_hook_active=False)
        code, out = run_hook(payload, "Stop", "--host", "cli", env={"T3CODE_THREAD_ID": THREAD})
        self.assertNotIn("t3_thread_send", json.loads(out)["reason"])

    def test_silent_cases(self):
        self.assertEqual(self.stop(tokens=249999), (0, ""))
        self.assertEqual(self.stop(agent_id="agent-1"), (0, ""))
        self.assertEqual(self.stop(session_id="../x"), (0, ""))
        plain = Path(self.tmp.name) / "plain"
        plain.mkdir()
        self.assertEqual(self.stop(cwd=str(plain)), (0, ""))
        self.assertFalse(self.fallback.with_suffix(".nudged").exists())
        write_transcript(self.transcript, [usage_line(300000)])
        self.assertEqual(self.run_cli("Stop", transcript_path=str(self.transcript), stop_hook_active=True), (0, ""))

    def test_nudges_once_until_a_compaction_even_without_a_file(self):
        self.assertEqual(json.loads(self.stop()[1])["decision"], "block")
        self.assertEqual(self.stop(), (0, ""))
        self.assertEqual(self.run_cli("SessionStart", source="compact"), (0, ""))
        self.assertEqual(json.loads(self.stop()[1])["decision"], "block")

    def test_pre_compact_without_a_file_is_silent(self):
        self.assertEqual(self.run_cli("PreCompact", trigger="manual"), (0, ""))

    def test_file_in_the_home_fallback_is_used_by_every_event(self):
        self.fallback.parent.mkdir(parents=True)
        self.fallback.write_text(f"Updated: 2026-11-22T10:00:00Z\nPlan: {self.plan}\nMilestone: HOME\n", encoding="utf-8")
        self.assertIn(str(self.fallback), self.run_cli("PreCompact", trigger="manual")[1])
        self.assertIn(str(self.fallback), json.loads(self.stop()[1])["reason"])
        code, out = self.run_cli("SessionStart", source="compact")
        text = json.loads(out)["hookSpecificOutput"]["additionalContext"]
        self.assertTrue(text.startswith("Live state restored after compaction"), text[:80])
        self.assertIn("Milestone: HOME", text)
        self.assertIn("- built M2", text)
        self.assertFalse(self.fallback.with_suffix(".nudged").exists())


EMPTY_INPUT = ('\x1b[38;5;244m' + '─' * 40 + '\n'
               '\x1b[39m❯ \x1b[2mTry "how do I log an error?"\x1b[0m\n'
               '\x1b[38;5;244m' + '─' * 40 + '\n'
               '\x1b[39m  \x1b[1m\x1b[38;5;246mHaiku 5.5\x1b[0m\n')  # captured from Claude Code 2.1.332
FOCUS = "plan plans/plan-x.md, M2 tests, next: write the guard"
RESUME_PROMPT = ("[auto-resume after compaction - not a new instruction from the user] "
                 "Continue with the next action in the live-state file.")


class AutoCompactTests(HookCase):
    """`--host cli` inside tmux: on the turn's second Stop the hook types the agent's /compact line itself."""

    def setUp(self):
        super().setUp()
        self.transcript = Path(self.tmp.name) / "t.jsonl"
        write_transcript(self.transcript, [usage_line(300000)])
        self.capture.write_text(EMPTY_INPUT, encoding="utf-8")
        self.state = write_state(self.repo, SID, "Resume: yes\nMilestone: M2\n", self.plan)

    def first_stop(self, **env):
        payload = self.payload("Stop", transcript_path=str(self.transcript), stop_hook_active=False)
        code, out = run_hook(payload, "Stop", "--host", "cli", env=dict({"TMUX_PANE": PANE}, **env), claude_parents=1)
        self.assertEqual(json.loads(out)["decision"], "block")

    def second_stop(self, message=f"State saved.\n/compact {FOCUS}", claude_parents=1, host="cli", **env):
        payload = self.payload("Stop", transcript_path=str(self.transcript), stop_hook_active=True,
                               last_assistant_message=message)
        return run_hook(payload, "Stop", "--host", host, env=dict({"TMUX_PANE": PANE}, **env),
                        claude_parents=claude_parents)

    def sent(self):
        calls = [json.loads(line) for line in self.tmux_log.read_text().splitlines()] if self.tmux_log.exists() else []
        return [call for call in calls if call[0] == "send-keys"]

    def run_cli_session_start(self):
        return run_hook(self.payload("SessionStart", source="compact"), "SessionStart", "--host", "cli")

    def assertNothingTyped(self, result=None):
        if result is not None:
            self.assertEqual(result, (0, ""))
        self.assertEqual(self.sent(), [])

    def test_nudge_asks_for_the_resume_line_and_says_the_hook_may_run_the_compact_line(self):
        payload = self.payload("Stop", transcript_path=str(self.transcript), stop_hook_active=False)
        decision = json.loads(run_hook(payload, "Stop", "--host", "cli")[1])
        for needed in ("third line", "Resume: yes", "Resume: no", "runs it itself"):
            self.assertIn(needed, decision["reason"])
        self.assertNotIn("Only the user can start", decision["reason"])
        self.assertIn("on its own", decision["systemMessage"])

    def test_second_stop_types_the_compact_line_then_enter(self):
        self.first_stop()
        self.assertEqual(self.sent(), [])
        self.assertEqual(self.second_stop(), (0, ""))
        self.assertEqual(self.sent()[:2], [["send-keys", "-t", PANE, "-l", f"/compact {FOCUS}"],
                                           ["send-keys", "-t", PANE, "Enter"]])

    def test_resume_yes_types_the_labelled_prompt_after_the_compact_line(self):
        self.first_stop()
        self.second_stop()
        self.assertEqual(self.sent(), [["send-keys", "-t", PANE, "-l", f"/compact {FOCUS}"],
                                       ["send-keys", "-t", PANE, "Enter"],
                                       ["send-keys", "-t", PANE, "-l", RESUME_PROMPT],
                                       ["send-keys", "-t", PANE, "Enter"]])

    def test_resume_missing_no_or_other_types_only_the_compact_line(self):
        for body in ("Milestone: M2\n", "Resume: no\n", "Resume: maybe\n", "Resume: yes please\n",
                     "Milestone: M2\nResume: yes\n"):  # only the third line counts
            with self.subTest(body=body):
                self.state.write_text(f"Updated: 2026-11-28T10:00:00Z\nPlan: {self.plan}\n{body}", encoding="utf-8")
                self.run_cli_session_start()
                self.tmux_log.unlink(missing_ok=True)
                self.first_stop()
                self.second_stop()
                self.assertEqual([call[-1] for call in self.sent()], [f"/compact {FOCUS}", "Enter"])

    def test_sends_once_per_cycle_and_again_after_a_compaction(self):
        self.first_stop()
        self.second_stop()
        self.second_stop()
        self.assertEqual(len(self.sent()), 4)
        self.assertTrue(self.state.with_suffix(".queued").exists())
        self.run_cli_session_start()
        self.assertFalse(self.state.with_suffix(".queued").exists())
        self.assertFalse(self.state.with_suffix(".nudged").exists())
        self.first_stop()
        self.second_stop()
        self.assertEqual(len(self.sent()), 8)

    def test_line_falls_back_to_the_newest_assistant_entry_of_the_transcript(self):
        reply = json.dumps({"type": "assistant", "message": {"content": [
            {"type": "text", "text": f"Saved.\n/compact {FOCUS}"}]}})
        side = json.dumps({"type": "assistant", "isSidechain": True, "message": {"content": [
            {"type": "text", "text": "/compact from a sub-agent"}]}})
        write_transcript(self.transcript, [usage_line(300000), reply, side])
        self.first_stop()
        self.second_stop(message=None)
        self.assertEqual(self.sent()[0][-1], f"/compact {FOCUS}")

    def test_without_a_pane_or_with_tmux_down_nothing_is_typed(self):
        self.first_stop()
        self.assertNothingTyped(self.second_stop(TMUX_PANE=""))
        self.assertNothingTyped(self.second_stop(FAKE_TMUX_DOWN="1"))

    def test_outside_a_claude_process_or_under_a_nested_claude_nothing_is_typed(self):
        self.first_stop()
        self.assertNothingTyped(self.second_stop(claude_parents=0))
        self.assertNothingTyped(self.second_stop(claude_parents=2))  # a nested claude would type into its parent's pane

    def test_a_pane_in_copy_mode_gets_nothing(self):
        self.first_stop()
        self.assertNothingTyped(self.second_stop(FAKE_PANE_IN_MODE="1"))  # keys would go to copy mode, not claude

    def test_a_pane_that_is_not_an_ancestor_gets_nothing(self):
        self.first_stop()
        self.assertNothingTyped(self.second_stop(FAKE_PANE_PID="999999999"))
        self.assertNothingTyped(self.second_stop(FAKE_PANE_PID="junk"))

    def test_a_draft_or_a_queued_user_message_gets_nothing(self):
        border = '\x1b[38;5;244m' + '─' * 40 + '\n'
        drafts = {
            "draft": border + '\x1b[39m❯ hello draft\n' + border,
            "blank first line": border + '\x1b[39m❯ \n  second line\n' + border,
            "draft in colour 2": border + '\x1b[39m❯ \x1b[38;5;2m/model\x1b[39m\n' + border,
            "draft after dim off": border + '\x1b[39m❯ \x1b[2mTry\x1b[22mtyped\n' + border,
            "queued hint": border + '\x1b[39m❯ \x1b[2mPress up to edit queued messages\x1b[0m\n' + border,
            "queued line": 'Queued · ctrl+x ctrl+s to send now\n' + border + '\x1b[39m❯ \n' + border,
            "no input line": 'Compacting conversation…\n',
        }
        self.first_stop()
        for name, capture in drafts.items():
            with self.subTest(name):
                self.capture.write_text(capture, encoding="utf-8")
                self.assertNothingTyped(self.second_stop())

    def test_a_bad_or_missing_line_gets_nothing(self):
        self.first_stop()
        for message in ("All done.", f"/compact {FOCUS}\nThanks!", "/compact ", "/compact \x1b[31mred",
                        "/compact " + "x" * 301, "", None):
            with self.subTest(message=message):
                self.assertNothingTyped(self.second_stop(message=message))

    def test_t3_host_never_types(self):
        self.first_stop()
        self.assertNothingTyped(self.second_stop(host="t3", T3CODE_THREAD_ID=THREAD))


if __name__ == "__main__":
    unittest.main()
