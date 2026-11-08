# Briefs

What review-this sends its reviewer. Fill the `<...>` fields, drop lines for another target, send the block as is. Each brief carries the severity rules and reply format, which you also use to re-grade findings.

## Round 1: code or implementation

```
Review only. Read files and run read-only commands as you need. Change nothing: write no files, make no commits, pushes or PR comments, and start no sub-agents or other reviewers.

Repo: <absolute path>   Base: <sha>   Paths: <paths, or "all changed">
Intent: <1-2 sentences>
Out of scope: <1-2 sentences>
Checks: <each command and its result; missing or already-failing checks named>
[Implementation only] Plan: <path>. Review the diff against the plan's steps and Done-when lines: a requirement it misses or gets wrong is a finding; work the plan doesn't ask for is a nit with "Fix: remove".

Read the surrounding code and its callers. Find bugs, broken callers and mismatches with the intent. Comment on style only when it hides a bug. Hold the change to the smallest one that meets the intent: flag code, tests or guards the intent doesn't need.

Severity:
- blocker: the intended case is wrong.
- should: a real bug callers will hit, within the intent.
- nit: everything else (other paths, rare cases, small performance costs, extra compatibility).

Reply in this format and nothing else, one line per finding, ids S1, S2, ... kept for later rounds:
VERDICT: APPROVE | CHANGES
S<n> [blocker|should|nit] <file>:<line> <claim>. Fix: <suggestion>
APPROVE means no blocker or should remains.

## Diff
<the diff, then each untracked file in full under its path>
```

## Round 1: plan

```
Review only. Read any project file to check the plan's claims, and run read-only commands as you need. Change nothing: write no files, make no commits, pushes or PR comments, and start no sub-agents or other reviewers.

You are reviewing an implementation plan before it is built. You did not write it. Find what would make the build fail or deliver the wrong thing.

Repo: <absolute path>   Plan: <path>
Request (the user's words): <request>
Out of scope: <1-2 sentences>

Look for:
1. Gaps: something the goal needs that no milestone covers; something only the user can supply that the plan doesn't list.
2. Errors: decisions, steps or constraints that contradict each other; claims about the project or its tools that are false (paths, commands, APIs, versions, what a file contains).
3. Checks: a milestone whose "Done when" is missing, vague, or needs a human when it could be automated.
4. Order and risk: a milestone that depends on a later one; a hard-to-undo step with no safeguard; a major risk with no mitigation.

The user made the plan's decisions. Challenge one only when it rests on a false fact or contradicts another, and begin that finding's claim with "needs decision:". Skip style and wording. The goal is the scope: make each Fix the smallest change that solves the problem within it. List ideas that add features, options or work beyond the goal under a final "Out of scope" heading, one line each, not as findings.

Severity:
- blocker: the build would fail or deliver the wrong thing.
- should: a real gap or error the build will hit, within the goal.
- nit: everything else.

Reply in this format and nothing else, one line per finding, ids S1, S2, ... kept for later rounds:
VERDICT: APPROVE | CHANGES
S<n> [blocker|should|nit] <plan section or milestone> <claim>. Fix: <suggestion>
APPROVE means no blocker or should remains.

## Plan
<the plan text>
```

## Follow-up round

The session already holds round 1. A fresh fallback sub-agent after a failed CLI gets the round-1 brief above this one.

The change since the last round is `diff -u "$dir/diff-<n-1>.patch" "$dir/diff-<n>.patch"` (plan: `diff -u "$dir/plan-<n-1>.md" "$dir/plan-<n>.md"`).

```
Round <n>. Same rules, severity and reply format as round 1. Still change nothing and start no sub-agents.

Ledger:
fixed: S<n> - <what changed, file:line>
disagree: S<n> - <evidence: file:line, test, output>
declined: S<n> - <one-line reason>

Check only the open ids and the changed code. Mark each earlier id on its own line as "S<n> resolved" or "S<n> still open: <reason>", then list new findings with new ids, after the last one used.
VERDICT: APPROVE | CHANGES
S<n> resolved
S<n> still open: <reason>
S<n> [blocker|should|nit] <file>:<line> <claim>. Fix: <suggestion>

## Change since last round
<the diff -u output>

## Current diff
<the current diff (plan: the current plan text)>
```
