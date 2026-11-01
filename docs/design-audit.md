# Design plugin audit (2026-11-01)

Why the `design` plugin was restructured in 2.0.0, and the routing numbers before and after. Plan: `plans/plan-design-skills.md` in the parent workspace.

## Usage before (design 1.0.1)

Across every session transcript under `~/.claude/projects/`:

| Skill | Model-picked | Invoked by the user |
|---|---|---|
| backend-design-review | 2 of 37 use-available-skills runs | 0 |
| dashboard-design | 0 | 0 |
| tool-for-users | 0 | 0 |
| user-types | 0 | 4 (`/ux:user-types`) |

## Root causes

- **Questioning skills are filtered out.** use-available-skills leaves out skills whose main job is to question the user, and, during planning, skills that produce files. user-types and tool-for-users ask at every step and write files; backend-design-review asks its own batch of up to four questions; dashboard-design says "Ask only for what is missing".
- **Planning writes only the plan.** plan-this can't let a skill write `UX/User_Types.md` mid-interview, so the user-type skills never fit the planning phase where they matter.
- **Arbitrary coverage.** Backend and dashboards only: no general UI, API contracts, accessibility, UX copy or bot/chat design, though Zephyr ships APIs and a Discord bot, Brain a Telegram bot, and Zephyr issue #15 was a copy bug.
- **Four shapes.** Each skill had its own modes, output format and file location, so plan-this had nothing uniform to fold into Decisions and Done-when checks.
- **Off the main flow.** which-skill listed design as a side section, not a step between plan and build.
- **Duplicated tooling.** A 979-line `ux.py` and `file-format.md` were copied into two skills; journeys and Mermaid diagrams were never used.
- **No ranking.** Issue #1 asks for user-types to be ranked.

## Routing test

`scripts/route-test` (5 goals × 3 runs, use-available-skills invoked directly in the planning phase, scratch clones of zephyr-homelab, brain-of-omniscience and cortana, default model).

### Before (design 1.0.1)

| Goal | Expected | Picks per run | Right | Asks after design skill |
|---|---|---|---|---|
| 1 ticket endpoint | backend-design-review or design-review | backend-design-review / backend-design-review / backend-design-review | 3/3 | 0 |
| 2 signups admin page | dashboard-design or ui-craft | backend-design-review, tool-for-users / backend-design-review, dashboard-design / backend-design-review, dashboard-design, tool-for-users | 2/3 | 0 |
| 2b signups page, build | dashboard-design or ui-craft | dashboard-design / dashboard-design / dashboard-design | 3/3 | 0 |
| 3 captains tool | product-context or tool-for-users or user-types | backend-design-review, tool-for-users / none / backend-design-review, tool-for-users | 2/3 | 0 |
| 4 brain backend | backend-design-review or design-review; not dashboard-design, ui-craft | backend-design-review / backend-design-review / backend-design-review | 3/3 | 0 |
| 5 log rotation | none | none / none / none | 3/3 | 0 |

Cost ~$5.80 for 15 runs on Opus. Invoked directly, use-available-skills already finds backend-design-review reliably; the 2-of-37 rate in real sessions comes from plan-this rarely reaching a design skill, and from the questioning and file-writing skills being skipped in planning. Goal 2 picks backend-design-review and tool-for-users alongside or instead of dashboard-design, and goal 3 never picks user-types (it writes a file). Row 2b (the same goal as a build milestone, use-available-skills in record-only mode) was added during the after-run and measured on 1.0.1 from a worktree of `origin/main`.

### After (design 2.0.0)

| Goal | Expected | Picks per run | Right | Asks after design skill |
|---|---|---|---|---|
| 1 ticket endpoint | backend-design-review or design-review | design-review / design-review / design-review, product-context | 3/3 | 0 |
| 2 signups admin page | dashboard-design or ui-craft | design-review / design-review / design-review | 0/3 | 0 |
| 2b signups page, build | dashboard-design or ui-craft | ui-craft / ui-craft / ui-craft | 3/3 | 0 |
| 3 captains tool | product-context or tool-for-users or user-types | design-review, product-context / design-review / design-review, product-context | 2/3 | 0 |
| 4 brain backend | backend-design-review or design-review; not dashboard-design, ui-craft | design-review / design-review / design-review | 3/3 | 0 |
| 5 log rotation | none | none / none / none | 3/3 | 0 |

Cost ~$6.45 for 18 runs on Opus.

- **Goal 2 misses its planning-phase target (0/3) by design.** use-available-skills holds build skills back until the build phase, and ui-craft is the build skill (Decision 1); every run said so and picked design-review, whose UI domain is the planning-time review. Row 2b shows the path that matters: as a build milestone, ui-craft is matched 3/3. dashboard-design used to slip through the planning filter.
- **Goal 3** reaches product-context in 2 of 3 runs; the third skips it as scope beyond the goal. plan-this's design pass runs product-context explicitly whenever the repo has no `PRODUCT.md`, so planning doesn't depend on this routing.
- **Goal 4** picks design-review and never ui-craft; **goal 5** picks nothing.
- **Asks after a design skill**: 0 everywhere. `-p` suppresses question cards, so the interactive check below is the real evidence.

### Interactive check (tmux)

`/design:design-review plans/plan-tickets.md` in an interactive session on a small paid-tickets plan: the skill printed its full output (Verdict through Open questions, four questions with recommended options), then loaded `workflow:interview`, and the first question card came from interview. The session transcript has no AskUserQuestion before the interview Skill call, and no file was written (Decision 9).

