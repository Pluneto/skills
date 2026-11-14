# Plan: dispatch as an ownership brief, no model enforcement

Created 2026-11-14 with /plan-this. Attach this file to a Claude chat and run /build-this (or say "build this plan") to continue.

## Goal

**Original request (user's words):** "I want to give as much freedom as possible to the dispatch skill when running in t3code. Remove the model enforcement, I want to change the skill as well to be more brief and let it decide for the task, I found that this helps dispatch a lot "Take ownership of these issues and solve problems that don't require me on your own. Keep your own context window clean. Dispatch appropriate level agents for the task." In general strip down a lot of the restrictions"

**Deepened goal:** Rewrite the workflow plugin's `dispatch` skill (repo `Pluneto/skills`, local clone `~/projects/pluneto-skills/skills`, currently workflow 1.14.2 on `origin/main`) for T3 Code as a short brief built around ownership. The orchestrator owns the named issues, solves whatever doesn't need the user, keeps its own context clean, and starts agents at whatever model and effort it judges right for each task. Remove all model enforcement: the model-table, floor, exclusion and fallback logic in dispatch, and the plugin-wide `agent_cap` hook. Remove the fixed worker-prompt template; the orchestrator writes each worker's brief from a short list of must-haves. Keep only the guardrails that prevent collisions or decisions made without the user. Ship it as one validated PR with version bumps, which the user merges.

**Constraints**
- Scope: dispatch skill, the `agent_cap` hook and its test/validate wiring, and the tracker template's Model database field (setup plugin plus the repo's own `docs/agents/issue-tracker.md`). Other skills' model guidance (build-this milestone-brief, research-this Haiku pin, fix-ladder tiers) stays untouched.
- `PlunetoD/t3-retro` is not changed; dispatch just stops reading `models.md`.
- SKILL.md stays at about 600 words or less, with the user's quote as its core.
- The skill keeps its `name: dispatch`, its folder, `disable-model-invocation: true` and `agents/openai.yaml` (validate requires `allow_implicit_invocation: false`).
- Repo rules (`~/projects/pluneto-skills/AGENTS.md`): run `python3 scripts/build-marketplace` and `python3 scripts/validate`; pre-commit hook needs a GitHub noreply author email; short imperative commit subjects.
- The user merges the PR (auto mode denies `gh pr merge`).
- Code follows KISS, and SOLID for object-oriented code.

**Skills used while planning:** none. Considered skill-tools:writing-for-agents and skill-tools:skill-updater (build-phase skills, matched below), and design:design-review (skipped: no users, UI or API).

**Plan review:** Codex gpt-6.1-sol at high, 2 rounds, approved. Fixed: S1 (Review command fields said blank = no pre-PR review, contradicting mandatory review; reworded), S2 (`measure-skills` can't measure SKILL.md words; size check uses `wc -w`). Disagreed, declined, needs decision: none.

## How we'll know it worked

- `python3 scripts/validate` and `python3 scripts/build-marketplace` pass on the branch (no leftover reference to `test-agent-cap` or `agent_cap`).
- `wc -w plugins/workflow/skills/dispatch/SKILL.md` prints about 600 or less (today SKILL.md + worker-prompt.md ≈ 3,500 words; `measure-skills` only counts always-on frontmatter, which is 0 for dispatch).
- `git grep -nE 'agent_cap|Floor|floor|models\.md|Model database|worker-prompt' -- plugins docs scripts README.md` shows no stale reference (except unrelated hits such as design-review's "rough floor").
- Behaviour dry run: `claude -p --plugin-dir plugins --add-dir plugins` with a prompt invoking dispatch on a throwaway or read-only set of issues, in plan-only mode (tell it not to launch or write to the tracker), reads as: picks models freely, names the guardrails, and writes worker briefs that contain claim, branch, checks, review, merge-on-green, release and park rules.
- Real-world outcome (after merge, on the user's next T3 batch): issues close without the user prompting each step, and no transcript shows a model-cap denial.

## Decisions

| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | `agent_cap` hook | Delete `plugins/workflow/hooks/agent_cap.py`, `hooks/hooks.json`, `scripts/test-agent-cap` and validate's reference to it | User wants no model enforcement; accepted that build-this/solve-this sessions can also start stronger sub-agents |
| 2 | Launch gate | Start right away when invoked: post the plan to the tracking issue and launch; the user can type `stop` | Matches "take ownership"; accepted no pre-launch review of the waves |
| 3 | Merging | Workers merge their own PR once CI is green and review passed; no `merge if green` keyword | Issues close without the user; CI + review are the gate |
| 4 | Worker brief | Delete `worker-prompt.md`; SKILL.md lists the must-haves each brief carries; the orchestrator writes each brief | Shortest and fitted to the task; accepted variation between briefs |
| 5 | Review | Every PR is reviewed by a different model before merge; worker or orchestrator picks the model and the way | Only gate besides CI on auto-merge; the fixed cross-provider rules go |
| 6 | Model table | Dispatch stops reading t3-retro `models.md`; that repo is untouched | Keeps the change to one repo; table becomes unused until decided separately |
| 7 | Other skills | Leave build-this, research-this, fix-ladder model guidance as is | Focused PR |
| 8 | Guardrails kept | Claim each issue via the tracker doc; never two workers on the same hotspot at once; park user-level decisions with the decision label; no writes to shared or staging data; fix a red main before merging more | Accepted default: these prevent collisions and decisions made without the user |
| 9 | Record | One tracking issue per batch as the running record | Accepted default: survives context loss, user can follow along |
| 10 | Watching | Orchestrator stays until every issue is closed, parked or released, then sends one report | Accepted default |
| 11 | Tracker template | Remove the Model database field (setup template, setup SKILL.md's keep-list, repo's own `docs/agents/issue-tracker.md`); keep Model tiers, Max workers, Areas map, Main health, Review commands (now optional helpers; blank no longer means "no review") | Accepted default: Model database has no reader left; the others are still used (fix-ladder, main-health.md) or are optional helpers |
| 12 | Size | SKILL.md about 600 words or less, the user's quote as its core | Accepted default |
| 13 | Versions | workflow → 1.15.0 (minor), setup → patch bump | Accepted default |

## Needs from you

- *can wait*: merge the PR (M1, last step); then run the next real T3 batch with the new dispatch and say how it went.

## Steps

### M1: Lean dispatch, no model enforcement, PR open

- [x] In `~/projects/pluneto-skills/skills` (on `main`, pulled to 90bbe3f on 2026-11-14): branch `dispatch-ownership`. Enable the hook if needed: `git config core.hooksPath scripts/hooks`.
- [x] Rewrite `plugins/workflow/skills/dispatch/SKILL.md` (≤ ~600 words): frontmatter (same name, updated description and argument-hint, `disable-model-invocation: true`); the user's quote as the core instruction; the kept guardrails (Decision 8) each with a one-clause reason; tracker doc as source of labels and claim/release commands; the tracking issue (Decision 9); start right away (Decision 2); worker-brief must-haves (claim, branch `t3/<n>-<slug>`, worktree, checks, review by a different model, merge when green, release, park user-level decisions with the decision label, plain-text questions in T3 threads, not question tools); red main via `main-health.md` and build-this's `fix-ladder.md`; load **t3-orchestration** for launching and waiting; watch until settled then one report (Decision 10). No model table, floor, tiers, fallbacks, override syntax or wave commands.
- [x] Delete `plugins/workflow/skills/dispatch/worker-prompt.md`; keep `main-health.md` (and `scripts/test-main-health`).
- [x] Update `plugins/workflow/skills/dispatch/agents/openai.yaml` `short_description` if the wording no longer fits.
- [x] Delete `plugins/workflow/hooks/agent_cap.py`, `plugins/workflow/hooks/hooks.json` and `scripts/test-agent-cap`; remove `test-agent-cap` from `scripts/validate` (docstring line 13 and the loop at line 123); `plugin.json` declares no `hooks` entry (the folder is auto-discovered), so deleting the folder's files is enough; remove the now-empty `hooks/` folder.
- [x] Remove the Model database field from `plugins/setup/skills/setup-pluneto-skills/issue-tracker-github.md`, from setup SKILL.md's keep-list (line 29), and from the repo's `docs/agents/issue-tracker.md`; reword fallbacks that no longer hold: Model tiers' "dispatch still suggests the effort", and both Review command fields' "blank: no pre-PR review" (blank now means: the worker gets its review from a different model some other way, e.g. a sub-agent or `delegate_task`; merging needs a passing review either way, Decision 5). Mark the Review commands as optional helpers.
- [x] Adjust the `which-skill` dispatch line and README if they describe the old behaviour.
- [x] `python3 scripts/bump workflow minor` and `python3 scripts/bump setup`; `python3 scripts/build-marketplace`; `python3 scripts/validate`; `wc -w plugins/workflow/skills/dispatch/SKILL.md`; the stale-reference grep.
- [x] Behaviour dry run (see How we'll know it worked), plan-only; fix wording if a must-have is missing from the briefs.
- [x] Commit (staged by name), push, open PR with summary and validation done; hand the PR link to the user to merge.

**Done when:** validate passes, SKILL.md ≤ ~600 words, no stale references, the dry run's briefs carry every must-have, and the PR is open.

**Skills:**
- `skill-tools:skill-updater`: Need: rewriting a skill in the Pluneto/skills marketplace clone; Provides: delivery rules for marketplace skills (`git pull` the source repo, keep `name`/frontmatter, edit or delete before adding); Without it: frontmatter or name drift, or an edit made in the plugin cache that gets lost.
- `skill-tools:writing-for-agents`: Need: a ≤ 600-word SKILL.md whose few steps still have checkable endings; Provides: completion-criterion and sprawl rules; Without it: vague "done" conditions, so the orchestrator stops early.

## Risks and assumptions

- **Auto-merge with free model choice ships a weaker change.** Mitigation: review by a different model is mandatory (Decision 5) and CI must be green; red main stops merges.
- **Collisions without fixed waves.** Mitigation: claims and the "no two workers on one hotspot" rule stay.
- **Hook deletion affects all workflow sessions.** Accepted (Decision 1); orchestrators may now start more expensive sub-agents.
- **t3-retro keeps maintaining an unused table.** Accepted (Decision 6); a separate decision later.
- **Assumption:** T3's `t3_thread_launch` works without a model argument (defaults to the provider's default). The orchestrator reads `orchestrator_capabilities` per t3-orchestration anyway.
- **Assumption:** Codex/Mistral workers can follow an orchestrator-written brief without a fixed template; to confirm on the first real batch.

## Build log

- 2026-11-14 M1 done (built inline, straight through; base 90bbe3f). Checks: validate ok; `wc -w` SKILL.md 801 (body ~755) vs ~3,500 before; stale-reference grep clean except design-review's unrelated "rough floor". Dry runs (claude -p, zephyr-homelab issues 249 250 269 75, read-only) on Sonnet medium and Opus high: no models.md read, per-task model picks, briefs carry every must-have and end with `merge if green`. Deviations: (1) SKILL.md ~800 words, not ~600: runs 1, 3 and 4 showed repos' tracker docs (Model database field) and older batch issues pull the agent back to the model table and the old prompt, so the skill names those fields to ignore; run 2 showed a brief without `merge if green` makes the worker skip `--merge` because repos' land rules look for that line, so every brief ends with it. (2) Also fixed stale dispatch wording in fix-ladder.md (2 lines), which-skill, README and the tracker label table; these describe dispatch, not model guidance (Decision 7 untouched). (3) Model tiers note in the tracker template now says it serves build-this's fix ladder. Skills: skill-updater (kept name/frontmatter, edited in the source clone, bump + validate), writing-for-agents (co-location fix: moved the legacy-field exception next to the doc read after run 4 ignored it a paragraph away).
- 2026-11-14 review-changes (spec axis): added the blank-Review-command fallback (sub-agent or `delegate_task`) to the review guardrail. Kept as designed: briefs ending in `merge if green` implement Decision 3 (the user no longer types it; repos' land rules need it in the task); Max workers as the cap, the stay-in-turn watch, stale claims and the local-tracker stop are carried over from the old skill in service of Decisions 8-10. The stale-reference grep's one `Model database` hit is SKILL.md's own instruction to ignore that field.
- 2026-11-14 review-changes (standards axis): fixed a stale "waves" line in to-tickets/SKILL.md:108. Kept: the legacy-field paragraph (dry runs 1, 3, 4 needed it), the user's quote, the guardrails restated in the brief (workers never see SKILL.md).
- 2026-11-14 review-this: Codex gpt-6.1-sol high, 2 rounds, APPROVE. Fixed S1 (red-main guardrail blocked its own fix PR; the fix now merges on its own green CI).
