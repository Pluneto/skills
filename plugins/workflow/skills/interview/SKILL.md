---
name: interview
description: Grill the user about a plan, decision or idea, in rounds over a design tree, until nothing is left assumed. Use when the user wants to stress-test their thinking or says "grill me", and when another skill needs the user's decisions.
---

# Interview

Interview the user relentlessly until every decision is either answered or listed as an accepted default, nothing silently assumed. Which questions exist and in what order is yours to work out; what follows is what makes the answers trustworthy.

## Input from a caller

A calling skill (plan-this, build-this, wayfinder) may pass:

- the **root**: the goal, idea or open decisions the tree hangs off. Called directly, the root is what the user wants stress-tested.
- **settled decisions**: fixed. They never come back as questions.
- **its own rules** for particular kinds of question: follow them alongside these.
- **unattended**: the caller has no user to ask. Ask nothing: take each recommended option, record it as an *unattended default*, mark with a placeholder anything only the user knows, and keep going. Being called by a skill is not this; unless the caller says unattended, the user is there and you ask.

## The design tree

Map the decisions as a **design tree**: each decision branches into the decisions that hang off it (*"online ordering"* opens *"which payment provider"*; *"no ordering"* closes that branch). The **frontier** is every decision whose prerequisites are settled: what you can ask now without guessing at answers you haven't heard.

## Facts are yours, decisions are theirs

- What is in the project, what a tool supports, what something costs, what the rules say: look it up, never ask. A choice put to the user rests only on facts you confirmed; hold a question until its facts are in, and ask the rest meanwhile.
- When a round's options are existing tools, services or approaches you have not verified, run **research-this** on them (quick depth; facts mode with an output path in a fresh `mktemp -d` for "what is true about X") and take the pros, cons and corrections from it.
- Read freely from what is already available; ask before connecting anything new. Change nothing while looking.
- Facts only the user knows (their fitness, whether they asked their employer) are asked plainly, with no recommendation: there is nothing to weigh.

## Asking

Ask the **whole frontier in one round** with the question tool (at most 4 questions per call, as many calls as needed, most foundational first); a question that depends on one still open waits for the next round. Without a question tool, ask in plain text, numbered, and wait.

Every question:

- is worded so **"yes" accepts your recommendation**, with the recommended option first, labelled "(Recommended)";
- has 2 to 4 options, each with a real one-line `Pro: … Con: …` in plain language. A con of "none" means it isn't a decision: look it up, or fold it into one *"Use these defaults: A, B, C?"* question (a "no" turns them back into separate questions).

Read the answers for what they open, close or change, including the root, and recompute the frontier. Show one progress line between rounds (*"Round 2 done: 7 decided, 3 open, about 1 round left."*).

## Done

The frontier is empty: every branch visited, every decision answered or an accepted default.

- **Called by a skill:** hand back every decision with its choice and reason, plus the accepted defaults.
- **Called directly:** summarise the decisions, ask whether this matches what the user wants, and act only once they confirm.
