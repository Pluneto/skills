# experimental

New skills land here for testing: `plugins/experimental/skills/<name>/SKILL.md` plus `agents/openai.yaml`.

- The plugin is published only while it holds a skill: `scripts/build-marketplace` skips a plugin without skills, and lists it in the marketplace once one exists.
- Bump it (`scripts/bump experimental`) with every change, like any plugin.
- A skill that proves itself moves with `git mv` into the plugin it belongs to, and gets a line in `which-skill`. One that doesn't moves to `archive/`.
