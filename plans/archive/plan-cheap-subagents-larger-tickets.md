# Plan: cheap sub-agents for workers, larger tickets

Created 2026-11-12 with /plan-this. Attach this file to a Claude chat and run /build-this (or say "build this plan") to continue.

## Goal

Original request (the user's words):

> Let the dispatch skill allow dispatched agents to spawn in their own cheap subagents to handle cheap tasks. Also with this in mind, let to-tickets make larger tickets

Approved goal: Widen dispatch's worker prompt (`plugins/workflow/skills/dispatch/worker-prompt.md`; step 4 today allows only a light sub-agent for test suites and CI logs, plus the standard and strong fixer rungs) so each worker may hand cheap, self-contained tasks to sub-agents on a cheaper model. The worker keeps every claim, decision, commit, push and tracker write, and checks what comes back before using it. The prompt stays self-contained (no skill names, every command spelled out). Give build-this's milestone brief the same rule. Change to-tickets' slice-size rule so a ticket fits one worker session that offloads cheap work: larger and fewer tickets, each still a vertical slice. Minor bump of the workflow plugin, build the marketplace, validate, one PR on Pluneto/skills, no merge without "merge if X".

**Constraints:**
- Edit the repo source under `plugins/workflow` only (plus this plan and generated marketplace files), never the plugin cache under `~/.claude-pool/plugins`.
- Worker-prompt text stays self-contained: it names no skill, slash command or `CLAUDE.md` (dispatch step 5's grep must stay clean).
- The fix ladder (`build-this/fix-ladder.md`) and its fixer rungs keep their behaviour; dispatch's tier picking for the worker itself is unchanged.
- `scripts/bump workflow minor` (1.8.0 to 1.9.0), `scripts/build-marketplace`, `scripts/validate` (needs PyYAML: `python3 -m venv /tmp/skills-venv && /tmp/skills-venv/bin/pip install pyyaml`, its bin first on PATH).
- One branch, one PR; Pluneto repo, so no merge unless the prompt says "merge if X".
- Code follows KISS, and SOLID for object-oriented code (no code expected; skill text only).

**Skills used while planning:** none. considered skill-tools:writing-for-agents, skipped: it governs writing the text (build phase). Design pass skipped: no users, UI or backend.

**Plan review:** Codex gpt-6.1-sol at high effort, 2 rounds, approved. Fixed: S2 (dispatch step 8 refills the sub-agent model fields and cap after overrides), S3 (a ticket also splits when it would outgrow one session). Disagreed: S1 (claimed Claude sub-agents cannot nest; the docs allow 3 layers by default), but a "can start sub-agents, else do it yourself" gate was added.

## How we'll know it worked

- `scripts/validate` and `scripts/build-marketplace --check` exit 0; the workflow plugin is at 1.9.0.
- Dispatch step 5's grep over the worker prompt's fenced block finds no hit telling the worker to load a skill, run a slash command or read `CLAUDE.md`.
- Keep-list greps still hit: `rg -n "Fix ladder" plugins/workflow/skills/dispatch/worker-prompt.md`, `rg -n "150 words" plugins/workflow/skills/dispatch/worker-prompt.md`, `rg -n "review-this" plugins/workflow/skills/build-this/milestone-brief.md`; `rg -n "single fresh context window" plugins/workflow/skills/to-tickets/SKILL.md` finds nothing.
- Dry run: a fresh sub-agent given only the new to-tickets rules and `plans/archive/plan-workflow-skill-updates.md` drafts a breakdown (no publishing) with fewer or equal tickets than a second fresh sub-agent given the old rules, every ticket still vertical with its own acceptance criteria.
- review-this by the other provider on the full diff returns VERDICT: APPROVE.

## Decisions

| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | What a worker may hand off | Read-heavy work plus mechanical edits, and (Decision 2) whole sub-features | Offloads the bulk that bloats a worker's context, which is what makes larger tickets possible |
| 2 | Two delegation tiers | **Light** (Claude Haiku, medium effort; Codex the light tier, else its smallest model): bounded, fully specified tasks only: searching the code, reading large files, docs or logs, running checks and test suites, triaging CI, mechanical edits in the ticket's own files (renames, boilerplate, a spelled-out change). **Standard** (Claude Sonnet, medium effort; Codex the standard tier, else its default model): more freedom: a sub-feature of the ticket given as goal, files or area it owns and the tests or criteria it must pass; it makes the implementation calls inside that | User: Haiku tasks bounded and specific, Sonnet tasks get more freedom |
| 3 | Model cap | A sub-agent never runs on a stronger model than its worker (light worker: light sub-agents only) | Delegation only ever makes a ticket cheaper and keeps dispatch's tier pick meaningful; a light worker does a harder piece itself |
| 4 | Ticket size rule in to-tickets | A ticket is one deliverable a single worker finishes in one session while handing cheap work to sub-agents: slices sharing an area or files merge; split only for a real blocker, a different Who (agent or human), a hotspot two tickets would both edit, or work that would outgrow one such session (each part still vertical) | Fewer tickets, claims and PRs, still vertical; accepted trade-off: fewer tickets per dispatch wave |
| 5 | build-this | Its milestone brief gets the same rule | Larger tickets also work when one build-this session builds them |

Accepted defaults:
- Every delegated sub-agent replies in at most 150 words, never touches git or GitHub (no commit, push, comment, label or claim) and starts no sub-agents of its own.
- Delegation applies only when the worker or child can start sub-agents with a chosen model; otherwise it does the work itself.
- One editing sub-agent at a time in the worktree (never parallel edits); read-only sub-agents may run in parallel. The worker reads every diff and re-runs the checks itself before committing.
- A standard sub-agent decides no user-level question (the worker prompt's step 5 list): it returns the question to the worker, which parks it as step 5 says (a build-this child marks it `TODO(user)`). It lists its engineering calls so they reach the PR's "Choices made".
- The cap covers this delegation only; the fix ladder's rungs (standard Sonnet, strong Opus) are unchanged.
- The light tier keeps one definition: the fix ladder's light child; the worker prompt's existing light-report format is reused, not duplicated.
- Dispatch step 5 fills the worker's own provider's light and standard models from the tracker doc's Model tiers line (blank: Claude Haiku and Sonnet; Codex its smallest and default model), so a Codex worker gets concrete model names.

## Needs from you

- Needed early: nothing.
- Can wait: the merge go-ahead for the PR ("merge if X"; Pluneto repo).

## Steps

### M1 Workers and build-this children hand cheap work to sub-agents

- [x] In `dispatch/worker-prompt.md` step 4, rewrite the "Save your context" paragraph as the delegation rule: the light and standard tiers with their tasks (Decision 2), the cap (Decision 3) and the accepted defaults; keep the existing light report format, CI-wait line and fix ladder paragraph as they are. Use fields `<light model>` and `<standard model>` for the models.
- [x] In `dispatch/SKILL.md` step 5, say how those two fields are filled (the worker's provider's Model tiers line; blank: Claude Haiku and Sonnet at medium effort, Codex its smallest and default model) and how the cap drops a tier above the worker's own model; in step 8, after overrides and catalog fallbacks settle the worker's provider and model, refill both fields and re-apply the cap (as it already refills the reviewer).
- [x] In `build-this/milestone-brief.md`, add the same rule to the brief's Rules in one or two lines for both T3 children and sub-agents (a nested sub-agent still commits nothing; the child keeps the review and commit).
- [x] Re-read step 5's grep over the edited worker prompt; fix any hit.

Done when: `rg -n "<standard model>" plugins/workflow/skills/dispatch/worker-prompt.md` and `rg -n "standard model" plugins/workflow/skills/dispatch/SKILL.md` hit (in step 5 and step 8); `rg -n -i "sonnet" plugins/workflow/skills/build-this/milestone-brief.md` hits; dispatch step 5's grep over `worker-prompt.md` has no skill, slash-command or `CLAUDE.md` instruction; `rg -n "Fix ladder" plugins/workflow/skills/dispatch/worker-prompt.md` still hits; `wc -w plugins/workflow/skills/dispatch/worker-prompt.md` grows by at most 200 words (baseline 1886).

Skills: skill-tools:skill-updater - Need: edit three existing skill files without duplicating the fix ladder's tier text; Provides: edit-before-adding, the general-lesson check and (through writing-for-agents) single-source and pruning rules; Without it: added lines repeat fix-ladder text and bloat an already long prompt.

### M2 Larger tickets, then ship

- [x] In `to-tickets/SKILL.md`, replace "Each slice fits in a single fresh context window" with the one-session rule (Decision 4), and make step 3's draft merge and step 4's granularity question consistent with it.
- [x] Check `build-this/tickets.md`, `dispatch/SKILL.md` and `which-skill/SKILL.md` for wording that assumes small tickets; adjust only real contradictions.
- [x] Run the dry run from "How we'll know it worked" with two fresh sub-agents (old rules, new rules) on `plans/archive/plan-workflow-skill-updates.md`; record both counts in the Build log.
- [x] `scripts/bump workflow minor`, `scripts/build-marketplace`, `scripts/validate` with the PyYAML venv on PATH, `scripts/build-marketplace --check`.
- [x] review-this (other provider) on the full diff against `main`; fix findings; commit, push, open the PR (pr skill body); leave it unmerged unless told "merge if X".

Done when: `rg -n "single fresh context window" plugins/workflow/skills/to-tickets/SKILL.md` finds nothing; the dry-run counts are logged with new ≤ old; `scripts/validate` and `scripts/build-marketplace --check` exit 0; review-this VERDICT: APPROVE; the PR is open.

Skills: skill-tools:skill-updater - Need: change to-tickets' size rule without breaking its vertical-slice and wide-refactor rules; Provides: smallest-good-edit and pruning rules; Without it: a new rule bolted on beside the old one, contradicting it.

## Risks and assumptions

- A cheap model's edit is subtly wrong: the worker reads every diff, re-runs the checks, and step 8's cross-provider review still sees the whole diff.
- Larger tickets mean fewer per wave, so less parallelism: the hotspot split rule keeps colliding work in separate tickets; dispatch's waves are unchanged.
- Codex's per-spawn model choice may be missing or ignored in some versions: the child then inherits the worker's model; the prompt says "when you can choose the model".
- Sub-agent usage counts toward the same subscription limits: the cap and the bounded light tasks keep it cheaper than the worker doing the work.
- `plans/plan-trim-workflow-skills.md` looks finished (PR #12 merged) but sits outside `plans/archive/`: out of scope here.
- Assumption: Claude Code's Agent tool takes a per-call model alias and effort, and Codex sub-agents are on by default with per-spawn model and effort (sources: code.claude.com/docs/en/sub-agents, learn.chatgpt.com/docs/agent-configuration/subagents, fetched 2026-11-12).

## Build log

- M1 done (2026-11-12): checks pass (greps hit; step-5 grep clean; worker-prompt.md 1886 -> 2081 words, +195). Deviations: Claude workers always get `haiku`/`sonnet` (the Agent tool takes only aliases), so the Model tiers line fills the fields for Codex only; the Standard line is a bracketed `[Worker above the light tier:]` line that dispatch drops, matching the template's convention; a clause says the fix ladder's fixers keep their own rules (they commit locally). Skills: skill-updater + writing-for-agents: kept the existing light report in place instead of a second copy (single source), edit-before-adding on "Save your context".
- M2 steps 1-4 (2026-11-12): to-tickets' "single fresh context window" rule replaced by the one-session rule; "narrow but" dropped from the first slice rule (larger tickets cut wider paths) and "area" defined as one module, skill or feature folder, not a whole package, after the first dry run collapsed a 4-milestone plan into 1 ticket by treating `plugins/workflow` as one area. Step 3's outcome merge and step 4's granularity question checked: consistent, unchanged. build-this/tickets.md, dispatch/SKILL.md and which-skill/SKILL.md checked: no small-ticket wording ("small context" in which-skill is the orchestrator's). Dry run on plans/archive/plan-workflow-skill-updates.md (fresh Sonnet sub-agents, rules only): old rules 7 tickets, new rules 3, each vertical with its own checks. Bumped workflow 1.8.0 -> 1.9.0; scripts/validate ok (6 targets), build-marketplace --check ok. review-changes: Spec fixes applied (sub-agent effort now in the worker prompt and milestone brief; hotspot kept as a reason to keep slices apart, per Decision 4; cap drops the Standard line for any worker below its provider's standard model); Standards fixes applied (negation, a doubled session limit, a no-op clause, field names in step 8). Left as judgement calls: the delegation rule appears in both worker-prompt.md and milestone-brief.md (both prompts must stand alone); model names appear in fix-ladder, worker prompt, dispatch step 5 and milestone brief.
- M2 step 5 (2026-11-12): review-this by Codex gpt-6.1-sol at high effort, 2 rounds, approved; fixed S1 (milestone-brief sub-agents change no git or GitHub state) and S2 (standard sub-agent lists its calls for the child's Deviations). validate ok, build-marketplace --check ok after the fixes.
