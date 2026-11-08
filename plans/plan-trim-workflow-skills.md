# Plan: trim the workflow plugin skills

Created 2026-11-08 with /plan-this. Attach this file to a Claude chat and run /build-this (or say "build this plan") to continue.

## Goal
Original request (the user's words):

> Goal: trim every skill in plugins/workflow/skills/ so each is shorter, and make them align with each other and work well on t3code (T3 orchestration tools: orchestrator_capabilities, delegate_task, t3_thread_launch, t3_thread_wait, task_status).
> Start: 1. Check whether PR https://github.com/Pluneto/skills/pull/11 (workflow 1.5.0) is merged. If it is, branch from main. If not, branch from t3/workflow-skill-updates (commit fbdcdfd) and say so in your PR. Its archived plan is plans/archive/plan-workflow-skill-updates.md: read its Goal and Decisions first, they are settled. 2. Run /workflow:plan-this on this goal. Measure first (wc -w plugins/workflow/skills/*/*.md and scripts/measure-skills plugins/workflow), so the plan has a baseline and a target. 3. Skills to use: skill-tools:skill-ozempic and skill-tools:writing-for-agents for the trimming, workflow:review-this on the final diff.
> Constraints: edit the repo source under plugins/workflow, never the plugin cache under ~/.claude-pool/plugins (it still holds 1.4.1). Bump the plugin (scripts/bump workflow minor or patch), run scripts/build-marketplace and scripts/validate (needs PyYAML: python3 -m venv /tmp/skills-venv && /tmp/skills-venv/bin/pip install pyyaml, then put its bin first on PATH). Trimming must not change behaviour the user already decided (see the archived plan). Open the PR, do not merge it unless told "merge if X" (Pluneto repo).

Approved goal: Trim every skill under plugins/workflow/skills/ (14 skills, 27,611 words by `wc -w plugins/workflow/skills/*/*.md`, ~1,038 always-on tokens by `scripts/measure-skills plugins/workflow`) by about 30% in total, the four biggest (build-this 3,714, plan-this 2,594, wayfinder 2,245, dispatch 2,217) cut hardest, and align them with each other and with t3code. The T3 rules live once in a new model-invoked reference skill `t3-orchestration`; build-this, dispatch, research-this, review-this and solve-this load it and keep only their own specifics. Behaviours settled in plans/archive/plan-workflow-skill-updates.md are a keep-list and survive. Branch `trim-workflow-skills` from `t3/workflow-skill-updates` (PR #11 is open, unmerged; the PR says so). Only plugins/workflow source is edited, never the plugin cache.
Constraints: edit only plugins/workflow (plus this plan, plans/, and generated marketplace files); bump the workflow plugin to a minor version (a new skill is added); run scripts/build-marketplace and scripts/validate; one branch, one PR, no merge unless the prompt says "merge if X" (Pluneto repo); keep the non-T3 fallbacks (sub-agents, plain-text questions); question-tool use unchanged; LICENSE-attributed skills (handoff, review-this, to-questionnaire, to-tickets, wayfinder, which-skill, wizard) are trimmed too, keeping their attribution lines; code, if any, follows KISS (scripts are not touched).
Cuts the user approved, beyond wording: build-this's one-line model recommendation and "Let me switch model first" option (the per-child model table stays) and its "Sub-agents" section; which-skill/PHASE-BOUNDARIES.md reduced to its five-option decision list; to-tickets' optional "Explore the codebase" step folded into step 1.
Skills used while planning: none loaded (use-available-skills not run; the user named writing-for-agents and review-this; design skills skipped: the goal has no users, UI or backend). skill-ozempic is user-invoked only (disable-model-invocation), so it cannot be run by the agent; its pruning is done through writing-for-agents, and the PR says so.
Plan review: Codex gpt-6.1-sol, medium effort; 2 passes; pass 1 found 3 (all fixed: budgets for the big four, caller-rule override of T3 defaults, preservation checklist); pass 2 found 2 (F2 fixed: build-marketplace in M1; F1 declined as false: the harness refused to run skill-ozempic for the agent, it is reserved for explicit user invocation).

## How we'll know it worked
- `wc -w plugins/workflow/skills/*/*.md` total is at most 19,300 (incl. the new skill); every pre-existing skill's SKILL.md and support files are shorter than the baseline in the table below; the four biggest SKILL.md are cut by at least 33% (budgets 2400, 1730, 1500, 1480).
- `scripts/measure-skills plugins/workflow` always-on total is at most 1,038 + 60 tokens (one new description).
- Keep-list greps all hit and the preservation checklist in the Build log is fully confirmed (see M4): `launch waves`, `merge if green`, `300 words`, `haiku` (research-this), `review-this` (build-this milestone-brief), and `rg -n "plan-review" plugins/` finds nothing.
- `scripts/validate` and `scripts/build-marketplace --check` exit 0.
- review-this on the final diff, from another model, returns VERDICT: APPROVE.

## Decisions
| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | Target | About 30% fewer words overall; four biggest skills cut hardest | Mostly duplication and repeated blocks, so behaviour is safe |
| 2 | Shared T3 rules | New model-invoked reference skill `t3-orchestration` | One source of truth; costs about 40-60 always-on tokens; must be listed in which-skill and have agents/openai.yaml |
| 3 | Cut depth | Also cut approved optional steps (model line + switch option, build-this Sub-agents, PHASE-BOUNDARIES extras, to-tickets explore step); everything else keeps its behaviour | User approved these four, nothing else |
| 4 | Version | Minor bump (1.5.0 to 1.6.0), a new skill is added | Replaces the earlier patch default |
Accepted defaults: keep the non-T3 fallbacks in every skill; question-tool use unchanged; LICENSE-attributed skills trimmed with attribution kept; no-tracker-doc.md (identical 376-word copy in build-this, to-tickets, wayfinder) stays in each place, trimmed; if PR #11 merges before this one, rebase onto main; skill-ozempic cannot be run by the agent (disable-model-invocation), writing-for-agents applied directly.

## Needs from you
- Needed early: nothing.
- Can wait: merge of the PR (Pluneto repo; only on "merge if X"); running `/skill-tools:skill-ozempic` over the result yourself if you want that pass too.

## Steps
### M1 Baseline, budgets and the t3-orchestration skill
- [x] Record the baseline (`wc -w` per file, `scripts/measure-skills`) and per-skill budgets in this plan's Build log. Budgets: build-this SKILL 3714 to 2400, plan-this 2594 to 1730, wayfinder 2245 to 1500, dispatch 2217 to 1480, research-this 1775 to 1300, to-tickets 1881 to 1400, review-this 1433 to 1050, use-available-skills 1353 to 950, which-skill 1159 to 900, solve-this 981 to 750, interview 894 to 700, wizard 673 to 520, to-questionnaire 470 to 370, handoff 215 to 170; support files about 30% off each; total at most 19,300.
- [x] Create `plugins/workflow/skills/t3-orchestration/SKILL.md` (about 400 words, model-invoked, short description) and `agents/openai.yaml`. Content, from the live tool schemas: default tool choice: native sub-agent (same provider and model, finishes this turn) versus `delegate_task` (other provider or model, background) versus `t3_thread_launch` (a new top-level thread only when the user asks or a wave worker needs one); a calling skill's own rule overrides these defaults (build-this always uses `delegate_task` children when T3 is available, same provider as the orchestrator, `isolation: shared`, sequential; dispatch uses `t3_thread_launch` workers); `orchestrator_capabilities` once per thread, settings in `target.options`; `isolation` is shared (parent checkout, default) or worktree (a separate checkout or PR per child, chosen by the caller); `mode: async` default; wait with `t3_thread_wait` (dispatch chains) or follow the tool's `next` and never poll; `task_status` only when a completion wakes you; cancel with `task_cancel`; every new review is a new `delegate_task`; fallbacks when T3 tools are missing.
- [x] Write the preservation checklist into the Build log: every Decision and accepted default of plans/archive/plan-workflow-skill-updates.md mapped to the file and section that carries it now (plan-this review-this/milestones/300 words; interview per-round research at quick depth; research-this Haiku 5.5 at high effort; handoff full prompt in a fenced block and as the file's first section, also build-this's check-in handoff; build-this T3 children, review-this before commit, Held state with no further child, review-changes once plus the post-approval edit rule; dispatch launch wave N / waves A-B / all waves, `merge if green`, stop at first stall; solve-this autopilot allowing interview research). Each later milestone and the final review re-check it.
- [x] List it in which-skill (validate requires every skill named there), then run `scripts/build-marketplace` so the generated plugin manifest lists the new skill.
Done when: `test -f plugins/workflow/skills/t3-orchestration/SKILL.md`; `rg -n "orchestrator_capabilities" plugins/workflow/skills/t3-orchestration/SKILL.md` hits; `scripts/build-marketplace --check` exits 0 after the new skill is registered; the baseline table is in the Build log.
Skills: writing-for-agents - Need: write a reference skill and its description pointer; Provides: pointer-wording and single-source rules; Without it: a long description and a bloated skill.

### M2 Trim the four biggest: build-this, plan-this, dispatch, wayfinder
- [ ] For each SKILL.md and its support files (milestone-brief, tickets, no-tracker-doc, worker-prompt): remove no-ops, duplicated meaning and repeated blocks; replace the inline T3 paragraphs in build-this and dispatch with a one-line "load t3-orchestration" plus their specifics; apply the approved cuts to build-this; keep the keep-list behaviours (dispatch `launch wave N`, `launch waves A-B`, `launch all waves`, chain only with `merge if green`; build-this T3 children each running review-this before committing; plan-this review-this for plans, milestones sized by outcome, 300-word goal).
- [ ] Check each pointer to a sibling file still resolves.
Done when: each file is at or under its budget; the four SKILL.md are cut at least 33%; `rg -n "launch waves" plugins/workflow/skills/dispatch/SKILL.md`, `rg -n "merge if green" plugins/workflow/skills/dispatch/SKILL.md`, `rg -n "300 words" plugins/workflow/skills/plan-this/SKILL.md`, `rg -n "review-this" plugins/workflow/skills/build-this/milestone-brief.md` hit; `rg -n "plan-review" plugins/` finds nothing.
Skills: writing-for-agents - Need: trimming skill text without losing behaviour; Provides: no-op, single-source-of-truth and disclosure rules; Without it: cuts by feel that drop behaviour or leave duplicates.

### M3 Trim the rest and align
- [ ] research-this, review-this (+ briefs, reviewer), solve-this, interview, use-available-skills, to-tickets (+ approved fold), which-skill (+ PHASE-BOUNDARIES to the decision list), handoff, wizard, to-questionnaire: same method; research-this, review-this and solve-this point to t3-orchestration for T3 rules; keep attribution lines and LICENSE files.
- [ ] Align shared wording across skills: same names for the same things (milestone, child, Held, base commit), same phrasing for the question-tool fallback, same phrasing for review-this calls.
Done when: each file at or under its budget; `rg -n "haiku" -i plugins/workflow/skills/research-this/SKILL.md` hits; the license/attribution lines are still present (`rg -n "tstack" plugins/workflow/skills/review-this/SKILL.md` hits).
Skills: writing-for-agents - same as M2.

### M4 Release and verify
- [ ] `scripts/bump workflow minor`, `scripts/build-marketplace`, update README or which-skill wording if it describes changed behaviour.
- [ ] Walk the preservation checklist against the final text, line by line. Run `scripts/validate` (with the PyYAML venv on PATH), `scripts/build-marketplace --check`, `scripts/measure-skills plugins/workflow`, the word-count table before/after, and every keep-list grep.
- [ ] review-this on the full diff against fbdcdfd; commit, push, open the PR (pr skill) saying it is based on t3/workflow-skill-updates because PR #11 is unmerged and that skill-ozempic was not run; the repo has no CI, so validate is the gate; leave unmerged.
Done when: `scripts/validate` exits 0, `scripts/build-marketplace --check` exits 0, the success checks above pass, review-this VERDICT: APPROVE, PR open.
Skills: none fit.

## Risks and assumptions
- A trimmed skill loses a nuance the user relied on: the keep-list greps plus the final review-this diff review catch the settled ones; the PR lists every approved cut.
- t3-orchestration is invoked by name from other skills: on a harness with no Skill tool or without the T3 tools the fallback lines in each skill still apply.
- PR #11 may merge or change before this PR: rebase onto main then.
- Assumption: the 30% total is reachable with the new skill included; if a skill cannot reach its budget without dropping behaviour, keep the behaviour and report the shortfall.

## Build log (details below)

### Baseline (wc -w, 2026-11-08, before any edit; always-on 1,038 tokens by scripts/measure-skills)
| File | Words |
|---|---|
| build-this/SKILL.md | 3714 |
| build-this/milestone-brief.md | 868 |
| build-this/no-tracker-doc.md | 376 |
| build-this/tickets.md | 444 |
| dispatch/SKILL.md | 2217 |
| dispatch/worker-prompt.md | 1504 |
| handoff/SKILL.md | 215 |
| interview/SKILL.md | 894 |
| plan-this/SKILL.md | 2594 |
| research-this/SKILL.md | 1775 |
| review-this/SKILL.md | 1433 |
| review-this/briefs.md | 756 |
| review-this/reviewer.md | 608 |
| solve-this/SKILL.md | 981 |
| to-questionnaire/SKILL.md | 470 |
| to-tickets/SKILL.md | 1881 |
| to-tickets/no-tracker-doc.md | 376 |
| use-available-skills/SKILL.md | 1353 |
| wayfinder/SKILL.md | 2245 |
| wayfinder/no-tracker-doc.md | 376 |
| which-skill/PHASE-BOUNDARIES.md | 699 |
| which-skill/SKILL.md | 1159 |
| wizard/SKILL.md | 673 |
| **Total** | **27611** |

### Preservation checklist (archived plan Decisions and defaults to file; verified by /tmp/keeplist.sh and re-read in M4)
1. plan-this: reviews through review-this (no plan-review.md), outcome-sized milestones (a simple task is one milestone), 300-word rewritten goal, draft plan in a temp file, ask first / automatic in autopilot (plan-this/SKILL.md)
2. interview: one research-this run per round at quick depth for facts behind the options, not user-only facts; rerun on new frontiers (interview/SKILL.md)
3. solve-this: autopilot allows interview's per-round research (solve-this/SKILL.md)
4. research-this: sub-agents Haiku 5.5 at high effort on Claude, unpinned elsewhere (research-this/SKILL.md)
5. handoff: full ready-to-paste next-session prompt, fenced block in the reply and first section of the file; also build-this's check-in handoff (handoff/SKILL.md, build-this/milestone-brief.md)
6. build-this: T3 delegate_task children when available (sub-agents otherwise), sequential, shared checkout, per-milestone model table, children inherit orchestrator provider, each runs review-this before committing, commits locally, never pushes, Held on stalemate/budget end/block and no further child until resolved, review-changes once, cross-model offer skipped while approvals cover the changes, edits after approval get a review-this pass (build-this/SKILL.md, milestone-brief.md, tickets.md)
7. dispatch: `launch wave N`, `launch waves A-B`, `launch all waves`; a chain requires `merge if green`; waits per wave with t3_thread_wait plus issue state; stops at the first stall with a report (dispatch/SKILL.md)
8. review-this: an explicit plan target from a caller overrides the implementation default, still without asking (review-this/SKILL.md)
9. Release: workflow minor bump, marketplace rebuilt, which-skill current.

### Build log
- M1 Baseline, budgets and t3-orchestration (main agent, built here): check pass - skill file exists (427 words), orchestrator_capabilities present, build-marketplace --check ok; deviations: none; owed: none; skills: writing-for-agents: no visible effect beyond keeping the description to one trigger sentence
- M2 Trim the big four (main agent, built here): check partial - keep-list greps pass, no plan-review hits, no-tracker-doc copies identical; words: build-this 3714 to 2481 (-33%), plan-this 2594 to 2095 (-19%), wayfinder 2245 to 1666 (-26%), dispatch 2217 to 1717 (-23%), worker-prompt 1504 to 1458, milestone-brief 868 to 764, tickets 444 to 385, no-tracker-doc 376 to 336 (x3); deviations: plan-this, wayfinder and dispatch miss the 33% / budget target because the remaining text is behaviour and commands (kept per the plan's risk rule); owed: the shortfall is made up in M3 or reported; skills: writing-for-agents: no visible effect beyond the rules guiding the cuts

