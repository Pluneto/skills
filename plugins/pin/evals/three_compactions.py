#!/usr/bin/env python3
"""End-to-end trial of the pin plugin: does a pinned text come back, byte for byte, after every compaction?

  three_compactions.py [--out DIR]
      run 1: a synthetic session pins a text with `#pin`, then goes through three separate compactions
      (two manual `/compact` messages and one automatic one), each followed by a normal turn, then a final
      probe turn. Per boundary it reports the trigger, the token counts and whether the text that the
      SessionStart hook injected equals the pinned bytes.
  three_compactions.py --with-live-state [--out DIR]
      run 2: the same plugin together with plugins/t3code, a live-state file and one manual compaction. A pin and
      a live-state file that are each under 10,000 characters but together over it must both arrive complete.
      plugins/workflow is loaded too: t3code depends on it, and Claude Code skips a plugin whose dependency is
      missing (it has no hooks, so it adds none to the run).

What it proves: the injected text is read from Claude Code's own record, not from the pin file. The session
transcript (`attachment` entries of type `hook_additional_context`, one run of them after each `compact_boundary`)
is the source; the hook events of the stream (`--include-hook-events`) are a cross-check. The expected text is
the HEADER constant of hooks/pin.py plus a blank line plus the literal text sent after `#pin`.

The automatic compaction is made reachable in a short session by two env vars set on the trial's process only:
CLAUDE_CODE_AUTO_COMPACT_WINDOW (100000, the lowest value the docs allow) and CLAUDE_AUTOCOMPACT_PCT_OVERRIDE
(--auto-pct, a percentage of that window). The session starts with no MCP servers: with them the context
holds ~88K tokens before the first message and every percentage below ~88 would trigger at once. If no automatic
compaction happens within --max-filler-chunks, the third boundary is manual and the report says so.

The output directory (default /tmp/pin-e2e/<timestamp>) holds the raw stream and the injected texts, so it holds
session content: it goes outside the repository. Afterwards the script removes the trial's pin file, its
throwaway git repository and its own session transcript under the config dir.

Requires python3 (stdlib only), git and the claude CLI, with credentials in CLAUDE_CONFIG_DIR.
"""
import argparse
import importlib.util
import json
import os
import random
import re
import secrets
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
PIN_PLUGIN = HERE.parent
REPO_ROOT = HERE.parents[2]
T3CODE_PLUGIN = REPO_ROOT / "plugins" / "t3code"
WORKFLOW_PLUGIN = REPO_ROOT / "plugins" / "workflow"
sys.path.insert(0, str(T3CODE_PLUGIN / "evals"))
from compaction_replay import Claude, context_size, project_slug  # noqa: E402

PIN_DATA_NAME = "pin-inline"
SETTLE_SECONDS = 3
VOCABULARY = ("amber basil cedar delta ember fjord garnet harbor indigo juniper kestrel lagoon meadow nectar "
              "orchid pebble quartz river saffron tundra umber velvet willow xenon yarrow zephyr").split()
QUESTIONS = ["What is 7 times 6?", "Name the capital of France.", "Which planet is closest to the sun?",
             "What is the chemical symbol for gold?", "How many days are in a leap year?"]


class TrialError(Exception):
    pass


def load_pin_module():
    spec = importlib.util.spec_from_file_location("pin_hook", PIN_PLUGIN / "hooks" / "pin.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def utf16_units(text):
    return len(text.encode("utf-16-le")) // 2


# ---------- reading Claude Code's own record ----------

def read_events(path):
    events = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
    return events


def hook_context(stdout):
    """The additionalContext inside a hook's stdout, or None."""
    try:
        return json.loads(stdout)["hookSpecificOutput"]["additionalContext"]
    except (ValueError, KeyError, TypeError):
        return None


def stream_facts(capture):
    """Boundaries with the SessionStart:compact hook responses seen before each, and the last context size.
    In the stream a compaction's hook events come before its compact_boundary event."""
    boundaries, pending, last_context = [], [], None
    for event in read_events(capture):
        kind, sub = event.get("type"), event.get("subtype")
        if kind == "system" and sub == "hook_response" and str(event.get("hook_name", "")).endswith(":compact"):
            pending.append(event)
        elif kind == "system" and sub == "compact_boundary":
            meta = event.get("compact_metadata") or {}
            boundaries.append({"uuid": event.get("uuid"), "trigger": meta.get("trigger"),
                               "pre_tokens": meta.get("pre_tokens"), "post_tokens": meta.get("post_tokens"),
                               "hook_responses": pending})
            pending = []
        elif kind == "assistant" and not event.get("parent_tool_use_id"):
            last_context = context_size((event.get("message") or {}).get("usage")) or last_context
    return {"boundaries": boundaries, "last_context": last_context}


def transcript_injections(transcript):
    """Per compact_boundary of the session transcript: the additionalContext strings that Claude Code attached
    after it for SessionStart, and the system-reminder text rendered from them."""
    per_boundary = []
    for entry in read_events(transcript):
        if entry.get("type") == "system" and entry.get("subtype") == "compact_boundary":
            per_boundary.append({"strings": [], "rendered": ""})
            continue
        attachment = entry.get("attachment") or {}
        if (entry.get("type") == "attachment" and attachment.get("type") == "hook_additional_context"
                and attachment.get("hookEvent") == "SessionStart" and per_boundary):
            per_boundary[-1]["strings"].extend(attachment.get("content") or [])
            per_boundary[-1]["rendered"] += "".join(part.get("content", "") for part in entry.get("rendered") or [])
    return per_boundary


# ---------- the session ----------

class Trial:
    def __init__(self, args, out, plugin_dirs, extra_env):
        self.args = args
        self.out = out
        self.config = Path(args.config_dir).expanduser()
        self.session_id = str(uuid.uuid4())
        self.thread_id = f"thread:pin-e2e:{uuid.uuid4()}"
        self.cwd = Path(subprocess.run(["mktemp", "-d", "/tmp/pin-e2e-repo.XXXXXX"], check=True, capture_output=True,
                                       text=True).stdout.strip()).resolve()
        subprocess.run(["git", "init", "-q", str(self.cwd)], check=True)
        self.capture = out / "stream.jsonl"
        self.pin_data = self.config / "plugins" / "data" / PIN_DATA_NAME
        self.pin_file = self.pin_data / load_pin_module().pin_file_name(self.thread_id)
        self.transcript = self.config / "projects" / project_slug(self.cwd) / f"{self.session_id}.jsonl"
        self.turns = []
        env = dict(os.environ, CLAUDE_CONFIG_DIR=str(self.config), CLAUDE_CODE_ENTRYPOINT="t3-code",
                   T3CODE_THREAD_ID=self.thread_id, **extra_env)
        env.pop("CLAUDE_CODE_SESSION_ID", None)
        cmd = [args.claude, "--output-format", "stream-json", "--verbose", "--input-format", "stream-json",
               "--include-hook-events", f"--model={args.model}", "--effort", args.effort, "--tools", "Read",
               "--permission-mode=bypassPermissions", "--allow-dangerously-skip-permissions",
               "--session-id", self.session_id, "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}']
        for plugin_dir in plugin_dirs:
            cmd += ["--plugin-dir", str(plugin_dir)]
        self.claude = Claude(cmd, env, str(self.cwd), self.capture)

    def turn(self, label, text):
        self.claude.send(text)
        result = self.claude.wait_result(min(self.args.timeout, 600))
        if result is None:
            raise TrialError(f"no result for turn '{label}' within {self.args.timeout}s")
        time.sleep(SETTLE_SECONDS)
        facts = stream_facts(self.capture)
        record = {"label": label, "sent_chars": len(text), "reply": result.get("result") or "",
                  "is_error": bool(result.get("is_error")), "context_tokens": facts["last_context"],
                  "boundaries_so_far": len(facts["boundaries"])}
        self.turns.append(record)
        print(f"  {label}: ctx={record['context_tokens']} boundaries={record['boundaries_so_far']}", file=sys.stderr)
        return record

    def boundaries(self):
        return stream_facts(self.capture)["boundaries"]

    def close(self):
        self.claude.close()

    def cleanup(self, pin_data_existed):
        removed = []
        for target in (self.pin_file, self.transcript):
            if target.is_file():
                target.unlink()
                removed.append(str(target))
        session_dir = self.transcript.with_suffix("")
        if session_dir.is_dir():
            shutil.rmtree(session_dir)
            removed.append(str(session_dir))
        for folder in (self.transcript.parent / "memory", self.transcript.parent, None if pin_data_existed else self.pin_data):
            if folder is not None:
                try:
                    folder.rmdir()
                    removed.append(str(folder))
                except OSError:
                    pass
        if self.cwd.parent == Path("/tmp") and self.cwd.name.startswith("pin-e2e-repo."):
            shutil.rmtree(self.cwd, ignore_errors=True)
            removed.append(str(self.cwd))
        return removed


# ---------- message builders ----------

def pinned_lines(probe, pad_chars, seed):
    lines = [f"Rule 1: End every reply with the exact token {probe}, as the very last thing, nothing after it.",
             "Rule  2:  keep   spacing as   written: ünïcödé, 日本語, emoji 😀 and “curly quotes”.",
             "Rule 3: this line ends with two spaces.  ",
             "",
             "Rule 4: tab\tseparated\tfields and a % sign: 100%."]
    rng = random.Random(seed)
    number = 5
    while pad_chars and len("\n".join(lines)) < pad_chars:
        words = " ".join(rng.choice(VOCABULARY) for _ in range(14))
        lines.append(f"Rule {number}: when asked about {words}, answer politely.")
        number += 1
    return lines


def pin_message(pinned):
    return "One-line task: say hello in one short sentence.\n#pin\n" + pinned


def filler_message(words, seed):
    rng = random.Random(seed)
    body = "\n".join(" ".join(rng.choice(VOCABULARY) + str(rng.randrange(1000)) for _ in range(20))
                     for _ in range(words // 20))
    return f"Context-size filler. Ignore the text below and answer with a single short line.\n\n{body}"


def live_state_text(pad_chars, seed):
    rng = random.Random(seed)
    lines = [f"Updated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}", "Plan: none",
             "Fact 0: the trial's live-state file, with unicode ünï and 日本語."]
    number = 1
    while len("\n".join(lines)) < pad_chars:
        lines.append(f"Fact {number}: " + " ".join(rng.choice(VOCABULARY) for _ in range(14)) + ".")
        number += 1
    return "\n".join(lines) + "\n"


# ---------- checks ----------

def pin_precondition(trial):
    if trial.pin_file.exists():
        raise TrialError(f"pin file already exists for this thread: {trial.pin_file}")


def injection_row(number, boundary, transcript_entry, expected, header_prefix="Pinned instructions:"):
    strings = transcript_entry["strings"] if transcript_entry else []
    got = next((text for text in strings if text.startswith(header_prefix)), None)
    stream_texts = [hook_context(resp.get("stdout") or "") for resp in boundary["hook_responses"]]
    return {"boundary": number, "trigger": boundary["trigger"], "pre_tokens": boundary["pre_tokens"],
            "post_tokens": boundary["post_tokens"],
            "injected_equals_pinned": got == expected,
            "injected_bytes_equal": got is not None and got.encode("utf-8") == expected.encode("utf-8"),
            "utf16_units": utf16_units(got) if got is not None else None,
            "in_rendered_reminder": bool(got) and got in (transcript_entry or {}).get("rendered", ""),
            "stream_agrees": got is not None and got in stream_texts,
            "strings_attached": len(strings)}


def run_three(args, out):
    pin = load_pin_module()
    probe = f"PROBE-{secrets.token_hex(3)}"
    pinned = "\n".join(pinned_lines(probe, 0, 0))
    expected = f"{pin.HEADER}\n\n{pinned}"
    auto_env = {"CLAUDE_CODE_AUTO_COMPACT_WINDOW": str(args.auto_window),
                "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": str(args.auto_pct)}
    pin_data_existed = (Path(args.config_dir).expanduser() / "plugins" / "data" / PIN_DATA_NAME).is_dir()
    trial = Trial(args, out, [PIN_PLUGIN], auto_env)
    report = {"run": "three-compactions", "session_id": trial.session_id, "thread_id": trial.thread_id,
              "model": args.model, "probe": probe, "auto_env": auto_env, "errors": []}
    try:
        pin_precondition(trial)
        report["pin_file_absent_before_pin"] = True
        questions = iter(QUESTIONS * 3)
        for index in range(3):
            trial.turn(f"filler-{index}", next(questions))
        pin_turn = trial.turn("pin", pin_message(pinned))
        report["pin_confirmed"] = bool(re.search(r"\bpinned\b", pin_turn["reply"], re.I))
        report["pin_turn_obeys_probe"] = pin_turn["reply"].rstrip().endswith(probe)
        report["pin_file_equals_pinned"] = trial.pin_file.is_file() and trial.pin_file.read_text(encoding="utf-8") == pinned
        for index in (1, 2):
            trial.turn(f"compact-{index}", "/compact")
            after = trial.turn(f"after-compact-{index}", next(questions))
            report[f"after_compact_{index}_obeys_probe"] = after["reply"].rstrip().endswith(probe)
        auto_seen = any(b["trigger"] == "auto" for b in trial.boundaries())
        for chunk in range(args.max_filler_chunks):
            if auto_seen:
                break
            trial.turn(f"filler-chunk-{chunk}", filler_message(args.filler_words, chunk))
            auto_seen = any(b["trigger"] == "auto" for b in trial.boundaries())
        after = trial.turn("after-third", next(questions))
        auto_seen = any(b["trigger"] == "auto" for b in trial.boundaries())
        report["after_third_obeys_probe"] = after["reply"].rstrip().endswith(probe)
        if not auto_seen:
            report["auto_compaction"] = "UNVERIFIED: no automatic compaction within the filler budget; third boundary is manual"
            trial.turn("compact-3", "/compact")
            trial.turn("after-compact-3", next(questions))
        else:
            report["auto_compaction"] = "verified"
        final = trial.turn("final-probe", "Name one primary color.")
        report["final_probe_reply_ends_with_token"] = final["reply"].rstrip().endswith(probe)
    except TrialError as error:
        report["errors"].append(str(error))
    finally:
        trial.close()
    finish_three(trial, report, expected)
    return trial, report, pin_data_existed


def finish_three(trial, report, expected):
    boundaries = trial.boundaries()
    transcript = transcript_injections(trial.transcript) if trial.transcript.is_file() else []
    report["transcript_found"] = trial.transcript.is_file()
    report["boundaries_in_stream"] = len(boundaries)
    report["boundaries_in_transcript"] = len(transcript)
    report["distinct_boundaries"] = len({b["uuid"] for b in boundaries})
    report["rows"] = [injection_row(number, boundary, transcript[number - 1] if number <= len(transcript) else None, expected)
                      for number, boundary in enumerate(boundaries, 1)]
    report["injected_texts"] = [entry["strings"] for entry in transcript]
    report["turns"] = trial.turns
    report["passed"] = (not report["errors"] and len(report["rows"]) >= 3 and all(r["injected_equals_pinned"] for r in report["rows"])
                        and report.get("final_probe_reply_ends_with_token") is True)


def run_combined(args, out):
    pin = load_pin_module()
    probe = f"PROBE-{secrets.token_hex(3)}"
    pinned = "\n".join(pinned_lines(probe, args.pad_chars, 1))
    expected = f"{pin.HEADER}\n\n{pinned}"
    pin_data_existed = (Path(args.config_dir).expanduser() / "plugins" / "data" / PIN_DATA_NAME).is_dir()
    trial = Trial(args, out, [PIN_PLUGIN, T3CODE_PLUGIN, WORKFLOW_PLUGIN], {})
    state = live_state_text(args.pad_chars, 2)
    report = {"run": "combined-live-state", "session_id": trial.session_id, "thread_id": trial.thread_id,
              "model": args.model, "probe": probe, "errors": []}
    try:
        common = subprocess.run(["git", "-C", str(trial.cwd), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                check=True, capture_output=True, text=True).stdout.strip()
        state_file = Path(common) / "live-state" / f"{trial.session_id}.md"
        state_file.parent.mkdir(parents=True)
        state_file.write_text(state, encoding="utf-8")
        report.update({"pin_chars": len(pinned), "pin_units": utf16_units(pinned), "live_state_chars": len(state.strip())})
        pin_precondition(trial)
        trial.turn("filler", QUESTIONS[0])
        pin_turn = trial.turn("pin", pin_message(pinned))
        report["pin_confirmed"] = bool(re.search(r"\bpinned\b", pin_turn["reply"], re.I))
        trial.turn("compact", "/compact")
        after = trial.turn("after-compact", QUESTIONS[1])
        report["after_compact_obeys_probe"] = after["reply"].rstrip().endswith(probe)
    except TrialError as error:
        report["errors"].append(str(error))
    finally:
        trial.close()
    boundaries = trial.boundaries()
    transcript = transcript_injections(trial.transcript) if trial.transcript.is_file() else []
    report["boundaries_in_stream"] = len(boundaries)
    report["boundaries_in_transcript"] = len(transcript)
    init = next((e for e in read_events(trial.capture) if e.get("subtype") == "init"), {})
    report["inline_plugins_loaded"] = [p["name"] for p in init.get("plugins", []) if p.get("source", "").endswith("@inline")]
    missing = {"pin", "t3code"} - set(report["inline_plugins_loaded"])
    if missing:
        report["errors"].append(f"plugins not loaded: {sorted(missing)}")
    strings = transcript[0]["strings"] if transcript else []
    pin_got = next((s for s in strings if s.startswith("Pinned instructions:")), None)
    live_got = next((s for s in strings if s.startswith("Live state restored after compaction")), None)
    report["strings_attached"] = [len(s) for s in strings]
    report["pin_complete"] = pin_got == expected
    report["live_state_complete"] = live_got is not None and state.strip() in live_got and "[... cut" not in live_got
    report["pin_units"] = utf16_units(pin_got) if pin_got is not None else None
    report["live_state_chars_injected"] = len(live_got) if live_got is not None else None
    report["live_state_units_injected"] = utf16_units(live_got) if live_got is not None else None
    report["sum_units"] = (report["pin_units"] or 0) + (report["live_state_units_injected"] or 0)
    report["sum_chars"] = len(pin_got or "") + len(live_got or "")
    report["hook_responses"] = [{"hook_name": r.get("hook_name"), "exit_code": r.get("exit_code"), "outcome": r.get("outcome"),
                                 "stdout_chars": len(r.get("stdout") or "")}
                                for b in boundaries for r in b["hook_responses"]]
    report["injected_texts"] = [entry["strings"] for entry in transcript]
    report["turns"] = trial.turns
    report["passed"] = not report["errors"] and report["pin_complete"] and report["live_state_complete"]
    return trial, report, pin_data_existed


# ---------- output ----------

def markdown(report):
    lines = [f"# pin e2e: {report['run']}", "", f"session {report['session_id']}, model {report['model']}, passed: {report['passed']}", ""]
    if report["errors"]:
        lines += [f"errors: {report['errors']}", ""]
    if report["run"] == "three-compactions":
        lines += ["| boundary | trigger | pre tokens | post tokens | injected == pinned | UTF-16 units | in reminder | stream agrees |",
                  "|---|---|---|---|---|---|---|---|"]
        lines += [f"| {r['boundary']} | {r['trigger']} | {r['pre_tokens']} | {r['post_tokens']} | {r['injected_equals_pinned']} | "
                  f"{r['utf16_units']} | {r['in_rendered_reminder']} | {r['stream_agrees']} |" for r in report["rows"]]
        lines += ["", f"pin confirmed in reply: {report.get('pin_confirmed')}; pin turn obeys probe: {report.get('pin_turn_obeys_probe')}",
                  f"pin file equals pinned text: {report.get('pin_file_equals_pinned')}",
                  f"auto compaction: {report.get('auto_compaction')}",
                  f"final probe reply ends with the token: {report.get('final_probe_reply_ends_with_token')}",
                  f"distinct boundaries: {report['distinct_boundaries']} (stream {report['boundaries_in_stream']}, transcript {report['boundaries_in_transcript']})"]
    else:
        lines += [f"inline plugins loaded: {report['inline_plugins_loaded']}",
                  f"pin complete: {report['pin_complete']} ({report['pin_units']} UTF-16 units)",
                  f"live-state complete: {report['live_state_complete']} ({report['live_state_chars_injected']} chars injected, file {report['live_state_chars']} chars)",
                  f"sum: {report['sum_units']} UTF-16 units / {report['sum_chars']} chars",
                  f"attached strings (chars): {report['strings_attached']}",
                  f"hook responses: {report['hook_responses']}"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", help="result directory (default /tmp/pin-e2e/<timestamp>); must be outside the repository")
    parser.add_argument("--with-live-state", action="store_true", help="run 2: pin and t3code live-state together")
    parser.add_argument("--model", default="claude-haiku-5-5")
    parser.add_argument("--effort", default="low")
    parser.add_argument("--claude", default=shutil.which("claude") or str(Path.home() / ".local/bin/claude"))
    parser.add_argument("--config-dir", default=os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude"))
    parser.add_argument("--auto-pct", type=int, default=20, help="CLAUDE_AUTOCOMPACT_PCT_OVERRIDE for run 1")
    parser.add_argument("--auto-window", type=int, default=100000, help="CLAUDE_CODE_AUTO_COMPACT_WINDOW for run 1")
    parser.add_argument("--filler-words", type=int, default=500, help="words in one filler message of the auto-compaction phase")
    parser.add_argument("--max-filler-chunks", type=int, default=8)
    parser.add_argument("--pad-chars", type=int, default=6000, help="size of the pin text and the live-state file in run 2")
    parser.add_argument("--timeout", type=int, default=600, help="seconds to wait for one turn (max 600)")
    parser.add_argument("--no-cleanup", action="store_true", help="keep the pin file, the repository and the transcript")
    args = parser.parse_args(argv)
    out = Path(args.out or f"/tmp/pin-e2e/{datetime.now().strftime('%Y%m%d-%H%M%S')}").resolve()
    if out == REPO_ROOT or REPO_ROOT in out.parents:
        raise SystemExit("--out must be outside the repository: the output holds session content")
    out.mkdir(parents=True, exist_ok=True)
    trial, report, pin_data_existed = (run_combined if args.with_live_state else run_three)(args, out)
    report["cleanup_removed"] = [] if args.no_cleanup else trial.cleanup(pin_data_existed)
    (out / "result.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "result.md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))
    print(f"results in {out}", file=sys.stderr)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
