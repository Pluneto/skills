---
name: t3-orchestration
description: T3 Code orchestration rules for starting, waiting on and cancelling child agents and threads. Load before using delegate_task, t3_thread_launch or sub-agents on T3 Code.
---

# T3 orchestration

The rules for T3 Code's orchestration tools. T3 MCP tools are deferred: load a tool's schema with ToolSearch before its first call. A calling skill's own rule beats the defaults here.

## Pick the tool

- **Native sub-agent** (the Agent tool): same provider and model as you, and it finishes this turn.
- **`delegate_task`**: another provider or model, settings the user named, background work, or a separate checkout. The child gets only `task` and no history, so put the goal, files and checks in it; it loads skills by name. `role` is implementation, research, review, design, test or general.
- **`t3_thread_launch`**: a new top-level thread, only when the user or a skill (dispatch) asks for one. "Subagent", "delegate" and "parallel" never mean one.
- **No T3 tools:** sub-agents; without those, do the work yourself or hand the user the prompt to paste into a new thread.

## Set it up

- Call `orchestrator_capabilities` once per thread, before the first `delegate_task`; again only after an error or when the user names another provider. Pass model as `target.model` and effort and other settings as `target.options`.
- A provider or model that is unavailable: say so. Never switch unasked or fall back to a CLI or workflow.
- `isolation`: `shared` (default) uses the parent checkout; `worktree` gives each child its own checkout from the parent commit (uncommitted edits stay out), for a separate branch or PR per child. Never create a child's checkout in the shell or the task text.
- Omit `runtimeMode` unless the user asked for a supervised child.

## Wait

- Start children `async` and follow the tool's `next`. Never poll: no `task_status` on a running task, sleep loops or watchers.
- To wait on a thread, call `t3_thread_wait` with a bounded timeout. When it times out with a `next`, end your turn; without one, call it again.
- Read a finished child with `task_status` (`result_available`). A turn that ended with live child work is not done.
- Stop a run you replace or no longer need with `task_cancel`, not `t3_thread_interrupt`.

## Checks, CI and fixes

- Waiting on CI, running predictable checks and repairing red follow build-this's [fix-ladder.md](../build-this/fix-ladder.md): no child waits idle (use `watch_pull_request` for a PR), a light child runs and triages, fixers climb standard then strong.

## Reviews and retries

- Every new review or re-check is a new `delegate_task` with the brief, the findings and any objections, not a message to a running child.
- Fix small review findings yourself.
- After an error or lost reply, retry with the same `clientRequestId`.
- Mention a thread by its `link`.
