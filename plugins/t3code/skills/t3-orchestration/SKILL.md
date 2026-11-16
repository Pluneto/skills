---
name: t3-orchestration
description: T3 Code orchestration rules for starting, waiting on and cancelling child agents and threads. Load before delegating to child agents, sub-agents or threads on T3 Code (delegate_task, t3_thread_launch), including when build-this, research-this or review-this is about to start one.
---

# T3 orchestration

How T3 Code's orchestration tools behave, so a child is started, waited on and stopped without stalling the thread. T3 MCP tools are deferred: load a tool's schema with ToolSearch before its first call. A calling skill's own rule beats the defaults here.

## Pick the tool

- **Native sub-agent** (the Agent tool): same provider and model family as you, and it finishes this turn.
- **`delegate_task`**: another provider or model, settings the user named, background work, or a separate checkout. The child gets only `task` and no history, so the goal, files and checks go in it; it loads skills by name. `role` is implementation, research, review, design, test or general.
- **`t3_thread_launch`**: a new top-level thread, only when the user or a skill (dispatch) asks for one. "Subagent", "delegate" and "parallel" never mean one.
- **No T3 tools:** sub-agents; without those, do the work yourself or hand the user the prompt to paste into a new thread.

## Set it up

- Call `orchestrator_capabilities` once per thread, before the first `delegate_task`; again only after an error or when the user names another provider. Pass the model as `target.model`, effort and other settings as `target.options`.
- A provider or model that is unavailable: say so. Switching or falling back to a CLI is the user's call.
- `isolation`: `shared` (default) uses the parent checkout; `worktree` gives the child its own checkout from the parent commit (uncommitted edits stay out), for a separate branch or PR per child. The tool creates the checkout, never the shell or the task text.
- Omit `runtimeMode` unless the user asked for a supervised child.

## Wait

- Start children `async` and follow the tool's `next`. Waiting is the tool's job: no `task_status` on a running task, sleep loops or watchers.
- To wait on a thread, call `t3_thread_wait` with a bounded timeout. When it times out with a `next`, end your turn; without one, call it again.
- Read a finished child with `task_status` (`result_available`). A turn that ended with live child work is not done.
- Stop a run you replace or no longer need with `task_cancel` (not `t3_thread_interrupt`).
- A PR you wait on: `watch_pull_request`, then end the turn.

## Reviews and retries

- Every new review or re-check is a new `delegate_task` carrying the brief, the findings and any objections; a running child is not messaged.
- Fix small review findings yourself.
- After an error or lost reply, retry with the same `clientRequestId`.
- Mention a thread by its `link`.
- Question tools break child threads: a child or worker puts a question to the user as plain text.

## Live state on T3

When you own a build, add these lines to build-this's live-state file and rewrite them as each changes (a child started or reported, a PR merged, a preview stopped); you alone write the file, and a child's brief never names it:

```
Delegates: <task id> <link> - <what it builds>; one line each, or none
Watched PRs: <url> - <waiting on>; or none
Previews: <port> - tmux <session>; or none
Holds: <phone queue or device session, until when>; or none
```

## Building a plan's milestones with T3 children

When build-this delegates milestones here:

- Children run **one after another** in the shared checkout (`isolation: shared`, role implementation), on your provider unless the user named another, each committing to the current branch and never pushing.
- A T3 child can load skills: name them in its brief. It runs **review-this** on its own milestone diff (base: the HEAD you noted before it started, intent: the milestone) and commits only on approval.
- No approval (stalemate, budget end, blocked): nothing is committed, the milestone is **held**, its unfinished paths go in the Build log, and no further child starts in that checkout until the user resolves it.
- Research sub-agents that should run cheap: `delegate_task` with model `claude-haiku-5-5` and option `effort: high`.
