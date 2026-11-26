# Plan: thread pin (`#pin`), instructions that survive compaction

*Created 2026-11-26 with /plan-this. Attach this file to a Claude chat and run /build-this (or say "build this plan") to continue.*

## Goal

**The request, in the user's words:** "At the start of threads I usually paste a set of instructions for the thread which are important, but these are most likely lost after a couple of compacts, but they should be reinjected." The user pastes a different selection per thread, line by line, from blocks such as "General Agent" (role, no code comments), "Orchestrator Agent" (keep the context clean, which sub-agent models are forbidden, cost) and an answer-style block.

**Accepted deepened goal:** Add a hooks-only plugin `pin` to the `Pluneto/skills` marketplace. A hook, not the agent, stores the instructions the user marks with a `#pin` line, word for word, in a pin file for that thread. A second hook re-injects them unchanged after every manual or automatic compaction, in every Claude Code thread that loads user-level plugins and their hooks (a session started with `--bare` or with hooks disabled is not covered), in every project, with or without a live-state file. The pin belongs to one thread: native sub-agents never get it, and a delegated child has its own pin. The pin stays under the 10,000-character limit for hook output and says so when it is cut. Proof is unit tests plus one end-to-end run through three compactions that shows the exact text after each one.

**Constraints**

- Hook-based. No change to T3 Code and nothing under `~/.t3`.
- Claude Code only. Codex threads are out of scope.
- The plugin has no skills, so it adds nothing to a thread's startup context.
- Python 3, standard library only, like the existing compaction hook. KISS.
- A hook must never fail the session: on any error it prints nothing and exits 0.
- Pin files hold the user's text: they stay on the box, in the plugin's data folder, never in a repository. The end-to-end run uses a synthetic session, not a real transcript.
- The injected text is worded as a statement of fact ("the user set these instructions earlier in this thread"), not as a command from the system. The hooks reference says imperative system-style text can trigger prompt-injection defences.
- `Pluneto/skills` is a Pluneto repo: the builder opens the PR and does not merge it without the user's "merge if".
- The box's Claude settings are changed only by their owner. The builder writes a *config-owner prompt*: a text that the user pastes to that owner. This file is public, so the build brief, not this file, names the owner, the box's two config folders and the sandbox project.

**Skills used while planning:** none.
considered `engineering:codebase-design`, skipped: the change is one small script, so no interface decision needs it.
considered `skill-tools:writing-for-agents`, skipped: it shapes the injected wording, which is build-phase work.

**Plan review:** review-this, plan target, by Codex CLI with `gpt-6.2-sol` at medium effort, 2 rounds, ended at plan-this's limit of two reviews (not an approval). Round 1 gave 10 findings, all fixed: the config-owner prompt installs the plugin instead of only enabling it; the transcript fallback became a build gate that stops the build; the 60-day expiry was removed; the end-to-end check became byte-exact at three separate boundaries with a fresh thread id and an empty data folder; the combined run with `t3code` became a Done-when item; one compaction must be automatic; two thread ids in one data folder are tested as independent; the goal names its coverage. Round 2 closed 7 of them and left 3, fixed afterwards and not seen again by the reviewer: the size budget in UTF-16 code units, the way to trigger an automatic compaction, and the cause check in the combined run. Nothing was re-asked and nothing declined.

## How we'll know it worked

1. **Unit tests** at the script's public seam: hook input JSON on stdin, then the hook's stdout and the pin file. `python3 scripts/validate` runs them, locally and in the `validate` CI run.
2. **Three-compaction run:** a synthetic Claude Code session, started the way T3 Code starts one (stream-json, `CLAUDE_CONFIG_DIR`, the plugin loaded with `--plugin-dir`). It pins a probe rule and goes through three separate compactions, at least one of them automatic. After each one, the text that the `SessionStart` hook injected equals the pinned bytes. After the third compaction the agent's reply still obeys the probe rule.
3. **Real thread:** after the plugin is enabled at user level, a new T3 thread in the sandbox project shows the same result through T3 Code itself.

## Decisions

| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | How the user marks the text | A marker line: `#pin` alone on a line, any letter case; everything below it to the end of that message is pinned | Exact text, works in any message of the thread, and task text above the marker stays out |
| 2 | Where the hook ships | A new hooks-only plugin `pin`, enabled once at user level | The `t3code` plugin runs in only 3 of 12 projects; a hooks-only plugin runs everywhere and lists no skills |
| 3 | Codex | Out of scope | The user's choice. Codex hooks under T3 Code are unverified, and Codex may already keep user messages |
| 4 | Baseline measurement | None | The user's choice. The end-to-end run tests only with the hook on |
| 5 | A second `#pin` in the same thread | It is added below the earlier pin | A rule added mid-thread never drops the rules from the start |
| 6 | Reusable named sets of rules | No | The user picks single lines per thread; one small mechanism |
| 7 | Who enables the plugin at user level | A config-owner prompt that the user pastes | The box config keeps one owner and survives a redeploy |

**Accepted defaults**

- `#unpin` alone on a line clears the thread's pin.
- The agent confirms a new pin in one line of its next reply (the capture hook tells it what was stored).
- A pin over the budget (9,500 UTF-16 code units for the whole injected text) is cut, with a note and the pin file's path so the agent can read the rest.
- The pin is keyed on the T3 thread (`T3CODE_THREAD_ID` when set, else the hook input's `session_id`), and stored under the plugin's data folder (`CLAUDE_PLUGIN_DATA`).
- The last check runs in a real T3 thread in the sandbox project; the builder may start that one thread.

## Needs from you

*Needed early:* nothing.

*Can wait (both for milestone 2):*

- **Merge the PR**, or say "merge if CI is green". Until then the PR stays open and milestone 1 is complete without it.
- **Paste the config-owner prompt** after the merge. The builder writes it at the end of milestone 1 and gives it with the PR: refresh the `pluneto-skills` marketplace, then install `pin@pluneto-skills` at user scope under both config folders. Until then every test loads the plugin with `--plugin-dir`.

## Steps

### Milestone 1: the `pin` plugin, built and proven (done, PR open)

**Outcome:** `plugins/pin` exists in `Pluneto/skills` on a branch with an open PR. A message with a `#pin` line stores the text below it, and after each compaction the session gets that text back unchanged.

**What constrains it**

- Work in a worktree off `origin/main` and leave the repository's main checkout alone.
- Layout follows the existing hooks-only plugin `plugins/cli-host`: `.claude-plugin/plugin.json` (version, no skills), `hooks/hooks.json`, one script, its tests next to it.
- Two hook events: `UserPromptSubmit` (capture) and `SessionStart` with matcher `compact` (re-inject).
- Behaviour the tests must fix:
  - `#pin` alone on a line, any case, pins the rest of that message; text above the marker is not pinned; a message without the marker changes nothing.
  - A second `#pin` adds below the first. `#unpin` alone on a line clears the pin; `#unpin` followed later in the same message by `#pin` clears, then pins.
  - Re-injection returns the stored text byte for byte, with one factual header line. No pin file: no output.
  - The complete injected text (header, pin, any cut note and path) stays within 9,500 UTF-16 code units, the unit in which Claude Code is reported to count its 10,000 limit. A longer pin is cut, and the output says so and names the file. One test uses a pin of emoji (two code units each).
  - Hook input with an `agent_id` (a native sub-agent): no capture, no injection.
  - The key is the T3 thread id when the environment has one, else the session id. The file name is safe for any id (thread ids contain `:` and `%`).
  - Two thread ids that share one data folder (a parent thread and its delegated child) never see or change each other's pin.
  - A pin stays until `#unpin`: no automatic expiry.
  - Malformed input or an unwritable folder: no output, exit 0.
- The repo's own rules: add the new tests to `scripts/validate`, add a README row for `pin` with one usage example, run `scripts/build-marketplace`, and keep the commit author on the GitHub noreply address.

**Hints (the builder owns the route)**

- [ ] `plugins/t3code/evals/compaction_replay.py` already starts `claude` the T3 Code way and sends `/compact`; reuse its launch code or extend it. Today it compacts once, keeps only the first segment after the compaction, and scores replies by normalised substrings, so it cannot prove a byte-exact injection as it is. A change under `plugins/t3code` needs `scripts/bump t3code`.
- [ ] A synthetic session is enough and cheap: a few filler turns, one `#pin` message with a probe rule whose effect is a fixed string in every reply, then compact, one turn, compact, one turn, compact, probe. Use the cheapest Claude model.
- [ ] For the automatic compaction, make a short session reach the threshold. The plan reviewer reports that the `autoCompactWindow` setting has a 100,000-token minimum and that the environment variable `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`, set for the trial's process only, lowers the trigger. Neither claim is verified: check both first.

**Build gate (before any other code):** in a session started as T3 Code starts one, confirm that `UserPromptSubmit` receives the user's raw message (also when it starts with a slash command and when it has several lines), and that `SessionStart` fires with source `compact` after `/compact`. If the prompt hook does not deliver the raw text, stop and report to the user. Reading the transcript at compaction time instead is a different design: it cannot confirm a pin on the turn that sends it, and a forked thread would inherit the parent's pin. That change needs the user's yes.

**Done when**

- `python3 scripts/validate` passes in the worktree, and `gh run view <run> --json conclusion,headSha` shows `success` on the PR's latest commit.
- The three-compaction run uses a fresh synthetic thread id and an empty plugin data folder, and asserts that no pin exists before the `#pin` message. Its result shows three separate compaction boundaries, at least one with an automatic trigger. At each one, the text injected by the `SessionStart` hook equals the pinned bytes, and the probe reply after the third obeys the probe rule. The automatic case counts as verified only when the run shows a boundary with an automatic trigger. If no setting makes a synthetic session reach it, the case is reported as unverified, not forced with a full-size context.
- A second run loads `plugins/t3code` too, with a live-state file, and sizes the pin and the live-state so that each is under 10,000 characters and their sum is over it. Both injections arrive complete. If one is missing or cut, first confirm that both hooks ran and printed their expected output. Only then is a shared cap the cause: stop and report, because the split is the user's decision.
- The result table, with the output of `claude --version`, is in the PR body under Evidence.
- The PR is open on `Pluneto/skills` and not merged, and the config-owner prompt for milestone 2 is in the report to the user.

**Skills:**
`engineering:tdd` - Need: the capture rules (marker, add, `#unpin`, cut at 9,500, sub-agent skip, thread key) are a behaviour list on one script with JSON in and text out; Provides: tests at the script's public seam with expected values from literals, one failing test before each slice; Without it: tests tied to internal helpers, or an add/clear rule that no test fixes and a later refactor breaks unnoticed.
`engineering:pr` - Need: the PR must carry the three-compaction result as its proof; Provides: the Summary / Evidence / Merge Danger body with a before and after; Without it: a PR whose reviewer cannot see that the text returned after each compaction.
considered `skill-tools:writing-for-agents`, skipped: the injected text is two fixed sentences, and its one rule (factual wording) is already a constraint of this plan.

### Milestone 2: live on the box

**Outcome:** the plugin runs in every Claude Code thread on the box, and a real T3 thread proves it.

**What constrains it**

- Starts only after the user merged the PR (or gave "merge if") and pasted the config-owner prompt. That prompt, written in milestone 1, says: after the merge, refresh the `pluneto-skills` marketplace (`claude plugin marketplace update pluneto-skills`), then run `claude plugin install pin@pluneto-skills --scope user` once under each of the box's two config folders; risk low; with the README line that explains `#pin` and `#unpin`. Enabling alone is not enough: a plugin must be installed first.
- The builder changes no box settings itself.
- A plugin enabled after a session started does not load in that session: the check needs a new thread.

**Done when**

- `claude plugin list` shows `pin` enabled at user scope under both config folders.
- In a new T3 thread in the sandbox project (it does not enable the plugin itself): a message with `#pin` and a probe rule gets a one-line confirmation; after two compactions the reply still obeys the rule, and the thread's transcript shows the injected text after each compaction; after `#unpin` and one more compaction nothing is injected.
- The report to the user gives the usage line: put `#pin` on its own line above the instructions; `#unpin` clears them.

**Skills:** none fit.

## Build log

- Build gate (before M1): pass - in a T3-style session `UserPromptSubmit` delivers the raw message (multi-line, and starting with a skill or unknown slash command); built-in `/compact` and `/help` never reach it; `SessionStart` fires with source `compact` after `/compact`.
- M1 the `pin` plugin, built and proven (orchestrator, with sonnet sub-agents for the trial and the review): check pass - 30 unit tests and `scripts/validate` green; three-compaction run byte-exact at 3 boundaries (manual, manual, auto), combined run with `t3code` complete (6,240 + 6,259 units, sum 12,499); PR #33 open, not merged; deviations: `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` works, `autoCompactWindow` or its env twin below 100,000 does not, so the trial sets window 100,000 plus a 20% override with no MCP servers; the trial also loads `workflow` because `t3code` depends on it; pin files are written and read as bytes so CRLF survives; owed: milestone 2 (merge, config-owner prompt, real-thread check)

## Risks and assumptions

- **`UserPromptSubmit` under T3 Code is unverified.** The docs say the same hook events fire on every surface, but nobody tested that T3 Code's messages reach the hook as raw text. Mitigation: the build gate at the start of milestone 1, which stops the build when it fails.
- **Two plugins inject on the same event.** In projects with `t3code`, its live-state injection and the pin both arrive after a compaction. Assumption to confirm: each hook's output has its own cap. Mitigation: the second run in milestone 1's Done when.
- **Pin files are never deleted automatically.** They are a few kilobytes per thread. Accepted: an expiry could erase the only copy of a dormant thread's pin.
- **The loss itself was never measured** (decision 4). In the planning thread, the first compaction kept the user's three rules word for word. The pin may turn out to protect against a rare event; its cost is one small script.
- **Any message that arrives as a user prompt can pin**, including one that another agent sends to the thread. Accepted: that message could give the same instructions without a pin.
- **A line that is exactly `#pin` in pasted material pins what follows it.** Accepted; `#unpin` undoes it.
- **A forgotten marker pins nothing, without a warning.** Accepted with decision 1.
- **A forked thread or a new session id outside T3 Code starts without the pin.** Accepted; the user pastes again.
- **Codex threads stay unprotected** (decision 3). Follow-up if the loss shows up there: Codex 0.172.0 documents the same two hook events.
- **Pasting stays** (decision 6): the pin keeps rules alive, it does not shorten the paste.
