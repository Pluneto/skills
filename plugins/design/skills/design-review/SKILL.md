---
name: design-review
description: Critique and shape a design while it is planned, or review an existing one - backend (architecture, data model, capacity, races and double-charge bugs, security), API contracts, UI flows, accessibility and UX copy, chat bots, and coverage of PRODUCT.md user-types. Challenges the approach itself and proposes alternatives. Use when planning or sanity-checking anything users or other systems touch, or asked "is this the right approach" or "will this hold up".
---

# Design review

Review like a sceptical senior designer who is paid to find what will hurt in a year, and who would rather replace the approach than polish a worse one. Mostly used while the work is still a plan, when changing it is cheap.

Read [contract.md](contract.md) first: who decides, the output shape, and where files go.

## Stance

- **Judge end states, not diffs.** For each significant decision ask: starting from zero today with these requirements, would I choose this? If not, say what you would choose and why, and recommend a different approach outright when its end state is better and not more complex to build and run (when it costs more, show the delta). Work already put into the plan is sunk cost. Patching a weaker design with add-ons (a cache here, a lock there, a tooltip over a confusing control) is the failure to avoid.
- **Complexity is a cost of the end state.** More components, screens or commands mean more failure modes and more to learn. Over-built plans deserve as much challenge as under-protected ones.
- **Specific and direct.** Open with the verdict. Every finding carries evidence from this work ("because X, at Y requests/s, Z happens"; "a screen-reader user can't reach the Save button because …"). When something is sound, say so in a line and move on.

## Domains

Work through every domain the design touches. Done when each touched domain's reference has been applied to the design.

| Domain | When the work has | Read |
|---|---|---|
| Backend | a server, data, storage, jobs, payments, capacity questions | [references/backend.md](references/backend.md) |
| API contracts | endpoints, webhooks, server actions, events or a CLI that other code or systems call | [references/api-contracts.md](references/api-contracts.md) |
| UI and interaction | screens, flows, forms, accessibility, UX copy | [references/ui-interaction.md](references/ui-interaction.md) |
| Converse | a chat bot, slash commands, Discord or Telegram messages, notifications people reply to | [references/converse.md](references/converse.md) |
| Coverage map | people use the feature and the repo has `PRODUCT.md` (or a legacy `UX/User_Types.md`) | [references/coverage-map.md](references/coverage-map.md) |

## Steps

1. **Read the input.** A goal, plan, spec, schema, architecture doc or codebase. With code, read it and search for the shapes the domain references name instead of reviewing the description alone. Look up every fact the repo can answer (scale hints, roles, existing patterns, the glossary). Done when what remains unknown is a list of assumptions.
2. **Challenge the requirements.** What must it do, for whom, and what does it cost when it misbehaves (a double charge, a leaked record, a member who can't sign up)? Separate real constraints from guesses; a few demanding requirements usually drive most of the complexity.
3. **Generate alternatives before judging.** Two or three materially different designs for the core of the problem, including the simplest that meets the requirements. Compare end states, pick one, and name what would make you switch.
4. **Apply each touched domain.** Correctness, security, data loss and flows some users can't complete outrank everything else, in every domain.
5. **Recommend a design, not only a list of faults.** If the best answer is a different approach, say so in the Verdict.
6. **Return** in the contract's output shape. Every Blocker and Major finding that a test, a command or a manual walk-through can verify gets a line in **Checks for Done when**. Assumptions that would flip the verdict and choices that are the user's become **Open questions**.

## Adjusting to the ask

- **Quick question:** answer from the one relevant domain, and still say whether the underlying approach looks right.
- **Existing system:** the same end-state comparison, but migration is a real cost. Give the ideal end state, the route to it (steps, risk, downtime, data moves) and a pragmatic fallback, so the cost of change is visible rather than a silent veto.
- **During a build** (a milestone's Skills line names this skill): review the milestone's work against the plan's Decisions and its Checks. Reopen an agreed decision only for a Blocker, and then as a finding with the nearest fix.
