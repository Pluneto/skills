#!/usr/bin/env python3
"""Thread pin: instructions that survive compaction.

Two hook events, chosen by the hook input's `hook_event_name`:
  UserPromptSubmit        a line that is exactly `#pin` pins the rest of that message, word for word
  SessionStart (compact)  the pinned text is re-injected after every manual or automatic compaction

The pin lives in one file per thread under the plugin's data folder (CLAUDE_PLUGIN_DATA).
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

MAX_UNITS = 9500  # Claude Code caps hook output at 10,000, counted in UTF-16 code units
PIN_MARKER = re.compile(r"^[ \t]*#pin[ \t]*\r?$", re.I)
UNPIN_MARKER = re.compile(r"^[ \t]*#unpin[ \t]*\r?$", re.I)

HEADER = "Pinned instructions: the user set these instructions earlier in this thread and they are re-attached unchanged after the compaction."
CUT_NOTE = "The pin is cut here to fit the limit for hook output; the full text is in {path}."
CLEARED_NOTE ="The pin hook cleared this thread's pinned instructions because the user message has an #unpin line."
STORED_NOTE = ("The pin hook stored the {lines} lines below the #pin line of this user message. "
               "The user expects one line in your reply that confirms the instructions are pinned.")


def pin_path(data):
    key = os.environ.get("T3CODE_THREAD_ID") or data.get("session_id") or ""
    return Path(os.environ["CLAUDE_PLUGIN_DATA"]) / f"{hashlib.sha256(key.encode('utf-8')).hexdigest()}.txt"


def apply_message(stored, prompt):
    """(new pin text, newly pinned block, whether a pin was cleared) after one user message.
    `#pin` starts capturing the lines below it; `#unpin` drops the stored pin and anything captured so far."""
    block, capturing, cleared = [], False, False
    for line in prompt.split("\n"):
        if UNPIN_MARKER.match(line):
            cleared = cleared or bool(stored or block)
            stored, block, capturing = "", [], False
        elif PIN_MARKER.match(line):
            capturing = True
        elif capturing:
            block.append(line)
    added = "\n".join(block).strip("\n")
    return (f"{stored}\n\n{added}" if stored and added else stored or added), added, cleared


def context(event, text):
    return json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}, ensure_ascii=False)


def on_prompt(data, path):
    stored = path.read_text(encoding="utf-8") if path.is_file() else ""
    pin, added, cleared = apply_message(stored, data.get("prompt") or "")
    if not added and not cleared:
        return ""
    if pin:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(pin, encoding="utf-8")
    else:
        path.unlink(missing_ok=True)
    notes = [CLEARED_NOTE] if cleared else []
    if added:
        notes.append(STORED_NOTE.format(lines=len(added.split("\n"))))
    return context("UserPromptSubmit", " ".join(notes))


def utf16_units(text):
    return len(text.encode("utf-16-le")) // 2


def prefix_within(text, units):
    """The longest prefix of `text` that is at most `units` UTF-16 code units."""
    used = 0
    for index, char in enumerate(text):
        used += 2 if ord(char) > 0xFFFF else 1
        if used > units:
            return text[:index]
    return text


def inject_text(pin, path):
    text = f"{HEADER}\n\n{pin}"
    if utf16_units(text) <= MAX_UNITS:
        return text
    head = f"{HEADER} {CUT_NOTE.format(path=path)}\n\n"
    return head + prefix_within(pin, MAX_UNITS - utf16_units(head))


def on_session_start(data, path):
    if data.get("source", "compact") != "compact" or not path.is_file():
        return ""
    return context("SessionStart", inject_text(path.read_text(encoding="utf-8"), path))


HANDLERS = {"UserPromptSubmit": on_prompt, "SessionStart": on_session_start}


def main():
    data = json.loads(sys.stdin.read() or "{}")
    handler = HANDLERS.get(data.get("hook_event_name"))
    return handler(data, pin_path(data)) if handler and not data.get("agent_id") else ""


if __name__ == "__main__":
    try:
        out = main()
    except Exception:  # a hook must never fail the session
        out = ""
    if out:
        try:
            sys.stdout.buffer.write(out.encode("utf-8") + b"\n")
        except Exception:
            pass
    sys.exit(0)
