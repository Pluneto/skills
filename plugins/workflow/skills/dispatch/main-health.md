# Main health

Dispatch's default **Main health command**: it prints `green`, `pending` or `red <run url>` for the commit at the head of the default branch. Dispatch uses it when the tracker doc's Main health field is blank or still holds an old generated default (text starting `[blank:`); a custom command in that field is used instead. Fill `<default branch>`; gh fills `{owner}/{repo}` from the checkout.

```sh
H=$(gh api repos/{owner}/{repo}/commits/<default branch> --jq .sha) && P=$(gh api 'repos/{owner}/{repo}/activity?ref=refs/heads/<default branch>&per_page=1' --jq '.[0] | "\(.after) \(.timestamp)"' 2>/dev/null); export H P; gh run list --branch <default branch> --event push --limit 50 --json headSha,status,conclusion,url,workflowName,createdAt --jq 'def failed: .status == "completed" and (.conclusion | IN("success", "skipped", "neutral") | not); def judge: group_by(.workflowName) | map(max_by(.createdAt)) | if any(failed) then "red " + (map(select(failed)) | .[0].url) elif any(.status != "completed") then "pending" else "green" end; ($ENV.P // "" | split(" ")) as $push | [.[] | select(.headSha == $ENV.H)] as $head | if ($head | length) > 0 then $head | judge elif ($push[0] != $ENV.H) or (now - ($push[1] | fromdateiso8601) < 120) then "pending" elif length == 0 then "green" else (max_by(.createdAt).headSha) as $s | [.[] | select(.headSha == $s)] | judge end'
```

How it reads main:

- **The head** is the branch's own SHA, never the newest run's: right after a merge, the new commit has no run for a few seconds, and the previous commit's green must not count.
- **A head with no run** is `pending` for 2 minutes after its push (push time from the repository activity API, used only when its `after` is the head; unknown push time stays `pending`). After that, commits CI skipped (path filters, `[skip ci]`) are judged by the newest commit that has runs.
- **Per workflow, only its newest run counts**, so a run cancelled by a newer one is ignored. Any failed run makes it `red`, even while others still run; `pending` only when nothing failed.

Tested by `scripts/test-main-health` in the skills repo.
