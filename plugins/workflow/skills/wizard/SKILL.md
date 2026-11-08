---
name: wizard
description: Generate an interactive bash wizard that walks a human through steps only they can perform. Use when provisioning infrastructure, setting up credentials or CI secrets, walking an unfamiliar third-party dashboard, or running a one-off migration or cutover. Don't invoke this for steps the agent can perform itself.
---

# Wizard

A **wizard** is a bash script that walks a human, step by step, through a manual procedure that's tedious by hand and tedious to re-explain to an AI: it opens each URL, says exactly what to click and copy, captures the values, writes them where they belong (`.env`, GitHub secrets), confirms at every stage and shows how many are left. It might configure third-party services or run a one-off migration.

[template.sh](template.sh) already solves the UX: progress, confirmation gates, cross-platform URL opening (including WSL), hidden secret entry, idempotent `.env` upserts, `gh secret`/`gh variable` writes, a closing summary. **Your job is only to scope the procedure and author its stages.** The library above the `STAGES` marker is identical in every wizard: never hand-edit it.

A wizard is ephemeral by default: saved to a scratch or `scripts/` path and deleted when the job is done. Commit it only when the user wants a repeatable setup path in the repo.

## Process

### 1. Scope the procedure

Work out every manual step the human must take and every value captured. Read the repo first, don't ask cold:

- For setup: `.env`, `.env.example`, `.env.*`, `README`, `docker-compose*`, framework config, and `.github/workflows/*` (every `secrets.*` / `vars.*` reference is a value the wizard must produce).
- For a migration or transition: the current state, the target state, and the irreversible actions between them.

Then show the ordered stages and the values each produces, and confirm: the user may add, drop or reorder.

**Done when:** every stage is named in order, and for each captured value you know (a) where the human gets it, (b) where it's written (`.env`, a GitHub secret, both, or nowhere; some stages are pure actions), and (c) whether it's secret (hidden entry) or public.

### 2. Map each stage's journey

For each stage, write the precise path a human follows: the URL, what to do there, where a value is shown, which variable it fills ("Dashboard → Developers → API keys → Reveal test key → copy"). Where you don't know the current UI or exact command, ask the user or check the docs; never invent steps.

**Done when:** every stage traces to concrete instructions a stranger could follow.

### 3. Author the wizard

Copy `template.sh` to the target path. Replace the example stage with one `stage` per step, in dependency order. Use the library helpers: `stage`, `say`/`step`, `open_url`, `ask`/`ask_secret`, `write_env`, `set_secret`/`set_var`, `pause`/`confirm`. Set `TOTAL_STAGES` to the number of stages you wrote.

Hold the template's bar: open the URL before asking for its value, `ask_secret` for anything secret, `write_env` every persisted value, `set_secret` only values CI needs, `confirm` before any irreversible action. Each `stage` clears the screen, so keep a stage to one focused task. Leave the library above the marker alone.

### 4. Verify and hand off

- `bash -n <script>`; run `shellcheck` if available.
- `chmod +x <script>`.
- Don't run it end-to-end: it opens browsers and blocks on human input. Trace it statically: every value from step 1 is captured and lands where step 1 said, and every `set_secret` name exactly matches a `secrets.*` reference in CI.
- Tell the user how to run it. A repeatable setup path is committed and linked from the README.
