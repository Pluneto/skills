---
name: "build-this"
description: Carry out an agreed plan from start to finish, milestone by milestone, without re-opening the user's decisions. Use whenever the user says "build this", "/build-this", "build this plan", attaches or points to a plan-*.md file or a tickets folder, or when /plan-this hands off after planning. If there is no plan at all and the goal is big, offer /plan-this in one line first.
---

# Build this

Take an agreed plan and turn it into the finished thing. The user already made the decisions, so this skill **trusts the plan**: it builds, verifies and solves what reality throws up, and asks only what nothing else can answer.

## Where the plan comes from

Use the first that exists:

1. **The plan agreed earlier in this conversation** (the usual case after /plan-this): goal, decisions, milestones and checks from its confirmed summary.
2. **A plan file**: the skill's argument, an attachment, or `plans/plan-*.md` / `plan-*.md` in the project. Read all of it.
3. **Tickets or issues**: a /to-tickets folder (`plans/<feature>/tickets/`), a GitHub issue list, or issues the user names. Each ticket is a milestone and its acceptance criteria are its done-when check. Read [tickets.md](tickets.md) first.
4. **A plan the user wrote** in a message or document.

No plan: a small, clear request is a one-milestone plan, so build it. A big or ambiguous one: offer /plan-this in one line (*"Lots of open choices. Plan it first with /plan-this, or build with sensible defaults?"*) and follow the answer.

---

## 1. Read the plan

Read it once and set up the task list: one item per milestone, plus a final "check everything and report". Note each milestone's **done when** check and **Skills** line. A milestone without a check gets the obvious one (the test that should pass, the page that should load), written by you.

**Resume, don't redo.** Ticked milestones and a `## Build log` (for tickets, resolved or closed ones) mean an earlier run got that far: start at the first unfinished milestone.

In a git repository, record the base commit now (`git rev-parse HEAD`) for step 5. Before an orchestrated build, save a plan that exists only in this conversation to `plans/plan-<short-topic>.md` (plan-this's Saving format), so progress has a file to live in.

If you'd have chosen differently, build what the plan says.

---

## 2. Choose how to build

Ask both questions in one call of the question tool (AskUserQuestion in Claude Code; numbered plain-text questions elsewhere), however small the plan: how to build is the user's call. Skip them only for an answer the user already gave, or under solve-this's autopilot (children at 3 or more milestones or tickets, straight through). For goals that aren't really "built" (a training plan, a job search), skip them and start the first milestone together.

**Children?** *"Should each milestone be built by its own fresh child (a T3 child when available, else a sub-agent), with me only coordinating?"* Recommend yes for 3 or more milestones or tickets, no below that.
- **Children:** Pro: the main context stays small and each milestone gets a matched model. Con: slower and costlier on small milestones, and the work is less visible.
- **Build here:** Pro: faster on small plans, every step visible. Con: context fills on long builds.

When you recommend children, show a table (milestone, child model, effort, few-word reason) in the same message. Pick the cheapest setup that reliably handles that milestone: Haiku for mechanical, fully specified work; Sonnet at medium effort for typical work; Opus at high effort for subtle correctness (auth, payments, migrations, concurrency); one step up for straight-through builds. Use family names, not versions. If the user picks the other answer, apply the same rule yourself and state your picks in one line.

**Straight through?** *"Should I build it all straight through, without stopping?"* Put the option that fits first, labelled "(Recommended)":
- **Straight through:** recommended when steps are reversible and checks run automatically. Pro: the user walks away and returns to a finished build. Con: a misunderstanding surfaces only at the end, and mid-build decisions are made for them.
- **Check in after each milestone:** recommended for risky or hard-to-undo steps, or when the user wants to steer. Pro: a wrong turn is caught early. Con: the user must stay and answer.

---

## 3. Straight through only: collect up front

A straight-through build must not stall waiting for something only the user has. List what **only the user can provide** across all milestones (start from the plan's **Needs from you** and check it against the milestones; plans miss things), in two groups:

- **Needed now:** an early or central milestone can't be built without it and no stub works.
- **Can wait:** a marked placeholder (sample content, mock, empty config value, `TODO(user)`) works until the end; so does anything only needed to deploy, publish or go live.

Ask for **all "needed now" items at once**: the question tool for items with options (up to 4 per call), plain text for free-form ones. Mention the "can wait" list in the same message, without asking for it.

**Secrets:** never ask for keys or passwords in chat. Say where each goes (a named `.env` variable, the host's secret settings) and reference it by name; until it exists, use a placeholder and add it to the end list.

---

## 4. Build

### Solving on the go

Plans meet reality: a package is renamed, an API differs from its docs, a step needs something the plan missed. Pick the **closest fix that keeps the plan's intent**, log it as a deviation with a one-line reason, and keep going. Small decisions the plan didn't cover (layout, naming, libraries, label wording) are yours: take the option you'd have recommended and log the ones that matter.

Raise the plan itself only when it **contradicts itself** so it can't be built, rests on a **false** fact that blocks the goal (the API it names was shut down), or needs something **hard to undo** the user didn't intend, and only if every nearby fix would change the goal or a decision they cared about.

### Code you write

Follow **KISS**, and **SOLID** for object-oriented code, even if the plan is silent: the simplest code that meets the milestone's check, no speculative abstractions. KISS wins a conflict; apply SOLID where it removes real coupling or duplication. Skim each code milestone for needless complexity. If the plan's design would hurt the build under these principles, build the closest compliant version and log a deviation.

### Every milestone

- Mark it in progress and load its skills first (in children mode the child loads them): those on its **Skills** line, at most 3, skipping any already loaded, with the Skill tool in Claude Code or your harness's equivalent; for a skill that exists only on disk, Read its SKILL.md at the plan's path.
  - Before loading, re-check each skill's **Need** against the milestone as it is now; if it no longer holds, skip the skill and log why. For a reason marked "(description only)", read the body as you load it and drop the skill, noting it, if the body doesn't deliver the **Provides** part.
  - A skill that can't be loaded: skip it and note it in the report. "None fit" means load nothing.
  - No Skills line, or "not checked": run **use-available-skills** once at the start for all milestones in record-only mode and load each milestone's matches as it begins. If that skill can't be found (also look in ~/.claude/skills, .claude/skills and plugin folders), carry on and say so in the report.
  - Never ask the user about skills, and a loaded skill never questions the user: take its recommended option, log it, keep going. The plan wins over a skill's advice.
- Build it, then **run its done-when check**. A failing check gets a fix and a re-run; when it stays red after a few honest attempts, climb the [fix ladder](fix-ladder.md) (standard, then strong fixer); an exhausted ladder is a blocker: log it and continue with milestones that don't depend on it. A long or predictable test suite can go to the ladder's light child instead of filling your context.
- Once it passes, tick the milestone in the plan file (a ticket's Finish step is its tick) and append one line to `## Build log` (format in [milestone-brief.md](milestone-brief.md)): check result, deviations, and what each skill actually changed (a step added, a mistake prevented), or "no visible effect". The log lets a compacted or fresh session carry on.

### Children mode

When step 2 chose children, you are the **orchestrator**: you hold the plan, decisions and short reports, and a fresh child builds each milestone, so build detail never enters your context. Launch a child for every milestone, however small: the user chose a rule they can predict. For tickets, [tickets.md](tickets.md) says who claims and finishes.

Waiting on CI, running checks and repairing red follow [fix-ladder.md](fix-ladder.md): waits cost no tokens, a light child runs and triages, fixers climb the ladder.

**Child kind.** With T3's `delegate_task` available, children are **T3 children**: load **t3-orchestration** and follow it. They run one after another in the shared checkout (`isolation: shared`, role implementation), on your own provider unless the user named another, each committing to the current branch. They load skills and run review-this themselves. Otherwise children are **sub-agents** (the Agent tool in Claude Code), which often can't see skills.

For each milestone, in order:

1. Pick the model and effort from the step 2 table (adjust if the milestone turned out harder or easier, and log it).
2. Re-check each skill's **Need**. A T3 child gets skill names; a sub-agent gets each `SKILL.md` path (plugin skills sit under `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/skills/<name>/`, newest version), or key lines pasted when no file exists.
3. In a git repository, note `git rev-parse HEAD`. Fill the brief in [milestone-brief.md](milestone-brief.md) (T3 child or sub-agent variant) and start the child, following t3-orchestration's waiting rules; a sub-agent runs in the foreground with that model and effort.
4. **Review before commit.** A T3 child runs **review-this** on its milestone diff (base from step 3, the milestone as intent) and commits locally only on APPROVE; it never pushes. For a sub-agent, you run review-this on its diff, then commit. Without a git repository, skip the review and commit. On a stalemate, budget end or block, nothing is committed: the milestone is **Held**, its unfinished paths go in the Build log, and no further child launches in this checkout until the user resolves it.
5. Read the report, then **re-run the done-when check** through the light child of [fix-ladder.md](fix-ladder.md), and confirm the commit exists (`git log <base>..HEAD`): the report is a claim, the check is the evidence, and its output stays out of your context. A failed check climbs the fix ladder (standard, then strong fixer, between children); an exhausted ladder is a blocker.
6. Tick the milestone and write its Build log line. Items the report lists under needs from the user or held for go-ahead follow the two modes below.

With no child tool, build each milestone yourself with the same progress record.

### Straight through

Don't ask between milestones; go until every milestone is done or blocked.

- Something only the user can provide that you missed: use a placeholder and add it to the end list.
- **Still stop for** anything hard to undo or outside the workspace (spending money, deleting data, publishing or deploying to production, sending messages, signing in, connecting new services). Do all the work that doesn't depend on it, then ask once, at the end. This skips the skill's own pauses, not the app's permission prompts or safety rules.

### With check-ins

After each milestone give a short status (built, check result, deviations), then ask with the question tool whether to continue or adjust. When the user must act first (a live test, console or consent steps), give the steps as plain text and end the turn: the question box hides text written just before it. Fold any open choice into that question; small decisions stay yours.

Always offer **"Write a handoff file"** beside continue and adjust. If chosen, write it as [milestone-brief.md](milestone-brief.md#the-handoff-file) describes without asking more, give the full path, then repeat the continue/adjust question.

---

## 5. Finish

**Review the diff once.** With a base commit and the **review-changes** skill available, invoke it with the base as the fixed point and the plan file or ticket folder as the Spec. Fix clear Spec misses (a requirement missing or implemented wrong) and re-run the affected checks; put Standards findings and judgement calls in the report. One pass: don't review again after fixing. If the skill isn't available, skip it and say so.

**Then offer a cross-model review.** If children mode ran review-this on every milestone, skip the offer while those approvals still cover the current files; files changed after a milestone's approval (review-changes fixes, a solve-this repair) get a review-this pass on just those edits (base: the HEAD before them) before they are committed. Otherwise, with a base commit and review-this available, ask once, after review-changes' results: *"Should a model from the other provider grill this build with review-this, round after round until it approves?"* Recommend yes when the other provider's CLI is on PATH (`codex` from Claude, `claude` from Codex; `command -v`), else skip, since review-this then falls back to a same-model sub-agent.
- **Run it:** Pro: a second model catches what this one misses, and fixes land before the report. Con: minutes per round, and the other provider's quota.
- **Skip it:** Pro: the report comes now. Con: only review-changes has checked the build.

Under autopilot, don't ask: run it when the other CLI is on PATH, else skip. Pass review-this the base commit and the plan file or ticket folder as the intent; called by a skill, it asks nothing. If the loop changed files, re-run the plan's success checks before archiving; one that now fails counts as failing.

**Archive the plan file, without asking.** If it lives in the project and every milestone is done with its check passing, move it (never delete) to `plans/archive/` and give the path in the report. If anything is blocked or failing, leave it as the working document. Skip this for plans that existed only in the conversation or came from outside the project.

Give one short, scannable report:

- **What was built**, and where.
- **Each success check** from the plan, with its result.
- **Review:** what review-changes found, what you fixed, judgement calls left for the user (or "skipped" and why).
- **Cross-model review:** rounds, verdict and changes from review-this's report (or "skipped" and why).
- **Skills used**, per milestone, each with its reason line and what it changed (or "no visible effect"), skills skipped with why, or "none"; the plan's "Skills used while planning" line; a note if use-available-skills was not found.
- **Decisions and deviations** made on the user's behalf, each with a one-line reason.
- **Blocked or failing**, what would unblock it, human tickets skipped, claims lost to another worker.
- **What's left for you:** the "can wait" items, each with exactly where it goes, plus hard-to-undo steps waiting for a go-ahead (deploy, publish, send). On the go-ahead, finish them and re-run the affected checks.
