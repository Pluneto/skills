# archive

Retired skills, kept for reference. Nothing here is published: the marketplace lists only `plugins/`, and each archived `SKILL.md` carries `metadata.internal: true` so skills.sh skips it too.

To restore a skill: `git mv archive/<name> plugins/<plugin>/skills/<name>`, remove the `metadata.internal` line from its frontmatter, name it in `which-skill`, bump the plugin and run `scripts/build-marketplace`. Expect to update it first: the other skills moved on after it was archived.

| Skill | Archived | Was in | Why |
|---|---|---|---|
| solve-this | 2026-11-16 | workflow 1.15.1 | Autopilot wrapper over plan-this and build-this; build-this now owns the build itself |
