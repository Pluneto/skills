---
name: "build-this"
description: Own an agreed plan through to a finished, proven result, milestone by milestone, without re-opening the user's decisions. Use whenever the user says "build this", "/build-this", "build this plan", attaches or points to a plan-*.md file, a tickets folder, issues or a milestone (`milestone "<name>"`), or when /plan-this hands off after planning. If there is no plan at all and the goal is big, offer /plan-this in one line first.
---

# Build this

You own the build: the plan's goal, built and proven. The user agreed to the plan's **goal**, **Decisions**, **Constraints** and each milestone's **Done when**; those bind. Its steps, their order and the milestone split are the planner's guess from before the work started: follow them while they are the best route, change them when the work shows a better one, and log why.

## The plan

Use the first that exists: the plan agreed earlier in this conversation; a plan file (the argument, an attachment, `plans/plan-*.md`); tickets or issues (a tickets folder, named issues, `milestone "<name>"`: read [tickets.md](tickets.md) first); a plan the user wrote. With no plan, build a small clear request as one milestone, and for a big or ambiguous one offer /plan-this in one line and follow the answer.

- **Resume.** Ticked milestones and a `## Build log` mean an earlier run got that far: read the log and start at the first unfinished milestone.
- **Base.** In a git repository note `git rev-parse HEAD` before the first change; reviews and the report measure from it.
- **A file to live in.** When the plan exists only in this conversation and the build may outlast one context, save it to `plans/plan-<short-topic>.md` first.

## How you work

Order, pace, tools, skills and delegation are yours to choose, and you start without asking how to build. A preference the user stated wins. What a run depends on:

- **Needs from the user.** Read the plan's **Needs from you** against the milestones. Ask once, at the start, for everything an early milestone cannot be built without; everything else gets a marked placeholder (`TODO(user)`) and a line in the report. Secrets never pass through chat: name the variable or secret setting each goes in.
- **Delegation.** Hand a milestone, a search or a check to a child agent when that keeps your context clean or gives the work a better-suited model. When a skill for starting and waiting on child agents in this harness is installed, load it before the first child and follow it. A child sees nothing of this conversation: brief it per [milestone-brief.md](milestone-brief.md). Its report is a claim; the check you re-run is the evidence.
- **Skills.** A milestone's **Skills** line is a recommendation with its reason: load a skill when its Need still holds for the milestone as it now is. With no Skills lines, run **use-available-skills** once. A loaded skill adds method; the plan's decisions win over its advice, and open questions it hands back are deviations to sort like any other.
- **Code** follows KISS, and SOLID for object-oriented code: the simplest thing that passes the check.

## Each milestone

A milestone is done when its Done-when check passes in a fresh run you made yourself, after the last change. A milestone without a check gets the obvious one, written down before you build.

1. Build it. A failing check or red CI goes through [fix-ladder.md](fix-ladder.md). When the ladder is exhausted the milestone is **blocked**: log it and carry on with the milestones that do not depend on it.
2. Tick it in the plan and append its line to the plan's `## Build log` (for tickets, [tickets.md](tickets.md) says where). A fresh session resumes from this log, not the conversation, so it carries what changed, what deviated and what is owed; a blocked milestone gets its line too and stays unticked, and a change you make to later milestones gets its own line (`- Plan change after M<n>: <what and why>`).

   ```
   - M<n> <title> (<who built it>): check pass|fail - <one-line result>; deviations: <…|none>; owed: <needs from the user, parked decisions, held steps, or none>; skills: <skill: what it changed|none>
   ```
3. Settle the deviations (below) before the next milestone starts.

## Deviations

Plans meet reality. Sort each surprise:

- **Engineering deviation** (a renamed package, an API that differs from its docs, a step in the wrong order, a missing step, naming, layout, a library pick): yours. Take the fix closest to the plan's intent, log it with a one-line reason, and adjust later milestones to match.
- **User-level deviation**: it would change a recorded Decision, the goal or scope, product behaviour, UI or copy, cost, a new service or dependency, privacy or security, or it needs something hard to undo. These are the user's.

For a user-level deviation, finish whatever part of the current milestone stands without it, then **before the next milestone starts** run the **interview** skill on the open decisions, giving it what you found, the evidence, the options and your recommendation. Collect several into one interview. When the decision blocks the current milestone itself, interview at once. Afterwards record each answer in the plan's Decisions table, rewrite the remaining milestones and their Done-when checks to fit, and continue.

**Unattended runs** (the caller said there is no user to ask) ask nothing, anywhere in this skill. A user-level decision is parked: log the question, options and your recommendation as owed, build everything that does not depend on it, leave what does unbuilt, and put it first in the report. A missing input gets its placeholder, or blocks the milestone that cannot stand on one. A hard-to-undo step without a go-ahead is listed as held.

## Hard-to-undo steps

Stop before anything hard to undo or outside the workspace: spending money, deleting data, publishing, deploying to production, merging, sending messages, signing in, connecting a new service. A go-ahead the user already gave for that exact step counts (for example "merge if green"). Otherwise do all the work that does not depend on it and ask once, at the end.

## Finish

The build is finished when every milestone is done or blocked with its reason, and every check under the plan's **How we'll know it worked** has been re-run fresh after the last change.

- **Review.** With a base commit, have the diff reviewed against the plan before you report: **review-changes** when available (one pass; fix what the plan asked for and the diff misses), and for a build where a miss is costly, **review-this** with a model from another provider when one is reachable. Re-run the affected checks after any fix. Say which reviews ran.
- **Archive.** When every milestone is done and the plan file lives in the project, move it to `plans/archive/`. A plan with anything blocked or failing stays where it is.
- **Report**, short and scannable, with evidence rather than assurance:
  - what was built, and where;
  - each success check: the command or observation, and its result;
  - decisions and deviations made on the user's behalf, each with its reason, and the decisions the user made in a deviation interview;
  - reviews: who reviewed, what was fixed, judgement calls left open;
  - skills that changed something, and what;
  - blocked or failing, with what would unblock it;
  - what is left for the user: placeholders with where each real value goes, parked decisions, and hard-to-undo steps awaiting a go-ahead.
