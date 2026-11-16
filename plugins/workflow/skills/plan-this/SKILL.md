---
name: "plan-this"
description: Turn any goal into a deep, agreed implementation plan. First deepens the goal the way a top professional in that field would, then interviews the user in rounds over a tree of design decisions until nothing is left assumed, then confirms the plan and hands off to /build-this or saves a Markdown plan. Planning only, it never builds. Use whenever the user says "plan this", "/plan-this", "help me plan", "make a plan for", asks for an implementation plan for any kind of goal, or names draft issues to plan ("/plan-this issues 12 14"). If the user describes a large, multi-step or high-stakes goal without asking for a plan, do not start the interview; offer this skill in one line instead.
---

# Plan this

Turn a goal into a plan that is **deeper, not bigger**: researched before anything is decided, agreed by the user decision by decision, and complete enough that a builder with none of this conversation can own it.

This skill only plans. Exploring read-only is yours to do freely; the only things written are the saved plan, temp files for research and review, and the tracker writes under **Draft issues**. It needs **research-this** and **interview** (possibly prefixed, such as `workflow:`): when either is missing, say which and stop.

The plan is agreed when four things have happened, in this order. How you get through each is your call.

**Unattended** (the caller says there is no user to ask): every question and confirmation below is answered with its recommended option and recorded as an *unattended default*, the review runs without asking, and the plan is saved and handed to whoever called. A goal with two readings that lead to completely different work is planned on the likelier one, with the other named first among the plan's assumptions.

## 1. The goal is deepened, and the user accepted the deeper version

A top professional's version of a task is a sharper target, better starting material, proper methods and an outside check, not more features. Work out:

1. what they would do that the user didn't ask for (the step an amateur skips);
2. the rawest material they would start from (the regulation, not the blog post about it);
3. the methods and tools by name (not "test it" but "Playwright end-to-end tests");
4. what, other than the user or you, would show the result is right (a test, a measurement, a real-world outcome, a standard).

When the goal touches third-party software, a service or a field with current practice, run **research-this** first on its core question, naming the facts the plan needs. Its verdict is a recommendation: a tool or approach the user hasn't chosen stays an open question with the verdict as the recommended option.

Rewrite the goal as one short paragraph asking for exactly that, keeping every restriction the user set; a restriction that blocks the professional approach becomes a trade-off question, never a quiet override. State what is settled and mark what is undecided as open. About 300 words in all.

Show the four points and the rewritten goal as visible reply text, then ask whether to plan for this deeper version, with the rewritten goal inside the question (a question card can cover text the user never read). Revise until they accept.

## 2. Every decision is the user's, or an accepted default

Run **interview** with the accepted goal as its root, the decisions already settled (the user's, a wayfinder map's), and these plan rules:

- Options among existing things (a provider, a library) come with researched facts; plain facts are your lookups, never questions.
- Code is planned to follow KISS, and SOLID for object-oriented code: a standing constraint, recorded once, no question spent.
- Keep a list of what only the user can supply (accounts, keys, real content, sign-offs, physical actions), each marked *needed early* or *can wait*.
- An unattended caller: pass that on, so interview asks nothing.

Around it:

- **Skills.** Run **use-available-skills** for the planning phase before the interview, and once milestones are known in record-only mode for the build phase, copying its reason lines into the plan unchanged. Its advice shapes your recommendations; the user is never asked which skills to use. Missing: write "not checked" on every Skills line.
- **Design.** For a goal with users, a UI, a bot, a backend or an API, run the design skills when available before the first round: **product-context** in Draft mode when the repo has no `PRODUCT.md` or the goal changes who the product is for, then **design-review** on the accepted goal. They write nothing. Their Open questions become interview decisions with their recommended options; their Decisions for the plan shape yours; design-review's Checks for Done when go into the milestones that build what it reviewed, and a drafted PRODUCT.md becomes the first milestone ("Apply PRODUCT.md from Decisions #<n>", Skills: product-context).
- **A map.** A goal from a wayfinder map keeps the map's decisions: plan only the gaps and cite the map.

**Milestones.** A milestone is a deliverable the user could check or demo on its own. A simple goal is one. Add another only for work that needs its own Done-when check, different skills, or an earlier deliverable to exist. The builder owns the route, so a milestone states its outcome, its Done when and what constrains it; steps are hints for a builder who wants them.

## 3. The plan survived an outside read and the user's confirmation

- **Independent review.** With **review-this** available, ask on its own whether another model should review the plan before the user confirms it (recommend yes; unattended, run it). Write the draft in the Saving format to `plan.md` in a fresh `mktemp -d` and pass it as an explicit plan target with the user's original request as the intent. Verify its report before trusting it. A finding that needs a decision goes back to the interview for that branch only. A fix that adds work the accepted goal doesn't need is scope creep: undo it. At most two reviews; what stays open goes under Risks.
- **Confirmation.** Summarise in plain, scannable language: the deepened goal, every decision with its choice, the milestones with their checks and skills, how success is checked overall, the main risks, and what the review changed. Ask "Does this match what you want?" as the only question in its call. Any change, however small, reopens the affected branches and then this summary. Only a plain yes moves on.

## 4. The user chose what happens next

Ask: **Build it now** (inside a project where the work can be done), **Save a Markdown plan** (the work happens elsewhere or later), or **Save the plan, then build**. For work spanning several sessions or parallel agents, add that `/to-tickets` splits a saved plan into tickets. To build, invoke **build-this** with the saved plan's path and let it take over; without it, save the plan and say so.

## Saving

`plans/plan-<short-topic>.md` in the project (never the root; with no project, send it as a file), self-contained for a reader with no other context. Start with a title and the line *"Created <date> with /plan-this. Attach this file to a Claude chat and run /build-this (or say "build this plan") to continue."* Then, in order:

- **Goal:** the request in the user's words, the accepted deepened goal, **Constraints**, **Skills used while planning** (each with its reason line, or "none", or "not checked"), and **Plan review** (review-this's Review line and what was fixed, re-asked or declined, or "not run").
- **How we'll know it worked:** the outside checks.
- **Decisions:** a table of #, Decision, Choice, Why; then accepted defaults.
- **Needs from you:** *needed early* items with the milestone needing each; *can wait* items with the placeholder used meanwhile.
- **Steps:** the milestones, each with its outcome, optional checkbox hints, a **Done when** check that names the command or observation, and a **Skills:** line (exact name, plus the path for a skill that exists only on disk, with its Need / Provides / Without it reason; or "none fit"; or "not checked").
- **Risks and assumptions:** each risk with its mitigation, and assumptions still to confirm in the real world.

## Draft issues

`issues <n…>` makes those issues the goal (GitHub tracker; labels and commands from `docs/agents/issue-tracker.md`, else the names `draft` and `planned`).

- Read each issue with its comments. One without the draft label is not a draft: say so and plan it only if the user insists.
- Drafts sharing a goal get one plan with the lowest number as parent; unrelated groups are planned one after another. Show the grouping above the deepened goal. Where a group's drafts differ in priority or milestone, ask which the parent takes (recommend the highest priority and the parent's own milestone).
- After the plain yes, per group: save the plan file, post it as a comment on the parent (`gh issue comment <parent> --body-file <plan file>`), set the chosen priority label and milestone, swap the draft label for the planned label, then make each other draft a sub-issue of the parent, remove its draft label and close it with the comment `planned in #<parent>`. Then name `/to-tickets <parent>` as the multi-session route.
