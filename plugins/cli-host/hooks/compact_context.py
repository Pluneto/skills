#!/usr/bin/env python3
"""Compaction hooks for sessions that keep a live-state file.

Usage: compact_context.py <Event> [--host t3|cli]. One script, three events (from the hook input's
`hook_event_name`, else argv[1]):
  PreCompact              print summary instructions
  SessionStart (compact)  re-inject the live-state file and the plan's Build log tail
  Stop                    at a turn boundary, past a context size, ask the agent to compact

Hosts (plugins/t3code and plugins/cli-host ship identical copies; each hooks.json passes its host):
  t3 (default)  T3 Code: only a thread (T3CODE_THREAD_ID, not a delegated task) with a live-state file is
                nudged, and the agent queues `/compact` to its own thread with t3_thread_send.
  cli           plain Claude Code: every main session in a git repository is nudged; the agent writes its
                live-state file (creating it if needed) and ends its turn with a `/compact` line the user runs.

The live-state file is `<common git dir>/live-state/<session_id>.md`, found from the hook's cwd. The common
dir is shared by all worktrees of a repository, so the file survives a worktree that is removed and recreated;
a file in the worktree's own git dir (where 1.1.0 kept it) is still found. On the cli host, with no such file,
the file is `~/.claude/live-state/<session_id>.md` (for sessions that can't write the git dir).
Every branch is a silent no-op outside a git repository, for a native sub-agent (`agent_id`), and on any
error; PreCompact and SessionStart also without the file, and Stop too on the t3 host.
Marker of a given nudge: `<session_id>.nudged` next to the file, cleared after a compaction.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

NUDGE_TOKENS = 250000          # context size at which Stop asks for a compaction; auto-compact (window 350000) follows at ~317k
NUDGE_ENV = "COMPACT_NUDGE_TOKENS"  # tests only
MAX_INJECT_CHARS = 9500        # Claude Code caps hook context at 10k chars
BUILD_LOG_LINES = 5
BUILD_LOG_LINE_CHARS = 300
UPDATED_CHARS = 80             # header fields are cut too, so the header always fits
PLAN_PATH_CHARS = 1000
TAIL_CHUNK = 64 * 1024         # first read from the end of the transcript; doubles until a usage line is found
SAFE_SESSION_ID = re.compile(r"^[\w.-]+$")

PRECOMPACT_TEXT = """\
The orchestrator's live-state file {path} is re-attached after this compaction, so the summary need not copy it. When writing the summary:
- Where the conversation records something newer than that file's `Updated:` time ({updated}) - a child started or reported, a PR merged, a question answered, a new rule - keep that newer fact explicitly.
- Keep verbatim: the rules the user gave in chat, the open questions to the user, the current milestone and next action, and the running children with their ids.
- Drop: CI logs, screenshots, command output and the detail of merged milestones."""

STOP_TEXT = """\
Context is {tokens} tokens: compact now, at this turn boundary. Do these in order and nothing else:
1. Rewrite the live-state file {path} so it holds everything you still need (keep its first two lines, `Updated:` and `Plan:`, with a fresh time). Only its first 9,000 characters come back after the compaction: put the facts you act on first, and move how-you-work text that the plan or a skill already holds out of it.
2. Call t3_thread_send with threadId "{thread}", mode "queue", and message "/compact " followed by a one-line focus (the plan path, the current milestone, your next action).
3. End your turn with no further tool calls."""

STOP_TEXT_CLI = """\
Context is {tokens} tokens: compact now, at this turn boundary. Only the user can start a compaction, so do these in order and nothing else:
1. Write the live-state file {path} (create it, and its folder, if missing) so it holds everything you still need: first line `Updated: <current UTC time>`, second line `Plan: <plan file path, or none>`, then short facts: the user's rules from this chat, open questions, the current step and the next action. Only its first 9,000 characters come back after the compaction: put the facts you act on first.
2. Reply in one short message: ask the user to run the line that follows, then make your last line exactly `/compact ` followed by a one-line focus (the plan or task, the current step, your next action). End your turn there, with no further tool calls."""

SYSTEM_MESSAGE_CLI = ("Context is {tokens} tokens. The agent is saving its state and will end its turn with a "
                      "/compact line: run it to compact before auto-compact cuts in mid-task.")


def git_dirs(cwd):
    """The repository's common git dir, then this worktree's own git dir (the pre-1.2.0 place)."""
    run = subprocess.run(["git", "-C", cwd, "rev-parse", "--path-format=absolute", "--git-common-dir", "--absolute-git-dir"],
                         capture_output=True, text=True)
    return list(dict.fromkeys(Path(line) for line in run.stdout.split("\n") if line)) if run.returncode == 0 else []


def state_paths(data, host):
    """(live-state file, nudge marker) for this session, or None when there is nothing to act on.
    On the cli host the file may not exist yet: then it is the one under ~/.claude/live-state."""
    session_id = data.get("session_id") or ""
    if data.get("agent_id") or not SAFE_SESSION_ID.match(session_id):
        return None
    directories = git_dirs(data.get("cwd") or os.getcwd())
    for directory in directories:
        state = directory / "live-state" / f"{session_id}.md"
        if state.is_file():
            return state, state.with_suffix(".nudged")
    if host == "cli" and directories:
        state = Path.home() / ".claude" / "live-state" / f"{session_id}.md"
        return state, state.with_suffix(".nudged")
    return None


def field(text, name):
    match = re.search(rf"^{name}:[ \t]*(.+?)[ \t]*$", text, re.M)
    return match.group(1) if match else ""


def build_log_tail(plan_path):
    """Last lines of the plan's Build log section, each cut; ([], False) when there is none."""
    try:
        lines = Path(plan_path).read_text(encoding="utf-8", errors="replace").splitlines()
    except (OSError, ValueError):
        return [], False
    start = next((i for i, line in enumerate(lines) if re.match(r"#+\s*build log\b", line, re.I)), None)
    if start is None:
        return [], False
    section = []
    for line in lines[start + 1:]:
        if re.match(r"#{1,6}\s", line):  # the next heading; a log line like "#29 merged" is not one
            break
        if line.strip():
            section.append(line)
    tail = section[-BUILD_LOG_LINES:]
    cut = any(len(line) > BUILD_LOG_LINE_CHARS for line in tail)
    return [line[:BUILD_LOG_LINE_CHARS] for line in tail], cut


def inject_text(state_path):
    state = state_path.read_text(encoding="utf-8", errors="replace")
    plan = field(state, "Plan")[:PLAN_PATH_CHARS]
    updated = field(state, "Updated")[:UPDATED_CHARS]
    log, log_cut = build_log_tail(plan) if plan else ([], False)
    log_block = ("Build log (last lines of the plan):\n" + "\n".join(log)) if log else ""

    def header(state_cut):
        cuts = []
        if state_cut:
            cuts.append("the live-state file below is cut")
        if log_cut:
            cuts.append(f"Build log lines are cut to {BUILD_LOG_LINE_CHARS} chars")
        note = (f" Cut: {'; '.join(cuts)}. Your first tool call must Read the live-state file in full, then the plan's Build log."
                if cuts else "")
        return (f"Live state restored after compaction. Live-state file: {state_path}. Plan: {plan or '(none named)'}. "
                f"File updated: {updated or '(unknown)'}.{note}")

    def assemble(head, body):
        return "\n\n".join(part for part in (head, body, log_block) if part)

    text = assemble(header(False), state.strip())
    if len(text) <= MAX_INJECT_CHARS:
        return text
    head = header(True)
    marker = "\n[... cut, Read the file for the rest]"
    room = MAX_INJECT_CHARS - len(assemble(head, marker))
    return assemble(head, state.strip()[:max(room, 0)] + marker)[:MAX_INJECT_CHARS]


def read_tail_usage(transcript_path):
    """Context size of the last main-thread assistant line after the last compaction, or None."""
    size = os.path.getsize(transcript_path)
    chunk = TAIL_CHUNK
    with open(transcript_path, "rb") as handle:
        while True:
            start = max(size - chunk, 0)
            handle.seek(start)
            lines = handle.read(size - start).split(b"\n")
            if start > 0:
                lines = lines[1:]  # first line is probably cut in half
            found = usage_in(lines)
            if found is not None or start == 0:
                return found if found != "boundary" else None
            chunk *= 2


def usage_in(lines):
    """Newest-first scan: a token count, "boundary" if a compaction comes first, None if neither is here."""
    for raw in reversed(lines):
        if b'"assistant"' not in raw and b"compact_boundary" not in raw:
            continue
        try:
            entry = json.loads(raw)
        except ValueError:
            continue
        if entry.get("type") == "system" and entry.get("subtype") == "compact_boundary":
            return "boundary"
        if entry.get("type") != "assistant" or entry.get("isSidechain"):
            continue
        usage = (entry.get("message") or {}).get("usage") or {}
        total = sum(usage.get(key) or 0 for key in
                    ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
        if total:
            return total
    return None


def nudge_threshold():
    try:
        return int(os.environ.get(NUDGE_ENV) or NUDGE_TOKENS)
    except ValueError:
        return NUDGE_TOKENS


def on_pre_compact(data, host, state, marker):
    if not state.is_file():
        return ""
    return PRECOMPACT_TEXT.format(path=state, updated=field(state.read_text(errors="replace"), "Updated")[:UPDATED_CHARS] or "unknown")


def on_session_start(data, host, state, marker):
    if data.get("source", "compact") != "compact":
        return ""
    marker.unlink(missing_ok=True)
    if not state.is_file():
        return ""
    return json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                              "additionalContext": inject_text(state)}}, ensure_ascii=False)


def on_stop(data, host, state, marker):
    thread = os.environ.get("T3CODE_THREAD_ID", "")
    on_t3 = host != "cli"
    if data.get("stop_hook_active") or marker.exists() or (
            on_t3 and (not thread or thread.startswith("thread:delegated-task:"))):
        return ""
    tokens = read_tail_usage(data["transcript_path"])
    if tokens is None or tokens < nudge_threshold():
        return ""
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(str(tokens))
    if on_t3:
        return json.dumps({"decision": "block", "reason": STOP_TEXT.format(tokens=tokens, path=state, thread=thread)})
    return json.dumps({"decision": "block", "reason": STOP_TEXT_CLI.format(tokens=tokens, path=state),
                       "systemMessage": SYSTEM_MESSAGE_CLI.format(tokens=tokens)})


HANDLERS = {"PreCompact": on_pre_compact, "SessionStart": on_session_start, "Stop": on_stop}


def main(argv):
    data = json.loads(sys.stdin.read() or "{}")
    host = argv[argv.index("--host") + 1] if "--host" in argv[:-1] else "t3"
    handler = HANDLERS.get(data.get("hook_event_name") or (argv[1] if len(argv) > 1 else ""))
    paths = state_paths(data, host) if handler else None
    return handler(data, host, *paths) if paths else ""


if __name__ == "__main__":
    try:
        out = main(sys.argv)
    except Exception:  # a hook must never fail the session
        out = ""
    if out:
        try:
            sys.stdout.buffer.write(out.encode("utf-8") + b"\n")
        except Exception:
            pass
    sys.exit(0)
