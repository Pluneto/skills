# Red main

A red default-branch run gets exactly one fixer; the `Main is red` issue is the lock. Only the fix merges while main is red.

1. **Find the canonical issue** by listing (search can miss a new one): `gh api --paginate 'repos/{owner}/{repo}/issues?state=open&per_page=100' --jq '.[] | select(.pull_request == null and (.title | startswith("Main is red"))) | .number' | sort -n | head -1`. None: open `Main is red: <short sha>` with the run URL, the tracker doc's bug type and high-priority label where it has them, and list again (the listing lags, so count your new issue in). The lowest number is canonical; close any other, linking it.
2. **Claim** it with the tracker doc's Claim, list again, and go on only if it is still the lowest. Lost: comment your run URL there and wait.
3. **Fix** in a fresh worktree thread from `origin/<default>` (`startFromOrigin: true`) on branch `t3/fix-main-<short sha>`. The fixer gets the run URL, `gh run view <run> --log-failed`, and the rule that the cause is fixed in the code: tests, fixtures and CI config keep their meaning. It gets its PR reviewed by a different model, pushes and opens `Fix main: <short sha>` with `Fixes #<issue>`. A fixer that fails is replaced once by a stronger model, told what the first tried; a second failure is **blocked**: comment `blocked:` with both attempts on the issue and tell the user.
4. **Land** the fix on its own green CI. A dispatch run is the go-ahead, unless the repo owner's rule asks for more.
5. **Confirm** on the merge commit's run. Green: comment `released: done in #<pr>` and tell waiting workers to land again. Red: reopen the issue and go to step 3's replacement.

Every worker that merges checks the run on its merge commit before reporting done; red starts here.
