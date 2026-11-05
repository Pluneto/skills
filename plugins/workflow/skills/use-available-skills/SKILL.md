---
name: "use-available-skills"
description: Decide, on evidence, whether any other available skill (user, project, plugin or claude.ai) is worth using for the current task or phase, and use only those with a specific written reason, without asking the user anything. The default is no skill; most of the time none passes, and that is a fine outcome. Use it at the start of a non-trivial task and at each new phase of work (planning, designing, building, reviewing, writing), and whenever plan-this or build-this needs to choose skills, even when the user never mentions skills. plan-this and build-this call it themselves at the right moment, so don't start a separate run inside them (or inside solve-this, which runs both). Not for trivial one-step requests.
---

# Use available skills

Another skill sometimes holds a method that clearly improves the work (a UI design skill for a front-end build, a review skill while a backend is still being designed), but a skill costs context for the rest of the session and a topical match is not a reason. This skill finds the candidates, makes each one earn its place with a written reason, loads only those that pass, and records the reasons. It runs on its own: never ask the user to choose, and never stall when nothing fits.

## 1. Scan

Collect each skill's `name` and `description` from every source that is present, and skip any source that is not:

- **The skill listing already in context.** It is the quickest source, but it is limited by a size budget and can silently drop descriptions when many skills are installed, so never treat it as complete.
- **Skill folders on disk** (read-only, only the first lines of each `SKILL.md`, which hold the frontmatter): personal (`~/.claude/skills/*/`), project (`.claude/skills/*/` in the working directory and its parents up to the repository root, plus nested `.claude/skills/` folders near the files being worked on), plugin (`skills/*/` folders inside installed plugins), synced claude.ai skills (`~/.claude/skills/synced/*/`), and `/mnt/skills/**` where it exists. This is how skills the listing hid become visible.
- **ListSkills and SearchSkills**, when those tools exist (load them with ToolSearch if they are deferred). Use SearchSkills with a few keywords from the task.

Merge by name. If a name appears in several places, treat it as one skill, and invoke it by the exact name the listing shows (plugin skills carry a prefix such as `plugin-name:skill-name`). claude.ai has no project scope, so project skills only exist in Claude Code sessions.

## 2. Decide

The default is **no skill**. A skill is used only if you can write a reason for it that survives reading what the skill actually says.

1. **Shortlist.** State the task and the phase in one line, then list the skills whose description relates to that work, after the filters below. Usually that is zero to three.
2. **Read before you decide.** For each shortlisted skill, read its instructions: Read its `SKILL.md` on disk when you can, skimming the headings and the steps that touch the task. If it is reachable only through the Skill tool or SearchSkills, don't load it just to judge it. Decide from its description and mark the reason `(description only)`, so the body gets read when the skill is actually loaded.
3. **Write the reason**, one line per skill: `<skill> - Need: ...; Provides: ...; Without it: ...`
   - **Need:** something specific in this task or milestone (a file, a feature, a requirement, a risk), not just its topic.
   - **Provides:** the step, rule or check in the skill that meets that need and that Claude would not do by default. Name it. When only the description is visible, it passes if the description itself names a specific check or step that matches the Need (for example "oversell and race-condition review" for a ticket purchase endpoint); a topic or "best practices" does not pass. In the build phase, state Provides as the check or rule that applies to this milestone, not a redesign of the agreed plan.
   - **Without it:** a defect a check could catch, or a named piece of rework. If the line would read the same for any other skill, it fails.

   If any part comes out generic ("makes it look better", "follows best practices") or only restates the description, the skill fails: don't use it. It also fails if its Provides conflicts with a constraint the user set (a bold redesign when they asked to keep the existing look).
4. **Note the near-misses.** For each shortlisted skill that failed, one line: `considered <skill>, skipped: <why>`. Skills that never made the shortlist don't need a line.

Filters for the shortlist, and rules for the rest:

- In a planning phase, only skills about planning, design decisions or review can be shortlisted. Skills that build or produce files wait for the build phase.
- Leave out plan-this, build-this, solve-this, research-this, interview, review-changes, review-this and this skill itself, so skills never route in circles (build-this already ends with review-changes and offers review-this). Leave out skills whose main job is to interview or question the user, since the callers already handle questions, and skills whose frontmatter says `disable-model-invocation: true` (they are for the user to start). Leave out skills for a file format the deliverable does not use.
- Skip any skill already loaded in this session, except in record-only mode (see step 3), where a skill loaded earlier still counts so that a saved plan stays complete.
- Use at most 3 per phase or milestone. That is a ceiling, not a target: one good reason beats three weak ones, and none is a normal result.
- Run once per phase: don't start a second run for a phase or milestone on your own, but do run again whenever a caller asks, even for a small task.
- A skill the user names explicitly is used without the reason test and doesn't count toward the ceiling, because the test is for skills you would choose yourself.
- Priority is the user's instructions and constraints first, then the agreed plan, then a skill's guidance. A skill adds method; it never overrides a decision the user already made. When you are working unattended or a caller invoked you, a loaded skill never questions the user (take its recommended option and note it) and never overrides the caller's own rules, such as plan-this only planning.

## 3. Load

If the caller asked you only to record matches for later (plan-this does this for the build phase), skip loading and return, for each milestone the caller listed, the reason lines and near-miss lines from step 2, each skill with its exact listed name and its path when it exists only on disk. The ceiling of 3 applies per milestone, not to the whole list.

Otherwise load only the skills you wrote a reason for, from the main agent, when their phase starts rather than all at the beginning:

- Use the Skill tool with the exact listed name.
- If the skill was found only on disk and cannot be invoked by name, Read its `SKILL.md` and follow it.
- If the reason was marked `(description only)`, check the body as soon as it is loaded. If it does not deliver the "Provides" part, stop using the skill and note that.

Sub-agents often cannot see skills, so never rely on one to discover or load them. When you hand work to a sub-agent, copy the few lines of guidance it needs into its brief as plain text, and do not mention the skill's name or path there (a mention can trigger the skill inside the sub-agent and end its run early).

## 4. Record

Finish with what the caller can reuse, in this shape:

```
Skills used: <skill> (<phase>) - Need: ...; Provides: ...; Without it: ...
considered <skill>, skipped: <why>
```

Write `Skills used: none` when nothing passed, followed by the near-miss lines. In record-only mode write `Skills matched (<milestone>):` instead, once per milestone. If a source could not be read, add a few words saying which. Then carry on with the task.
