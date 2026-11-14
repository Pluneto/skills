---
name: dispatch
description: Take ownership of a repo's open agent tickets (or named issues, or a milestone's) on T3 Code and see them through with parallel workers until each is merged, parked or released.
argument-hint: "[issue numbers, e.g. 29 31, or milestone \"<name>\"]"
disable-model-invocation: true
---

# Dispatch

Take ownership of these issues and solve the problems that don't need the user on your own. Keep your own context window clean. Dispatch agents at the level each task needs.

You orchestrate; workers build. Provider, model, effort, sub-agents and how to split the work are your calls, per task, judged from the task alone.

First load **t3-orchestration** and read `docs/agents/issue-tracker.md`. Take from it the labels, the claim, release and winner commands, and from Parallel work: Max workers, Areas map, Land, Verify and Review commands, Main health command, Decision owner. Its Model database and Model tiers fields, and the model table they point to, were written for an earlier version of this skill: ignore them and run no command they name. Older batch issues' numbered prompts are from that version too: write each brief fresh from the list below.

## Guardrails

Each prevents a collision or a decision made without the user.

- **Claims.** A worker claims its issue with the doc's commands, checks it won before its first change, and releases it when merged or giving up. Claimed, draft and planned issues are not yours.
- **Hotspots.** Two workers never edit the same hotspot at once: files many tickets touch (generated types, registries, lockfiles, shared SQL functions), from the doc's Areas map, else `git log --name-only`. Blocked issues wait for their blockers; at most Max workers run at once.
- **User-level decisions** (product behaviour, UI or copy, scope, real data, privacy or security, a new dependency, service or cost) are parked: question, options and recommendation as an issue comment mentioning the Decision owner, the decision label, the same question as plain text in the thread (question tools break T3 threads), then wait. Everything else is an engineering call, noted in the PR.
- **Real data.** Workers write only to a local stack, never to shared or staging data.
- **Review, then merge.** Every PR is reviewed by a different model from its author's (the doc's Review command, else a sub-agent or `delegate_task` on another model), then the worker merges it once CI and main are green (a PR that fixes the red main merges on its own green CI). Dispatching is the user's go-ahead: end every brief with the line `merge if green`, which repos' land rules look for.
- **Red main first.** Only the fix merges onto a red main. Check with the doc's Main health command (blank: [main-health.md](main-health.md)), repair per [fix-ladder.md](../build-this/fix-ladder.md)'s Red main, then tell waiting workers to land again.

## Run

1. **Check the tracker.** Done when the doc describes a GitHub tracker; a local one hides claims from other threads, so stop and suggest one `/build-this` thread.
2. **Take stock.** Done when every open agent issue (only those named, or `--milestone "<name>"`) is free, taken or blocked, with priority and likely hotspots; human issues listed apart.
3. **Open the tracking issue** `Batch YYYY-MM-DD`: `- [ ] #<n> <title> · <provider, model, effort>` per issue in launch order, then blocked, taken and human issues. Keep it current: a fresh session resumes from it. Start without waiting for a go-ahead; the user says `stop` to halt.
4. **Launch** with `t3_thread_launch`: own worktree on `t3/<n>-<slug>` from the default branch (`startFromOrigin: true`), title `#<n> <title>`, the model and effort you chose (ids and options from `orchestrator_capabilities`), and a message pointing to the brief, written to a file outside the worktree. Done when each launch has a `#<n> → thread <link> (<provider>, <model>, <effort>)` comment on the tracking issue.
5. **Watch until settled**: every issue closed, parked or released. Block with bounded `t3_thread_wait` calls and stay in the turn meanwhile (overriding t3-orchestration's end-the-turn rule). Unblock what you can (answer engineering questions, relaunch stuck workers, repair red main) and launch the next issues as hotspots free up. Tick closed lines.
6. **Report once**: merged PRs, parked questions with URLs, released issues with why, stale claims (over a day old, no open PR). Close the tracking issue when every line is ticked.

## Worker brief

The worker sees nothing of this thread and a Codex or Mistral worker can't load skills: plain commands, no skill names. Beyond the issue it carries:

- repo, issue URL, batch, branch, and hotspots shared with other workers;
- read `AGENTS.md` first; acceptance criteria define done; a `decided:` comment is the user's answer;
- the doc's claim and release commands filled in, and the repo's check, verify and land commands;
- the guardrails that bind it: parking, real data, review, merge, red main;
- keep its context clean by handing search, logs and mechanical work to sub-agents it picks;
- a PR body with `Fixes #<n>`, verification, review result and choices made, then a short report.
