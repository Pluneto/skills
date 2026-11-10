# Plan: a fix ladder for orchestrated builds (issue #14)

Created 2026-11-10 with /plan-this. Attach this file to a Claude chat and run /build-this (or say "build this plan") to continue.

## Goal

Original request, [Pluneto/skills#14](https://github.com/Pluneto/skills/issues/14) "Let sub-agents troubleshoot during orchestration":

> Current Behavior: A main orchestrator agent during e,g, build-this with sub-agents has to troubleshoot the problems itself if a main marge / pr comes back red. Additionally the main orchestrator doesn't monitor main, and has to be reported by user.
> New Behavior: The main orchestrator dispatches haiku 5.5 agents to monitor the building sub agents and main that report back if problem. If a problem occurs then main orchestrator dispatches a sonnet 5.5 agent on medium to fix the problem, if the sonnet agent comes back and it is still broken escalate it to an opus 5.5 medium agent. Let the orchestrator be the orchestrator and let it delegate tasks smartly and save its own context window.
> Comment: Also let cheaper sub agents run and monitor predictable tests.

**Approved goal:** Give the workflow skills one shared **fix ladder** so an orchestrator only coordinates. Waiting costs no tokens: a background `gh run watch` (its completion re-invokes the orchestrator), or T3's `watch_pull_request` on T3 Code, never an idle agent. A **light** child (Haiku on Claude) runs predictable test suites and done-when checks, and triages red CI on PRs and on `main` after a merge, reporting at most 150 words that quote the command, the exit code and the last output lines. A failure goes to a **standard** fixer (Sonnet, medium effort), then a **strong** fixer (Opus, medium effort), each given a fixed handoff (the failure, the logs, what was already tried), then becomes a blocker for the user. It covers build-this (children mode, PR CI, `main` CI after a merge), dispatch (workers and the chain orchestrator), solve-this and t3-orchestration, keeps the non-T3 fallbacks, and bumps the workflow plugin.

**Constraints:**
- Edit only `plugins/workflow/` source (plus `plans/` and generated marketplace files), never the plugin cache under `~/.claude-pool/plugins`.
- Bump the workflow plugin minor (`scripts/bump workflow minor`: 1.6.0 to 1.7.0, new behaviour), run `scripts/build-marketplace` and `scripts/validate` (needs PyYAML: `python3 -m venv /tmp/skills-venv && /tmp/skills-venv/bin/pip install pyyaml`, its bin first on PATH).
- Keep the non-T3 fallbacks (plain sub-agents; doing it yourself when no child tool exists) and the existing question-tool use.
- Use tier and family names, never version numbers, in skill text (repo convention; research-this's existing Haiku 5.5 pin is out of scope).
- Pluneto repo: one branch, one PR; merge only on "merge if X".
- Code follows KISS, and SOLID for object-oriented code (here: skill Markdown; `scripts/` is not touched).

**Skills used while planning:**
- design-review (planning) - Need: several dispatch workers and the orchestrator can all see the same red `main` and start rival fixers, and the ladder needs a bounded end; Provides: backend race review and "alternatives before judging"; Without it: two fix PRs for one red `main`, or an unbounded ladder. Result: one fixer per red `main` via the `Main is red` issue as a claim; fixers never in the shared checkout while a builder runs; flake rerun first; no Haiku watching builder children; tiers instead of pinned versions.
- considered codebase-design, skipped: no code module designed. considered writing-for-agents, skipped in planning: build-phase skill. product-context skipped: the goal doesn't change who the plugin is for.

**Plan review:** Codex gpt-6.1-sol at high effort, 4 rounds - approved. Fixed: S1 one canonical `Main is red` issue (direct paginated listing, re-check after claim); S2 the chain resumes only on a green main run; S3 every merging agent triages main's run on its merge; S4 parked workers resumed, waiting on main is not a stall; S5 the ladder is the only repair loop and its end is terminal; S6 M4 adds a standard-to-strong-to-blocker case; S7 test unchanged proven against the fixture commit. Disagreed, declined, needs decision: none.

## How we'll know it worked

- `scripts/validate` and `scripts/build-marketplace --check` exit 0; the workflow plugin is at 1.7.0.
- Greps: `rg -n "fix-ladder.md" plugins/workflow/skills/{build-this/SKILL.md,build-this/tickets.md,solve-this/SKILL.md,t3-orchestration/SKILL.md,dispatch/SKILL.md}` hits each file; `rg -n -i "light|standard|strong" plugins/workflow/skills/build-this/fix-ladder.md` hits; `rg -n "5\.5" plugins/workflow/skills/build-this/fix-ladder.md plugins/workflow/skills/dispatch/worker-prompt.md` finds nothing; `rg -n "Main is red" plugins/workflow/skills/build-this/fix-ladder.md` hits.
- Live run (M4) on a private sandbox repo: a PR with a deliberately failing test goes red, the light triage reports it, the standard fixer pushes a fix, CI goes green; then a red `main` gets one `Main is red` issue, one fixer claim, a `Fix main: <sha>` PR that merges on green under the run's go-ahead, and main's next run is green. Evidence: the PR, issue and run URLs.
- review-this from Codex on the final diff returns VERDICT: APPROVE.

## Decisions

| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | Where the ladder lives | `plugins/workflow/skills/build-this/fix-ladder.md`; build-this, tickets.md, solve-this, t3-orchestration and dispatch point to it; dispatch's `worker-prompt.md` carries a self-contained copy of the worker part | One source, loaded only when needed, no always-on tokens; Codex workers can't load skills. Accepted: the inlined copy can drift (validate's PAIRED check can't cover a partial copy) |
| 2 | Model naming | Tiers light / standard / strong; on Claude the Haiku / Sonnet / Opus families; elsewhere the provider's own tiers (tracker doc's Model tiers line where set); efforts: light as needed by the caller (default medium), standard medium, strong medium | Works on Codex, survives model releases; matches dispatch's existing tier scheme. Accepted: less exact than the issue's 5.5 pins |
| 3 | Red main during a dispatch chain | The chain orchestrator auto-launches the main fixer (ladder) instead of stalling. It resumes only when the `Main is red` issue is closed **and** the Main health command reports green for the new main commit (closing via `Fixes #` happens at merge, before main's CI); a red run then is the next rung. Workers parked on red main are resumed by the orchestrator (`t3_thread_send` "main is green" to each parked thread), and a worker waiting on main is not a stall. It stalls only when the ladder ends in a blocker | User wants the chain to repair main unattended |
| 4 | Merge authority for main-fix PRs | Merge on green only when the run already has a merge go-ahead: a dispatch chain (which needs "merge if green"), "merge if" in the prompt, or the repo owner's rule; otherwise leave the green fix PR for the user | Keeps box rules; a Brain-style repo that deploys on merge never gets an unasked fix |
| 5 | Fixer rules | (a) never skip, delete or weaken tests or CI config to get green; (b) a fix PR gets the same cross-provider review as a worker PR, at most 2 rounds; (c) title `Fix main: <sha>`, body `Fixes #<Main is red issue>`; (d) after a merge the light child triages main's next run; red again counts as that rung failing; (e) every merging agent (worker, fixer, build-this landing a ticket) waits for and triages main's run for its merge commit before it reports done, opening or joining the `Main is red` issue when red | An unattended merge can't fake green; every fix is reviewed |
| 6 | One fixer per red main | The `Main is red: <sha>` issue is the lock. An observer lists open issues directly, not through indexed search (every page: `gh api --paginate 'repos/{owner}/{repo}/issues?state=open&per_page=100' --jq '.[] | select(.pull_request == null and (.title | startswith("Main is red"))) | .number' | sort -n | head -1`), opens one if none, then lists again: the open one with the lowest number is canonical (a later duplicate is closed with a comment linking it). It then claims the canonical issue with the tracker's Claim protocol (`claimed by <branch>` comment, winner command) and, after the claim is confirmed, lists once more and launches a fixer only if its issue is still the lowest-numbered open one; losers comment the run URL and wait | Design review: prevents rival fixers |
| 7 | Where fixers run | A PR fixer runs in that PR's checkout only when no builder child is running there (build-this children are sequential, so between children); a main fixer gets its own worktree from `origin/<default>` and branch `t3/fix-main-<shortsha>` | Design review: no two agents editing one checkout |
| 8 | Flakes | When the light triage calls a failure likely flaky (infra, timeout, network, a test passing locally), run `gh run rerun <run> --failed` once before any fixer; a second red goes up the ladder | Avoids "fixing" flakes |
| 9 | Builder children | No light child watches builder children (they report back); the light child instead re-runs each milestone's done-when check for the orchestrator (build-this step 5) | Same evidence, kept out of the orchestrator's context |
| 10 | Live test | Private sandbox repo `PlunetoD/fix-ladder-sandbox`, archived after the run | Shows the ladder works, not just reads well |

Accepted defaults: the ladder is the only repair loop for a red check or CI run: it replaces worker-prompt step 7's open fix-and-verify loop and runs before solve-this's "different approach" rule, and an exhausted ladder (strong rung failed) is terminal for that failure (solve-this counts it as its three approaches and calls it blocked); the ladder replaces build-this's "one fresh child one model step up, then a blocker" rule (standard then strong, then blocker); each rung gets one attempt; the light report format is fixed (`Check: <cmd> -> exit <code>`, `Verdict: pass | real failure | likely flaky`, last ~20 output lines trimmed, `Cause: <one line>`, `Files: <likely files>`); the orchestrator trusts the light report's exit code instead of re-reading logs; without a child tool the orchestrator runs every rung itself (fallback); on T3, waiting on a PR uses `watch_pull_request`, waiting on `main` uses a background `gh run watch <run> > /dev/null` and reading `gh run view <run> --json conclusion,headSha` (exit code not trusted).

## Needs from you

- Needed early: nothing.
- Can wait: "merge if X" for this repo's PR (Pluneto repo); M4 creates and later archives `PlunetoD/fix-ladder-sandbox` (PlunetoD owns it, no action from you).

## Steps

### M1 The fix ladder, wired into build-this
- [x] Write `plugins/workflow/skills/build-this/fix-ladder.md`: tiers and the Claude mapping (Decision 2); zero-token waits per harness (accepted defaults); the light child's two jobs (run a check, triage a red run) with its brief and fixed report; the flake rerun (Decision 8); the standard then strong fixer brief with the fixed handoff (failure, light report, logs path, what was tried, files owned) and fixer rules (Decision 5); where fixers run (Decision 7); red `main`: the `Main is red` issue as lock (Decision 6), main fixer worktree and branch, merge authority (Decision 4), re-triage after merge; the end: blocker in the report or tracker. Under about 900 words.
- [x] `build-this/SKILL.md`: children step 5 re-runs the done-when check through a light child; the failed-check rule points to the ladder; "Finish" CI waits and red CI use the ladder; non-T3 fallback kept.
- [x] `build-this/tickets.md`: "Finish" waits for CI without tokens, a red PR or red main after landing goes through the ladder.
- [x] `build-this/milestone-brief.md`: if the fixer brief lives in fix-ladder.md, only point to it; the T3/sub-agent split stays.
Done when: `test -f plugins/workflow/skills/build-this/fix-ladder.md`; `rg -n "fix-ladder.md" plugins/workflow/skills/build-this/SKILL.md plugins/workflow/skills/build-this/tickets.md` hits both; `rg -n "Main is red" plugins/workflow/skills/build-this/fix-ladder.md` hits; `rg -n "rerun" plugins/workflow/skills/build-this/fix-ladder.md` hits; `rg -n "5\.5" plugins/workflow/skills/build-this/fix-ladder.md` finds nothing; fix-ladder.md states: observers converge on the lowest-numbered open `Main is red` issue via direct listing (not search) before claiming and re-check it after the claim, and a losing observer comments and waits instead of fixing; a main fixer works in its own worktree; no fixer edits the shared checkout while a builder child runs; the light report quotes command, exit code and last output lines; fixers never weaken tests or CI config.
Skills:
- skill-tools:writing-for-agents - Need: a new support file reached by pointers from five skills; Provides: pointer wording and single-source-of-truth rules; Without it: pointers that agents skip, or the ladder duplicated in each skill.
- design:design-review - Need: the race and checkout rules this file must carry (Decisions 6-8); Provides: during-build review of the milestone against the plan's Decisions and Checks; Without it: a ladder that lets two fixers act on one red main.

### M2 Dispatch, solve-this and t3-orchestration use the ladder
- [x] `dispatch/worker-prompt.md`: steps 6, 7, 10 and 11 (step 7's fix loop becomes the ladder) hand test runs and CI triage to a light sub-agent when the worker's harness has one (else the worker runs them), and a red PR goes standard then strong fixer before the worker reports a block; a red main follows Decision 6 (open or comment on the issue, claim before fixing) with the existing "Fixes #<m>" merge-anyway rule; after its own merge the worker waits for main's run on its merge commit and triages it (Decision 5e) before releasing; a worker parked on red main resumes when the orchestrator tells it main is green. Self-contained: no skill names (step 5's grep stays clean).
- [x] `dispatch/SKILL.md` chaining: a `Main is red` issue no longer stalls the chain; the orchestrator launches one main fixer thread (`t3_thread_launch`, worktree from the default branch, branch `t3/fix-main-<shortsha>`, strong-tier fallback after a failed standard fixer), with the chain's `merge if green`; it continues only when the issue is closed and the Main health command reports green, then resumes parked workers (Decision 3); a worker waiting on main is no longer a stall; it stalls only when the ladder ends in a blocker. Point to fix-ladder.md for the rules.
- [x] `solve-this/SKILL.md` step 3: a failing check or red CI goes through fix-ladder.md first; an exhausted ladder counts as its three failed approaches (blocked); `t3-orchestration/SKILL.md`: one line saying light children run checks and triage and fixers follow fix-ladder.md.
Done when: `rg -n "fix-ladder.md" plugins/workflow/skills/{solve-this,t3-orchestration,dispatch}/SKILL.md` hits all three; dispatch's step 5 grep finds no skill or slash-command instruction in worker-prompt.md; `rg -n "5\.5" plugins/workflow/skills/dispatch/worker-prompt.md` finds nothing; dispatch's Chaining no longer lists an open `Main is red` issue as a stall by itself and resumes only on a green Main health result; worker-prompt.md has a post-merge main check before release; `rg -n "fix-ladder" plugins/workflow/skills/solve-this/SKILL.md` hits in step 3.
Skills:
- skill-tools:writing-for-agents - Need: editing four skills to point to one file and a self-contained worker prompt; Provides: no-op and single-source rules; Without it: drift between the ladder and its copies.
- design:design-review - Need: the chain now repairs main unattended (Decision 3) while workers wait on it; Provides: during-build race review against Decisions 3, 4 and 6; Without it: a chain worker and the chain's fixer both fixing main.

### M3 Release and cross-model review
- [ ] `scripts/bump workflow minor`; `scripts/build-marketplace`; update README or which-skill only if they describe changed behaviour.
- [ ] `scripts/validate`; review-this (Codex) on the diff against the base commit, the plan as intent.
Done when: `scripts/validate` and `scripts/build-marketplace --check` exit 0; `grep '"version"' plugins/workflow/.claude-plugin/plugin.json` shows 1.7.0; review-this returns APPROVE.
Skills: none fit (review-this is the step itself).

### M4 Live run on a sandbox repo
- [ ] `gh repo create PlunetoD/fix-ladder-sandbox --private`, a tiny project with a test and a GitHub Actions workflow running it; invite Pluneto.
- [ ] PR case: open a PR with a deliberately broken function; drive it with build-this's ladder from this branch's skill text; record the light report, the fixer, the green run.
- [ ] Main case: push a red commit to main, then follow the ladder: one `Main is red` issue, one claim, a `Fix main: <sha>` PR, review, merge on green (PlunetoD repo: owner rule allows), main's next run green.
- [ ] Escalation case: a PR whose test demands contradictory behaviour (unfixable without weakening the test): the standard fixer fails, the strong fixer gets the handoff and fails, the ladder ends in a blocker with no test weakened.
- [ ] Record URLs in the Build log; archive the repo (`gh repo archive`).
Done when: the Build log holds the PR, issue and run URLs, the light report text and each rung used (the escalation case shows standard then strong, then a blocker, with the test unchanged: `git diff --exit-code <fixture-sha> -- <test-path>` exits 0 after both fixer attempts, where `<fixture-sha>` is the commit that added the contradictory test), main's final run is `success`, and the repo is archived.
Skills: none fit.

## Risks and assumptions

- The inlined worker-prompt copy drifts from fix-ladder.md: M2 and the final review compare them; a later PAIRED-style check is out of scope.
- Cheap-tier economics: the ladder only saves money when the light and standard tiers solve most cases (research: about 70%+); the strong tier and blocker cap the cost of a miss.
- A light child misreads a pass: its report must quote the exit code and last output lines; the PR's CI and the final review are outside checks.
- A chain's auto-fixer merges to main unattended (Decisions 3-4): limited to runs with a merge go-ahead, with review and the no-weakened-tests rule.
- Assumption: T3's `watch_pull_request` re-invokes the parent on check completion; if not, fall back to the background `gh run watch`.
- Assumption: Codex workers in dispatch can start a light sub-agent; if not, they run the checks themselves (fallback written in).
- M4 drives the ladder by hand from this branch's text (the installed plugin is still 1.6.0); it tests the text, not the plugin install.

## Build log

- M1 The fix ladder, wired into build-this (main agent): check pass - fix-ladder.md written (tiers, token-free waits, light child brief and report, flake rerun, standard/strong fixer brief, Red main lock with paginated listing and re-check, merge go-ahead, the end); build-this SKILL.md (every-milestone rule, children intro, step 5), tickets.md (Finish, post-merge triage) and milestone-brief.md point to it; deviations: fix-ladder.md is 1,154 words, not about 900 (the plan review's race fixes added the lock procedure); owed: none; skills: writing-for-agents: pointers worded as the ladder's leading words (rung, light/standard/strong) and one source of truth, briefs kept in fix-ladder.md only; design-review: during-build check against Decisions 6-8 found no gap (the `{owner}/{repo}` placeholder needs the repo checkout as cwd, which every caller has).
- M2 Dispatch, solve-this and t3-orchestration use the ladder (main agent): check pass - worker-prompt step 4 carries a self-contained light sub-agent, token-free wait and fix ladder; steps 6, 7, 10 and 11 use it; red main uses paginated listing with duplicate close; post-merge main check before release; dispatch Chaining repairs red main with a fixer thread, resumes on closed issue + green Main health, wakes `waiting on main` workers; solve-this step 3 routes failing checks and red CI to the ladder first (exhausted = blocked, not revisited); t3-orchestration has a Checks, CI and fixes line; deviations: solve-this's diagnosing-bugs line now goes into a T3 fixer's brief (the ladder replaced the direct repair it guarded); worker prompt step 10 keeps its blocking `gh pr checks --watch` with timeout (a single shell call, no tokens spent while waiting); owed: none; skills: writing-for-agents: worker prompt kept skill-free and self-contained, ladder rules stated once in step 4 and referenced by step number; design-review: only the chain orchestrator launches a main fixer, workers comment and park, so no rival fixers.
