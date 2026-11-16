# pluneto-skills

An agent-skills marketplace: plan-then-build workflows, engineering practice, skill authoring, and design and UX reviews. Built for Claude Code; the same files install in Codex, GitHub Copilot and, through skills.sh, other agents. Every plugin is plain Markdown instructions (plus a bash template in `wizard`), with one exception: `t3code` also ships compaction hooks (a Python 3 script, no dependencies). No MCP servers or binaries.

## Plugins

| Plugin | Skills | Install |
|---|---|---|
| `workflow` | plan-this, interview, build-this, research-this, review-this, use-available-skills, wayfinder, to-tickets, to-questionnaire, wizard, handoff, which-skill. Host-neutral: any repo, any harness, code or not | per project |
| `t3code` | t3-orchestration, dispatch (`/dispatch`). Only for [T3 Code](https://github.com/t3dotgg/t3code); depends on `workflow`, which installs with it | per project or user scope, on T3 Code |
| `engineering` | tdd, diagnosing-bugs, review-changes, pr, prototype, codebase-design, improve-codebase-architecture, domain-modeling | per project |
| `skill-tools` | writing-for-agents, skill-updater, skill-ozempic, reflect | per project |
| `design` | product-context, design-review, ui-craft | per project |
| `experimental` | Skills under test. Listed in the marketplace only while it holds one (currently none); see [plugins/experimental](plugins/experimental/README.md) | when you want to try them |
| `setup` | setup-pluneto-skills (`/setup:setup-pluneto-skills`, user-invoked only) | user scope, once per machine |

Not sure which to use? Type `/which-skill`. The main flow is `/plan-this` → `/build-this` → `/reflect`. build-this owns the build: it chooses its own route, proves each milestone with its check, keeps a live-state file outside the working tree so a context compaction loses nothing it needs, and interviews you before the next milestone only when a deviation needs a decision that is yours. `/to-tickets` splits a plan for multi-session work, and on T3 Code `/dispatch` (t3code) takes ownership of those tickets and finishes them with parallel workers. Retired skills live in [archive/](archive/README.md), unpublished. On a GitHub tracker, "note this idea" files a `draft` issue, `/plan-this issues <n>` plans it (`planned`) and `/to-tickets <n>` makes its tickets, worked `priority:high` first and `priority:low` last.

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

### Moving to workflow 2.0

`workflow` 2.0.0 is host-neutral, so three skills left it: `dispatch` and `t3-orchestration` moved to the new `t3code` plugin, and `solve-this` was archived (build-this now owns the build without the opening questions). Updating `workflow` removes them, with no notice in the app. On T3 Code:

1. `claude plugin marketplace update pluneto-skills`
2. `claude plugin install t3code@pluneto-skills` at the scope `workflow` has (it pulls in `workflow`)
3. in each repo, `/setup:setup-pluneto-skills repair` refreshes the CLAUDE.md block and offers `t3code`.

A tracker doc's **Model tiers** field is no longer read; delete the line.

### Moving from the old layout

The `ux` plugin was merged into `design`, and mattpocock-skills is now vendored here. In each repo that used them:

1. `claude plugin marketplace update pluneto-skills`
2. install the new plugins where wanted (`design` where `ux` was enabled, `engineering`)
3. run `/setup:setup-pluneto-skills repair`: it replaces `ux` with `design`, offers `engineering`, and flags an installed `mattpocock-skills` as a duplicate to uninstall.

## Edit a skill

1. Edit `plugins/<plugin>/skills/<skill>/SKILL.md` (copy files in; symlinks are rejected). A new skill also needs `agents/openai.yaml` and a line in `which-skill` (except in `t3code` and `experimental`, which the host-neutral router leaves out). New skills start in `plugins/experimental`; retired ones move to `archive/`.
2. Bump the plugin's version: `scripts/bump <plugin>` (patch; pass `minor` or `major` for bigger changes). Installed copies only update when the version changes, and `scripts/validate` fails if a plugin changed since `origin/main` without a bump.
3. Run `scripts/build-marketplace` (it regenerates `.claude-plugin/marketplace.json` and each plugin's `skills` list), stage everything, then commit to `main` and push. The pre-commit hook refuses unstaged or untracked changes under `.claude-plugin/`, `plugins/` and `scripts/` (so it checks exactly what is committed), fails if the generated files are out of date, and runs `scripts/validate`.

New plugin: add `plugins/<name>/.claude-plugin/plugin.json` (`name`, `version`, `description`, `author`, `license`) and a `skills/` folder.

After cloning, enable the hook: `git config core.hooksPath scripts/hooks` (needs `claude` and Python 3 with PyYAML). The hook also refuses commits whose author or committer email is not a GitHub noreply address, so a personal address never lands in public history: `git config user.email <id>+<user>@users.noreply.github.com`.

## Scripts

- `scripts/build-marketplace`: regenerates the marketplace file and each plugin.json's `skills` list (a plugin without skills is left out), and checks skill frontmatter (valid YAML, `name` matches the folder, `description` present) and that there are no symlinks. It writes nothing when a check fails; `--check` writes nothing and fails when a generated file is out of date.
- `scripts/validate`: `claude plugin validate --strict` on the marketplace and every plugin, plus the repo's checks: versions bumped (untracked files count as changes), `agents/openai.yaml` matching each skill's invocation, licences kept on vendored skills, every skill named in which-skill as a whole word (t3code and experimental excepted), no host names under `plugins/workflow` (`HOST_TERMS` in the script), generated files current (`build-marketplace --check`), the files copied into several skills still identical (`PAIRED` in the script), and dispatch's Main health command passing its fixtures (`scripts/test-main-health`, needs bash and jq).
- `scripts/test-main-health [file]`: runs the command in t3code's `dispatch/main-health.md` (or `file`'s first `sh` block) against fixture `gh` output for each red, pending and green case.
- `scripts/bump`: bumps a plugin's version.
- `scripts/measure-context`: estimates always-on skill tokens outside any project (see `docs/baseline.md`); `scripts/measure-skills <plugin-dir>...` does the same for plugin folders.

## Licence

MIT, see [LICENSE](LICENSE). Many skills are adapted from [mattpocock/skills](https://github.com/mattpocock/skills) 1.3.1 (MIT, (c) 2026 Matt Pocock; his notice is kept in each copied folder): handoff, wayfinder, to-tickets, to-questionnaire, wizard, which-skill, writing-for-agents, setup-pluneto-skills (from setup-matt-pocock-skills) and every `engineering` skill. `docs/merge-map.md` lists what came from where. `engineering/skills/pr` also credits Dex Horthy and carries HumanLayer's MIT licence for the part it reproduces (see its `CREDITS.md`). Anthropic's source-available skills (docx, pdf, pptx, xlsx, …) are deliberately not included.
