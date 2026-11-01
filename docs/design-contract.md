# Design contract (maintainers)

The rules every skill in the `design` plugin (product-context, design-review, ui-craft) follows, so that the workflow plugin can use them unattended. Reasons are in [design-audit.md](design-audit.md).

## Runtime copy

The part the skills read at run time is `contract.md` in each design skill's folder. The three copies are identical (`PAIRED` in `scripts/validate`): edit all three. It covers:

- **Who decides.** A design skill never questions the user itself. Every choice that is the user's goes into **Open questions**, and the caller resolves them: plan-this turns them into interview frontier decisions; build-this, solve-this or any unattended run takes the recommended option and logs it; when the user typed the skill and no workflow skill is running, the skill hands them to interview, then continues (Decision 9 of the plan).
- **Draft vs Apply.** Draft returns the proposed content and writes nothing. Apply writes the approved result. Planning only ever drafts.
- **Where files go.** Planning writes nothing. product-context Apply writes `PRODUCT.md` at the repo root. design-review writes `plans/<topic>-design.md` only when the caller has no plan to fold it into. ui-craft writes the UI it builds.
- **Output shape.** Verdict, Assumptions, Alternatives, Findings by severity, Decisions for the plan, Checks for Done when, Open questions, in that order, with sections that don't apply skipped.
- **Open questions format.** Numbered questions, recommended option first and marked, a one-line pro and con for each option: the interview skill's own format, so plan-this can pass them on unchanged.
- **IDs.** User-type and requirement IDs (`UT-NN`, `UT-NN-M1`, `BL-M1`) are never renumbered or reused. `PRODUCT.md` carries a "Next user-type ID" line. Before editing or dropping an ID, grep the repo for it and list every hit.

## No-asking gate

`scripts/validate` fails when any file under `plugins/design/` contains `AskUserQuestion`, "question tool", "ask the user", "ask which" or "ask only" (case-insensitive). Those are the wordings that made use-available-skills filter the 1.x skills out. Write the positive instead: "add it to Open questions", "state the assumption".

## Adding a design skill

Follow the contract: end with Open questions, write nothing while planning, use the shared output shape, copy `contract.md` into its folder and add it to the PAIRED group, add it to which-skill, and keep `scripts/measure-skills plugins/design` at or under 650 tokens.
