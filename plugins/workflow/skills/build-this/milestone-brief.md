# Milestone brief, Build log and handoff file

## The brief

In children mode, fill the `<…>` fields per milestone and drop the bracketed lines that don't apply. The child sees nothing of the conversation, so the brief must stand alone. A **T3 child** can run skills: name them. A **sub-agent** often can't: give skills only as file paths, since naming one can trigger it inside the sub-agent and end its run early.

```
You are building one milestone of an agreed plan. Its decisions are settled: build what it says.

Plan file: <path>. Read its Goal, Constraints and Decisions, and the milestone below; other milestones belong to other workers.
[Ticket: <path, or issue number and URL>. Read it whole (`gh issue view <n> --comments`); its acceptance criteria are the Done when. The plan file is the one it was split from; drop that line when there is none.]
Milestone: <M<n>. title>
Steps: <the milestone's checkbox steps>
Done when: <the check, with the exact command>
You own: <files or area>. Change nothing outside it [except <…>].
Decisions it touches: <# and choice of each bearing on this milestone>
Already built: <one line per earlier milestone this depends on, from the Build log>
[T3 child: Method: load the skill <name> and follow it for <the Provides part of its reason line>.]
[Sub-agent: Method: Read <path>/SKILL.md and follow it for <the Provides part of its reason line>.]
[Method notes: <key lines pasted for a skill with no file on disk>]

Rules:
- Solve problems with the closest fix that keeps the plan's intent; note each as a deviation.
- Ask no questions. Mark anything only the user can supply `TODO(user)`; reference secrets by variable name only.
- Stop before anything hard to undo or outside the workspace (spending money, deleting data, publishing, deploying, sending, signing in). Do the rest, then list it under "Held".
- Code follows KISS, and SOLID for object-oriented code.
- Run the done-when check yourself before reporting. Leave the plan file's ticks and Build log alone.
[T3 child, in a git repository: Base: <sha>. When the check passes, run review-this on your diff against the base, with this milestone as the intent; it asks nothing. Commit locally (message `M<n> <title>`) only when it approves, and never push. On a stalemate, budget end or block, commit nothing and report Held: review not approved, with the open items.]
[Sub-agent: commit nothing; the orchestrator reviews and commits.]

Reply with this report only, at most 150 words, no code or file contents:
Status: done | blocked
Check: <command> -> pass | fail (<one-line reason>)
Changed: <files>
Deviations: <one line each, or none>
Needs from user: <item -> where it goes, or none>
Held: <hard-to-undo step awaiting go-ahead, or review not approved with open items, or none>
Commit: <sha, or none>
Method: <what each method file changed, "no visible effect", or none>
```

## The Build log

At the end of the plan file add a `## Build log` the first time a milestone finishes or blocks, then one line per milestone, blocked ones included (left unticked). [tickets.md](tickets.md) says where it goes for tickets.

```
- M<n> <title> (<model>, <effort> | main agent): check pass|fail - <one-line result>; deviations: <…|none>; owed: <needs from user and held steps, or none>; skills: <skill: what it changed|none>
```

A fresh session reads this log, not the conversation: say what changed, what is still owed, and what the next milestone needs.

## The handoff file

Written when the user picks "Write a handoff file" at a check-in, so a fresh agent can continue the build.

- **Location:** the OS temp directory (`$TMPDIR`, else `/tmp`; `%TEMP%` on Windows), never the workspace. Name it `handoff-<short-topic>.md`.
- **Prompt first:** open with a **Prompt for the next session**: a complete, ready-to-paste prompt (goal, where the build stands, the plan file to read, the skills to load first, the exact first action). Show the same prompt in a fenced block in the reply.
- **Content:** milestones done with their check results, the one in progress, what remains; deviations and decisions with one-line reasons; blockers; the "can wait" items still owed. Tailor it to the next session's focus if the user named one.
- **Point, don't copy:** reference the plan file and Build log, specs, issues, commits and diffs by path or URL.
- **Suggested skills:** the skills the next agent should load, from the plan's Skills lines and those that changed something, each with a one-line reason.
- **Redact** keys, passwords and personal data; say where a secret lives (a named `.env` variable), never its value.
