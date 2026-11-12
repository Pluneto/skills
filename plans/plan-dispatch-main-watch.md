# Plan: dispatch watches main for red

Created 2026-11-12 with /plan-this. Attach this file to a Claude chat and run /build-this (or say "build this plan") to continue.

## Goal

Original request (the user's words):

> The dispatch skill ran into a problem that unlike the build-this skill it doesn't monitor main for red, so main just stayed red while another agent tried merging onto it.

Gaps found in the current text (workflow 1.9.0):
- `dispatch/SKILL.md` step 8 repairs red main only in a **chain**. After `launch wave <N>` the orchestrator ends its turn: a worker files `Main is red` and parks `waiting on main`, and no fixer is ever started.
- Even in a chain, the orchestrator looks at main only after `t3_thread_wait` settles the whole wave, not while workers are merging.
- The **Main health command** (tracker template, `issue-tracker-github.md` line 100) reads the newest *run* on the default branch, not the head *commit*. Right after a merge, before GitHub has created that commit's push run, it prints the previous commit's `green`, so a second worker merges onto a main that is about to be red.
- Red from outside the batch (a human push) is only seen when a worker next tries to merge.

**Approved goal:** Make dispatch watch main for red the way build-this does. Whenever a wave is running (single or chained), the orchestrator watches the default branch and starts fix-ladder's Red main as soon as a run goes red. Workers can't merge onto a red or unverified main, because Main health checks the head commit itself, not the newest run. When main is green again, the workers that are waiting get woken. Guarantee, as narrowed in decision 8: no worker merges onto a head already known red or not yet checked; two workers landing within one CI run of each other are caught afterwards by the watcher and each merger's post-merge check.

**Constraints:**
- Edit only source under `plugins/` (plus `docs/agents/issue-tracker.md`, `scripts/`, `plans/` and generated marketplace files), never the plugin cache under `~/.claude-pool/plugins`.
- Bump with `scripts/bump`: workflow minor (1.9.0 to 1.10.0), setup patch (1.3.0 to 1.3.1); run `scripts/build-marketplace` and `scripts/validate` (needs PyYAML: `python3 -m venv /tmp/skills-venv && /tmp/skills-venv/bin/pip install pyyaml`, its bin first on PATH).
- Keep the non-T3 fallback (point to the prompts in the tracking issue) and the plain-message (no question tool) rule in step 8.
- Use tier and family names, never version numbers, in skill text.
- Pluneto repo (`Pluneto/skills`): one branch, one PR; merge only on "merge if X".
- Code follows KISS, and SOLID for object-oriented code (here: skill Markdown and one small test script).

**Skills used while planning:** none. considered design-review, skipped: the race is already located in one `jq` command and the change is skill prose, not a system boundary with users. considered skill-tools:writing-for-agents, skipped in planning: it is a build-phase skill.

**Plan review:** Codex gpt-6.1-sol at high effort, 3 rounds - approved. Fixed: S1 a wave settles only after every worker thread finishes (post-merge triage included) and a last Main health; S2 head SHA from the branch, push time from the activity API only when its SHA matches, unknown push time stays pending; S3 an unsuperseded failure is red even while other runs are pending; S4 one source file `dispatch/main-health.md`, old tracker docs' default resolves to it. Re-asked: S5 near-simultaneous merges (decision 8: guarantee narrowed). Disagreed, declined: none.

## How we'll know it worked

- A fixture test (`scripts/test-main-health`, run by `scripts/validate`) feeds the new Main health command recorded JSON and asserts: head commit with a green run → `green`; head commit with a failed run → `red <url>`; head pushed under 2 minutes ago with no run, older commit green → `pending`; head pushed over 2 minutes ago with no run, newest commit with runs green → `green` (and red → `red <url>`); an old-dated commit pushed just now with no run → `pending` (grace counts from the push, not the commit date); activity unavailable, or its `after` still the previous SHA, with a head that has no run → `pending`; head with a `cancelled` run plus a newer successful run of the same workflow for the same commit → `green`; `cancelled` alone → `red <url>`; an in-progress run alone → `pending`; one failed and one in-progress run on the head → `red <url>`.
- `scripts/validate` and `scripts/build-marketplace --check` pass.
- The command run live against a real repo with push CI (e.g. `PlunetoD/<some repo>` or `Pluneto/splitscan-v2`, read-only) prints `green`, `pending` or `red <url>` matching `gh run list` by hand.
- Reading dispatch step 8: `launch wave <N>` keeps the orchestrator in its turn until the wave settles, runs Main health between waits, and starts Red main on red; a chain does the same during each wave.
- review-this from the other provider approves the diff.

## Decisions

| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | Who may merge a dispatch fixer's PR | Always, once its CI is green, even without `merge if green`, unless a stricter repo-owner rule (CLAUDE.md, e.g. the box's "merge if" rule for Pluneto repos) forbids it; then the fixer opens the PR and the orchestrator reports it | Red main blocks every worker; the owner's rule overrides skills anyway, so the text must not contradict it |
| 2 | How a single wave is watched | The orchestrator stays in its turn as a chain does: `t3_thread_wait` on the wave's threads with a ~10-minute timeout, Main health between waits, until the wave settles: every worker thread has finished its turn (which comes after its post-merge triage) or is parked on a decision, no Red-main repair is running, and one last Main health after the last thread prints `green` (or the red is handed to Red main) | Reuses the chain loop; red caught within ~10 minutes. Accepted: the dispatch thread stays busy for the whole wave |
| 3 | A head commit with no CI run | `pending` for 2 minutes after the head was pushed; after that, judge the newest commit that has push runs. The head SHA comes from the branch itself (`gh api repos/{owner}/{repo}/commits/<default branch> --jq .sha`); the push time from the repository activity API (`gh api 'repos/{owner}/{repo}/activity?ref=refs/heads/<default branch>&per_page=1'`: `after`, `timestamp`; checked live on `Pluneto/skills`), used only when its `after` equals the head SHA. Push time unknown (activity unavailable or lagging): a head without runs stays `pending`, never judged by commit date | Closes the no-run-yet race; a docs-only or `[skip ci]` merge costs at most 2 minutes; commit dates can be old for a freshly pushed commit |
| 4 | Main health with a Land command | The orchestrator always runs Main health; the land script still guards each worker's own merge | Orchestrator needs one signal regardless of how workers land |
| 5 | `cancelled` runs and mixed states | A `cancelled` run is ignored when the same commit has a newer run of the same workflow; otherwise it counts as failed. Any failed run that is not superseded makes the result `red`, even while other runs are pending; `pending` only when nothing failed | `concurrency: cancel-in-progress` setups shouldn't read as red; a failed workflow must not hide behind a slow one |
| 6 | Versions and copies | workflow 1.10.0, setup 1.3.1; update the template `issue-tracker-github.md` and this repo's `docs/agents/issue-tracker.md`; rebuild the marketplace | Behaviour change in workflow; template text change in setup |
| 7 | How the health command is tested | A small fixture script `scripts/test-main-health` with recorded `gh` JSON, called from `scripts/validate`, testing the command text taken from its one source file | Repo has no CI; validate is the gate |
| 8 | How far the merge guarantee goes | Narrowed: no merge onto a head already known red or unchecked; no merge lock and no branch protection | No new locking, waves stay fast; the watcher and post-merge checks catch two near-simultaneous merges |
| 9 | Where the default command lives, and old tracker docs | One source: `plugins/workflow/skills/dispatch/main-health.md` (the command in one fenced block). The template's field says `[blank: dispatch's main-health.md]`. Dispatch treats a Main health field that is blank or still holds the old generated default (starts with `[blank:`) as "use main-health.md"; a custom command is kept | Repos set up before this change carry the old racy command in their doc; a custom command is the owner's choice |

Accepted defaults: the "always merge" fixer rule applies to dispatch only (build-this keeps fix-ladder step 4's go-ahead rule); waking workers stays `t3_thread_send` "main is green, land again" to every worker that commented `waiting on main`; the stall rules of a chain are unchanged, and a single wave reports the same stalls when it settles.

## Needs from you

- *needed early:* none.
- *can wait:* merging the PR (Pluneto repo: needs "merge if" from you).

## Steps

### M1 Main health checks the head commit

- [x] Bump versions first: `scripts/bump workflow minor`, `scripts/bump setup patch`.
- [x] Write `scripts/test-main-health` first with fixture JSON for every case under "How we'll know it worked"; it fails against the current command.
- [x] Write the new command in `plugins/workflow/skills/dispatch/main-health.md` (decision 9): read the head SHA from the branch and the push time from the activity API (decision 3), the push runs (`gh run list --branch <default branch> --event push --limit 50 --json headSha,status,conclusion,url,workflowName,createdAt`), and apply decisions 3 and 5. Keep it a single copy-pasteable command (a short `sh -c` with `jq` is fine) whose `gh` calls the test can replace with fixture JSON.
- [x] In `plugins/setup/skills/setup-pluneto-skills/issue-tracker-github.md` and this repo's `docs/agents/issue-tracker.md`, set the field's blank text to `[blank: dispatch's main-health.md]` and drop "used only without a Land command" (decision 4: workers without one still use it before merging; the orchestrator always does).
- [x] Hook the test into `scripts/validate`; run validate.
- [x] Run the command once live, read-only, on a repo with push CI and compare with `gh run list` by hand.

**Done when:** `scripts/test-main-health` passes every case (and fails at least the no-run-yet and mixed-state cases against the old command), `scripts/validate` passes, and the live run matches `gh run list`.

**Skills:** engineering:tdd - Need: the fixture test must prove the no-run-yet race before the command changes; Provides: red-green order (failing test against the old command first); Without it: a test written after the command just mirrors it and never shows the race.

### M2 Dispatch watches main during every wave

- [ ] `dispatch/SKILL.md` steps 1 and 5: resolve Main health per decision 9 (blank or old `[blank:` default → main-health.md; custom kept) and fill `<main health command>` with the result.
- [ ] `dispatch/SKILL.md` step 8: after launching any wave (single or in a chain), stay in the turn: `t3_thread_wait` on the wave's threads with a ~10-minute timeout, run Main health after each return (this loop overrides t3-orchestration's end-the-turn rule, as the chain already says), and tick closed lines. A single wave ends the loop when the wave settles as decision 2 defines it, then reports and waits for the next reply as today.
- [ ] Move "Red main in a chain" to apply to every launch: on `red <url>` (or an open `Main is red` issue), follow fix-ladder's Red main, launching the fixer thread as today; its go-ahead is decision 1 (always, unless the repo owner's rule is stricter: then report the green fix PR and keep watching). Resume and wake waiting workers exactly as the chain does now.
- [ ] `build-this/fix-ladder.md` Red main step 4: add "a dispatch orchestrator's fixer" to the go-aheads, subject to the owner's rule; nothing else changes for build-this.
- [ ] `dispatch/worker-prompt.md`: fill `<main health command>` for every worker (also with a land command, for the post-merge check if useful) only if needed; keep the prompt's own red-main report unchanged.
- [ ] Keep step 8 no longer than needed: cut chain text that now duplicates the shared loop.
- [ ] `scripts/build-marketplace`, `scripts/validate`.

**Done when:** a walk-through of the last-worker case (the final worker merges, its ticket closes, its main run then goes red) shows the loop still running and starting Red main; an old tracker doc holding the `[blank: ...gh run list...]` default resolves to main-health.md; step 8 reads as above for both `launch wave <N>` and chains, fix-ladder step 4 names the dispatch go-ahead, `scripts/validate` and `scripts/build-marketplace --check` pass, and review-this (other provider) approves the diff.

**Skills:** skill-tools:writing-for-agents - Need: rewriting dispatch step 8 and fix-ladder Red main, read by agents on every launch; Provides: branch-per-pointer wording and pruning of always-loaded text; Without it: step 8 grows by a duplicated loop instead of one shared one.

## Risks and assumptions

- **The dispatch thread stays busy during a wave.** The user can still type into it (T3 queues the message); the loop handles `status` replies after the next wait returns. Mitigation: 10-minute timeout keeps replies at most that late.
- **GitHub sometimes creates push runs later than 2 minutes** (outages). Then Main health judges the previous commit; the orchestrator's watcher and each merger's post-merge triage still catch red. Assumption to confirm on the live run.
- **Two workers merge within one CI run of each other** (decision 8): accepted; the second merger's post-merge triage and the orchestrator's next Main health catch it, and Red main repairs it.
- **The activity API lags or is unavailable** for a repo: a head without runs then stays `pending`; workers already stop after 30 minutes of pending and report, and the orchestrator's next check retries. Confirm the lag on the live run.
- **Workflows triggered by something other than `push`** on main (e.g. `workflow_run`) aren't counted. Same as today.
- **Always-merge fixer** could merge a wrong fix; the fixer's own review step and the post-merge triage (Confirm step) remain, and a failed strong rung blocks.
- **No CI in `Pluneto/skills`:** local `scripts/validate` output in the PR body is the gate.

## Build log

- M1 Main health checks the head commit (here): check pass - test-main-health 13/13 (old command fails 6, incl. no-run-yet and mixed-state), validate ok, live: splitscan-v2 `pending` (CI in progress), zephyr-homelab `green` via the no-run fallback, both match gh run list; deviations: command uses gh's own `--jq` with `$ENV` (no separate jq dependency for workers), the test stub uses jq 1.7 while gh uses gojq, so the live run is the gojq check; owed: none; skills: tdd: old command run first as the red step, proving the race before the rewrite
