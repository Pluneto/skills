# Design contract

<!-- Kept identical in every design skill (scripts/validate PAIRED): edit all copies. -->

Shared by product-context, design-review and ui-craft, so the workflow skills can run them unattended.

## Who decides

The design skill decides nothing that is the user's to decide. Each such choice becomes an **Open question**, resolved by whoever called the skill:

- **plan-this** (or interview) is running: return the Open questions. They become frontier decisions in its interview.
- **build-this, solve-this, or any unattended run**: take the recommended option, note it as `Assumed: <choice> (<why>)` in the output, and carry on.
- **The user typed the skill** and no workflow skill is running: after the output, hand the Open questions to the **interview** skill as its frontier, then finish the work with its answers (for product-context, Apply). Without interview, end the turn on the numbered Open questions.

Facts you can look up (in the repo, the docs, the code) are never Open questions: look them up. A choice with one sensible answer is an assumption: state it under Assumptions instead.

## Files

- **While planning, write nothing.** Return the content; plan-this folds it into the plan.
- **product-context** Apply writes `PRODUCT.md` at the repo root.
- **design-review** writes `plans/<topic>-design.md` only when its caller has no plan to fold the review into.
- **ui-craft** writes the UI it builds.

## Output shape

Use these sections in this order, skipping any that don't apply, scaled to the ask (a quick question gets a verdict and a line or two):

1. **Verdict**: one short paragraph. Is the approach right? If a different one is better, say so here.
2. **Assumptions**: what you took as given, flagging the ones that would flip the verdict.
3. **Alternatives**: materially different options, the pick, and what would make you switch.
4. **Findings**: ordered by severity, each with its evidence and a concrete fix.
   - **Blocker**: correctness, security, data loss, a Must-need left uncovered, a flow some users can't complete.
   - **Major**: a one-way door chosen casually, fails at the target load or horizon, an accessibility failure, a missing state (empty, loading, error).
   - **Minor**: friction, inconsistency, polish.
5. **Decisions for the plan**: rows ready for a plan's Decisions table (`Decision | Choice | Why`).
6. **Checks for Done when**: concrete, checkable statements a milestone can carry as its done-when ("two concurrent purchases of the last place: exactly one succeeds", "every action reachable by keyboard").
7. **Open questions**: in this format, recommended option first:

```markdown
### Open questions

1. <The question, with the one fact that makes it matter>?
   - **<Option> (Recommended)**: pro <one line>; con <one line>.
   - **<Option>**: pro <one line>; con <one line>.
```

Write only questions whose answer changes the design, at most four per run, most consequential first. With none, write `### Open questions` and `None.`

## IDs

User-type and requirement IDs (`UT-03`, `UT-03-M2`, `BL-M1`) are permanent: code, migrations and plans cite them. Never renumber or reuse one; new ones take the "Next user-type ID". Before rewording, editing or dropping an ID, grep the repo for it (`grep -rn "UT-03"`) and list every hit in Findings.
