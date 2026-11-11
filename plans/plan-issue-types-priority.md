# Plan: issue types, priority, draft and planned labels

Created 2026-11-11 with /plan-this. Attach this file to a Claude chat and run /build-this (or say "build this plan") to continue.

## Goal

**Original request:** "Incorporate in the plugins the GitHub Issue type (Bug, Feature, Task) and adjust the issue labels, including adding a draft label for jotting down quick notes or ideas that haven't been worked out. Add in low and high priority labels. Low priority can be done whenever and high priority should be addressed immediately. Incorporate GitHub milestones if they are a good option."

**Deepened goal:** Extend the pluneto-skills `workflow` and `setup` plugins so GitHub tickets carry a native issue type (Bug, Feature, Task), skipped and recorded when a repo has none. The tracker template gains four label roles: **draft** (a rough note or idea; no agent builds, claims, tickets or dispatches it), **planned** (plan-this has planned it; it waits for to-tickets or build-this), **high** priority (address immediately: worked first and flagged) and **low** priority (do whenever: worked last). Drafts flow `draft → /plan-this issues <n…> → planned → /to-tickets → tickets as sub-issues`. Milestones stay the user's (releases, time boxes); skills keep them, pass them on to tickets and accept a milestone as the set of tickets to work. to-tickets, wayfinder, dispatch, build-this, plan-this and the fix ladder set and respect all of this; setup and repair create and check it; the three `no-tracker-doc.md` copies stay identical. Proof: `scripts/validate` plus a live end-to-end test on a new private PlunetoD sandbox repo.

**Constraints:**
- GitHub tracker only; the local Markdown tracker (`issue-tracker-local.md`) stays unchanged.
- Priority is labels, not GitHub issue fields (no `gh` flag for fields; PlunetoD gets FORBIDDEN reading them).
- Existing labels are never edited or deleted; GitHub's default `bug`/`enhancement` labels stay, unused by the skills.
- Label names are roles, renamable per repo in setup step 2b, like the existing roles.
- No agent sets `priority:high` on its own, except on a `Main is red` issue.
- The three `no-tracker-doc.md` copies stay byte-identical (`scripts/validate` PAIRED check).
- Every changed plugin gets a version bump (`scripts/bump`); `scripts/validate` must pass.
- Skills stay plain Markdown instructions: no hooks, scripts or binaries added.
- Instructions follow KISS: the simplest wording and the fewest new paths that meet each check.

**Skills used while planning:** none.
- considered skill-tools:writing-for-agents, skipped: build-phase writing method (matched to M1–M3 below).
- considered engineering:domain-modeling, skipped: no GLOSSARY.md or ADRs; the new terms are defined in the tracker template.
- considered design:design-review, skipped (design pass too): agent instruction text and GitHub conventions, no UI, bot or API.

**Research (research-this, quick, 2026-11-11):** Extend: use native issue types via `gh --type`, keep priority and draft as labels.
- Issue types are GA on user-owned repos since 2026-11-04 ([github/roadmap#1344](https://github.com/github/roadmap/issues/1344)); defaults Task, Bug, Feature, up to 25, managed in the owner's Settings → Planning → Issue types ([docs](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/managing-issue-types-in-an-organization)). `GET repos/<o>/<r>/issue-types` lists them; `Pluneto/skills` and PlunetoD repos have all three enabled.
- During the September 2026 preview, third parties reported GitHub silently discarding type writes on personal repos; a post-GA write is **untested** (M1's first step).
- `gh issue create/edit --type <name>`, `--remove-type`, `list --type` since gh 2.94.0 (2026-06-10); the box has 2.103.3. REST issues carry a `type` object (null when unset).
- A milestone groups issues and PRs with a due date and % complete; an issue holds at most one ([docs](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/about-milestones)).

**Plan review:** Codex gpt-6.1-sol at high, 3 rounds. Fixed: S1 to-tickets match search excludes draft, planned and `planned in #` issues; S2 version bumps moved to the start of M1; S3 worker-prompt's inline `Main is red` creator gets type and priority; S4 wayfinder frontier ordered by priority; S6 no CI in the repo, so local `scripts/validate` output in the PR body is the gate. Re-asked: S5 grouped drafts' priority and milestone (decision 18).

## How we'll know it worked

1. `scripts/validate` passes locally on the final commit (the repo has no CI) (plugin validation, versions bumped, PAIRED copies identical, router names every skill).
2. In a new private PlunetoD sandbox repo, a live run shows, by `gh` output, not by reading the skill text:
   - setup creates `draft`, `planned`, `priority:high`, `priority:low` and records `Issue types: yes` with the Type column;
   - an issue created with `--type Bug` reads back `type.name == "Bug"` from `gh api repos/<o>/<r>/issues/<n> --jq .type.name`;
   - a draft issue run through `/plan-this issues <n>` ends with a plan comment and `planned` replacing `draft`;
   - `/to-tickets <n>` publishes tickets that are sub-issues of `<n>` with a type, the inherited priority and milestone, and removes `planned`;
   - `gh issue list --type Bug --label priority:high` and `--milestone "<name>"` return the expected tickets;
   - dispatch's ticket list leaves out a draft and puts a `priority:high` ticket in wave 1.
3. Repair on an existing tracker doc (a copy of today's template) adds the four roles and Type column and creates the missing labels; a second repair run changes nothing.

## Decisions

| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | Issue types | Native types via `gh --type` (Bug, Feature, Task) | GA on personal repos; no labels needed |
| 2 | Repo without issue types | Skip the type; setup records `Issue types: yes/no` in the tracker doc from the issue-types API | Simplest; types exist on all of github.com now |
| 3 | Priority mechanism | Labels `priority:high` / `priority:low`; no label = normal | Issue fields have no gh flag and aren't readable by PlunetoD |
| 4 | Default `bug`/`enhancement` labels | Leave them; skills don't use them | Nothing lost on repos with history; setup never edits labels |
| 5 | Milestones | The user's (releases, time boxes); skills keep any milestone, tickets inherit the source issue's, and build-this and dispatch accept `milestone "<name>"` as the ticket set | Releases keep the one milestone slot; the user can still point agents at a release |
| 6 | Draft flow | `draft` issue → `/plan-this issues <n…>` reads body and comments as the goal → after the user's yes, plan posted on the issue, `draft` swapped for `planned` → `/to-tickets <n>` → tickets as sub-issues of `<n>` (progress bar) → build-this / dispatch | Reuses plan-this and to-tickets; every step is visible on the issue |
| 7 | Where a draft's plan lives | Both: a comment on the issue and `plans/plan-<topic>.md` | Each T3 thread has its own worktree; the comment lets any thread find the plan |
| 8 | Several drafts in one /plan-this | Group by goal: drafts sharing a goal get one plan, the lowest number is the parent, the others become its sub-issues and close with `planned in #<parent>`; unrelated drafts are planned one after another. plan-this shows the grouping first | Related ideas get one plan without forcing unrelated ones together |
| 9 | State after planning | `planned` label replaces `draft` | A filterable state between draft and tickets (user's choice over just removing draft) |
| 10 | Label names | `draft`, `planned`, `priority:high`, `priority:low`, renamable per repo | Follows the existing role/label pattern, so setup and repair cover them |
| 11 | Type column | Tracker doc gets a "Type in this repo" column (roles bug, feature, task), filled by setup from the issue-types API | Lets a repo with renamed types still work |
| 12 | Who picks the type | to-tickets per ticket (Bug fixes wrong behaviour, Feature adds behaviour, Task otherwise); wayfinder map and tickets, dispatch's Batch issue: Task; `Main is red`: Bug | Clear rule, no question per issue |
| 13 | Drafts given to other skills | build-this, dispatch and to-tickets refuse a draft and point to `/plan-this issues <n>`; to-tickets removes `planned` once its tickets exist | Drafts are never worked unplanned |
| 14 | Who sets priority | Tickets inherit the source issue's priority; to-tickets shows a Priority column in its breakdown for the user to change; otherwise the user sets it by hand; only `Main is red` gets `priority:high` automatically | Keeps high meaningful |
| 15 | What high and low do | build-this works high tickets first, low last (within blocker order); dispatch puts high tickets (and their blockers) in the earliest wave allowed, low tickets last; dispatch's loose ends and `status` list open high issues not in a wave at the top | High starts next and never hides; no mid-chain re-planning |
| 16 | Local tracker | Unchanged; GitHub only | Matches the request; local is single-thread |
| 17 | Other defaults | "Note this idea" files a draft issue with a type and any priority the user names; a `planned` issue given to build-this is built from its plan comment with a PR saying `Fixes #<n>`; repair adds the roles to existing tracker docs and creates the labels (Pluneto/skills's own doc and labels included); versions workflow 1.8.0, setup 1.3.0; which-skill and README describe the flow; the live test uses a new private PlunetoD sandbox repo, archived afterwards | Accepted defaults |
| 18 | Grouped drafts with differing priority or milestone | plan-this asks the user, in its grouping step, which priority and which milestone the parent takes whenever the grouped drafts differ | Review finding S5: inheriting only the lowest number's values could downgrade high work; user chose to always be asked |

## Needs from you

- *needed early:* nothing. PlunetoD can create the sandbox repo, and issue types are already enabled on PlunetoD and Pluneto repos.
- *can wait:* "merge if" for the PR on `Pluneto/skills` (a Pluneto repo; without it the build reports the PR URL and stops). Placeholder: PR left open.

## Steps

### M1: Tracker contract and setup

- [x] Bump versions first, so `scripts/validate` passes on every milestone: `scripts/bump` workflow to 1.8.0 and setup to 1.3.0 (any other plugin whose files change later gets its bump in that milestone).
- [x] Probe: create the private sandbox `PlunetoD/issue-types-sandbox`, `gh issue create --type Bug`, and confirm `gh api repos/PlunetoD/issue-types-sandbox/issues/<n> --jq .type.name` prints `Bug`. If the type is discarded, stop and report: decisions 1, 2 and 12 rest on it.
- [x] `plugins/setup/skills/setup-pluneto-skills/issue-tracker-github.md`: add rows `draft`, `planned`, `high` (`priority:high`), `low` (`priority:low`) to the Labels table with meanings; add an **Issue types** section (`Issue types: yes|no`, a role → "Type in this repo" table for bug/feature/task, and the rule for which type each issue gets); add conventions for `--type`, `--milestone` (keep, inherit, filter), priority ordering (high first, low last, within blocker order), "when a user says note this idea" (file a draft) and the draft → planned → tickets flow, including that agents never build, claim, ticket or dispatch a `draft` issue.
- [x] The three `no-tracker-doc.md` copies (to-tickets, wayfinder, build-this): add the four labels to the created-label list and the type default (`--type` when `gh api repos/<o>/<r>/issue-types` lists the type, else skip), identically.
- [x] `plugins/setup/skills/setup-pluneto-skills/SKILL.md`: step 2b also reads `gh api repos/<o>/<r>/issue-types` and fills the Type column and `Issue types: yes|no`; step 4 creates the four new labels; repair check 11 also requires the four roles and the Issue types section; add a repair check that every recorded type is enabled when `Issue types: yes`.
- [x] `docs/agents/issue-tracker.md` (this repo's own): update from the new template, keeping its label names and Parallel work values.
- **Done when:** `scripts/validate` passes; `diff` of the three `no-tracker-doc.md` copies is empty; `rg -n "priority:high|planned|Issue types" plugins/setup plugins/workflow/skills/*/no-tracker-doc.md docs/agents/issue-tracker.md` hits every file; the probe printed `Bug`.
- **Skills:** skill-tools:writing-for-agents - Need: rewriting the tracker template and setup SKILL.md, which every tracker skill reads by role; Provides: its context-pointer rule (a pointer's wording decides when an agent reaches the material) and SKILL-MECHANICS for frontmatter; Without it: new roles defined but weakly pointed to, so skills miss the draft and priority rules.

### M2: Skills set and respect type, priority, draft, planned and milestone

- [x] plan-this: accept `issues <n…>` (GitHub tracker): read each issue's body and comments; refuse non-draft issues unless the user insists; group drafts by goal and show the grouping (decision 8); when grouped drafts differ in priority or milestone, ask which the parent takes (decision 18) and set it on the parent before closing the siblings; after the user's plain yes in step 3, save the plan file, post it as a comment on the parent issue, swap `draft` for `planned`, make grouped drafts sub-issues of the parent and close them with `planned in #<parent>`. Note in the skill that these are its only tracker writes.
- [x] to-tickets: accept a `planned` issue as its source (plan from its plan comment); refuse a `draft`; set `--type` per ticket (decision 12); show a Priority column in the breakdown; tickets inherit the source issue's priority and milestone; make tickets sub-issues of the source; remove `planned` after publishing. In its step 1/3 match search, leave out `draft` and `planned` issues and drafts closed with a `planned in #<parent>` comment (they are plans, not work), so they never count as duplicate, done or append targets.
- [x] build-this (`SKILL.md`, `tickets.md`): refuse a `draft` with the `/plan-this issues <n>` pointer; build a `planned` issue from its plan comment with `Fixes #<n>`; order tickets high → normal → low within blocker order; accept `milestone "<name>"` as the ticket set.
- [x] build-this `fix-ladder.md`: `Main is red` issues get `--type Bug` and `priority:high`.
- [x] dispatch (`SKILL.md`, `worker-prompt.md`): the worker prompt's own red-main report (`worker-prompt.md` step 4) creates `Main is red` issues inline, so it gets the same `--type <bug type>` and `--label <high label>` filled from the tracker doc; exclude draft and planned issues; accept `milestone "<name>"`; place high tickets and their blockers in the earliest wave, low tickets last; Batch issue `--type Task`; loose ends and `status` list open high issues not in a wave at the top.
- [x] wayfinder (and the tracker doc's Wayfinding Frontier line): map and tickets get `--type Task`; "first frontier ticket" becomes high first, then normal, then low, map order within each; amend "the map and type labels are the only labels" so a priority label is allowed and the native type is not counted as a label.
- [x] which-skill and README: one line each on the draft → `/plan-this issues` → `/to-tickets` flow and priority labels.
- **Done when:** `scripts/validate` passes; `rg -n "draft" plugins/workflow/skills/{plan-this,to-tickets,build-this,dispatch}` shows the refuse/skip rule in each; `rg -n "\-\-type" plugins/workflow/skills/{to-tickets,wayfinder,dispatch,build-this}` hits each issue creator, `worker-prompt.md` included; `rg -n "priority" plugins/workflow/skills/wayfinder/SKILL.md` shows the frontier order; the KISS check: no skill gains more than one new section for this change.
- **Skills:** skill-tools:skill-updater - Need: extending six existing skills (plan-this, to-tickets, build-this, dispatch, wayfinder, which-skill); Provides: its "restate the lesson in general terms" check and autonomy principle (a default plus stated assumption over a new user stop); Without it: edits bloat the skills or add new questions the user must answer. skill-tools:writing-for-agents - Need: new trigger wording (`issues <n…>`, `milestone "<name>"`) in skill bodies and descriptions; Provides: its context-pointer wording rule; Without it: plan-this doesn't recognise the issues input reliably.

### M3: Live end-to-end test and rollout

- [ ] In `PlunetoD/issue-types-sandbox` (from M1), with the edited plugins loaded from this worktree: run setup's GitHub steps (labels, Type column, `Issue types: yes`); create a milestone `v-test` and a draft issue with `priority:high` in it; run `/plan-this issues <n>` (a tiny goal) and confirm the comment and `planned`; run `/to-tickets <n>` and confirm types, priority, milestone, sub-issues and removed `planned`; run the `gh issue list --type … --label … --milestone …` queries; run dispatch up to its wave table (no launch) with an extra draft and a low ticket present, and confirm the draft is absent, high is in wave 1 and low is last.
- [ ] Repair test: put a copy of the old template in the sandbox as `docs/agents/issue-tracker.md`, run repair, confirm the four roles, Type column and labels appear; run repair again and confirm it changes nothing.
- [ ] Apply repair to `Pluneto/skills`: create the four labels there (`gh label create`, no `--force`).
- [ ] Archive the sandbox (`gh repo archive PlunetoD/issue-types-sandbox`).
- [ ] Commit, push, open the PR with the `pr` skill, pasting the `scripts/validate` output into its body. `Pluneto/skills` has no CI (no `.github/workflows`), so local validation is the gate; merge only with the user's "merge if".
- **Done when:** every check in "How we'll know it worked" item 2 and 3 has passing `gh` output pasted in the build log; `gh label list -R Pluneto/skills` shows the four labels; the sandbox is archived; `scripts/validate` passes on the PR's latest commit and its output is in the PR body.
- **Skills:** none fit.

## Risks and assumptions

- **Type writes discarded on personal repos** (seen during the preview): M1's probe runs first and stops the build if the type doesn't stick.
- **plan-this gains tracker writes** (comment, labels, closing grouped drafts): limited to the issues the user named, only after the plain yes in step 3; closing grouped drafts is reversible (reopen) and each gets a `planned in #<parent>` comment.
- **Live skill runs in the sandbox may need the plugins loaded from this worktree, not the installed cache:** assume `claude --plugin-dir` (or equivalent) works; otherwise test by following the edited skill text step by step with the same `gh` commands, and say so in the report.
- **Long plan comments:** GitHub's comment limit is 65,536 characters; plans are well below it. If one exceeds it, post a summary plus the plan file path.
- **Renamed types in a repo** (e.g. "Defect" for Bug): handled by the Type column; a repo that disabled a type gets it skipped like `Issue types: no`.
- **Assumption:** `gh issue list --type` and `--milestone` combine with `--label` filters in one call (checked in M3).

## Build log

- M1 Tracker contract and setup (Sonnet, medium): check pass - validate ok, no-tracker-doc copies identical, rg hits all files, probe PlunetoD/issue-types-sandbox#1 reads back type Bug; review-this (Codex) approved in 2 rounds, commit 2610b7b; deviations: new repair check numbered 15, repair re-runs checks 13 and 15 after check 11's rewrite; owed: none; skills: writing-for-agents: role-named short entries
- M2 Skills set and respect type, priority, draft and milestone (Opus, high): check pass - validate ok, draft/type/priority greps hit every skill, only plan-this gained a section; review-this (Codex) approved in 2 rounds, 3 findings fixed, commit 3092f83; deviations: build-this's milestone set takes only agent/human-labelled issues; dispatch puts low tickets no earlier than the last high/normal wave; a plan comment is identified by its "Created <date> with /plan-this" line; grouped drafts' priority/milestone question joins step 1's question call; owed: none; skills: skill-updater: defaults instead of new stops; writing-for-agents: `issues <n…>` and `milestone "<name>"` added to descriptions and argument hints
