---
name: "plan-this"
description: Turn any goal into a deep, agreed implementation plan. First deepens the goal the way a top professional in that field would, then interviews the user in rounds over a tree of design decisions until nothing is left assumed, then confirms the plan and hands off to /build-this or saves a Markdown plan. Planning only, it never builds. Use whenever the user says "plan this", "/plan-this", "help me plan", "make a plan for", or asks for an implementation plan for any kind of goal. If the user describes a large, multi-step or high-stakes goal without asking for a plan, do not start the interview; offer this skill in one line instead.
compatibility: Requires the research-this and interview skills. The use-available-skills skill is optional.
---

# Plan this

Turn a goal into a plan that is **deeper, not bigger**, researched before anything is decided, and agreed to by the user decision by decision.

This skill only plans: don't act on the goal (write code, create files, book things). Read-only exploration to find facts is fine, and the only file written is the saved plan.

## 0. Check requirements first

Confirm the **research-this** and **interview** skills are available (they may be listed with a plugin prefix such as `workflow:`). If either is missing, do nothing else: cancel and tell the user which is missing and that it must be installed before /plan-this can run. Planning without research reinvents what already exists, and without the interview nothing gets decided.

## 1. Deepen the goal

A top professional's version of a task is usually *not* more features. It's a sharper target, better starting material, proper methods, and an outside way to check the result. That's what this step finds.

**Research before you deepen.** If the goal involves third-party software, a service, or a field with current practice, run **research-this** once, at quick depth (standard only when the goal is costly or hard to undo: money, a migration, a large build), on the goal's core question ("what already does <the goal>?") with every constraint the user gave and the decision it feeds. Name the facts the plan needs rather than asking for everything: when the goal installs third-party software, its installer prompts and defaults that affect privacy, exposure or performance, and known problems with the user's exact setup. A narrow brief keeps the run short and on topic. Skip this only for goals that need no outside facts. Fold its verdict and facts into the deepened goal and the interview, so none of it surfaces first during the build. Treat its verdict as a recommendation, not a decision: if the user hasn't chosen the tool or approach themselves, it stays an open question for round 1, with the verdict as the recommended option. Run it yourself rather than in a sub-agent: sub-agents often can't see skills.

Then work out four things:

1. **What a top professional would do here that the user didn't ask for.** The step an amateur skips: talking to real users first, measuring a baseline, checking legal requirements, designing the data model before the UI.
2. **The rawest material they'd start from**, instead of what has already been digested. Raw data instead of a summary, the source code instead of a tutorial, actual customers instead of a persona template, the official regulation instead of a blog post about it.
3. **The specific methods and tools they'd use**, by name. Not "test it" but "Playwright end-to-end tests"; not "train more" but "an 80/20 easy/hard split with a long run each week".
4. **What, other than the user or Claude, would show the result is right.** Something outside the conversation: an automated test, a measurement, a real-world outcome, a third-party review, a standard it can be checked against.

Rewrite the goal as a short paragraph that asks for exactly that, keeping every restriction the user set. Deepening never overrides a stated constraint. If a constraint blocks the professional approach, that becomes a trade-off question in the interview rather than something you quietly decide.

**Keep it short: about 200 words in total.** One line per point, then the rewritten goal. The user has to read and approve this before any question, so a wall of text here slows everything down. Offer more detail if they want it; don't front-load it.

**Commit or mark as open.** Everything the rewritten goal states is settled once the user approves it, so it must not come back as a question in round 1. If something is genuinely undecided (which race, which scope), don't half-pick it ("most likely X"); mark it plainly as open, e.g. *"(race: open, first question)"*, and ask it in round 1.

**Show it before you ask.** Text written between tool calls is summarised in the interface, so a question card can appear over a plan the user never read. Send the four points and the rewritten goal as visible reply text (with `SendUserMessage` in Claude Code, when available), then ask *"Shall we plan for this deeper version?"* (Recommended: yes) with the question tool, putting the rewritten goal paragraph inside the question text so the user approves something visible right there. If the only way to show the plan is plain text, end the turn after it and ask in plain text. If they adjust, revise and repeat.

## 2. Interview in rounds

### Skills that fit

Before the first round, run the **use-available-skills** skill on the approved goal for the planning phase. It loads only the skills that pass its written reason test (the need in this goal, what the skill provides, what goes wrong without it), and "none" is a normal result. Use whatever it loads while you map the tree and write the options, so recommendations are sharper (a design-review skill for a backend plan, say). A skill's advice shapes your recommendations only; the user still decides. The skill is optional: if it can't be found (look in ~/.claude/skills, .claude/skills and plugin skill folders too, since the listing can drop entries), skip this and write "not checked" as the Skills line of every milestone. Once the milestones are known (just before step 3, and again if they change at the confirmation), run it for the build phase in record-only mode, passing the milestone list, so it returns, per milestone, the skills that pass its reason test (usually fewer than 3) with their reason lines, without loading them, because /build-this loads them when each milestone starts. Copy the reason lines into the plan as they are, including any "(description only)" mark. Never ask the user which skills to use, and don't spend an interview question on them. Sub-agents often can't see skills, so paste any guidance a sub-agent needs into its brief.

### Design pass

When the goal has users, a UI, a bot, or a backend or API, run the design skills before the first round, if they are available (outside use-available-skills' ceiling; one it already loaded counts as run): **product-context** in Draft mode when the repo has no `PRODUCT.md` or the goal changes who the product is for, then **design-review** on the approved goal. Both write nothing and return the same shape. Their **Open questions** go into the interview as frontier decisions (see the rules below), and their **Decisions for the plan** shape your recommended options. When the milestones are known, put design-review on the Skills line of each milestone that builds what it reviewed, with its matching **Checks for Done when** in that milestone's Done when, and when product-context drafted, make the first milestone "Apply PRODUCT.md from Decisions #<n>" (Skills: product-context). Skip this for goals with no users and no system boundary (a host config change, a one-off script).

### Run the interview

Invoke the **interview** skill (in Claude Code, call the Skill tool with `interview`). It maps the plan as a design tree and asks the user in rounds until the frontier is empty. Pass it:

- **Root:** the approved deepened goal. Everything the goal states is settled.
- **Settled decisions:** any the user already made, including those from a wayfinder map (see Input from a map).
- **Autopilot**, when solve-this is running this skill.
- **These plan-specific rules:**
  - **Choosing among existing options.** When a decision means picking an existing tool, product, provider or approach (which payment provider, which library), offer the options and recommendation from the first research run when it already covers them; only if it doesn't, run research-this at quick depth on that one choice before asking. Plain facts (a price, a date, what a tool supports) stay ordinary lookups.
  - **Design questions.** Each Open question from the design pass is a node in the tree: put it on the frontier once its prerequisites are settled, with its recommended option and pros and cons as the design skill wrote them.
  - **Plan code simply.** If the plan involves code, plan it to follow **KISS**, and **SOLID** for object-oriented code; KISS wins when they conflict. These are standing constraints, so spend no question on them; record them once under **Constraints** in the plan.
  - **Needs from you.** Keep a running list of what only the user can supply (accounts, keys, real content, sign-offs, physical-world actions) for the plan's **Needs from you** section, tagged *needed early* or *can wait*.

Use the decisions it hands back for step 3.

### Input from a map

When the goal comes from a wayfinder map (`plans/<effort>/map.md` or its issue), the map's settled decisions are fixed: deepen and interview only the gaps the map leaves open, and cite the map in the plan's Goal section.

## 3. Confirm shared understanding

Summarise in plain language: the deepened goal, every decision with its choice, the milestones with their "done when" checks and skills (each with its one-line reason), how success will be checked overall, and the main risks. Keep it scannable. Then ask *"Does this match what you want?"* as the only question in that call; never bundle step 4's question with it. Any change or addition in the answer, even a small one, sends you back to step 2 for the affected branches (research if needed, interview, record the decision), then repeat this step with the revised summary. Go to step 4 only after a plain yes.

## 4. Next step

Once step 3 got a plain yes, ask with the question tool what to do next, recommending by situation: **Build it now** (recommended when you're working inside a project or workspace where the work can actually be done), **Save a Markdown plan** (recommended when the work happens elsewhere or later), or **Save the plan, then build**.

Milestones are the unit of work by default. Only when the work spans several sessions or parallel agents, add one line after the question: the user can save the plan and type `/to-tickets` on it to split it into tickets with blockers, and build-this then works those tickets in order.

If they choose to build (with or without saving first), invoke the **build-this** skill (the Skill tool in Claude Code) and let it take over; pass the saved plan's path as the argument if you saved one, otherwise it picks the plan up from the conversation. Don't build inside this skill, and don't ask build-this's questions (how to build, which model) yourself. If build-this isn't available, say so in one line, save the plan file, and tell the user to attach it in a session that has build-this.

### Saving

Write `plan-<short-topic>.md` (e.g. `plan-bakery-website.md`) and make it self-contained so a fresh Claude with no other context can act on it; save it in the project's `plans/` folder (create it if missing), never the project root, so plans don't clutter it and /build-this has a place to archive them when done; if there is no project, send it as a file. Start with a title and the line *"Created <date> with /plan-this. Attach this file to a Claude chat and run /build-this (or say "build this plan") to continue."* Then these sections, in order:

- **Goal:** the original request in the user's words, the approved deepened goal, and **Constraints** (everything the user restricted or required; for plans that involve code also "Code follows KISS, and SOLID for object-oriented code"), plus a line **Skills used while planning:** the skills loaded in step 2, each with its reason line, or "none" (with any near-miss notes the helper returned), or "not checked (helper not found)".
- **How we'll know it worked:** the outside checks (test, measurement, outcome, review).
- **Decisions:** a table with #, Decision, Choice and Why (reason or trade-off accepted), followed by any accepted defaults.
- **Needs from you:** *needed early* items (with the milestone that needs each) and *can wait until the end* items (with the placeholder used until then).
- **Steps:** milestones, each with checkbox steps, a **Done when** check and a **Skills:** line giving each build-phase skill for that milestone (exact name, plus the path for one that exists only on disk) followed by its reason line (Need / Provides / Without it), or "none fit", or "not checked" when the helper was unavailable.
- **Risks and assumptions:** each risk with its mitigation, plus any assumption still to confirm in the real world.
