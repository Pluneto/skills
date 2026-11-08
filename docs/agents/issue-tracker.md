# Issue tracker: GitHub

Tickets and wayfinder maps for this repo live as GitHub issues. Plans stay as files under `plans/`. Use the `gh` CLI for every operation; it infers the repo from `git remote -v`.

## Labels

Skills name a **role**; apply the label in the "Label in this repo" column.

| Role | Default label | Label in this repo | Meaning (read by) |
|---|---|---|---|
| map | `wayfinder:map` | `wayfinder:map` | A wayfinder map issue (wayfinder) |
| research | `wayfinder:research` | `wayfinder:research` | Wayfinder ticket: find something out (wayfinder) |
| prototype | `wayfinder:prototype` | `wayfinder:prototype` | Wayfinder ticket: a throwaway build that answers a question (wayfinder) |
| interview | `wayfinder:interview` | `wayfinder:interview` | Wayfinder ticket: the user decides (wayfinder) |
| task | `wayfinder:task` | `wayfinder:task` | Wayfinder ticket: a piece of work on the way (wayfinder) |
| agent | `ready-for-agent` | `ready-for-agent` | Fully specified; an agent can build it unattended (to-tickets, build-this, dispatch) |
| human | `ready-for-human` | `ready-for-human` | Needs the user: a console step, a decision, a physical action (to-tickets, build-this, dispatch) |
| claim | `in-progress` | `in-progress` | A worker holds this ticket (Claim, Release, dispatch's stale-claim list) |
| decision | `needs-decision` | `needs-decision` | A worker parked this ticket on a question only the user can answer (dispatch's worker prompts and `status`) |

Every ticket from to-tickets carries exactly one of the agent and human labels.

## Conventions

- **Target repo**: before the first `gh issue create` of a session, run `gh repo view --json nameWithOwner`. In a fork, `gh` can default to the upstream parent; when the name is not the user's repo, confirm with the user before creating anything.
- **Create an issue**: `gh issue create --title "..." --body "..." --label "<label>"`, with a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <n> --json number,title,body,labels,comments`.
- **List issues**: `gh issue list --state open --json number,title,labels` with `--label` and `--state` filters.
- **Sub-issue of a parent**: `gh issue create --parent <parent> ...`, or `gh issue edit <parent> --add-sub-issue <child>` (gh 2.94+). Without sub-issues, put `Part of #<parent>` at the top of the child body.
- **Blocking**: GitHub's native issue dependencies. `gh issue create --blocked-by <n>,<n> ...` or `gh issue edit <child> --add-blocked-by <blocker>` (gh 2.94+). Older gh: `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, where the database id comes from `gh api repos/<owner>/<repo>/issues/<n> --jq .id` (not the `#number`). Where dependencies aren't available, a `Blocked by: #<n>, #<n>` line at the top of the body. A ticket is unblocked when every blocker is closed.
- **Count open blockers**: `gh api repos/<owner>/<repo>/issues/<n> --jq .issue_dependencies_summary.blocked_by` (0 means startable). `gh issue view <n> --json blockedBy` also lists closed blockers; filter it with `--jq '[.blockedBy.nodes[] | select(.state == "OPEN")] | length'`.
- **Comment**: `gh issue comment <n> --body "..."`.
- **Labels**: `gh issue edit <n> --add-label "..."` / `--remove-label "..."`.
- **Close**: `gh issue comment <n> --body "..."`, then `gh issue close <n>` (on an already-closed issue, `gh issue close --comment` drops the comment and still exits 0).

## Claim

One way to hold a ticket, used by every skill and worker (wayfinder too). Labels have no compare-and-set, so the **claim comment** decides, not the label: the earliest `claimed by` comment since the last `released:` comment wins. Only comments from the owner, members and collaborators count, so outsiders on a public repo can neither claim nor release.

**Winner command** (prints the winning claim's URL, or an empty line when the ticket is free):

```sh
gh issue view <n> --json comments --jq 'reduce (.comments[]
    | select(.authorAssociation | IN("OWNER","MEMBER","COLLABORATOR"))) as $c (null;
  if ($c.body | startswith("released:")) then null
  elif . == null and ($c.body | startswith("claimed by ")) then $c.url
  else . end)'
```

1. **Check it is free**: `gh issue view <n> --json state` says `OPEN` and the winner command prints an empty line. Otherwise stop: someone else holds it.
2. **Claim**: `gh issue comment <n> --body "claimed by <branch>"`, and note the comment URL it prints (your claim's identity, since two claims can have the same text); then `gh issue edit <n> --add-label "<claim label>"`. The comment goes first, so a crash in between leaves a claim that Release can clear, not a bare label.
3. **Confirm**: wait 10 s (a rival's comment can take a moment to show), then run the winner command. Done when it prints your claim's URL: you hold the ticket. Any other URL means you lost: stop, change nothing, leave the label (the winner holds it), and report the winning comment.

## Release

Every claim ends with a `released:` comment, so a reopened issue is free again.

- **Done**: the PR body says `Fixes #<n>`, so merging closes the issue. Then `gh issue comment <n> --body "released: done in #<pr>"` and `gh issue edit <n> --remove-label "<claim label>"`.
- **Abandoned or stale** (the worker stopped, or dispatch lists the claim as stale): `gh issue comment <n> --body "released: <reason>"`, then `gh issue edit <n> --remove-label "<claim label>"`.

## Parallel work

Read by dispatch and by its worker prompts. A blank field uses the fallback in brackets.

- **Max workers**: 5
- **Land command**: [blank: push the branch, open the PR with `Fixes #<n>`, watch CI, merge per the repo owner's rule]
- **Land status command**: [blank: `gh pr checks <pr>`, re-run every few minutes until no check is pending; "no checks reported" means the repo has no CI, so treat it as green]
- **Areas map**: `docs/agents/areas.md` [missing: dispatch infers areas from the issues and `git log --name-only`]
- **Model tiers**: [blank: each provider's default model; dispatch still suggests the effort]. One line per T3 provider, its `light / standard / strong` models by their T3 model ids, for example `Codex (pool): <light> / <standard> / <strong>`. List only models the subscription behind that provider serves; one model may fill several tiers.
- **Verify command**: [blank: the check commands are the verification]. What a worker runs before opening its PR to prove the change, and the command that reports its result, for example a land script's dry run and its status command.
- **Review command, Codex reviewer** (reviews Claude workers): [blank: no pre-PR review; the PR says "Review: none configured"]. `<dir>` holds `input.md` (instructions, issue, diff) and gets `review.md`; dispatch fills `<dir>`, `<model>` and `<effort>`. On T3 with the pools: `CODEX_HOME=~/.codex-pool codex exec --ephemeral --skip-git-repo-check -s read-only -C <dir> -m <model> -c 'model_reasoning_effort="<effort>"' -o <dir>/review.md - < <dir>/input.md`
- **Review command, Claude reviewer** (reviews Codex workers): [blank: as above]. On T3 with the pools: `cd <dir> && CLAUDE_CONFIG_DIR=~/.claude-pool claude -p --model <model> --effort <effort> --tools "" --no-session-persistence < input.md > review.md`
- **Main health command**: used only without a Land command (a land script checks main itself). [blank: prints `green`, `pending` or `red <run url>` for the newest commit on the default branch: `gh run list --branch <default branch> --event push --limit 20 --json headSha,status,conclusion,url --jq '(.[0].headSha) as $s | [.[] | select(.headSha == $s)] | if any(.status != "completed") then "pending" elif all(.conclusion == "success" or .conclusion == "skipped" or .conclusion == "neutral") then "green" else "red " + ([.[] | select(.conclusion != "success" and .conclusion != "skipped" and .conclusion != "neutral") | .url][0]) end'`]
- **Decision owner**: [blank: the repo owner's login]. The GitHub login a parked worker mentions (`@<login>`) so the person who makes product calls gets the notification; set it when a machine account owns the repo.
- **Model database**: [blank: Model tiers for every ticket]. A command that prints the table of task type, rank, provider, model, effort and evidence that dispatch picks workers from, for example `gh api repos/<owner>/<repo>/contents/models.md --jq .content | base64 -d`.

## When a skill says "publish to the issue tracker"

Create a GitHub issue. A to-tickets ticket gets the agent or human label; a wayfinder ticket gets the label of its type instead.

## When a skill says "fetch the relevant ticket"

Read it as in **Read an issue**.

## Wayfinding operations

Used by `/wayfinder`. The map is one issue with child issues as tickets.

- **Map**: an issue with the map label (`gh issue create --label "<map label>"`).
- **Child ticket**: a sub-issue of the map, with the label of its type (research, prototype, interview, task).
- **Frontier**: the map's open children with no open blocker (see **Count open blockers**, or every issue in the `Blocked by` line is closed) and no live claim (the winner command prints an empty line); first in map order wins.
- **Claim**: as in **Claim**, the session's first write; then `gh issue edit <n> --add-assignee @me` so the issue shows who drives it.
- **Resolve**: `gh issue comment <n> --body "<answer>"`, `gh issue close <n>`, `gh issue comment <n> --body "released: resolved"`, then append a context pointer (gist + link) to the map's Decisions so far.
