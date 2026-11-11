---
name: "plan-this"
description: Turn any goal into a deep, agreed implementation plan. First deepens the goal the way a top professional in that field would, then interviews the user in rounds over a tree of design decisions until nothing is left assumed, then confirms the plan and hands off to /build-this or saves a Markdown plan. Planning only, it never builds. Use whenever the user says "plan this", "/plan-this", "help me plan", "make a plan for", asks for an implementation plan for any kind of goal, or names draft issues to plan ("/plan-this issues 12 14"). If the user describes a large, multi-step or high-stakes goal without asking for a plan, do not start the interview; offer this skill in one line instead.
argument-hint: "[goal, or issues <n…>]"
compatibility: Requires the research-this and interview skills. The use-available-skills and review-this skills are optional.
---

# Plan this

Turn a goal into a plan that is **deeper, not bigger**, researched before anything is decided, and agreed to by the user decision by decision.

This skill only plans: don't act on the goal (write code, create files, book things). Read-only exploration is fine; the only files written are the saved plan and temp files for the plan review and research facts, and the only tracker writes are those in **Input from draft issues**.

## 0. Check requirements first

Confirm **research-this** and **interview** are available (possibly with a plugin prefix such as `workflow:`). If either is missing, do nothing else: cancel and tell the user which one must be installed before /plan-this can run.

## Input from draft issues

`issues <n…>` (GitHub tracker; labels and commands from `docs/agents/issue-tracker.md`, else the default names `draft` and `planned`) makes those issues the goal:

1. **Read** each issue's body and comments (the doc's **Read an issue**). An issue without the draft label is not a draft: say so and plan it only if the user insists.
2. **Group by goal.** Drafts sharing a goal get one plan, the lowest number as the parent; unrelated groups are planned one after another, each through steps 1 to 4. Show the grouping above step 1's deepened goal. When a group's drafts differ in priority label or milestone, add a question to step 1's question call: which the parent takes (recommend the highest priority and the parent's own milestone).
3. **After the plain yes in step 3**, per group: save the plan file (Saving), post it as a comment on the parent (`gh issue comment <parent> --body-file <plan file>`), set the chosen priority label and milestone on the parent, swap the draft label for the planned label, then make each other draft a sub-issue of the parent and close it with the comment `planned in #<parent>` (the doc's **Sub-issue of a parent** and **Close**). In step 4 the plan is already saved; name `/to-tickets <parent>` as the multi-session route.

## 1. Deepen the goal

A top professional's version of a task is a sharper target, better starting material, proper methods and an outside check, not more features.

**Research before you deepen.** If the goal involves third-party software, a service, or a field with current practice, run **research-this** yourself (sub-agents often can't see skills) once at quick depth (standard only for costly or hard-to-undo goals: money, a migration, a large build) on the goal's core question ("what already does <the goal>?"), with the user's constraints and the decision it feeds. Name the facts the plan needs (for installed software: installer prompts and defaults affecting privacy, exposure or performance, known problems with the user's exact setup); a narrow brief keeps the run short. Skip for goals needing no outside facts. Fold its verdict and facts into the deepened goal and the interview. The verdict is a recommendation: if the user hasn't chosen the tool or approach, it stays an open round 1 question with the verdict as the recommended option.

Then work out four things:

1. **What a top professional would do that the user didn't ask for.** The step an amateur skips: talking to real users, measuring a baseline, checking legal requirements, designing the data model before the UI.
2. **The rawest material they'd start from:** raw data instead of a summary, source code instead of a tutorial, actual customers instead of a persona, the regulation instead of a blog post about it.
3. **The specific methods and tools, by name:** not "test it" but "Playwright end-to-end tests".
4. **What, other than the user or Claude, would show the result is right:** an automated test, a measurement, a real-world outcome, a third-party review, a standard.

Rewrite the goal as a short paragraph that asks for exactly that, keeping every restriction the user set. A constraint that blocks the professional approach becomes a trade-off question in the interview, never a quiet override.

**Keep it to about 300 words in total:** one line per point, then the rewritten goal.

**Commit or mark as open.** Everything the approved goal states is settled and never returns as a round 1 question. Anything genuinely undecided (which race, which scope) is marked plainly, e.g. *"(race: open, first question)"*, not half-picked, and asked in round 1.

**Show it before you ask.** Text between tool calls is summarised in the interface, so a question card can appear over a plan the user never read. Send the four points and the rewritten goal as visible reply text (`SendUserMessage` in Claude Code, when available), then ask *"Shall we plan for this deeper version?"* (Recommended: yes) with the question tool, putting the rewritten goal inside the question text. With plain text only, end the turn and ask in plain text. If they adjust, revise and repeat.

## 2. Interview in rounds

### Skills that fit

Before the first round, run **use-available-skills** on the approved goal for the planning phase; "none" is a normal result. Its advice shapes your recommendations only; the user still decides. The skill is optional: if it can't be found (also look in ~/.claude/skills, .claude/skills and plugin folders), skip this and write "not checked" as every milestone's Skills line. Once the milestones are known (just before step 3, and again if they change at the confirmation), run it for the build phase in record-only mode with the milestone list; it returns per milestone the skills that pass (usually fewer than 3) with reason lines, without loading them, since /build-this loads them per milestone. Copy the reason lines into the plan as they are, including any "(description only)" mark. Never ask the user which skills to use; paste any guidance a sub-agent needs into its brief.

### Design pass

When the goal has users, a UI, a bot, or a backend or API, run the design skills before the first round, if available (outside use-available-skills' ceiling; one it already loaded counts as run): **product-context** in Draft mode when the repo has no `PRODUCT.md` or the goal changes who the product is for, then **design-review** on the approved goal. Both write nothing; their **Open questions** go into the interview as frontier decisions and their **Decisions for the plan** shape your recommended options. Once milestones are known, put design-review on the Skills line of each milestone that builds what it reviewed, with its **Checks for Done when** in that Done when; if product-context drafted, make the first milestone "Apply PRODUCT.md from Decisions #<n>" (Skills: product-context). Skip for goals with no users and no system boundary (a host config change, a one-off script).

### Run the interview

Invoke **interview** (the Skill tool in Claude Code). It maps the plan as a design tree and asks in rounds until the frontier is empty. Pass it:

- **Root:** the approved deepened goal; everything it states is settled.
- **Settled decisions:** any the user already made, including a wayfinder map's.
- **Autopilot**, when solve-this is running this skill.
- **These plan-specific rules:**
  - **Choosing among existing options** (which payment provider, which library): offer the first research run's options and recommendation when they cover it; interview's per-round research covers the rest. Plain facts (a price, a date) stay ordinary lookups.
  - **Design questions.** Each Open question from the design pass is a tree node: put it on the frontier once its prerequisites are settled, with the design skill's recommended option and pros and cons.
  - **Plan code simply.** If the plan involves code, plan it to follow **KISS**, and **SOLID** for object-oriented code; KISS wins a conflict. Standing constraints: spend no question on them, record them once under **Constraints**.
  - **Needs from you.** Keep a running list of what only the user can supply (accounts, keys, real content, sign-offs, physical-world actions) for the plan's **Needs from you** section, tagged *needed early* or *can wait*.

Use the decisions it hands back for step 3.

### Input from a map

When the goal comes from a wayfinder map (`plans/<effort>/map.md` or its issue), its settled decisions are fixed: deepen and interview only the gaps it leaves, and cite the map in the plan's Goal section.

### Milestones

A **milestone** is a deliverable the user could check or demo on its own, holding as many checkbox steps as it takes. Fold steps serving one deliverable into one milestone; a simple goal is exactly one. Add another only when the work needs its own Done when check, a different set of skills, or must wait for an earlier deliverable.

### Independent review

Once the interview is done and the milestones are known, ask on its own with the question tool: *"Should another model review the plan before you confirm it?"* (Recommended: yes. Pro: a reader who wasn't in this conversation catches gaps and false facts. Con: a few minutes, and the other provider's usage.) In autopilot, run it without asking. When **review-this** isn't available (also look in ~/.claude/skills, .claude/skills and plugin folders), skip the review and write "not run (review-this not found)" on the plan's Review line.

If yes, write the draft plan in the Saving format to `plan.md` in a fresh temp folder (`mktemp -d`) and invoke **review-this** with that file as an explicit **plan** target and the user's original request as the intent. It edits the temp plan for fixable findings: take that file as the draft from then on. Verify its report before acting on it, then:

- **Fixed**: the plan already holds the fix.
- **Needs your decision** (a decision is missing, or rests on a false fact): go back to the interview for the affected branches only; settled decisions stay settled.
- **Scope creep**, whatever the finding's tag: a fix adding work the approved goal and its checks don't need (a new feature, option, tool or milestone). Undo it and keep the plan, because only the user widens the approved scope. A gap the goal itself needs is not creep.

Run review-this again only when a re-interview changed the plan, at most twice in all; open items go under Risks. Step 3's summary lists the report's Fixed, Disagreed, Declined and Needs-your-decision lines briefly.

## 3. Confirm shared understanding

Summarise in plain language: the deepened goal, every decision with its choice, the milestones with their done-when checks and skills (each with its one-line reason), how success is checked overall, and the main risks. Keep it scannable. Then ask *"Does this match what you want?"* as the only question in that call. Any change in the answer, even a small one, sends you back to step 2 for the affected branches (research if needed, interview, record the decision), then repeat this step. Go to step 4 only after a plain yes.

## 4. Next step

After a plain yes, ask with the question tool: **Build it now** (recommended inside a project where the work can be done), **Save a Markdown plan** (recommended when the work happens elsewhere or later), or **Save the plan, then build**.

When the work spans several sessions or parallel agents, add one line after the question: the user can save the plan and run `/to-tickets` to split it into tickets with blockers, which build-this then works in order.

To build, invoke **build-this** and let it take over, passing the saved plan's path if you saved one (otherwise it uses the conversation). Don't build here, and don't ask build-this's questions yourself. If build-this isn't available, say so in one line, save the plan file, and tell the user to attach it in a session that has build-this.

### Saving

Write `plan-<short-topic>.md`, self-contained so a fresh Claude with no other context can act on it, in the project's `plans/` folder (create it if missing), never the root, so /build-this can archive it; with no project, send it as a file. Start with a title and the line *"Created <date> with /plan-this. Attach this file to a Claude chat and run /build-this (or say "build this plan") to continue."* Then these sections, in order:

- **Goal:** the original request in the user's words, the approved deepened goal, and **Constraints** (everything the user restricted or required; for code, "Code follows KISS, and SOLID for object-oriented code"), then **Skills used while planning:** the skills loaded in step 2, each with its reason line, or "none" (with the helper's near-miss notes), or "not checked (helper not found)". Then **Plan review:** review-this's **Review** line (reviewer, model, effort, rounds, verdict) with findings fixed, re-asked or declined, or "not run".
- **How we'll know it worked:** the outside checks (test, measurement, outcome, review).
- **Decisions:** a table with #, Decision, Choice, Why (reason or trade-off accepted), then any accepted defaults.
- **Needs from you:** *needed early* items (with the milestone needing each) and *can wait* items (with the placeholder used meanwhile).
- **Steps:** outcome-sized milestones, each with checkbox steps, a **Done when** check and a **Skills:** line giving each build-phase skill (exact name, plus the path for one that exists only on disk) with its reason line (Need / Provides / Without it), or "none fit", or "not checked" when the helper was unavailable.
- **Risks and assumptions:** each risk with its mitigation, plus any assumption still to confirm in the real world.
