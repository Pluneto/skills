# Phase boundaries

A **phase** is a chunk of work inside a session (the interview, the implementation, the QA); it ends when you think *"ok, we're done with that"*. The **phase boundary** is the gap between two phases, and the only place this decision belongs. Mid-phase, continue, or split the remaining work into subagents; compacting mid-phase loses the thread.

## The five options

| Option | What it does |
| --- | --- |
| **Continue** | Stay in the session. No context switch. |
| **`/clear`** | Empty the context window and start from nothing. |
| **`/handoff`** | Write a portable markdown file and seed a session anywhere with it. |
| **Subagent** | Send the task to its own context window and get a report back. |
| **`/compact`** | Compress this context and seed a fresh session with the summary. |

## The tree

Work top to bottom at the boundary. The first **yes** wins.

1. **Can you continue in this session?** Yes when the next phase needs this phase as a **primary source** (interview to implementation is the standard yes: the implementation wants the reasoning verbatim), or enough room is left (~150k tokens, the [smart zone](https://www.aihero.dev/ai-coding-dictionary/smart-zone)) for the next phase to fit.
2. **Is the context irrelevant to what comes next?** If the exploration, decisions and dead ends are all disposable: **`/clear`**, the cheapest move, and the old session stays resumable. Clearing a *relevant* context loses the **why** behind what you built, and re-reading the diff won't restore it.
3. **Do you need to hand off?** **`/handoff`** only when swapping to a new harness (Claude to Codex), moving to a new directory or repo, sending the work to a colleague, or forking a side task found mid-phase. It buys **portability**; if nothing is travelling, skip it.
4. **Can the task be done AFK?** If it is scoped tightly enough to run with you away from the keyboard, send it to a **subagent** and leave this session untouched. Automated review is the standard case.
5. **Otherwise, `/compact`**: relevant context, same harness and directory, you need to stay in the loop. It is the default, not the first reach: pass it an instruction (`/compact we're going to QA this area`) so the summary keeps what the next phase needs, since a fresh session can be confidently wrong about a decision the summary flattened.

Every move except **Continue** turns a **primary source** into a **secondary** one (the session as it happened, replaced by a summary): lossy but less noisy, with more room to move. That is why question 1 comes first. The questions have taste in them; ask them **in order**, at the boundary.
