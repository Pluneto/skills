#!/usr/bin/env python3
"""PreToolUse hook on the Agent tool: a sub-agent never runs above the session that starts it.

Denies an Agent call when the sub-agent's effective model ranks above the parent's (haiku < sonnet < opus),
when its effective effort ranks above the parent's, or when the model is Fable (excluded from dispatch).
The parent's model is the newest `api-request` record's `params.model` or assistant `message.model` in the
transcript (hook input has no model field; the assistant message holding the Agent call isn't written yet);
its effort is the input's `effort`. When the parent's model can't be read, the call is allowed with a
warning on stderr, so a format change never blocks every sub-agent.

Python 3 stdlib only. Set AGENT_CAP_LOG=<file> to append each hook input to that file (debugging).
"""
import json
import os
import re
import sys
from pathlib import Path

TIERS = ("haiku", "sonnet", "opus")
EFFORTS = ("low", "medium", "high", "xhigh", "max")
TAIL = 4 << 20  # read at most the transcript's last 4 MiB
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---", re.S)


def tier(model):
    """haiku/sonnet/opus (alias or full id) -> 0/1/2; fable -> 'fable'; anything else -> None."""
    m = (model or "").lower()
    if "fable" in m:
        return "fable"
    return next((i for i, t in enumerate(TIERS) if t in m), None)


def parent_model(transcript_path):
    """The model of the last assistant message in the transcript, or None."""
    path = Path(transcript_path or "")
    if not path.is_file():
        return None
    with path.open("rb") as f:
        f.seek(max(0, path.stat().st_size - TAIL))
        lines = f.read().decode("utf-8", "replace").splitlines()
    for line in reversed(lines):
        if '"assistant"' not in line and '"api-request"' not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") == "api-request":  # written before the reply, so it already names this turn's model
            model = (d.get("params") or {}).get("model")
        elif d.get("type") == "assistant":
            model = (d.get("message") or {}).get("model")
        else:
            continue
        if model and not model.startswith("<"):  # skip "<synthetic>"
            return model
    return None


def effort_level(value):
    """An effort as the hook input or tool input gives it: a string or {"level": ...}."""
    if isinstance(value, dict):
        value = value.get("level")
    return value.lower() if isinstance(value, str) else None


def config_dir():
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def agent_definition(subagent_type, cwd):
    """Frontmatter of the agent definition named `subagent_type` ({} when none is found)."""
    if not subagent_type:
        return {}
    plugin, _, name = subagent_type.rpartition(":")
    dirs = []
    if not plugin:
        here = Path(cwd or ".").resolve()
        dirs += [p / ".claude" / "agents" for p in (here, *here.parents)]
        dirs.append(config_dir() / "agents")
    dirs += sorted(config_dir().glob(f"plugins/cache/*/{plugin or '*'}/*/agents"), reverse=True)
    for d in dirs:
        f = d / f"{name}.md"
        if f.is_file():
            m = FRONTMATTER.match(f.read_text(encoding="utf-8", errors="replace"))
            if not m:
                return {}
            return {k.strip(): v.strip().strip("'\"") for k, _, v in
                    (line.partition(":") for line in m.group(1).splitlines()) if v.strip()}
    return {}


def child_model(tool_input, definition, parent):
    env = os.environ.get("CLAUDE_CODE_SUBAGENT_MODEL")
    if env and os.environ.get("CLAUDE_CODE_SUBAGENT_MODEL_FORCE") == "1":
        return env
    model = tool_input.get("model") or definition.get("model")
    if model == "inherit":
        return parent
    return model or env or parent


def child_effort(tool_input, definition, parent):
    """The sub-agent's effective effort; relative values step from the effective default."""
    default = effort_level(definition.get("effort")) or effort_level(os.environ.get("CLAUDE_CODE_SUBAGENT_EFFORT")) \
        or parent
    asked = effort_level(tool_input.get("effort"))
    if asked in ("higher", "lower") and default in EFFORTS:
        i = EFFORTS.index(default) + (1 if asked == "higher" else -1)
        return EFFORTS[min(max(i, 0), len(EFFORTS) - 1)]
    return asked or default


def verdict(data):
    """None to allow, or the reason to deny."""
    tool_input = data.get("tool_input") or {}
    parent = parent_model(data.get("transcript_path"))
    definition = agent_definition(tool_input.get("subagent_type"), data.get("cwd"))
    model = child_model(tool_input, definition, parent)
    if tier(model) == "fable":
        return f"Sub-agent model {model} is excluded (Fable is never used). Pick haiku, sonnet or opus."
    if parent is None:
        print("agent_cap: parent model unknown (transcript unreadable); sub-agent allowed unchecked", file=sys.stderr)
        return None
    pt, ct = tier(parent), tier(model)
    if isinstance(pt, int) and isinstance(ct, int) and ct > pt:
        return (f"A sub-agent never runs above its parent: this session runs {parent}, the sub-agent would run "
                f"{model}. Use {TIERS[pt]} or a lower model, or do the work yourself.")
    parent_effort = effort_level(data.get("effort"))
    effort = child_effort(tool_input, definition, parent_effort)
    if parent_effort in EFFORTS and effort in EFFORTS and EFFORTS.index(effort) > EFFORTS.index(parent_effort):
        return (f"A sub-agent never thinks harder than its parent: this session runs at {parent_effort} effort, "
                f"the sub-agent would run at {effort}. Use {parent_effort} or lower.")
    return None


def main():
    raw = sys.stdin.read()
    if os.environ.get("AGENT_CAP_LOG"):
        with open(os.environ["AGENT_CAP_LOG"], "a", encoding="utf-8") as log:
            log.write(raw.strip() + "\n")
    try:
        reason = verdict(json.loads(raw))
    except Exception as e:  # never block every sub-agent because of a bug here
        print(f"agent_cap: {type(e).__name__}: {e}; sub-agent allowed unchecked", file=sys.stderr)
        return 0
    if reason:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": reason}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
