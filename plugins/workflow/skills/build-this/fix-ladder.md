# Fix ladder

How an orchestrator waits on CI, runs predictable checks and repairs red while it only **coordinates**: children read the logs and diffs, so they stay out of its context. A **rung** is one child's attempt: light → standard → strong.

| Tier | Job | Claude |
|---|---|---|
| light | run a check, triage a red run | Haiku |
| standard | first fix | Sonnet |
| strong | second fix | Opus |

All at medium effort.

On another provider, use the tracker doc's **Model tiers** line, else its smallest, default and largest models. On T3, start children per **t3-orchestration**; elsewhere as sub-agents. With no child tool, climb the rungs yourself.

## Waiting

Waits run in the background. A PR on T3: `watch_pull_request`. Otherwise run `gh run watch <run> > /dev/null` as a background command (find the run with `gh run list --branch <branch> --limit 1`, or `--commit <sha>`), then read `gh run view <run> --json conclusion,headSha`; its exit code proves nothing. A PR is green only when `gh pr checks <pr>` shows every check passed ("no checks reported": no CI, green).

## Light child

It runs a done-when check or test suite, or triages a red run (`gh run view <run> --log-failed`), changing nothing. Brief: the command or run URL, the checkout, what it guards, and this reply (at most 150 words):

```
Check: <command or run URL> -> exit <code> | <conclusion>
Verdict: pass | real failure | likely flaky
Cause: <one line>   Files: <likely files>
Output: <last lines of the failing output, up to 10>
```

**Likely flaky** (runner, network, timeout, passes on a local re-run): `gh run rerun <run> --failed` once; red again is real.

## Fixer rungs

A real failure goes to a fresh **standard** fixer; still red, a fresh **strong** one gets the same brief with the standard rung under "Already tried". Each rung starts on a clean checkout (commit pending work first); note HEAD before it.

```
You are the <standard|strong> fixer: make <check command or run URL> green.
Checkout: <path>, branch <branch>. You own: <files or area>.
Intent: <milestone, ticket or PR, one line>
Failure: <the light report>
Logs: gh run view <run> --log-failed
Already tried: <each earlier rung: change, commit, result; or none>
Rules: fix the cause in the code; tests, fixtures and CI config keep their meaning (no skipping, deleting, loosening or retry-wrapping). Run the check until it passes, commit locally as `fix: <one line>`, push only if told: <push rule>. Ask nothing; stop before anything hard to undo.
Reply in at most 150 words:
Status: fixed | not fixed   Check: <command> -> exit <code>
Cause: <one line>   Commit: <sha, or none>
Tried: <one line for the next rung>
```

Then the light child confirms (re-run the check, or triage the new CI run). Green: log the rung.

**Review** the rung's commits (base: HEAD before it) as the repaired work is reviewed, at most 2 rounds: review-this in build-this, the reviewer step in dispatch's worker prompt. Until approved they count as uncommitted edits: nothing is pushed or built on them. A failed rung (not fixed, still red, or rejected) is undone before the next: `git reset --hard <HEAD before it> && git clean -fd`.

**Where.** A milestone or PR fixer works in the failure's checkout, never while a builder child runs there.

## Red main

A red default-branch run gets exactly one fixer; the `Main is red` issue is the lock.

1. **Find the canonical issue** by listing (search can miss a new one): `gh api --paginate 'repos/{owner}/{repo}/issues?state=open&per_page=100' --jq '.[] | select(.pull_request == null and (.title | startswith("Main is red"))) | .number' | sort -n | head -1`. None: open `Main is red: <short sha>` with the run URL, `--type "<bug type>"` and `--label "<high label>"` (the tracker doc's **Issue types**), and list again (the listing lags too, so count your new issue in). The lowest number is canonical; close any other, linking it.
2. **Claim** it with the tracker doc's Claim (no doc: [no-tracker-doc.md](no-tracker-doc.md)); list again and go on only if it is still the lowest. Lost: comment your run URL there and wait.
3. **Fix** in a fresh checkout of `origin/<default>` on branch `t3/fix-main-<short sha>-<tier>`: dispatch's worktree strategy (`startFromOrigin: true`); on T3 otherwise `isolation: worktree`, whose child first runs `git fetch origin && git switch -c <branch> origin/<default>`; elsewhere `git worktree add -b <branch> <path> origin/<default>` after `git fetch origin`. The fixer reviews, pushes and opens `Fix main: <short sha>` with `Fixes #<issue>`.
4. **Land** only with a go-ahead already given: a chain's `merge if green`, a "merge if" in the prompt, or the repo owner's rule. Otherwise report the green PR and stop.
5. **Confirm**: the light child triages the run on the merge commit. Green: comment `released: done in #<pr>`. Red: reopen the issue, next rung.

**Every agent that merges** (worker, fixer, build-this landing a ticket) triages the run on its merge commit before reporting done; red starts this section.

## The end

When the strong rung fails, that failure is **blocked**: log the last light report and each rung's "Tried" line (on red main, also a `blocked:` comment on the issue) and stop. Only the user restarts it.
