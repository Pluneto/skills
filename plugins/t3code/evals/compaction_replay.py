#!/usr/bin/env python3
"""Replay a long Claude Code session through /compact and score what it still knows.

Each trial forks the transcript (cut at a clean turn boundary, new session id) into a throwaway
detached `git worktree` of a repo at a given commit, launches `claude` the way T3 Code does
(stream-json, CLAUDE_CONFIG_DIR) and resumes the fork. It sends `/compact`, then the probe
questions, and scores the answers by fixed strings.

  compaction_replay.py scan TRANSCRIPT [--min-tokens N]
      list clean cut points (assistant turns that end in plain text) with their context size
  compaction_replay.py run --transcript T --cutoff-line N --repo R --commit C --probes P
      --out DIR [--worktree-root DIR] [--model M] [--plugin-dir D] [--trial baseline] [--trial ours:STATE_FILE] ...
      run the trials one at a time and print the score table (also written to DIR/scores.md)

A trial is `baseline` (no plugin, no live-state file) or `ours:STATE_FILE` (the plugin dir is loaded and
STATE_FILE is written to `<git dir>/live-state/<session id>.md` of the trial's worktree; `{worktree}` and
`{session_id}` in it are replaced). Repeat --trial; the same spec twice is two runs.

The probes file is JSON: {"preamble": "...", "probes": [{"q": "...", "all": ["id", "a|b"]}]}.
A probe passes when its answer contains every string of `all`; "a|b" accepts either. Matching ignores case,
markdown marks and extra whitespace. The script asks for one line per question, starting `A<number>:`.

The trial worktrees and the trial's transcripts under the config dir are removed afterwards; the raw stream,
answers, the text after the compaction and a result.json per trial stay in DIR (it holds the session's
content: keep it out of repositories). Requires python3 (stdlib only), git and the claude CLI.
"""
import argparse
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

FORMAT_NOTE = ("Reply with one line per question, each starting with its label: A1: ..., A2: ..., and so on. "
               "Keep each answer short and exact (ids, numbers, ports, names).")
NUDGE_MARKER = "at this turn boundary"  # text of the t3code Stop hook's nudge
PHASE_TIMEOUT = 1500


# ---------- transcript helpers ----------

def context_size(usage):
    return sum((usage or {}).get(key) or 0 for key in ("input_tokens", "cache_read_input_tokens",
                                                       "cache_creation_input_tokens"))


def read_lines(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read().splitlines()


def assistant_calls(lines):
    """(line number, entry, context size) for each main-thread model call, one per message id."""
    seen = None
    for number, raw in enumerate(lines, 1):
        try:
            entry = json.loads(raw)
        except ValueError:
            continue
        if entry.get("type") != "assistant" or entry.get("isSidechain"):
            continue
        message = entry.get("message") or {}
        if message.get("id") != seen:
            seen = message.get("id")
            yield number, entry, context_size(message.get("usage"))


def ends_in_text(entry):
    blocks = (entry.get("message") or {}).get("content") or []
    return bool(blocks) and blocks[-1].get("type") == "text" and not any(b.get("type") == "tool_use" for b in blocks)


def dangling_tool_calls(lines):
    """ids of tool_use blocks in `lines` that have no tool_result."""
    used, answered = set(), set()
    for raw in lines:
        try:
            entry = json.loads(raw)
        except ValueError:
            continue
        content = (entry.get("message") or {}).get("content")
        for block in content if isinstance(content, list) else []:
            if block.get("type") == "tool_use":
                used.add(block.get("id"))
            elif block.get("type") == "tool_result":
                answered.add(block.get("tool_use_id"))
    return used - answered


def fork_transcript(lines, cutoff_line, session_id):
    """The first `cutoff_line` lines under a new session id. Refuses a cut inside a tool call."""
    kept = lines[:cutoff_line]
    open_calls = dangling_tool_calls(kept)
    if open_calls:
        raise SystemExit(f"cutoff line {cutoff_line} leaves tool calls without a result: {sorted(open_calls)[:3]}")
    out = []
    for raw in kept:
        try:
            entry = json.loads(raw)
        except ValueError:
            out.append(raw)
            continue
        if "sessionId" in entry:
            entry["sessionId"] = session_id
        out.append(json.dumps(entry, ensure_ascii=False))
    return "\n".join(out) + "\n"


def project_slug(path):
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


# ---------- scoring ----------

def normalize(text):
    text = re.sub(r"[*_`]", "", text.replace(" ", " "))
    return re.sub(r"\s+", " ", text).strip().casefold()


def split_answers(text):
    """{number: answer text} from lines that start with `A<number>:`."""
    text = re.sub(r"[*`]", "", text)
    parts = re.split(r"(?m)^[ \t]*A(\d+)[ \t]*[:.)][ \t]*", text)
    return {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def score_probe(answer, expected):
    """(passed, missing strings) for one answer against a probe's `all` list."""
    if answer is None:
        return False, list(expected)
    haystack = normalize(answer)
    missing = [item for item in expected if not any(normalize(alt) in haystack for alt in item.split("|"))]
    return not missing, missing


def score_answers(final_text, probes):
    answers = split_answers(final_text or "")
    rows = []
    for number, probe in enumerate(probes, 1):
        passed, missing = score_probe(answers.get(number), probe["all"])
        rows.append({"n": number, "passed": passed, "missing": missing, "answer": answers.get(number)})
    return rows


# ---------- driving claude ----------

class Claude:
    """One claude process driven over stream-json, as T3 Code does it."""

    def __init__(self, cmd, env, cwd, capture):
        self.capture = open(capture, "w", encoding="utf-8")
        self.proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=open(str(capture) + ".err", "w"), text=True, bufsize=1)
        self.events = queue.Queue()
        threading.Thread(target=self._pump, daemon=True).start()

    def _pump(self):
        for line in self.proc.stdout:
            self.capture.write(line)
            self.capture.flush()
            try:
                self.events.put(json.loads(line))
            except ValueError:
                pass
        self.events.put(None)

    def send(self, text):
        self.proc.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n")
        self.proc.stdin.flush()

    def wait_result(self, timeout=PHASE_TIMEOUT):
        """The next `result` event, or None on timeout or exit."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                event = self.events.get(timeout=5)
            except queue.Empty:
                continue
            if event is None:
                return None
            if event.get("type") == "result":
                return event
        return None

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=30)
        except Exception:
            self.proc.kill()
        self.capture.close()


def claude_command(args, session_id, plugin_dir):
    settings = {"showThinkingSummaries": True}
    if args.deny:
        settings["permissions"] = {"deny": [f"{tool}({path})" for path in args.deny for tool in ("Read", "Grep", "Glob")]}
    cmd = [args.claude, "--output-format", "stream-json", "--verbose", "--input-format", "stream-json",
           "--thinking=adaptive", "--thinking-display=summarized", f"--effort={args.effort}", f"--model={args.model}",
           "--tools", args.tools, "--permission-mode=bypassPermissions", "--allow-dangerously-skip-permissions",
           "--include-partial-messages", "--resume", session_id, "--settings", json.dumps(settings)]
    if args.no_mcp:
        cmd += ["--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}']
    if plugin_dir:
        cmd += ["--plugin-dir", str(plugin_dir)]
    return cmd


def analyse_stream(capture):
    """Facts from a stream-json capture: init tools, compaction, per-call context, tool use, hook events."""
    info = {"tools": [], "boundary": None, "calls": [], "after_boundary": None, "tool_uses": [], "hook_events": {},
            "final_text": None, "results": 0, "nudge_fired": False}
    last_id, boundary_seen = None, False
    with open(capture, encoding="utf-8") as handle:
        stream = handle.read().splitlines()
    for line in stream:
        if NUDGE_MARKER in line:
            info["nudge_fired"] = True
        try:
            event = json.loads(line)
        except ValueError:
            continue
        kind, sub = event.get("type"), event.get("subtype") or ""
        if kind == "system" and sub == "init":
            info["tools"] = event.get("tools") or []
        elif kind == "system" and sub == "compact_boundary":
            meta = event.get("compact_metadata") or event.get("compactMetadata") or {}
            info["boundary"] = {"trigger": meta.get("trigger"), "pre_tokens": meta.get("pre_tokens", meta.get("preTokens")),
                                "post_tokens": meta.get("post_tokens", meta.get("postTokens"))}
            boundary_seen = True
        elif kind == "system" and sub.startswith("hook"):
            name = f"{sub}:{event.get('hook_event') or event.get('hook_name') or ''}"
            info["hook_events"][name] = info["hook_events"].get(name, 0) + 1
        elif kind == "assistant" and not event.get("parent_tool_use_id"):
            message = event.get("message") or {}
            for block in message.get("content") or []:
                if block.get("type") == "tool_use":
                    info["tool_uses"].append({"name": block.get("name"), "input": block.get("input")})
            if message.get("id") != last_id:
                last_id = message.get("id")
                size = context_size(message.get("usage"))
                info["calls"].append(size)
                if boundary_seen and info["after_boundary"] is None:
                    info["after_boundary"] = size
        elif kind == "result":
            info["results"] += 1
            info["final_text"] = event.get("result")
    return info


def prepare_worktree(repo, commit, path):
    subprocess.run(["git", "-C", repo, "worktree", "add", "--detach", "-q", str(path), commit], check=True)
    git_dir = subprocess.run(["git", "-C", str(path), "rev-parse", "--absolute-git-dir"], check=True,
                             capture_output=True, text=True).stdout.strip()
    return Path(git_dir)


def save_post_compact(transcript, dest):
    """Transcript lines from the compaction boundary to the first assistant answer: the summary and what was re-attached."""
    if not transcript.is_file():
        return
    lines = read_lines(transcript)
    start = next((i for i, raw in enumerate(lines) if '"compact_boundary"' in raw), None)
    if start is None:
        return
    kept = []
    for raw in lines[start:]:
        kept.append(raw)
        if '"type":"assistant"' in raw.replace(" ", "") and len(kept) > 1 and '"isCompactSummary"' not in raw:
            break
    dest.write_text("\n".join(kept) + "\n", encoding="utf-8")


def run_trial(args, spec, number, source_lines, probes_doc, outdir):
    label = spec.split(":", 1)[0]
    state_file = spec.split(":", 1)[1] if ":" in spec else None
    name = f"{label}-{number}"
    trial_out = outdir / name
    trial_out.mkdir(parents=True)
    session_id = str(uuid.uuid4())
    worktree = Path(args.worktree_root or args.out).resolve() / f"wt-{name}"
    config = Path(args.config_dir).expanduser()
    project_dir = config / "projects" / project_slug(worktree)
    git_dir = prepare_worktree(args.repo, args.commit, worktree)
    result = {"trial": name, "session_id": session_id, "model": args.model}
    try:
        project_dir.mkdir(parents=True)
        transcript = project_dir / f"{session_id}.jsonl"
        transcript.write_text(fork_transcript(source_lines, args.cutoff_line, session_id), encoding="utf-8")
        if label == "ours":
            target = git_dir / "live-state" / f"{session_id}.md"
            target.parent.mkdir(parents=True)
            text = Path(state_file).read_text(encoding="utf-8")
            target.write_text(text.replace("{worktree}", str(worktree)).replace("{session_id}", session_id), encoding="utf-8")
        env = dict(os.environ, CLAUDE_CONFIG_DIR=str(config), CLAUDE_CODE_ENTRYPOINT="t3-code",
                   T3CODE_THREAD_ID=f"replay-{name}")
        cmd = claude_command(args, session_id, args.plugin_dir if label == "ours" else None)
        session = Claude(cmd, env, str(worktree), trial_out / "stream.jsonl")
        probe_prompt = "\n\n".join([probes_doc["preamble"], FORMAT_NOTE] +
                                   [f"Q{n}: {p['q']}" for n, p in enumerate(probes_doc["probes"], 1)])
        try:
            session.send("/compact")
            compacted = session.wait_result()
            result["compact_result"] = bool(compacted)
            session.send(probe_prompt)
            answered = session.wait_result()
            result["answer_result"] = bool(answered)
        finally:
            session.close()
        save_post_compact(transcript, trial_out / "post-compact.jsonl")
        info = analyse_stream(trial_out / "stream.jsonl")
        rows = score_answers(info["final_text"], probes_doc["probes"])
        (trial_out / "answers.txt").write_text(info["final_text"] or "", encoding="utf-8")
        mcp_calls = [use["name"] for use in info["tool_uses"] if str(use["name"]).startswith("mcp__")]
        result.update({
            "score": sum(row["passed"] for row in rows), "of": len(rows),
            "failed": [{"n": r["n"], "missing": r["missing"], "answer": r["answer"]} for r in rows if not r["passed"]],
            "answers": {r["n"]: r["answer"] for r in rows},
            "boundary": info["boundary"], "context_after_compaction": info["after_boundary"],
            "max_context": max(info["calls"], default=None), "nudge_fired": info["nudge_fired"],
            "tools_loaded": [t for t in info["tools"] if str(t).startswith("mcp__")],
            "mcp_tool_calls": mcp_calls, "hook_events": info["hook_events"],
            "tool_calls": [f"{u['name']} {json.dumps(u['input'])[:160]}" for u in info["tool_uses"]],
        })
    finally:
        subprocess.run(["git", "-C", args.repo, "worktree", "remove", "--force", str(worktree)], capture_output=True)
        if project_dir.parent == config / "projects" and project_dir.name == project_slug(worktree):
            shutil.rmtree(project_dir, ignore_errors=True)
        (trial_out / "result.json").write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    return result


def table(results):
    head = "| trial | score | failed probes | context after compaction | trigger | pre-tokens | nudge | mcp calls |\n|---|---|---|---|---|---|---|---|"
    rows = []
    for r in results:
        boundary = r.get("boundary") or {}
        failed = ", ".join(f"P{f['n']}" for f in r.get("failed", [])) or "-"
        rows.append(f"| {r['trial']} | {r.get('score', '?')}/{r.get('of', '?')} | {failed} | "
                    f"{r.get('context_after_compaction')} | {boundary.get('trigger')} | {boundary.get('pre_tokens')} | "
                    f"{'fired' if r.get('nudge_fired') else 'silent'} | {len(r.get('mcp_tool_calls', []))} |")
    return head + "\n" + "\n".join(rows)


# ---------- commands ----------

def command_scan(args):
    lines = read_lines(args.transcript)
    for number, entry, size in assistant_calls(lines):
        if size >= args.min_tokens and ends_in_text(entry) and not dangling_tool_calls(lines[:number]):
            print(f"line {number}  {entry.get('timestamp', '')}  context {size}")


def command_run(args):
    outdir = Path(args.out).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    probes_doc = json.loads(Path(args.probes).read_text(encoding="utf-8"))
    source_lines = read_lines(args.transcript)
    if not args.trial:
        raise SystemExit("give at least one --trial")
    if any(t.startswith("ours") for t in args.trial) and not args.plugin_dir:
        raise SystemExit("an `ours` trial needs --plugin-dir")
    results = []
    for number, spec in enumerate(args.trial, 1):
        results.append(run_trial(args, spec, number, source_lines, probes_doc, outdir))
        print(table(results[-1:]).splitlines()[-1], file=sys.stderr)
    text = table(results)
    (outdir / "scores.md").write_text(text + "\n", encoding="utf-8")
    print(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan")
    scan.add_argument("transcript")
    scan.add_argument("--min-tokens", type=int, default=0)
    run = sub.add_parser("run")
    run.add_argument("--transcript", required=True)
    run.add_argument("--cutoff-line", type=int, required=True)
    run.add_argument("--repo", required=True)
    run.add_argument("--commit", required=True)
    run.add_argument("--probes", required=True)
    run.add_argument("--out", required=True, help="existing or new directory for the results; trial worktrees go inside it")
    run.add_argument("--worktree-root", help="directory for the trial worktrees (default: --out); keep it apart from the probes")
    run.add_argument("--trial", action="append", help="baseline | ours:STATE_FILE (repeat)")
    run.add_argument("--plugin-dir")
    run.add_argument("--model", default="claude-fable-5-2")
    run.add_argument("--effort", default="medium")
    run.add_argument("--claude", default=str(Path.home() / ".local/bin/claude"))
    run.add_argument("--config-dir", default=os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude"),
                     help="CLAUDE_CONFIG_DIR for the trials (default: the caller's, else ~/.claude)")
    run.add_argument("--tools", default="Read,Grep,Glob", help="tools the session may use (default: read-only)")
    run.add_argument("--deny", action="append", help="path pattern Read, Grep and Glob must not touch (repeat)")
    run.add_argument("--no-mcp", action="store_true", help="start with no MCP servers")
    args = parser.parse_args(argv)
    return command_scan(args) if args.command == "scan" else command_run(args)


if __name__ == "__main__":
    sys.exit(main())
