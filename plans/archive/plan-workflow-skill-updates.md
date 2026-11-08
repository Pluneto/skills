
# Plan: workflow plugin skill updates

Created 2026-11-08 with /plan-this. Attach this file to a Claude chat and run /build-this (or say "build this plan") to continue.

## Goal
Original request (the user's words):

> the plan-this skill should use the review-this skill instead of its own review set. also milestones should be milestones and not micro tasks so especially for simple tasks combine them in one milestone. increase the limit of the rewritten goal to 300. All the options in the interview skill should be researched and fact checked before they reach the user, so if during the interview new frontiers are unlocked make sure to run the research-this skill. If the research this skill invokes a sub agent then the sub agents use Haiku 5.5 on high effort. The handoff skill should always provide a full prompt for starting the next session.
> 
> build-this skill should use the t3 orchestration instead of sub agents if available since they can run skills, let each sub-agent run review-this at the end before committing anything.
> 
> dispatch should allow for waves to either be launched one by one or to have the waves launch one after another, let the user specify e.g. launch waves 1-3 automatically.
Approved goal: Update the `workflow` plugin in this repo (plugins/workflow, minor version bump, `solve-this` autopilot still working): plan-this reviews through review-this (plan-review.md goes away), uses outcome-sized milestones (small tasks merge into one) and a 300-word rewritten-goal limit; interview researches and fact-checks every option before the user sees it, running research-this when new frontiers open; research-this sub-agents run on Haiku 5.5 at high effort; handoff always ends with a full ready-to-paste prompt for the next session; build-this builds each milestone in a T3 delegate_task child when available (sub-agents otherwise), each child running review-this before committing; dispatch launches waves one by one or chains them (`launch waves 1-3`).
Constraints: skill files only, edits stay in this repo's worktree; one branch, one PR, no merge unless the prompt says "merge if X" (Pluneto repo); children commit locally, never push; skills follow the repo's writing rules (concise, SKILL.md well under 500 lines).
Skills used while planning: none (considered design-review and product-context, skipped: they target UI/backend design, and these are prose skill files).
Plan review: Codex gpt-6.1-sol, medium effort; 2 passes; pass 1 found 7 (6 fixed, F6 declined as scope creep), pass 2 re-reported F1-F4 because my edits had not applied to the text it saw (now applied) and found F5 (fixed).

## How we'll know it worked
- `scripts/validate` exits 0 (claude plugin validate --strict, version bumped, agents/openai.yaml matching, generated files current).
- `scripts/build-marketplace --check` exits 0.
- `rg -n "plan-review" plugins/` finds nothing.
- review-this on the final diff returns VERDICT: APPROVE from another model.

## Decisions
| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | Build children layout | Sequential, shared checkout, each child commits to the current branch | One branch, linear commits, no merge step; parallel milestones dropped in T3 mode |
| 2 | Final review in build-this | Keep review-changes once; skip the end-of-build cross-model offer when every milestone was reviewed | Avoid double cross-model review |
| 3 | Chained waves | `launch waves A-B` is refused unless the same reply says `merge if green` | Waves start only when earlier tickets close; Pluneto repos merge only on explicit say-so |
| 4 | Interview research | One research-this run per round at quick depth covering all facts behind that round's options; not for facts only the user knows | Bounded cost, every option checked |
Accepted defaults: plan-this writes its draft to a temp file and runs review-this on it (asking first, automatic in autopilot); findings that change a decision go back to the interview; a milestone is a checkable deliverable with checkbox steps inside, a simple task is exactly one milestone; research-this sub-agents Haiku 5.5 high effort on Claude (Agent tool model haiku + effort high; T3 claude-haiku-5-5), unpinned elsewhere; build children inherit the orchestrator's provider and use the per-milestone model table, commit locally after review-this approves, never push; on stalemate/budget end/block they commit nothing and report Held; without T3 tools, sub-agents are used and the orchestrator runs review-this itself before committing; handoff shows the full prompt in a fenced block in the reply and as the first section of the file (build-this's check-in handoff too); dispatch accepts `launch wave N`, `launch waves A-B`, `launch all waves`, a chain waits via t3_thread_wait plus issue state and stops at the first stall (parked decision, red main, unclosed ticket) with a report; bump workflow minor and rebuild the marketplace.

## Needs from you
- Needed early: nothing.
- Can wait: merge of the PR (Pluneto repo; only on "merge if X").

## Steps
### M1 Planning-side skills: plan-this, interview, research-this, handoff
- [x] plan-this: raise the goal limit to about 300 words; add the milestone sizing rule; write the draft plan to a temp file and run review-this on it (keep the ask-first question and the autopilot run), move the scope-creep rule into plan-this, step 3 summary lists review-this's report fields; delete plan-this/plan-review.md and every reference to it; pass review-this the plan as an explicit plan target together with the original request
- [x] review-this: one line saying an explicit plan target from a caller overrides its "called by a skill: the target is the implementation" default, still without asking
- [x] interview: before each round, run research-this once at quick depth on the facts behind that round's options (not for user-only facts); rerun when answers unlock new frontiers; for facts mode give research-this a temp output path (and allow that temp file in plan-this's rule on written files) so nothing lands in the project
- [x] solve-this: allow interview's per-round and newly unlocked research runs under autopilot (replace "without adding runs of your own")
- [x] research-this: sub-agents run on Haiku 5.5 at high effort on Claude, unpinned elsewhere
- [x] handoff: always include the full next-session prompt (fenced block in the reply and first section of the file)
Done when: `rg -n "plan-review" plugins/` has no hit; `rg -n "300 words" plugins/workflow/skills/plan-this/SKILL.md` hits; `rg -n "haiku" -i plugins/workflow/skills/research-this/SKILL.md` hits; wc -l of each edited SKILL.md under 500.
Skills: writing-for-agents - Need: SKILL.md edits that must stay short; Provides: its pointer and pruning rules; Without it: the edited skills grow (plan-this is already ~2,500 words).

### M2 build-this
- [x] Prefer T3 delegate_task children (orchestrator_capabilities first, `isolation: shared`, sequential, per-milestone model and effort) over Agent sub-agents; sub-agents stay the fallback
- [x] Brief (milestone-brief.md): each child runs review-this at its end on its milestone diff, commits locally on approval, never pushes, leaves work uncommitted and reports Held on stalemate/budget end/block, after which the orchestrator launches no further child in that checkout until that milestone is resolved (unfinished paths go in the Build log); fallback orchestrator runs review-this itself before committing
- [x] Step 5: keep review-changes, skip the cross-model offer only while milestone approvals still cover the current changes: edits made after review-changes get a review-this pass before they are committed; update tickets.md, solve-this references and the check-in handoff text (full prompt)
Done when: `rg -n "delegate_task" plugins/workflow/skills/build-this/SKILL.md` hits; `rg -n "review-this" plugins/workflow/skills/build-this/milestone-brief.md` hits; each edited SKILL.md under 500 lines.
Skills: writing-for-agents - same Need/Provides/Without as M1.

### M3 dispatch
- [x] Step 8 and the replies it advertises: `launch wave N`, `launch waves A-B`, `launch all waves`; a chain requires `merge if green`, waits per wave with t3_thread_wait plus issue state, ticks lines, stops at the first stall with a report
Done when: `rg -n "launch waves" plugins/workflow/skills/dispatch/SKILL.md` hits; SKILL.md under 500 lines.
Skills: writing-for-agents - same as M1.

### M4 Release and verify
- [x] `scripts/bump workflow minor`, `scripts/build-marketplace`, README/which-skill wording updated if they describe changed behaviour
- [x] `scripts/validate`, `scripts/measure-skills plugins/workflow` (route-test checks design routing and needs repos missing on this box, so it is not used)
- [x] review-this on the diff, commit, push the branch, open the PR (pr skill body); the repo has no CI (no .github), so scripts/validate and the pre-commit hook are the gate; if a run exists for the branch, watch it and check conclusion and headSha; the PR is left unmerged
Done when: `scripts/validate` exits 0, `scripts/build-marketplace --check` exits 0, review-this VERDICT: APPROVE, PR open.
Skills: none fit.

## Risks and assumptions
- Another provider's review CLI may be missing: review-this falls back to a sub-agent. 
- Chained dispatch can stall on a parked decision: it stops and reports.
- Assumption: T3 delegate_task children can run skills (stated by the user).
- Skill bodies are long; edits could push a SKILL.md over 500 lines: the Done-when checks count lines.

## Build log
- M1 Planning-side skills (main agent, built in this conversation): check pass - no plan-review hits, "300 words" and Haiku lines present, all SKILL.md under 500 lines; deviations: none; owed: none; skills: writing-for-agents: kept edits short (no visible effect beyond pruning two no-op sentences after review)
- M2 build-this (main agent): check pass - delegate_task and review-this present; deviations: sub-agent fallback also runs sequentially (plan said parallel dropped in T3 mode only); owed: none; skills: writing-for-agents: no visible effect
- M3 dispatch (main agent): check pass - `launch waves` present; deviations: none; owed: none; skills: writing-for-agents: no visible effect
- M4 Release and verify (main agent): check pass - workflow bumped to 1.5.0, scripts/validate ok, build-marketplace --check ok, review-this (Codex gpt-6.1-sol, high) APPROVE after 3 rounds; route-test not run (needs repos missing on this box), PyYAML installed in /tmp/skills-venv for the scripts; deviations: also edited review-this, solve-this and which-skill (small consistency edits); owed: PR merge (Pluneto repo, needs "merge if X")
