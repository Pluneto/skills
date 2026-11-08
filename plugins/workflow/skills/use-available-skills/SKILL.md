---
name: "use-available-skills"
description: Decide, on evidence, whether any other available skill (user, project, plugin or claude.ai) is worth using for the current task or phase, and load only those with a specific written reason, without asking the user anything. The default is no skill; "none" is a fine outcome. Use at the start of a non-trivial task and at each new phase (planning, designing, building, reviewing, writing), and whenever plan-this or build-this needs to choose skills. plan-this and build-this call it themselves, so don't start a separate run inside them (or inside solve-this). Not for trivial one-step requests.
---

# Use available skills

A skill sometimes holds a method that clearly improves the work (a UI design skill for a front-end build), but it costs context for the rest of the session and a topical match is not a reason. This skill finds candidates, makes each earn its place with a written reason, loads only those that pass, and records the reasons. Never ask the user to choose, and never stall when nothing fits.

## 1. Scan

Collect each skill's `name` and `description` from every source present:

- **The skill listing already in context**: quickest, but size-limited and able to drop descriptions silently, so never treat it as complete.
- **Skill folders on disk** (read-only, the first lines of each `SKILL.md`): personal (`~/.claude/skills/*/`), project (`.claude/skills/*/` in the working directory and its parents up to the repository root, plus nested ones near the files being worked on), plugin (`skills/*/` inside installed plugins), synced claude.ai (`~/.claude/skills/synced/*/`), and `/mnt/skills/**` where it exists. This reveals skills the listing hid.
- **ListSkills and SearchSkills**, when those tools exist (load them with ToolSearch if deferred); search with a few keywords from the task.

Merge by name and invoke by the exact listed name (plugin skills carry a prefix such as `plugin-name:skill-name`). claude.ai has no project scope.

## 2. Decide

The default is **no skill**. Use one only if you can write a reason that survives reading what the skill says.

1. **Shortlist.** State the task and phase in one line, then list the skills whose description relates to the work, after the filters below (usually zero to three).
2. **Read before you decide.** Read each shortlisted skill's `SKILL.md` on disk when you can, skimming the headings and the steps that touch the task. If it is reachable only through the Skill tool or SearchSkills, don't load it just to judge it: decide from its description and mark the reason `(description only)`, so the body is read when it is actually loaded.
3. **Write the reason**, one line per skill: `<skill> - Need: ...; Provides: ...; Without it: ...`
   - **Need:** something specific in this task or milestone (a file, feature, requirement, risk), not its topic.
   - **Provides:** the step, rule or check in the skill that meets that need and that Claude would not do by default. When only the description is visible, it passes if the description names a specific check or step matching the Need (e.g. "oversell and race-condition review" for a ticket purchase endpoint); a topic or "best practices" does not. In the build phase, state the check or rule that applies to this milestone, not a redesign of the agreed plan.
   - **Without it:** a defect a check could catch, or named rework. A line that would read the same for any other skill fails.

   A generic reason ("makes it look better"), one that only restates the description, or a Provides that conflicts with a user constraint (a bold redesign when they asked to keep the look) fails the skill.
4. **Note near-misses:** for each shortlisted skill that failed, `considered <skill>, skipped: <why>`. Skills that never made the shortlist need no line.

Filters and rules:

- In a planning phase, only skills about planning, design decisions or review qualify; skills that build or produce files wait for the build phase.
- Leave out plan-this, build-this, solve-this, research-this, interview, review-changes, review-this and this skill, so skills never route in circles. Leave out skills whose main job is to question the user, skills with `disable-model-invocation: true`, and skills for a file format the deliverable doesn't use.
- Skip any skill already loaded in this session, except in record-only mode (step 3), where it still counts so a saved plan stays complete.
- At most 3 per phase or milestone: a ceiling, not a target. One good reason beats three weak ones.
- Run once per phase; run again whenever a caller asks, even for a small task.
- A skill the user names explicitly needs no reason test and doesn't count toward the ceiling.
- Priority: the user's instructions and constraints, then the agreed plan, then a skill's guidance. A skill adds method; it never overrides a decision the user made. Unattended or called by another skill, a loaded skill never questions the user (take its recommended option and note it) and never overrides the caller's rules (such as plan-this only planning).

## 3. Load

If the caller asked only to record matches for later (plan-this does this for the build phase), skip loading and return, per milestone the caller listed (ceiling 3 each), the reason lines and near-miss lines from step 2, each skill with its exact listed name and its path when it exists only on disk.

Otherwise load only the skills you wrote a reason for, from the main agent, when their phase starts, not all at the beginning:

- Use the Skill tool with the exact listed name; for a skill found only on disk, Read its `SKILL.md` and follow it.
- For a reason marked `(description only)`, check the body once loaded; if it doesn't deliver the "Provides" part, stop using the skill and note that.

Sub-agents often cannot see skills: copy the few lines of guidance a sub-agent needs into its brief as plain text, without the skill's name or path (a mention can trigger the skill inside the sub-agent and end its run early).

## 4. Record

Finish with what the caller can reuse:

```
Skills used: <skill> (<phase>) - Need: ...; Provides: ...; Without it: ...
considered <skill>, skipped: <why>
```

Write `Skills used: none` when nothing passed, followed by the near-miss lines. In record-only mode write `Skills matched (<milestone>):` instead, once per milestone. If a source could not be read, say which in a few words. Then carry on with the task.
