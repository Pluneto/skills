---
name: "use-available-skills"
description: Decide, on evidence, whether any other available skill (user, project, plugin or claude.ai) is worth using for the current task or phase, and load only those with a specific written reason, without asking the user anything. The default is no skill; "none" is a fine outcome. Use at the start of a non-trivial task and at each new phase (planning, designing, building, reviewing, writing), and whenever plan-this or build-this needs to choose skills. plan-this and build-this call it themselves, so don't start a separate run inside them. Not for trivial one-step requests.
---

# Use available skills

A skill sometimes holds a method that clearly improves the work (a UI design skill for a front-end build), but it costs context for the rest of the session, and a topical match is not a reason. Find the candidates, make each earn its place with a written reason, load only those that pass, and record the reasons. The default is **no skill**. The user is never asked to choose, and nothing stalls when none fits.

## Find them

The skill listing in context is quickest but size-limited and drops descriptions silently, so also read the first lines of `SKILL.md` in the skill folders that exist: personal (`~/.claude/skills/*/`, `~/.claude/skills/synced/*/`), project (`.claude/skills/*/` up to the repository root and near the files being worked on), installed plugins (`skills/*/`), `/mnt/skills/**`, and any ListSkills or SearchSkills tool. Merge by name; invoke by the exact listed name (plugin skills carry a prefix such as `plugin-name:skill-name`).

## Make each earn its place

State the task and phase in one line, shortlist the skills whose description relates to the work (usually zero to three), and read each one's `SKILL.md` on disk before deciding. A skill reachable only through a tool is judged from its description and marked `(description only)`, so its body is checked when it is actually loaded. Then write, per skill:

`<skill> - Need: ...; Provides: ...; Without it: ...`

- **Need:** something specific in this task or milestone (a file, feature, requirement, risk), not its topic.
- **Provides:** the step, rule or check in the skill that meets that need and that you would not do by default. In a build phase, the check or rule for this milestone, not a redesign of the agreed plan.
- **Without it:** a defect a check could catch, or named rework. A line that would read the same for any other skill fails.

A generic reason, one that restates the description, or a Provides that conflicts with a user constraint fails the skill. For each shortlisted skill that failed: `considered <skill>, skipped: <why>`.

Limits:

- A planning phase takes only skills about planning, design decisions or review; skills that build or produce files wait for the build phase.
- Leave out plan-this, build-this, research-this, interview, review-changes, review-this and this skill (no routing in circles), skills whose main job is to question the user, skills with `disable-model-invocation: true`, skills for a file format the deliverable doesn't use, and skills already loaded this session (except in record-only mode).
- At most 3 per phase or milestone, a ceiling and not a target. A skill the user names needs no reason and doesn't count.
- The user's instructions, then the agreed plan, then a skill's guidance. Unattended or called by another skill, a loaded skill never questions the user and never overrides the caller's rules.

## Load, or record

**Record-only** (plan-this asks this for the build phase): load nothing and return, per milestone the caller listed, the reason and near-miss lines, each skill with its exact listed name and its path when it exists only on disk.

Otherwise load the skills that passed, from the main agent, when their phase starts: the Skill tool with the exact name, or Read the `SKILL.md` of one found only on disk. A `(description only)` skill whose body doesn't deliver its Provides is dropped, and you note that. Sub-agents often cannot see skills: paste the few lines they need into the brief as plain text, without the skill's name or path (a mention can trigger the skill inside the sub-agent and end its run early).

Finish with what the caller can reuse, then carry on with the task:

```
Skills used: <skill> (<phase>) - Need: ...; Provides: ...; Without it: ...
considered <skill>, skipped: <why>
```

`Skills used: none` when nothing passed, followed by the near-miss lines; in record-only mode `Skills matched (<milestone>):` once per milestone. Say in a few words if a source could not be read.
