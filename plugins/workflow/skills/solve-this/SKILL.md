---
name: "solve-this"
description: Solve a task end to end on autopilot with minimal user input, then prove it is solved. Runs /plan-this and /build-this without asking the user anything, keeps diagnosing and retrying until the result passes its checks, and stops with one report containing evidence. Use when the user says "/solve-this", "solve this", "handle this end to end", "autopilot", or hands over a goal and wants no interview, approvals or check-ins, even if they don't name the skill. Not for goals where the user wants to steer decisions (use /plan-this).
compatibility: Requires the plan-this, interview, build-this and research-this skills. The use-available-skills skill and a sub-agent tool (the Agent tool in Claude Code) are optional (skill discovery; independent verification).
---

# Solve this

Autopilot over /plan-this and /build-this: they supply the method, this skill removes the human gates, adds a retry loop, and demands proof. The user handed over a goal, not a conversation: ask no questions and wait for no approval.

## 0. Check requirements first

Confirm **plan-this**, **interview**, **build-this** and **research-this** are available (possibly with a plugin prefix such as `workflow:`). If any is missing, do nothing else: cancel and tell the user which one must be installed before /solve-this can run. **use-available-skills** is optional: if it can't be found (also look in ~/.claude/skills, .claude/skills and plugin folders), carry on and list that under the step 5 assumptions.

## 1. Plan

Run /plan-this with these changes:
- Run it in **autopilot** and pass autopilot to every skill it invokes (interview, and any a later step calls): answer every question yourself, take the recommended option and record it as an *autopilot default*. Research facts instead of guessing, using the research-this runs plan-this and interview make (one per interview round, at the depth they set, plus reruns when answers unlock new frontiers), adding none of your own; take its verdict as the recommended option and its Gaps as assumptions. Use a marked placeholder for anything only the user knows.
- plan-this's skills step runs as written (it asks nothing); the skills it picks end up in the plan.
- plan-this's Independent review (review-this on the draft plan) runs without asking, fixes what it can, and answers re-opened decisions with the recommended option.
- Skip every approval, confirmation and next-step question: save the plan file and go straight to building.
- Ask one question, up front, only if the goal has two readings leading to completely different work; otherwise state your reading in one line.
- Every milestone needs a **done when** check that runs without a human, and the plan needs at least one check from outside the conversation (test, measurement, validator, standard). These are the proof in step 4.

## 2. Build

Run /build-this on the plan file, choosing **build straight through** yourself and skipping its children and model questions and up-front collection (placeholders; secrets by variable name only). With 3 or more milestones or tickets it builds each in a child (a T3 child when available) and picks their models itself. Run it through its step 4 (Build) only: its step 5 (Finish) runs once, in this skill's step 5, after the proof. Tick milestones off in the plan file as their checks pass; build-this loads each milestone's skills itself.

## 3. Keep going until solved

When a check fails or a step blocks:
1. A failing check or red CI climbs build-this's [fix-ladder.md](../build-this/fix-ladder.md) first (a non-obvious cause: name **diagnosing-bugs** in a T3 fixer's brief); an exhausted ladder counts as rule 3's three approaches, not revisited. Otherwise read the actual error or output before changing anything; re-running unchanged isn't a new attempt.
2. After two failures of one approach, switch to a genuinely different one.
3. Call something blocked only after three different approaches have failed; continue with independent milestones and revisit it once at the end. The exception is a milestone build-this holds because review-this did not approve it: it leaves unapproved edits in the shared checkout, so stop and report it.
4. If the plan itself is wrong, amend the plan file and log it; don't restart.

Stop when every check passes, only user-only or hard-stop items remain (as /build-this defines them), or no untried approach is left.

## 4. Prove it

Claim nothing without evidence.
- Re-run every success check fresh, after the last change.
- If you can start sub-agents, have a fresh one run the checks against the result using only the plan's goal and checks, so it can't grade your work generously. Fix and loop to step 3 on any failure.
- Capture the proof: per check, what was run, the actual output (trimmed), pass or fail. Save it as `proof-<short-topic>.md` next to the plan file, before anything moves the plan, and send it with the deliverables.

## 5. Report and stop

Run /build-this's step 5 (Finish) now: its reviews; when they changed files, re-run every success check and refresh `proof-<short-topic>.md` (a failed check goes back through step 3's repair loop and step 4's proof without repeating the reviews, except that build-this's review-this pass still covers edits made after a milestone's approval before they are committed); then archive the plan (move the proof file with it to `plans/archive/`), then give its one report, plus:
- **Proof:** a verdict of **Solved**, **Partly solved** or **Not solved**, with the check table. A check that couldn't be run, or passed only by assumption, is unproven and listed as such.
- **Assumptions I made for you:** the autopilot defaults, and whether use-available-skills was missing (so no skills were looked up).

Then stop, with no follow-up questions.
