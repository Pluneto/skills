# pluneto-skills

An agent-skills marketplace: plan-then-build workflows, engineering practice, skill authoring, and design and UX reviews. Built for Claude Code; the same files install in Codex, GitHub Copilot and, through skills.sh, other agents. Every plugin is plain Markdown instructions (plus a bash template in `wizard`): no hooks, MCP servers or binaries.

## Plugins

| Plugin | Skills | Install |
|---|---|---|
| `workflow` | plan-this, interview, build-this, solve-this, research-this, use-available-skills, wayfinder, to-tickets, dispatch, to-questionnaire, wizard, handoff, which-skill | per project |
| `engineering` | tdd, diagnosing-bugs, review-changes, pr, prototype, codebase-design, improve-codebase-architecture, domain-modeling | per project |
| `skill-tools` | writing-for-agents, skill-updater, skill-ozempic, reflect | per project |
| `design` | product-context, design-review, ui-craft | per project |
| `setup` | setup-pluneto-skills (`/setup:setup-pluneto-skills`, user-invoked only) | user scope, once per machine |

Not sure which to use? Type `/which-skill`. The main flow is `/plan-this` → `/build-this` (which ends with review-changes) → `/reflect`; `/to-tickets` splits a plan for multi-session work, and `/dispatch` runs those tickets as waves of parallel workers.

## Install

Pick **one** route per agent: installing both a plugin and skills.sh copies gives you every skill twice.

**Claude Code**

```bash
# once per machine
claude plugin marketplace add Pluneto/skills
claude plugin install setup@pluneto-skills --scope user

# per repo
claude plugin install workflow@pluneto-skills --scope project   # likewise engineering, skill-tools, design
# then in Claude Code: /setup:setup-pluneto-skills   (setup or repair)
```

Inside a session the same works as `/plugin marketplace add Pluneto/skills`. No GitHub credentials are needed; on a machine without a GitHub SSH key, set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` if adding fails. Auto-update is off for third-party marketplaces: turn it on in `/plugin` → Marketplaces → pluneto-skills → Enable auto-update, or run `claude plugin marketplace update pluneto-skills` now and then.

**Codex**

```bash
codex plugin marketplace add Pluneto/skills
codex plugin add workflow@pluneto-skills   # likewise engineering, skill-tools, design
```

Updates itself at startup.

**GitHub Copilot (CLI and VS Code)**

```bash
copilot plugin marketplace add Pluneto/skills
copilot plugin install workflow@pluneto-skills   # likewise engineering, skill-tools, design
```

To update automatically, set `"autoUpdate": true` once for the `pluneto-skills` entry under `extraKnownMarketplaces` in `~/.copilot/settings.json`. In VS Code, run **Chat: Install Plugin From Source** with `https://github.com/Pluneto/skills`.

**Every other agent (skills.sh, manual updates)**

```bash
npx skills@latest add Pluneto/skills -a <agent>   # omit -a to choose
```

Update with `npx skills@latest update`, and re-run `add` to pick up new skills.

Codex and Copilot read the same `.claude-plugin/` manifests. This repo uses the layout Matt Pocock verified on Codex 0.161.0 and Copilot CLI (explicit `skills` lists, `agents/openai.yaml` per skill, no symlinks), but nobody has run these two routes against this repo yet. `setup` is Claude Code only.

Plugins run with your permissions and skills enter the agent's context, so read what you install.

### Moving from the old layout

The `ux` plugin was merged into `design`, and mattpocock-skills is now vendored here. In each repo that used them:

1. `claude plugin marketplace update pluneto-skills`
2. install the new plugins where wanted (`design` where `ux` was enabled, `engineering`)
3. run `/setup:setup-pluneto-skills repair`: it replaces `ux` with `design`, offers `engineering`, and flags an installed `mattpocock-skills` as a duplicate to uninstall.

## Edit a skill

1. Edit `plugins/<plugin>/skills/<skill>/SKILL.md` (copy files in; symlinks are rejected). A new skill also needs `agents/openai.yaml` and a line in `which-skill`.
2. Bump the plugin's version: `scripts/bump <plugin>` (patch; pass `minor` or `major` for bigger changes). Installed copies only update when the version changes, and `scripts/validate` fails if a plugin changed since `origin/main` without a bump.
3. Run `scripts/build-marketplace` (it regenerates `.claude-plugin/marketplace.json` and each plugin's `skills` list), stage everything, then commit to `main` and push. The pre-commit hook refuses unstaged or untracked changes under `.claude-plugin/`, `plugins/` and `scripts/` (so it checks exactly what is committed), fails if the generated files are out of date, and runs `scripts/validate`.

New plugin: add `plugins/<name>/.claude-plugin/plugin.json` (`name`, `version`, `description`, `author`, `license`) and a `skills/` folder.

After cloning, enable the hook: `git config core.hooksPath scripts/hooks` (needs `claude` and Python 3 with PyYAML). The hook also refuses commits whose author or committer email is not a GitHub noreply address, so a personal address never lands in public history: `git config user.email <id>+<user>@users.noreply.github.com`.

## Scripts

- `scripts/build-marketplace`: regenerates the marketplace file and each plugin.json's `skills` list, and checks skill frontmatter (valid YAML, `name` matches the folder, `description` present) and that there are no symlinks. It writes nothing when a check fails; `--check` writes nothing and fails when a generated file is out of date.
- `scripts/validate`: `claude plugin validate --strict` on the marketplace and every plugin, plus the repo's checks: versions bumped (untracked files count as changes), `agents/openai.yaml` matching each skill's invocation, licences kept on vendored skills, every skill named in which-skill as a whole word, generated files current (`build-marketplace --check`), and the files copied into several skills still identical (`PAIRED` in the script).
- `scripts/bump`: bumps a plugin's version.
- `scripts/measure-context`: estimates always-on skill tokens outside any project (see `docs/baseline.md`); `scripts/measure-skills <plugin-dir>...` does the same for plugin folders.

## Licence

MIT, see [LICENSE](LICENSE). Many skills are adapted from [mattpocock/skills](https://github.com/mattpocock/skills) 1.3.1 (MIT, (c) 2026 Matt Pocock; his notice is kept in each copied folder): handoff, wayfinder, to-tickets, to-questionnaire, wizard, which-skill, writing-for-agents, setup-pluneto-skills (from setup-matt-pocock-skills) and every `engineering` skill. `docs/merge-map.md` lists what came from where. `engineering/skills/pr` also credits Dex Horthy and carries HumanLayer's MIT licence for the part it reproduces (see its `CREDITS.md`). Anthropic's source-available skills (docx, pdf, pptx, xlsx, …) are deliberately not included.
