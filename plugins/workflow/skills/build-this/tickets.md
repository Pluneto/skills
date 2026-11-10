# Working tickets and issues

Tickets come from /to-tickets as local files (`plans/<feature>/tickets/`) or GitHub issues, or are issues the user names (`build #12 #14`, issue URLs). Work them by `docs/agents/issue-tracker.md` (Claim, Release and Parallel work), or without it by the defaults in [no-tracker-doc.md](no-tracker-doc.md). Each ticket is a milestone; its acceptance criteria are its done-when check.

- **Read** each ticket whole (the file, or `gh issue view <n> --comments`), plus the plan or parent issue it was split from.
- **Order:** blocker order; a ticket starts once everything in its `Blocked by` is done. When the user named the issues, they are the set: an open blocker outside it holds its ticket back, and you report it.
- **Human tickets** (the human label, or `Who: human`) are the user's: skip them, work every agent ticket they don't block, and list each with what it needs.
- **Claim** each ticket before its first change, as the tracker doc's Claim says. On a lost claim, leave that ticket and the ones it blocks, and report the winning claim.
- **Finish** when the check passes. On GitHub, open the PR with `Fixes #<n>` in its body and wait for green CI per [fix-ladder.md](fix-ladder.md). Merging publishes, so land it (the doc's Land command, polling its status command, or the blank field's fallback) only when the user said so, for example "merge if green"; then triage the run on the merge commit (fix-ladder.md) and release as the doc's Release (Done) says. Without that go-ahead, list the green PRs under "What's left for you" and keep the claims. Locally, set `Status: resolved`.
- **Resume:** a resolved local ticket or closed issue is done. A ticket with an open PR from an earlier run awaits its go-ahead: list it, don't rebuild it.
- **Children mode:** you claim each ticket before launching its child and finish it after re-running its check yourself, since claims, PRs and landing need the tracker doc's commands and the user's go-ahead. The child builds (and, if a T3 child, reviews and commits); you claim, open the PR and land. Fill the brief's ticket line so the child reads the ticket itself.
- **Progress record:** the ticket's status is its tick. Build log lines go in the plan file the tickets were split from; without one, under a `## Build log` heading in the ticket's own file, or as a comment on the issue.
