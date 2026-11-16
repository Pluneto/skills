# Fix ladder

How a red check or red CI gets repaired without the repair filling your context or weakening the check. A **rung** is one fresh attempt. Each rung gets more capable than the last: a cheap model to run and triage, a standard one for the first fix, the strongest available for the second. With no child agents, climb the rungs yourself.

## Waiting on CI

Wait in the background, not by polling in your context: `gh run watch <run> > /dev/null` (find the run with `gh run list --branch <branch> --commit <sha> --limit 1`), then read `gh run view <run> --json conclusion,headSha`; the watch command's exit code proves nothing. A PR is green only when `gh pr checks <pr>` shows every check passed on its latest commit; "no checks reported" means the repo has no CI.

## Triage

Run the check, or read the failing run (`gh run view <run> --log-failed`), changing nothing, and settle one of three verdicts: **pass**, **real failure** (with the cause in one line, the likely files and the last lines of output), or **likely flaky** (runner, network, timeout, passes on a local re-run). Re-run a flaky one once (`gh run rerun <run> --failed`); red again is real.

## Fixing

- Start each rung from a clean checkout (commit pending work first) and note HEAD, so a failed rung can be undone: `git reset --hard <that HEAD> && git clean -fd`.
- The fixer gets the intent in one line, the triage verdict, the logs and what earlier rungs tried. It fixes the **cause in the code**: tests, fixtures and CI config keep their meaning, so nothing is skipped, deleted, loosened or wrapped in retries to get green.
- Afterwards re-run the check. Green: have the rung's commits reviewed the way the repaired work is reviewed; until then nothing is pushed or built on them.
- One fixer works in a checkout at a time, never beside a builder.

## The end

When the strongest rung has failed, the failure is **blocked**: log the last triage verdict and what each rung tried, and stop climbing. The user restarts it.

## After a merge

Whoever merges triages the run on the merge commit before reporting done. A red default branch is repaired before anything else lands on it, by exactly one fixer.
