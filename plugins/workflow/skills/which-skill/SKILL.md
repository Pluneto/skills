---
name: which-skill
description: Ask which skill or flow fits your situation. A router over the pluneto-skills plugins.
disable-model-invocation: true
---

# Which skill

You don't remember every skill, so ask. Answer the user's situation with the one or two skills that fit, the flow they sit on, and the plugin each lives in.

Before stating what a skill does or recommending a step be skipped, read that skill's SKILL.md: the summaries here are for orientation only. A skill whose plugin isn't installed is still worth naming, with the plugin to install.

A **flow** is a path through the skills. Most work travels the **main flow**; **on-ramps** generate work that merges onto it; everything else is standalone or a vocabulary layer underneath.

## The main flow: goal → shipped (workflow, design, engineering)

1. **`/plan-this`** (workflow) deepens the goal the way a top professional would, researches what already exists (research-this), interviews you over a design tree (interview), offers a review of the plan by another provider (Codex from Claude, Claude from Codex), and ends with a plan with milestones and checks: saved as a file, handed straight to build-this, or both.
2. **Design** (design) runs inside the flow, on goals with users, a UI, a bot or an API. While planning, plan-this runs **product-context** (drafts `PRODUCT.md`, the repo's ranked user-types with MoSCoW needs under permanent IDs; converts a legacy `UX/User_Types.md`) and **design-review** (critiques the design: backend, API contracts, UI and accessibility, UX copy, chat bots, coverage of the user-types). Their Open questions join the interview and their checks land in the milestones' Done when. While building, milestones carry design-review on their Skills lines, and use-available-skills matches **ui-craft** (builds any UI so it looks deliberate: theme first, surface modes, states, accessibility, no AI-generated tells) to the milestones that build a UI. Each also runs on its own, for example `/design:design-review` on any plan or existing system.
3. **Branch: is this a multi-session build?**
   - **No** (the usual case) → **`/build-this`** works the plan milestone by milestone; it asks whether to build each milestone in a fresh child, a T3 child or sub-agent (recommended at 3 or more milestones or tickets) and logs progress in the plan file, so long builds keep a small context and can resume.
   - **Yes** → **`/to-tickets`** (workflow) splits the saved plan into tracer-bullet tickets with blocking edges (local files under `plans/<feature>/tickets/`, or GitHub Issues, as the repo's tracker doc says), then **`/build-this`** works the tickets in blocker order, one session or several. To run them **in parallel** (GitHub tracker only), **`/dispatch`** (workflow) groups them into waves that touch no shared hotspot, writes a tracking issue with a self-contained prompt per ticket (Claude or Codex), and launches a wave as T3 threads when you reply `launch wave N` (or chains waves with `launch waves 1-3 merge if green`).
   - **Want it done with no questions?** → **`/solve-this`** runs plan-this and build-this on autopilot, retries until the checks pass, and proves it.
4. While building, code gets written test-first with **tdd** (engineering) when the milestone calls for it, and build-this closes with **review-changes** (engineering): a two-axis review (Standards from `CODING_STANDARDS.md`, Spec from the plan or ticket) of the diff, then offers **review-this** (workflow): a reviewer from the other provider grills the build against the plan, round after round until it approves (solve-this runs it without asking). Use **`/review-changes`** on its own to review any branch or PR since a fixed point. **pr** (engineering) shapes the PR body when the work goes up as a pull request.
5. **`/reflect`** (skill-tools) closes the loop, in the same session: it finds what caused friction and applies up to five lean fixes to notes, skills, checks or coding standards, so the next build starts further ahead.

**Design questions on paper won't settle?** Detour through **`/prototype`** (engineering): throwaway code that answers one question (a state model, a UI), captured into the plan or ticket.

## On-ramps

- **Something's broken** → **diagnosing-bugs** (engineering). For the hard ones: it builds a tight feedback loop that goes red on this bug before theorising, then fixes with a regression test. solve-this calls it when a check keeps failing. Afterwards, `/reflect` asks what would have prevented it.
- **A huge, foggy effort, too big for one session** → **`/wayfinder`** (workflow). It charts a map of decision tickets (interview, research, prototype) and resolves them one at a time. When the map clears it hands off to `/plan-this`, which keeps the map's decisions and plans only the gaps. Save it for efforts you can't hold in one session; a well-scoped feature goes straight to `/plan-this`.
- **Is there already a tool for this? / what's true about X?** → **research-this** (workflow): a sourced Adopt / Extend / Build verdict, or in facts mode a cited Markdown file from primary sources.

## Codebase health (engineering)

- **`/improve-codebase-architecture`** surveys the codebase for deepening opportunities and interviews you through the one you pick; the result is a goal to take into `/plan-this`.
- **codebase-design** is the deep-module vocabulary (module, interface, depth, seam, adapter) for designing a module's shape. tdd and improve-codebase-architecture both speak it.
- **domain-modeling** sharpens the project's domain language: challenge a fuzzy term, keep `GLOSSARY.md` clean, record a hard-to-reverse decision as an ADR.

## Standalone (workflow)

- **interview**: the design-tree interview on its own. Say "grill me" on any plan, decision or idea, with or without a repo.
- **review-this**: grill a diff, plan or implementation with another model (Codex from Claude, Claude from Codex), round after round until it approves. review-changes is the one-pass review.
- **`/to-questionnaire`**: when the blocker is in **someone else's** head, it writes them a questionnaire aimed at the gap. What comes back feeds `/plan-this`.
- **wizard**: for steps only a human can take (provisioning, credentials, CI secrets, a third-party dashboard): an interactive bash script that walks through them. The agent reaches for it when it hits such a wall.
- **`/handoff`**: a portable Markdown file to continue in another harness, directory or with a colleague.
- **use-available-skills**: decides, on evidence, which other skills are worth loading for a task. plan-this and build-this run it themselves.

## Writing skills (skill-tools)

- **writing-for-agents**: the reference for anything an agent reads: skills, AGENTS.md, CLAUDE.md.
- **skill-updater**: change or fix an existing skill and deliver it the right way (commit and push for a marketplace clone).
- **`/skill-ozempic`**: slim a bloated skill, cut by cut, with you approving each.

## Phase boundaries

At the boundary between two phases (planning → building, building → review) choose: continue, `/clear`, `/handoff`, a subagent, or `/compact`, in that order of preference. Read [PHASE-BOUNDARIES.md](PHASE-BOUNDARIES.md) for the ordered questions. Within one long build, build-this can keep context small by giving each milestone a fresh sub-agent; it also offers a handoff file at each check-in.

## Precondition

**`/setup:setup-pluneto-skills`** (setup, installed once at user scope): installs and repairs the plugins in a repo, configures the tracker (GitHub Issues or local `plans/` files) and writes the CLAUDE.md block.
