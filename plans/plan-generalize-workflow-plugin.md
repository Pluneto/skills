# Plan: general workflow plugin, t3code plugin, ownership-style skills

Created 2026-11-16 with /plan-this. Attach this file to a Claude chat and run /build-this (or say "build this plan") to continue.

## Goal

Original request (the user's words):

> Take ownership of this marketplace, you may also suggest edits other than these.
> - Make the workflow plugin a general work plugin that will work in any repo or scenario.
> - Move t3code related skills into seperate plugin called t3code. This includes t3-orchestration and dispatch.
> - Create an archive folder, move solve-this skill there.
> - Create another plugin called experimental. That is where new skills go for testing.
> - Make build-this more adaptable to deviations from the plan and have the agent take ownership of the build rather than just execute the plan, so make changes to the skills so that you can run them more effectively autonomosly and only include pre-set structure where specifically you would need it, otherwise give yourself freedom to use your own reasoning. Only the purpose of the skills should remain, everything else is up to you. Also if there are deviations in the plan that require new decisions interview the user before starting the next milestone

Approved goal: restructure the `Pluneto/skills` marketplace into a host-neutral `workflow` plugin (usable in any repo, harness or non-code goal), a `t3code` plugin (dispatch, t3-orchestration and every T3-specific rule now embedded in other skills, depending on `workflow`), an `experimental` staging plugin and an unpublished `archive/` folder holding solve-this. Rewrite build-this so the agent owns the outcome instead of executing steps, keeping only the structure a run depends on: done-when checks, the resumable Build log, hard-to-undo stops, and an interview before the next milestone when a deviation needs a new user decision. Rewrite every other workflow skill the same way (purpose kept, fixed structure only where a run needs it). Update scripts, validator, setup, router, README and versions, with a migration path for existing installs.

**Constraints**
- Edit the repo source in this worktree (branch `t3/generalize-workflow-plugin`), never the plugin cache under `~/.claude-pool/plugins`.
- One branch, one PR. `Pluneto/skills` is a Pluneto repo: no merge unless the user says "merge if X".
- Plain Markdown skills only (plus the existing bash template): no hooks, MCP servers or binaries. Skills must still install in Codex and through skills.sh, so every skill keeps `agents/openai.yaml`.
- No symlinks (`scripts/build-marketplace` rejects them). A plugin cannot read another plugin's files (each is cached separately; `..` paths are rejected), so nothing in one plugin links by relative path into another.
- Skills copied from mattpocock/skills keep their LICENSE files.
- Each skill's purpose, name and trigger (frontmatter `name`, and the triggering cases in `description`) stay; everything else in its body is the builder's call.
- Scripts follow KISS (and SOLID for object-oriented code).
- The user may be offered further edits, but only these are in scope.

**Skills used while planning:** research-this (plugin docs facts), interview. use-available-skills: none loaded; considered skill-tools:writing-for-agents (read for the planning phase to shape options; it is a build-phase skill and is on the milestones below); considered design:design-review, skipped: no users, UI, bot or API in the goal.

**Plan review:** Codex gpt-6.1-sol at high effort, 2 rounds, verdict CHANGES on round 2 with one item open (S4), fixed afterwards and not re-reviewed. Round 1 found 5 (1 blocker, 4 should), all verified and fixed: S1 unattended rule no longer overrides the deviation interview; S2 version bumps moved before each milestone's validation; S3 term cleanup moved into M2; S4 archived solve-this marked `metadata.internal: true` for skills.sh, listing check uses `--full-depth`; S5 absolute `--plugin-dir` path in the behaviour scenarios. None disagreed or declined; none needed a user decision.

**Facts the plan rests on** (Claude Code plugin docs, fetched 2026-11-16: code.claude.com/docs/en/plugins-reference, /plugin-dependencies, /plugins/host-marketplace.md):
- `plugin.json` accepts `"dependencies": ["workflow"]`; a bare name resolves in the same marketplace and is installed with the plugin; the dependent plugin is disabled when the dependency is disabled or missing.
- No deprecation state exists. A skill removed from a plugin disappears for installed users on update. `renames` in `marketplace.json` covers whole plugins only (not needed here: no plugin is renamed or removed).
- Folders outside `plugins/` are not published.
- Not verified: how Codex and skills.sh treat `dependencies` (assumed ignored; see Risks).

## How we'll know it worked

- `scripts/validate` and `scripts/build-marketplace --check` exit 0 locally, and the `validate` workflow is green on the PR's latest commit.
- Host-neutrality gate: `scripts/validate` fails on any case-insensitive match of `\bt3\b|t3-|t3code|delegate_task|t3_thread|orchestrator_capabilities` under `plugins/workflow/`; it passes on the final tree and is shown failing once on a seeded line.
- `rg -n -i "solve-this|autopilot" plugins/` finds nothing; `archive/solve-this/SKILL.md` exists.
- Install smoke test in a scratch directory with a scratch `CLAUDE_CONFIG_DIR`: add the worktree as a local marketplace, `claude plugin install t3code@pluneto-skills`, then `claude plugin list --json` shows both `t3code` and `workflow` enabled; `claude plugin details workflow` lists no dispatch, t3-orchestration or solve-this.
- Behaviour check of the new build-this, headless (`claude -p --plugin-dir <absolute path of this worktree>/plugins/workflow`, run from a scratch git repo; the run's transcript must show build-this loaded from that path), three scenarios: (a) a two-milestone sample plan builds to the end with no opening question, both checks run and a `## Build log` line per milestone; (b) a plan whose second milestone rests on a Decision the first milestone proves impossible ends milestone 1 with the user-level question raised and milestone 2 not started (a headless run has no one to answer, so asking and stopping is the pass); (c) the same plan with the prompt stating the run is unattended parks the decision in the Build log and report, asks nothing, and does not build the dependent milestone.
- review-this on the final diff, from another model, returns APPROVE.

## Decisions

| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | General plugin's name | Keep `workflow` | Existing installs, `workflow:` prefixes and repo settings keep working |
| 2 | Autopilot mode after solve-this is archived | Keep the rule, generalised: one caller-neutral **unattended** rule ("when the caller says the run is unattended: ask nothing, take the recommended option, record it"), set only by a caller that has no user to ask (a headless run, a child or worker brief). Being called by a skill does not by itself mean unattended: an interactive build-this calls interview with the user present, and interview asks. The words `solve-this` and `autopilot` leave every published skill | build-this children, dispatch workers and headless runs still need it |
| 3 | `experimental` on day one | `plugins/experimental/` with `plugin.json` and a README, unpublished: the build script skips a plugin with no skills and lists it once it holds one | No empty install, nothing unproven forced in |
| 4 | Rewrite depth | Every workflow skill gets the ownership rewrite | One consistent style; accepted: a large diff |
| 5 | build-this's opening questions (children? straight through?) | Removed. The agent decides delegation and pace itself; it pauses only for new user-level decisions and hard-to-undo steps. A preference stated in the prompt wins | The ownership goal; accepted: the user no longer chooses up front |
| 6 | Which deviations stop the build for an interview | User-level only: a change to a recorded Decision, the goal, scope, product behaviour, UI or copy, cost, a new service or dependency, privacy or security. The interview skill runs at the milestone boundary, before the next milestone starts. Engineering fixes are made and logged | The user's explicit requirement, scoped so builds still flow |
| 7 | Delegation in the general build-this | Generic wording: delegate when it keeps the context clean, with whatever the harness offers, and follow the host's orchestration skill when one is installed. t3-orchestration carries the T3 child rules (T3 children, review-before-commit, waiting) | Works on any harness; accepted: T3 children need `t3code` installed |

Accepted defaults:
1. `fix-ladder.md` splits: the generic check-and-repair ladder stays with build-this; the T3 waits and the red-main procedure move into `t3code` (red main beside dispatch, with `main-health.md`).
2. `archive/solve-this/` at the repo root, outside validation and the marketplace.
3. Setup repair gains a check that offers `t3code` where T3 tools are present and `workflow` is enabled; README documents the move.
4. `scripts/validate` enforces the host-neutrality gate above.
5. Versions: `workflow` 2.0.0 (skills removed), `t3code` 1.0.0, other plugins bumped as touched (`scripts/bump`).
6. The finished `plans/plan-trim-workflow-skills.md` moves to `plans/archive/`.
7. The which-skill router stays in `workflow` and names no host: the validator's "named in which-skill" check exempts `t3code` and `experimental`; which-skill carries one neutral line that host plugins add their own orchestration skills, and `t3code` skills are listed in README.

## Needs from you

- *Needed early:* nothing.
- *Can wait:* the "merge if" go-ahead for the PR (until then the PR stays open, green). After merge: run `claude plugin marketplace update pluneto-skills`, `claude plugin install t3code@pluneto-skills --scope user` on the box, and `/setup:setup-pluneto-skills repair` in repos that list the old skills in their CLAUDE.md block.

## Steps

### M1. Restructure plugins and scripts

- [x] `git mv` `plugins/workflow/skills/{dispatch,t3-orchestration}` to `plugins/t3code/skills/`; create `plugins/t3code/.claude-plugin/plugin.json` (version 1.0.0, `dependencies: ["workflow"]`, same author/license/homepage fields as the others).
- [x] `git mv plugins/workflow/skills/solve-this archive/solve-this`; add `metadata: {internal: true}` to its frontmatter so skills.sh (which scans the whole repo; `skills` 1.7.4 skips `metadata.internal === true`) no longer offers it; add `archive/README.md` (what the folder is; to restore a skill, move it back and remove the marker).
- [x] Bump before validating (the validator rejects a changed plugin whose version equals origin/main's): `workflow` to 2.0.0 now, once, by `scripts/bump workflow major`.
- [x] Create `plugins/experimental/.claude-plugin/plugin.json` (0.1.0) and `plugins/experimental/README.md` (new skills land here; promote by `git mv` into a published plugin).
- [x] `scripts/build-marketplace`: skip (no manifest rewrite, no marketplace entry, no error) a plugin with no `skills/<name>/` folders; keep `dependencies` and other manifest fields intact when regenerating.
- [x] `scripts/validate`: skip the same skill-less plugin for the CLI and version checks; exempt `t3code` and `experimental` skills from the router check; drop `solve-this` handling; point `scripts/test-main-health`'s default at `plugins/t3code/skills/dispatch/main-health.md`.
- [x] Repair the links the moves broke so the tree validates (dispatch and t3-orchestration no longer link into `../build-this/`; a temporary copy of the needed fix-ladder text into t3code is fine, M2 settles it).
- **Done when:** `scripts/build-marketplace` then `scripts/validate` exit 0; `marketplace.json` lists design, engineering, setup, skill-tools, t3code, workflow and not experimental; `scripts/test-main-health` passes; `npx skills@latest add <worktree path> --list --full-depth` does not list solve-this, and does list it when the marker is temporarily removed (so the check proves the marker, not the default shallow scan).
- **Skills:** t3-lessons - Need: this milestone changes the validator that CI runs; Provides: the box's recorded CI lessons for this repo family; Without it: a repeat of a known CI failure. (Box rule; load if present, else skip.)

### M2. Make `workflow` host-neutral

- [ ] Split `build-this/fix-ladder.md`: generic ladder (tiers, light check, fixer rungs, review of a rung, the end) stays, with provider-neutral tier wording; T3 waits (`watch_pull_request`), T3 child start and the Red main section move into `plugins/t3code/` (red main as a dispatch support file; child and wait rules in t3-orchestration).
- [ ] Move the T3 child rules out of build-this's SKILL.md, `milestone-brief.md` and `tickets.md` into t3-orchestration (a "Building a plan's milestones with T3 children" section: child kind, shared checkout, review-this before commit, Held).
- [ ] Remove T3 wording from research-this (sub-agent model line becomes harness-neutral; the T3 form moves to t3-orchestration), to-tickets (the `#<n>` composer note; `/dispatch` offer becomes "a parallel-worker skill, if your host plugin has one"), which-skill.
- [ ] Generalise autopilot (Decision 2) in interview, plan-this, review-this, use-available-skills, and in engineering (tdd, diagnosing-bugs, review-changes) and design (the three identical `contract.md` copies, ui-craft): one wording, no `solve-this`, no `autopilot`.
- [ ] Setup's `issue-tracker-github.md` template and this repo's `docs/agents/issue-tracker.md`: keep the Parallel work section (dispatch reads it) but drop T3-pool examples from the template; fields obsolete since dispatch 1.15 (Model tiers) are removed or reworded host-neutrally.
- [ ] Remove the remaining `solve-this` and `autopilot` mentions in build-this (opening and finishing rules; M3 rewrites the rest) and in setup's repair check 12, so this milestone's zero-match check can pass.
- [ ] Bump each plugin this milestone first touches (setup, engineering, design; skill-tools if touched) with `scripts/bump <plugin>`, once per plugin for the whole PR.
- [ ] Add the host-neutrality gate to `scripts/validate`.
- **Done when:** the gate passes on the tree and fails on a seeded `delegate_task` line under `plugins/workflow/` (then removed); `rg -n -i "solve-this|autopilot" plugins/` is empty; `scripts/validate` exits 0; every relative Markdown link under `plugins/` resolves inside its own plugin.
- **Skills:** skill-tools:writing-for-agents - Need: rules are being moved between skills and reworded; Provides: single source of truth, pointer wording and positive-phrasing rules; Without it: the same rule left in two plugins, or a host hook too weak to trigger t3-orchestration.

### M3. Rewrite build-this for ownership

- [ ] Rewrite `build-this/SKILL.md` around the outcome: the agent owns getting the plan's goal built and proven; the plan is the agreed intent and decisions, not a script. Milestone steps are a suggestion; done-when checks and Decisions are binding.
- [ ] Keep, as explicit structure: where the plan comes from and resume from the Build log; run each done-when check and treat reports as claims; the Build log line per milestone; deviations (engineering: fix and log; user-level per Decision 6: finish the current milestone if it can stand, then run **interview** on the open decisions before the next milestone starts, record the answers in the plan's Decisions table, and re-plan the remaining milestones); hard-to-undo stops; secrets by name only; the final report with evidence; archive the plan.
- [ ] Remove the opening questions (Decision 5), the model table, the per-step skill-loading procedure and other steps the agent reasons out itself; delegation per Decision 7; only a run its caller declared unattended (Decision 2) parks user-level deviations instead of interviewing, and continues with independent milestones; every other run interviews.
- [ ] Shrink `milestone-brief.md` to what a child cannot infer (what the brief must carry, the report fields, the Build log line, the handoff file), and `tickets.md` and the generic `fix-ladder.md` likewise. `no-tracker-doc.md` stays byte-identical in its three copies.
- [ ] Update plan-this's hand-off and Saving format to match: milestones state the outcome, Done when and constraints; checkbox steps become optional hints.
- **Done when:** the three headless behaviour scenarios in "How we'll know it worked" pass; `wc -w plugins/workflow/skills/build-this/*.md` (5,099 before) is at most 3,000; a preservation checklist in the Build log confirms each kept item above is present in the new text; `scripts/validate` exits 0.
- **Skills:** skill-tools:writing-for-agents - Need: a 2,478-word step script becomes a short ownership document; Provides: completion criteria (clarity and demand), no-op hunting, positive phrasing, progressive disclosure; Without it: vague bounds that let a build stop early, or prohibitions that reintroduce the scripted behaviour.

### M4. Rewrite the other workflow skills

- [ ] Same treatment for plan-this, interview, research-this, review-this, use-available-skills, to-tickets, wayfinder, to-questionnaire, handoff, wizard, which-skill, and for dispatch and t3-orchestration in `t3code`: state the purpose and what done looks like, keep only structure a run depends on (output formats other skills or tools parse, tracker commands, guardrails against collisions or unasked decisions, budgets), delete what the agent does by default.
- [ ] Before each rewrite, list that skill's contracts with others (what callers pass and expect back: plan file sections, review-this's verdict line, research-this's Verdict and Facts lines, interview's hand-back, ticket and label conventions from the tracker doc) and confirm each after.
- [ ] Keep frontmatter `name` and the triggering cases in each `description`; refresh `agents/openai.yaml` where a description changed.
- **Done when:** every contract in the per-skill lists is confirmed in the Build log; `wc -w plugins/workflow/skills/*/*.md plugins/t3code/skills/*/*.md` total is below the 23,324 baseline minus solve-this; `scripts/measure-skills plugins/workflow` always-on total does not rise; `scripts/validate` exits 0.
- **Skills:** skill-tools:writing-for-agents - Need: thirteen skills pruned to purpose; Provides: the pruning tests (relevance, no-ops, duplication, sediment) and split rules; Without it: cuts that remove a cross-skill contract, or rewrites that keep sediment.

### M5. Migration, docs, release

- [ ] Setup skill: plugin list includes `t3code` (not recommended by default; offered where T3 tools are present); repair check for it; CLAUDE.md block rule unchanged.
- [ ] which-skill: main flow without solve-this and T3 wording; one neutral host-plugin line. README: plugin table, install lines, a "Moved in workflow 2.0" note (dispatch and t3-orchestration → `t3code`; solve-this archived; how to update), script descriptions. This repo's `CLAUDE.md` block and `.claude/settings.json` enable `t3code`.
- [ ] Confirm every changed plugin was bumped exactly once against origin/main (workflow 2.0.0, t3code 1.0.0); `scripts/build-marketplace`; move `plans/plan-trim-workflow-skills.md` to `plans/archive/`.
- [ ] Install smoke test; open the PR with the pr skill; watch CI; run review-this on the diff.
- **Done when:** every check in "How we'll know it worked" passes; the PR is open with green CI on its latest commit; nothing is merged.
- **Skills:** engineering:pr - Need: the PR body for a large restructuring; Provides: the repo's PR body format; Without it: a body reviewers can't scan. t3-lessons - Need: CI and release work on this box (box rule); Provides: recorded lessons; Without it: a repeated known failure.

## Risks and assumptions

- **Behaviour drift from rewriting 13 skills at once.** Mitigation: per-skill contract lists confirmed before and after (M4), the headless build-this scenarios, cross-model review of the diff. Residual: skills other than build-this are not behaviour-tested end to end.
- **Existing users lose dispatch, t3-orchestration and solve-this on update** with no in-product notice (no deprecation state exists). Mitigation: README note, setup repair check, major version. Known users are this box and the owner.
- **t3-orchestration may not trigger from build-this's generic hook.** Mitigation: its description names the trigger ("before delegating or waiting on child agents on T3 Code"); checked once by a headless run on this box with `t3code` loaded if T3 tools are reachable there, else recorded as unverified.
- **Codex and skills.sh** are assumed to ignore `dependencies`; not verified. `t3code` skills name the workflow skills they call, so a missing one is visible.
- **The headless scenarios cost model usage** and can be flaky; each is run at most 3 times and the result recorded as it is.
- **Assumption:** `claude plugin validate --strict` accepts `dependencies` in `plugin.json` on the CI's Claude Code version (the field is documented); M1's validate run confirms it.

## Build log

- M1 Restructure plugins and scripts (main agent): check pass - build-marketplace ok (6 plugins: design engineering setup skill-tools t3code workflow), validate ok (7 targets), test-main-health 13/13, skills.sh `--list --full-depth` omits solve-this with the marker and lists it without; deviations: fix-ladder.md copied whole into t3code/dispatch as the temporary link repair (M2 splits it), plans/plan-trim-workflow-skills.md archived here instead of M5; owed: none; skills: t3-lessons: index read, no topic matched (no workflow file changed), no visible effect
