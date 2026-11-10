# Fix ladder

What an orchestrator does when it has to wait on CI, run a predictable check, or repair something red: it **coordinates**, and children do the waiting, testing and fixing, so logs and diffs stay out of its context. Read by build-this, solve-this, dispatch and t3-orchestration. A **rung** is one child's attempt; the ladder climbs light → standard → strong, then ends.

## Tiers

| Tier | Job | Claude | Effort |
|---|---|---|---|
| light | run a check, triage a red run | Haiku | medium |
| standard | first fix attempt | Sonnet | medium |
| strong | second fix attempt | Opus | medium |

Use family names, never version numbers. On another provider, take its tiers from the tracker doc's **Model tiers** line, else its smallest, default and largest models. Start each child the caller's way: on T3, `delegate_task` per **t3-orchestration** (`target.model`, effort in `target.options`); elsewhere a sub-agent (the Agent tool with model `haiku`, `sonnet` or `opus` and that effort). With no child tool, climb the rungs yourself.

## Waiting costs no tokens

No child or loop sits idle on CI.
- **A PR on T3:** `watch_pull_request`; the completion wakes you.
- **Anything else** (a PR elsewhere, a run on the default branch): find the run (`gh run list --branch <branch> --limit 1`, or `gh run list --commit <sha>` for a merge commit), start `gh run watch <run> > /dev/null` as a background command, and when it completes read `gh run view <run> --json conclusion,headSha`. Its exit code proves nothing; `conclusion` on the expected `headSha` does.

Green ends the wait. Red, or any conclusion besides success, skipped and neutral, goes to the light child.

## The light child

Two jobs, one report:
- **Run a check:** a milestone's done-when command or a predictable test suite, in the checkout it names. The orchestrator takes the report as its evidence instead of reading the output.
- **Triage a red run:** read `gh run view <run> --log-failed` (or the failing check's output) and name the cause.

Its brief: the command or run URL, the checkout path, one line of what it guards, "change nothing, run only what is named, ask nothing", and this reply, at most 150 words:

```
Check: <command or run URL> -> exit <code> | <conclusion>
Verdict: pass | real failure | likely flaky
Cause: <one line, or none>
Files: <likely files, or none>
Output: <the last lines of the failing output, up to 10>
```

**Likely flaky** means infra, a network or runner error, a timeout, or a test that passes on a local re-run. A likely flaky run gets `gh run rerun <run> --failed` once, then the wait again; red a second time is a real failure.

## Fixer rungs

A real failure goes to a **standard** fixer; if the check is still red after its report, a **strong** fixer gets the same brief with the standard rung added to "Already tried". Each rung gets one attempt, a fresh child that sees only this brief:

```
You are the <standard|strong> fixer on a fix ladder: make <check command or run URL> green.
Checkout: <path>, branch <branch>. You own: <files or area>; change nothing outside it.
Intent: <the milestone, ticket or PR this guards, one line>
Failure: <the light report, verbatim>
Logs: gh run view <run> --log-failed   (or: <check command>)
Already tried: <each earlier rung: what it changed, its commit, the result; or none>

Rules:
- Fix the cause in the code. Tests, fixtures and CI config keep their meaning: get green by making the code right, never by skipping, deleting, loosening or retry-wrapping a test or job.
- Run <check command> yourself until it passes, then commit locally (`fix: <one line>`); push only when told: <push instruction, or "do not push">.
- Ask no questions. Stop before anything hard to undo or outside the checkout.

Reply in at most 150 words:
Status: fixed | not fixed
Check: <command> -> exit <code>
Cause: <one line>
Changed: <files>   Commit: <sha, or none>
Tried: <one line for the next rung>
```

After a rung reports, the orchestrator confirms with the light child (re-run the check, or wait on the new CI run and triage it). Green: done, log the rung. Red: next rung.

**Review before it lands.** A fix commit gets the same review as the work it repairs, at most 2 rounds: review-this in build-this, the worker prompt's reviewer step in dispatch. A fix the review rejects counts as that rung failing.

**Where a fixer runs.** A milestone or PR fixer works in the checkout the failure lives in, and only while no builder child is running there (build-this children run one at a time, so between them). A main fixer always gets its own checkout (below).

## Red main

A red run on the default branch, after a merge or seen by anyone, gets exactly one fixer. The `Main is red` issue is the lock:

1. **Find the canonical issue** by listing every open issue (search is indexed and can miss a new one):
   `gh api --paginate 'repos/{owner}/{repo}/issues?state=open&per_page=100' --jq '.[] | select(.pull_request == null and (.title | startswith("Main is red"))) | .number' | sort -n | head -1`
   None: open `Main is red: <short sha>` with the run URL, then list again. The lowest open number is canonical; close any other with a comment linking it.
2. **Claim it** with the tracker doc's Claim (no doc: the defaults in [no-tracker-doc.md](no-tracker-doc.md)). Lost: comment your run URL there and wait for it to close.
3. **Re-check:** list again; launch a fixer only if your claimed issue is still the lowest open one, else release it and treat step 2 as lost.
4. **Fix** up the ladder in a fresh checkout from `origin/<default>` on branch `t3/fix-main-<short sha>` (on T3, `isolation: worktree` or dispatch's worktree strategy; elsewhere `git worktree add`). The fixer pushes and opens a PR titled `Fix main: <short sha>` whose body says `Fixes #<issue>`.
5. **Land** only with a merge go-ahead already in hand: a dispatch chain's `merge if green`, a "merge if" in the user's prompt, or the repo owner's rule. Without one, report the green PR for the user and stop.
6. **Confirm:** the light child triages the default branch's run on the merge commit. Green: comment `released: done in #<pr>` on the issue. Red: reopen the issue and climb to the next rung.

**Every agent that merges** (a worker, a fixer, build-this landing a ticket) waits for the default branch's run on its merge commit and triages it before reporting done; red starts this section.

## The end

When the strong rung fails, the ladder is exhausted and that failure is **blocked**: put the last light report and each rung's "Tried" line in the Build log or report (on red main, as a `blocked:` comment on the issue too), and stop climbing. Nothing restarts the ladder for that failure except the user.
