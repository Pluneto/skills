# Milestone brief, Build log and handoff file

## The brief

In orchestrator mode, fill the `<…>` fields for each milestone's child and drop the bracketed lines that don't apply. The child sees nothing of the conversation, so the brief has to stand on its own. A **T3 child** can run skills: name them. A **sub-agent** often can't: refer to skills only by their file paths, because naming one can trigger it inside the sub-agent and end its run early.

```
You are building one milestone of an agreed plan. The plan's decisions are settled: build what it says.

Plan file: <path>. Read its Goal, Constraints and Decisions, and the milestone below; other milestones belong to other workers.
[For a ticket: Ticket: <path, or issue number and URL>. Read it whole (`gh issue view <n> --comments` for an issue); its acceptance criteria are the Done when. The plan file is the one it was split from; drop that line when there is none.]
Milestone: <M<n>. title>
Steps: <the milestone's checkbox steps>
Done when: <the check, with the exact command to run>
You own: <files or area>. Change nothing outside it [except <…>].
Decisions it touches: <# and choice of each plan decision that bears on this milestone>
Already built: <one line per earlier milestone this one depends on, from the Build log>
[T3 child: Method: load the skill <name> and follow it for <the Provides part of its reason line>.]
[Sub-agent: Method: Read <path>/SKILL.md and follow it for <the Provides part of its reason line>.]
[Method notes: <key lines pasted for a skill with no file on disk>]

Rules:
- Solve problems along the way with the closest fix that keeps the plan's intent, and note each one as a deviation.
- Ask no questions. Use a marked placeholder (`TODO(user)`) for anything only the user can supply, and reference secrets by variable name only.
- Stop before anything hard to undo or outside the workspace (spending money, deleting data, publishing, deploying, sending, signing in). Do everything else, then list it under "Held".
- Code follows KISS, and SOLID for object-oriented code.
- Run the done-when check yourself before reporting. Leave the plan file's ticks and Build log alone.
[T3 child, in a git repository: Base: <sha>. When the check passes, run review-this on your milestone's diff against the base, with this milestone as the intent; it asks nothing. Commit locally (message `M<n> <title>`) only when it approves, and never push. On a stalemate, budget end or block, commit nothing and report Held: review not approved, with the open items.]
[Sub-agent: commit nothing; the orchestrator reviews and commits.]

Reply with this report and nothing else, at most 150 words, with no code or file contents:
Status: done | blocked
Check: <command> -> pass | fail (<one-line reason>)
Changed: <files>
Deviations: <one line each, or none>
Needs from user: <item -> where it goes, or none>
Held: <hard-to-undo step waiting for a go-ahead, or review not approved with its open items, or none>
Commit: <sha, or none>
Method: <what each method file changed, or "no visible effect", or none>
```

## The Build log

Append a `## Build log` section at the end of the plan file the first time a milestone finishes or blocks, then add one line per milestone, blocked ones included (left unticked). For tickets, [tickets.md](tickets.md) says where the log goes.

```
- M<n> <title> (<model>, <effort> | main agent): check pass|fail - <one-line result>; deviations: <…|none>; owed: <needs from user and held steps, or none>; skills: <skill: what it changed|none>
```

A fresh session reads this log, not the conversation, so each line should say enough to build on: what changed, what is still owed, and anything the next milestone needs to know.

## The handoff file

Written when the user picks "Write a handoff file" at a check-in: a short Markdown document that lets a fresh agent continue the build.

- **Location:** the temporary directory of the user's OS (`$TMPDIR`, else `/tmp`; `%TEMP%` on Windows), never the project workspace. Name it `handoff-<short-topic>.md`.
- **Prompt first:** open the file with a **Prompt for the next session**, a complete ready-to-paste prompt (goal, where the build stands, the plan file to read, the skills to load first, the exact first action), and show the same prompt in a fenced block in the reply.
- **Content:** where the build stands (milestones done with their check results, the one in progress, what remains), deviations and decisions made so far with their one-line reasons, blockers, and the "can wait" items still owed by the user. If the user said what the next session will focus on, tailor the document to it.
- **Point, don't copy:** reference what other artifacts already hold (the plan file and its Build log, specs, issues, commits, diffs) by path or URL.
- **Suggested skills:** a section naming the skills the next agent should load with the Skill tool, taken from the plan's Skills lines and the skills that actually changed something so far, each with a one-line reason.
- **Redact** API keys, passwords and personal data (ID or account numbers, addresses): say where a secret lives (for example a named variable in `.env`), never its value.
