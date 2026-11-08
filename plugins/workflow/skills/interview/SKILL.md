---
name: interview
description: Grill the user about a plan, decision or idea, in rounds over a design tree, until nothing is left assumed. Use when the user wants to stress-test their thinking or says "grill me", and when another skill needs the user's decisions.
---

# Interview

Interview the user relentlessly until every decision is either answered or listed as an accepted default, nothing silently assumed.

## Input from a caller

A calling skill (plan-this, wayfinder, improve-codebase-architecture) may pass:

- the **root**: the goal or idea the tree hangs off. Called directly, the root is what the user wants stress-tested.
- **settled decisions**: fixed. They never come back as questions.
- **its own rules** for particular kinds of question (when to run research first, constraints needing no question): follow them alongside these.
- **autopilot** (set by solve-this, passed down through plan-this): ask nothing. Take each recommended option, record it as an *autopilot default*, use a marked placeholder for anything only the user knows, and keep going.

## The design tree

Map the decisions as a **design tree**: each decision branches into the decisions that hang off it (*"online ordering"* opens *"which payment provider"*; *"no ordering"* closes that branch). The **frontier** is every decision whose prerequisites are settled: the questions you can ask now without guessing at answers you haven't heard.

## Each round

1. **Separate facts from decisions.** Facts (what's in the project, what a tool supports, what something costs, what the rules say, a date) are your job, never the user's: look them up, in a sub-agent where you can, so the lookup runs while you ask the rest. A running lookup is an unsettled prerequisite: only the questions depending on it wait.
   - **Verify before you ask.** Never put a choice to the user that rests on a fact you haven't confirmed. Check it first, or hold that question until the check is done.
   - **Research every round's options.** Before asking a round, run **research-this** yourself (sub-agents often can't see skills) at quick depth on the facts behind that round's options: what each does, costs and supports, and its known problems for the user's setup, passing the options and every constraint. For "what is true about X" questions use its facts mode with an output path in a fresh `mktemp -d`, so nothing lands in the project. Read the result before writing the questions: correct or drop a refuted option and take pros and cons from it. Questions only the user can answer need no run. When answers unlock a new frontier, run it again for that frontier's options. A caller's own research run covers the options it already settled.
   - **Where to look.** Read freely from what is already available: the working folder, connected tools, the web, attached files. Ask before attaching or connecting anything new (a repository, a connector, a sign-in). Change nothing while looking.
   - Facts only the user knows (their fitness, whether they've asked their employer) are asked plainly, without a recommendation or pros and cons: there's nothing to weigh.
2. **Ask the whole frontier in one round** with the question tool (AskUserQuestion in Claude Code), at most 4 questions per call and as many consecutive calls as needed, most foundational first. A question depending on another still open in this round belongs to a later round.
3. **Format every question the same way:**
   - Word it so **"yes" accepts your recommendation** ("Should the site use Stripe for payments?").
   - Put the recommended option **first**, labelled "(Recommended)".
   - Give 2–4 options, plain ones like "No, adjust it" included, each with a **one-line pro and con** in plain language: `Pro: … Con: …`; explain unavoidable jargon in a few words.
   - Every con must be real: "Con: none" means it isn't a decision (bundle it as a default or look it up).
   - The user can always type their own answer: no "Other" option.
   - Without a question tool, ask in plain text: numbered questions, each with your recommendation and a one-line pro and con per option, the whole frontier at once, then wait.
4. **Read the answers carefully.** A typed answer can open new branches, close others, or even change the root. Recompute the frontier from what they actually said.
5. **Show one short progress line** before the next round, e.g. *"Round 2 done: 7 decided, 3 open, about 1 round left."*

Bundle decisions that have a conventional default and no real trade-off into one *"Use these defaults: A, B, C?"* question (Recommended: yes). A "no" turns them back into separate questions next round.

## Done

The interview is done when the frontier is empty: every branch visited, every decision answered or listed as an accepted default.

- **Called by a skill:** hand back every decision with its choice and reason, plus the accepted defaults. The caller confirms and acts.
- **Called directly:** summarise the decisions and ask whether this matches what the user wants. Act on it only once they confirm.
