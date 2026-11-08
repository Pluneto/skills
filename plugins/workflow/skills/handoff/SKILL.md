---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS - not the current workspace.

Start the document with a **Prompt for the next session**: a complete, ready-to-paste prompt a fresh agent can act on with no other context. It states the goal, where the work stands, the files, plans, issues or commits to read (by path or URL), the skills to invoke first, and the exact first action. Then print the same prompt in a fenced block in your reply, after the file's full path, so the user can copy it without opening the file.

Include a "suggested skills" section in the document, naming which skills the next agent should invoke.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
