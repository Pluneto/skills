---
name: setup-pluneto-skills
description: Set up or repair the pluneto-skills plugins in the current repo (setup | repair).
argument-hint: "setup | repair"
disable-model-invocation: true
---

# Set up or repair pluneto-skills in this repo

The `pluneto-skills` marketplace (`Pluneto/skills`) has these plugins: `workflow`, `engineering`, `skill-tools`, `design`, and `setup` (this skill, installed at user scope). Read the current list from `.claude-plugin/marketplace.json` in the marketplace's install location (`claude plugin marketplace list --json`) rather than trusting this line.

**Mode:** the argument, if given. Otherwise **repair** when the repo's `.claude/settings.json` already enables a `*@pluneto-skills` plugin, else **setup**. State the mode you picked.

Both modes inspect first, show findings, and write only after the user confirms once. Commands run from the repo root (`git rev-parse --show-toplevel`; outside git, use the current directory and say so).

## Setup

1. **Inspect.** Read `.claude/settings.json`, `.claude/settings.local.json`, `CLAUDE.md` and `AGENTS.md`, `docs/agents/issue-tracker.md` if present, `git remote -v`, and the output of `claude plugin list --json` and `claude plugin marketplace list --json`. Done when you know which pluneto-skills plugins are already installed for this repo (user scope included), whether a remote points at GitHub, and what an existing tracker doc says.
2. **Choose plugins.** Show the available plugins with one line each (from `marketplace.json`), marking the ones already present, and ask which this repo should have. Recommend `workflow` and `engineering` for a code repo. Done when the user has picked; if `workflow` is among them, continue with 2a–2c, otherwise go to step 3.
   - **2a. Tracker.** Ask where tickets live: **GitHub Issues** or **local files under `plans/`**. Recommend the one an existing tracker doc names; else local when `plans/*/tickets/` already holds tickets (older setups wrote no doc for local); else GitHub when `git remote -v` points at GitHub (tickets sit beside the code, and parallel workers need it), local otherwise. For GitHub, run `gh repo view --json nameWithOwner,isFork`; if it fails, stop, say what is missing (no GitHub remote, or `gh` not signed in), and leave the remotes as they are: the user fixes it and re-runs setup. When it is a fork or not the user's repo, confirm which repo gets the labels, and pass `--repo <owner/name>` to every `gh label` command below. Done when the choice is made and, for GitHub, the target repo is confirmed.
   - **2b. Label names (GitHub only).** Run `gh label list --json name --limit 1000`, then ask "Keep the default label names?" (recommended: yes; when an existing tracker doc already maps them, show its names and ask "Keep this repo's label names?" instead). On no, show every role in the template's Labels table in one message with its recommended name (the closest existing label, else the default), and take the user's changes in one reply. Done when every role has one label name.
   - **2c. Land command (GitHub only).** If the repo has a script that lands a PR (for example `deploy/land.sh` or `scripts/land*`), ask whether workers should finish with it, and which of its commands reports a land's progress (for example `deploy/land.sh --status`); these fill the Land command and Land status command fields. Without such a script, leave both blank. Done when both are set or deliberately blank.
3. **Confirm.** Show the exact changes as a list: the commands below and the files they touch, the tracker doc draft (its label column and Parallel work fields, as a diff when a tracker doc already exists), and the labels that will be created. Apply after one yes.
4. **Apply.**
   - Pin the marketplace in the repo, so a fresh clone is prompted: `claude plugin marketplace add Pluneto/skills --scope project` (skip if `.claude/settings.json` already has `extraKnownMarketplaces.pluneto-skills`).
   - For each chosen plugin: `claude plugin install <plugin>@pluneto-skills --scope project`.
   - If `workflow` is chosen:
     - Create `plans/archive/` with an empty `plans/archive/.gitkeep` (plan-this saves to `plans/`, build-this archives to `plans/archive/`).
     - Write `docs/agents/issue-tracker.md` from the matching template in this skill's folder, [issue-tracker-github.md](issue-tracker-github.md) or [issue-tracker-local.md](issue-tracker-local.md), for either choice. For GitHub, fill the "Label in this repo" column from 2b and the Parallel work fields from 2c, keeping the values an existing doc already has in the fields setup doesn't ask about (Max workers, Areas map, Model tiers, Verify command, both Review commands, Main health command, Model database). Done when the file exists and, for GitHub, its label column matches 2b.
     - For GitHub, create each label in that column that `gh label list --json name --limit 1000` lacks, comparing names case-insensitively (GitHub treats `In-Progress` and `in-progress` as one label): `gh label create "<name>" --description "<meaning>"`. An "already exists" error counts as success. Existing labels stay as they are (no `--force`, no `gh label edit`). Done when every label in the column is in the list; a re-run creates nothing.
   - Write the CLAUDE.md block (template below).
5. **Verify.** Run every repair check. Done when all pass; then tell the user to run `/reload-plugins` (or restart) so the new skills load. User-invoked skills (this one, `workflow:handoff`) never appear in the model's skill list, so judge installs by `claude plugin list --json`, not by that list.

## Repair

Run every check, collect the findings into one table (check, status, fix), confirm once, then apply the fixes and re-run the checks that failed. Done when every check passes or a remaining failure is reported with what only the user can do about it.

| # | Check | How | Fix |
|---|---|---|---|
| 1 | Marketplace registered | `pluneto-skills` in `claude plugin marketplace list --json` | `claude plugin marketplace add Pluneto/skills` |
| 2 | Marketplace current | `git -C <installLocation> rev-parse HEAD` equals `git ls-remote https://github.com/Pluneto/skills HEAD` | `claude plugin marketplace update pluneto-skills` |
| 3 | Enabled means installed (Claude Code loads nothing, silently, for a plugin enabled in settings but not installed) | Every `<id>: true` in `enabledPlugins` of `.claude/settings.json` and `.claude/settings.local.json`, any marketplace, has a `claude plugin list --json` entry with that `id` whose scope is `user` or whose `projectPath` is this repo | `claude plugin install <id> --scope project` (`--scope local` if it came from `settings.local.json`) |
| 4 | Installed plugin current | For each `*@pluneto-skills` entry in `claude plugin list --json` that applies to this repo (scope `user`, or `projectPath` is this repo; ignore other projects' installs), its `version` matches the `version` in that plugin's `.claude-plugin/plugin.json` in the marketplace's install location | `claude plugin update <id>` |
| 5 | No duplicate skills | For each skill in an enabled pluneto-skills plugin (folder names under its `installPath`/`skills/`), run `ls -d ~/.claude/skills/<name> ~/.claude/skills/synced/*/<name> .claude/skills/<name> 2>/dev/null`; any output is a candidate. Compare its SKILL.md frontmatter `description` with the plugin skill's: the same or nearly the same means a duplicate; a different one is a **name clash** (an unrelated skill that happens to share a generic name such as `pr` or `tdd`), reported and left alone unless the user picks it. Passes only when every skill name was checked in all three places, the claude.ai `synced` folder included | Duplicate, user-level copy: move it to `~/.claude/skills-backup/<YYYY-MM-DD>/` (outside `~/.claude/skills`, so it stops loading; Claude Code manages `.trash` itself). claude.ai copy (`synced`): the user deletes it in claude.ai → Customize → Skills; it disappears at the next sync. Repo copy: report it and ask, since the repo may depend on its version |
| 6 | Plans folders | If `workflow` is enabled: `plans/` and `plans/archive/` exist | Create `plans/archive/.gitkeep` |
| 7 | CLAUDE.md block current | The block below exists exactly once, in the file its placement rule picks, and lists exactly the pluneto-skills plugins that apply to this repo (enabled here, plus `setup` when it is installed at user scope), each with the skills in its `plugin.json` `skills` array in the marketplace's install location | Write or rewrite it there, and remove any copy from the other file |
| 8 | Marketplace pinned in repo | `.claude/settings.json` has `extraKnownMarketplaces.pluneto-skills` | `claude plugin marketplace add Pluneto/skills --scope project` |
| 9 | No removed plugins | No `ux@pluneto-skills` in `enabledPlugins` of either settings file, and none in `claude plugin list --json` for this repo (`ux` was merged into `design`) | Remove the `ux@pluneto-skills` key (uninstall it too if it is still listed), then `claude plugin install design@pluneto-skills` at the same scope |
| 10 | No mattpocock-skills duplicate | No `mattpocock-skills@*` enabled in either settings file, or installed for this repo or at user scope in `claude plugin list --json` (its skills now ship in `workflow`, `engineering` and `skill-tools`) | `claude plugin uninstall <id> --scope <its scope>`, and remove its key from `enabledPlugins`. User scope affects every repo, so name that in the confirmation |
| 11 | Tracker doc current | If `docs/agents/issue-tracker.md` exists, it mentions none of Matt's triage leftovers (`needs-triage`, `needs-info`, `wontfix`, `.scratch/`), and has every `##` section of the matching template | Rewrite it from this skill's [issue-tracker-local.md](issue-tracker-local.md) or [issue-tracker-github.md](issue-tracker-github.md), matching the tracker it described and keeping its "Label in this repo" column and Parallel work values. Move any `.scratch/` tickets to `plans/` only if the user asks |
| 12 | Engineering offered | If `workflow` is enabled in a code repo and `engineering` isn't, report it as optional (not a failure): build-this ends with its review-changes and solve-this uses its diagnosing-bugs | `claude plugin install engineering@pluneto-skills --scope project`, on the user's yes |
| 13 | Labels exist | On a GitHub tracker doc, every name in its "Label in this repo" column exists, compared as in setup step 4 | Create the missing ones as in setup step 4 |
| 14 | Tracker doc offered | If `workflow` is enabled and `docs/agents/issue-tracker.md` is missing, report it as optional (not a failure): to-tickets and wayfinder then ask where tickets go on every run | On the user's yes, run setup steps 2a–2c and write the doc |

## CLAUDE.md block

Put it in `CLAUDE.md`; in `AGENTS.md` instead when there is no `CLAUDE.md`, or when `CLAUDE.md` holds nothing but an `@AGENTS.md` import (the block belongs in the file that holds the content). With neither file, create `CLAUDE.md`. Place it under the file's `## Agent skills` heading (create the heading at the end if missing), replacing any earlier `### pluneto-skills` block. Keep it this short: it loads in every session.

```markdown
### pluneto-skills

Installed here:
- `<plugin>`: <its skills, comma-separated>

Plans go in `plans/`, finished ones in `plans/archive/`. Missing or stale skills: run `/setup:setup-pluneto-skills repair`.
```

One `- <plugin>` line per plugin that check 7 lists, its skills taken from that plugin's `plugin.json` `skills` array (folder names, alphabetical).

Leave out the plans sentence when `workflow` is not enabled.
