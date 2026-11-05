---
name: "solve-this"
description: Solve a task end to end on autopilot with minimal user input, then prove it is solved. Runs /plan-this and /build-this without asking the user anything, keeps diagnosing and retrying until the result passes its checks, and stops with one report containing evidence. Use when the user says "/solve-this", "solve this", "handle this end to end", "autopilot", or hands over a goal and wants no interview, approvals or check-ins, even if they don't name the skill. Not for goals where the user wants to steer decisions (use /plan-this).
compatibility: Requires the plan-this, interview, build-this and research-this skills. The use-available-skills skill and a sub-agent tool (the Agent tool in Claude Code) are optional (skill discovery; independent verification).
---

# Solve this

Autopilot over /plan-this and /build-this: they supply the method, this skill removes the human gates, adds a retry loop, and demands proof. The user handed over a goal, not a conversation, so don't ask questions or wait for approval.

## 0. Check requirements first

Confirm **plan-this**, **interview**, **build-this** and **research-this** are available (they may be listed with a plugin prefix such as `workflow:`). If any is missing, do nothing else: cancel and tell the user which skill is missing and that it must be installed before /solve-this can run. (plan-this calls research-this and interview itself, so a missing one would otherwise only surface mid-run.) The **use-available-skills** skill is optional: if it can't be found (look in ~/.claude/skills, .claude/skills and plugin skill folders too, since the listing can drop entries), carry on and list that under the assumptions in step 5.

## 1. Plan

Run /plan-this with these changes:
- Run it in **autopilot**, and pass autopilot on to every skill it invokes (interview, and any skill a later step calls): answer every question yourself, take the recommended option and record it as an *autopilot default*. Research facts instead of guessing, using plan-this's research-this calls at the depth plan-this sets, without adding runs of your own (take its verdict as the recommended option, and note its Gaps as assumptions); use a marked placeholder for anything only the user knows.
- Let plan-this's skills step run as written: it asks nothing, so it needs no change. The skills it picks end up in the plan.
- Let plan-this's Independent review run: in autopilot it runs without asking, fixes what it can, and answers re-opened decisions with the recommended option.
- Skip all approval, confirmation and next-step questions. Save the plan file and go straight to building.
- Ask a question only once, up front, and only if the goal has two readings that lead to completely different work. Otherwise state your reading in one line.
- Every milestone needs a **done when** check that runs without a human, and the plan needs at least one check from outside the conversation (test, measurement, validator, standard). Those checks are the proof in step 4.

## 2. Build

Run /build-this on the plan file, choosing **build straight through** yourself and skipping its model and sub-agent questions and up-front collection (use placeholders; secrets by variable name only); with 3 or more milestones or tickets it builds each in a sub-agent and picks their models itself. Run it through its step 4 (Build) only: its step 5 (Finish) runs once, in this skill's step 5, after the proof. Tick milestones off in the plan file as their checks pass. /build-this loads each milestone's skills itself; don't add steps for that.

## 3. Keep going until solved

When a check fails or a step blocks:
1. Read the actual error or output before changing anything. Re-running unchanged isn't a new attempt. For a failing check whose cause isn't obvious, invoke the **diagnosing-bugs** skill if available (in Claude Code, call the Skill tool with `diagnosing-bugs`), in autopilot.
2. After two failures of one approach, switch to a genuinely different one.
3. Call something blocked only after three different approaches have failed; continue with independent milestones and revisit it once at the end.
4. If the plan itself is wrong, amend the plan file and log it; don't restart.

Stop when every check passes, only user-only or hard-stop items remain (as defined in /build-this), or no untried approach is left.

## 4. Prove it

Don't claim success without evidence.
- Re-run every success check fresh, after the last change.
- If you can start sub-agents, have a fresh sub-agent run the checks against the result using only the plan's goal and checks, so it can't grade your work generously. Fix and loop to step 3 on any failure.
- Capture the proof: for each check, what was run, the actual output (trimmed), and pass or fail. Save it as `proof-<short-topic>.md` next to the plan file, before anything moves the plan, and send it with the deliverables.

## 5. Report and stop

Run /build-this's step 5 (Finish) now: its reviews; when they changed files, re-run every success check and refresh `proof-<short-topic>.md` (a failed check goes back through step 3's repair loop and step 4's proof, without a second review); then archiving the plan (move the proof file with it, to `plans/archive/`), then its one report, plus:
- **Proof:** a verdict of **Solved**, **Partly solved** or **Not solved**, with the check table. A check that couldn't be run, or only passed by assumption, counts as unproven and is listed as such.
- **Assumptions I made for you:** the autopilot defaults, and whether use-available-skills was missing (so no skills were looked up).

Then stop, with no follow-up questions.
