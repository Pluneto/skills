---
name: "build-this"
description: Carry out an agreed plan from start to finish, milestone by milestone, without re-opening the user's decisions. Use whenever the user says "build this", "/build-this", "build this plan", attaches or points to a plan-*.md file or a tickets folder, or when /plan-this hands off after planning. If there is no plan at all and the goal is big, offer /plan-this in one line first.
---

# Build this

Take a plan that has already been agreed and turn it into the finished thing.

The planning is done. The user already made the decisions, often through a long interview with /plan-this, so this skill **trusts the plan**. Its job is to build, verify, and solve the problems reality throws up along the way, not to re-open questions the user already answered. Every question you ask here costs the user attention they already spent during planning, so ask only what genuinely can't be answered any other way.

## Where the plan comes from

Use the first of these that exists:

1. **The plan agreed earlier in this conversation** (the usual case when /plan-this hands off): the deepened goal, decisions, milestones and checks from its confirmed summary.
2. **A plan file** passed as the skill's argument, attached, or in the project (`plans/plan-*.md`, or `plan-*.md` in the root). Read all of it.
3. **Tickets from /to-tickets**: a folder (`plans/<feature>/tickets/`) or an issue list, worked by `docs/agents/issue-tracker.md` (its Claim, Release and Parallel work sections), or, when the repo has none, by the defaults in [no-tracker-doc.md](no-tracker-doc.md). Each ticket is a milestone and its acceptance criteria are its done-when check. Work them in blocker order (a ticket starts once every ticket in its `Blocked by` is done).
   - **Human tickets** (the human label, or `Who: human`) are the user's: skip them, keep working every agent ticket they don't block, and list them in the report with what each needs.
   - **Claim** each ticket before its first change, as the tracker doc's Claim says. When the claim is lost, another worker holds it: leave that ticket and the tickets it blocks, and report the winning claim.
   - **Finish** each ticket when its check passes. On GitHub, open the PR with `Fixes #<n>` in its body and wait for green CI. Merging publishes, so land it (the doc's Land command, polling its status command, or the blank field's fallback) only when the user said so, for example "merge if green" with the build mode; then release as in the doc's Release (Done). Without that go-ahead, list the green PRs under "What's left for you" and keep the claims: the open PRs hold the tickets. Locally, set `Status: resolved`.
4. **A plan the user wrote themselves**, in a message or a document.

If there's no plan, look at the size of the request. Small and clear: just build it, treating the request as a one-milestone plan. Big or ambiguous: offer /plan-this in one line (*"This has a lot of open choices. Want to plan it first with /plan-this, or should I just build with sensible defaults?"*) and go with their answer.

---

## 1. Read the plan

Read the plan once, carefully, and set up the task list: one item per milestone, in order, plus a final "check everything and report" item. Note each milestone's **done when** check (and its **Skills** line, if it has one); those checks are how you'll know a milestone is really finished, so if a milestone has none, write the obvious one yourself (the test that should pass, the page that should load, the file that should exist) rather than asking.

**Resume, don't redo.** Ticked milestones and a `## Build log` in the plan file mean an earlier run got that far: trust the log and start at the first unticked milestone.

**Long plans run in orchestrator mode** (3 or more milestones or tickets, whatever their size; see step 4). Save a plan that exists only in this conversation to `plans/plan-<short-topic>.md` first, in plan-this's Saving format, so progress has a file to live in.

If the work happens in a git repository, record the base commit now (`git rev-parse HEAD`) for the review in step 5.

Trust the plan: if you'd have chosen differently, build what it says (see "Solving on the go" for the rare exceptions).

---

## 2. Choose how to build

Ask one question with the question tool (AskUserQuestion in Claude Code; a numbered plain-text question elsewhere), and put the model recommendation in the same message.

### Recommend a model and effort

Say in one or two lines which Claude model and effort level fits this build, covering both build modes, with a short reason. Recommend the cheapest setup that reliably handles the hardest milestone, not the average one: Haiku for mechanical, fully specified work; Sonnet at medium effort for typical builds; Opus at high effort for subtle-correctness work such as auth, payments, migrations or concurrency. Go one step up for straight-through builds, since no one catches a wrong turn until the end. Use family names (Haiku, Sonnet, Opus), not version numbers.

In orchestrator mode the sub-agents do the building, so apply the same rule per milestone instead: show a short table (milestone, sub-agent model, effort, a few-word reason) in place of the one-line recommendation, and the sub-agents run at those settings.

### The question

*"Should I build it all straight through, without stopping?"* Put the option that fits the plan first, labelled "(Recommended)", each with a one-line pro and con:

- **Build straight through:** recommended when the steps are reversible and the milestone checks can be run automatically. Pro: the user can walk away and come back to a finished build. Con: a misunderstanding isn't caught until the end, and decisions that come up mid-build are made for them.
- **Check in after each milestone:** recommended when the plan has risky or hard-to-undo steps, or the user wants to steer as it takes shape. Pro: catch a wrong turn early. Con: the user has to stay around and answer between milestones.
- **Let me switch model first:** include this when your recommendation differs from the current setup, outside orchestrator mode. Pro: the build runs on the right model. Con: one extra message. If chosen, stop here and tell them to send "go" with their build mode once they've switched, since the model can't change in the middle of a turn.

For goals that aren't really "built" (a training plan, a job search), skip the model recommendation and this question: start the first milestone together, checking in naturally.

---

## 3. Straight-through only: collect up front

A straight-through build only works if it doesn't stall halfway waiting for something only the user has. So before starting, go through every milestone and list what **only the user can provide**: things you can't look up, generate or decide yourself.

If the plan has a **"Needs from you"** section, start from it, but check it against the milestones; plans miss things.

Sort the list into two groups:

- **Needed now:** an early or central milestone can't be built properly without it, and a placeholder wouldn't work (no sensible stub exists, or swapping it in later would mean redoing work).
- **Can wait:** the build can go ahead with a clearly marked placeholder (sample content, a mocked service, an empty config value, a `TODO(user)` marker) and the real thing slots in at the end. Anything only needed for the final step (deploying, publishing, going live) belongs here too.

Ask for **everything in "needed now" in one go**, as few messages as possible: the question tool for anything with options (up to 4 questions per call, consecutive calls if needed), plain text for free-form items. Briefly mention the "can wait" list in the same message so the user isn't surprised later, but don't ask for those items yet.

**Secrets:** don't ask the user to paste keys or passwords into the chat. Tell them exactly where to put each one (for example a named variable in the project's `.env` file, or the hosting provider's secret settings) and reference it by name in the code. If it isn't there yet, build against the placeholder and add it to the end list.

---

## 4. Build

### Solving on the go

Plans meet reality: a package is renamed, an API behaves differently than documented, a step turns out to need something the plan didn't mention. Handle these yourself:

- Pick the **closest fix that keeps the plan's intent**: the equivalent library, the documented workaround, the small extra step.
- **Log it** as a deviation with a one-line reason, for the final report.
- **Keep going.** Don't stop to re-plan or ask permission for something the user would obviously want you to sort out.

Small decisions the plan didn't cover (file layout, naming, helper libraries, wording of a label) are yours to make: take the option you'd have recommended, keep it consistent with the plan and the existing project, log the ones that matter, and move on.

Raise something about the plan itself only when it **contradicts itself** in a way that can't be built, rests on a fact that is **false** in a way that blocks the goal (the API it names was shut down), or would mean doing something **hard to undo** that the user clearly didn't intend. Even then, look for the nearest fix first, and ask only if every fix would change the goal or a decision they clearly cared about.

### Code you write

Whenever the build involves writing code, follow **KISS** and, for object-oriented code, **SOLID**, even if the plan doesn't mention them: write the simplest code that meets the milestone's check, with no speculative abstractions. When they conflict, KISS wins; apply SOLID where it removes real coupling or duplication. Skim each code milestone for needless complexity before calling it done. If the plan's design would hurt the build under these principles, build the closest compliant version and log it as a deviation.

### Every milestone

- Mark it in progress in the task list and load its skills first, from the main agent (in orchestrator mode the sub-agent reads them instead): those on its **Skills** line (at most 3, skipping any already loaded), with the Skill tool in Claude Code or your harness's way of loading a skill (for a skill that exists only on disk, Read its SKILL.md at the path the plan gives). If a named skill can't be loaded (the plan may come from another chat or machine), skip it, note it in the report and never ask. A line saying "none fit" means load nothing. Before loading a skill, re-check its **Need** against the milestone as it is now, since the work may have shifted or turned out simpler: if the Need no longer holds, skip the skill and log why in one line. If its reason is marked "(description only)", read its body as you load it and drop the skill, noting it, when the body doesn't deliver the **Provides** part. When the plan has no Skills line for the milestone, or says "not checked" (a hand-written plan, an older plan, or one made without the helper), run the **use-available-skills** skill once at the start for all milestones in record-only mode, and load each milestone's matches as it begins. That skill is optional: if it can't be found (look in ~/.claude/skills, .claude/skills and plugin skill folders too, since the listing can drop entries), carry on without it and say so in the report. Never ask the user about skills, and a loaded skill never questions the user either: take its recommended option, log it and keep going. The plan still wins over a skill's advice: build what the plan says, and use a skill for how to do it well.
- Build it, then **run its done-when check**.
- If the check fails, fix and re-run it. Don't move on with a failing check. If it still fails after a few honest attempts, note it as a blocker and continue with milestones that don't depend on it.
- Once the check passes, tick the milestone in the plan file (a ticket's Finish step is its tick) and append one line to its `## Build log` (format in [milestone-brief.md](milestone-brief.md)): the check result, deviations, and what each skill you used actually changed (a step it added, a mistake it prevented, a rule it enforced), or "no visible effect". Be honest: a skill that changed nothing is useful to know about. The log is what lets a compacted or fresh session carry on.

### Orchestrator mode

For plans with 3 or more milestones or tickets, you are the **orchestrator**: you hold the plan, the decisions and short reports, and a fresh sub-agent builds each milestone, so build detail never enters your context. The count decides, not your sense of size: launch the sub-agent even for a one-line milestone, because the user chose a rule they can predict over a judgement call, and small milestones still add up. (The model can't run `/clear` or `/compact` itself; this is how a long build keeps its context small.) For each milestone, in order (independent ones may run in parallel when they touch different files):

1. Pick the sub-agent's model and effort from the step 2 table (adjust if the milestone turned out harder or easier, and log it).
2. Resolve the paths of its skills' `SKILL.md` files (plugin skills sit under `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/skills/<name>/`; take the newest version) after re-checking each **Need** as in Every milestone. Don't load them yourself: the sub-agent reads them. A skill with no file on disk gets its few key lines pasted into the brief instead.
3. Fill the brief in [milestone-brief.md](milestone-brief.md) and run the sub-agent in the foreground, passing that model and effort to the sub-agent tool.
4. Read its report, then **re-run the done-when check yourself**; the report is a claim, the check is the evidence. A failure gets one fresh sub-agent with the failure output in its brief, one model step up; then it's a blocker.
5. Tick the milestone and write its Build log line. Items the report lists under needs from the user or held for go-ahead follow the Straight through or With check-ins rules below.

Without a sub-agent tool, build each milestone yourself with the same progress record; the harness's own compaction then carries the load and the Build log keeps it lossless.

### Sub-agents

Outside orchestrator mode, use sub-agents (the Agent tool in Claude Code) for research that would otherwise interrupt or clutter the build (docs lookups, API behaviour, an unfamiliar codebase) and for independent milestones or tasks that can run in parallel. Keep dependent milestones sequential, and don't run parallel agents that edit the same files. Give each sub-agent a self-contained brief: its goal, the files or area it owns, and its done-when check, plus, as plain text, the few lines of guidance it needs from the skills you loaded (sub-agents often can't see skills, and naming one in a brief can trigger it inside the sub-agent). Where a sub-agent accepts a model and effort setting, run it at the recommended setup. Verify each result against the milestone's done-when check before marking it done.

### Straight through

The user handed over the whole build, so don't ask between milestones. Keep going until every milestone is done or blocked.

- **New things only the user can provide** that you missed up front: use a placeholder and add them to the end list, rather than stopping.
- **Still stop for** anything hard to undo or that reaches outside the workspace: spending money, deleting data, publishing or deploying to production, sending messages, signing in or connecting new services. Do all the work that doesn't depend on it first, then ask once, at the end. Building straight through skips this skill's own pauses; it doesn't override the app's permission prompts or safety rules.

### With check-ins

After each milestone, give a short status (what was built, its check result, any deviations), then ask with the question tool whether to continue or adjust. When the user must act first (a live test, console or consent steps), give those steps as plain text and end the turn instead of asking with the question tool: the question box hides text written just before it. Fold any genuinely open choice that came up into that same check-in question rather than interrupting mid-milestone. Small decisions are still yours; bring only the ones that meaningfully change what the user gets.

Always include **"Write a handoff file"** as one of the check-in options (alongside continue and adjust), because a check-in is the natural moment to stop and resume in a fresh session with a clean context. If the user picks it, write the handoff yourself as [milestone-brief.md](milestone-brief.md#the-handoff-file) describes, without asking anything further, tell them its full path, then repeat the continue/adjust question so the build carries on if they want.

---

## 5. Finish

**Review the diff once.** If you recorded a base commit and the **review-changes** skill is available, invoke it (in Claude Code, call the Skill tool with `review-changes`), passing the base commit as the fixed point and the plan file or ticket folder as the Spec. Fix the clear Spec misses (a requirement missing or implemented wrong) and re-run the affected checks. Put Standards findings and other judgement calls in the report without acting on them. One pass: don't review again after fixing. If review-changes isn't available, skip this and say so in the report.

**Archive the plan file first, without asking.** If the plan lives as a file in the project and every milestone is done with its check passing, move it to `plans/archive/` (create the folder if missing) so finished plans stay out of the project root and `plans/`. Move, never delete, so it stays recoverable. If anything is blocked or failing, leave the plan where it is, since it's still the working document. Skip this for plans that only existed in the conversation or were attached from outside the project. Mention the new path in the report.

Give one report, short and scannable:

- **What was built**, and where to find it.
- **Each success check** from the plan, with its result.
- **Review:** what review-changes found, what you fixed, and the judgement calls left for the user (or "skipped" and why).
- **Skills used**, per milestone, each with its reason line (Need / Provides / Without it) and what it changed (or "no visible effect"), any skill skipped at build time with why, or "none"; plus the plan's "Skills used while planning" line if it has one, and a note if the helper was not found.
- **Decisions and deviations** you made on the user's behalf, each with a one-line reason.
- **Blocked or failing**, if anything, and what would unblock it, including human tickets skipped and claims lost to another worker.
- **What's left for you:** the "can wait" items and anything collected along the way, each with exactly where it goes, plus the hard-to-undo steps waiting for their go-ahead (deploy, publish, send). If they give the go-ahead or the items, finish those steps and re-run the affected checks.
