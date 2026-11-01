# Coverage map

Checks that a feature serves the people it is for: features → ranked user-types → their Must-needs, as a plain table. Uncovered Must-needs are findings. Needs `PRODUCT.md` at the repo root (or a legacy `UX/User_Types.md`, read the same way).

1. **Read the user-types.** Rank, access level, contexts and requirement IDs for each. With no such file, add a Major finding: "No user-types: run product-context (Draft) before planning this feature", carry on with the target users the goal names, and mark the map "provisional".
2. **List the features.** Split a feature when user-types need different access to parts of it ("view attendees" vs "edit attendees"); merge when splitting adds nothing.
3. **Match the users.** For each feature, the user-types who touch it: those the goal names, plus those who plainly will (the admin who configures it, the system that syncs it), marked *suggested*. A target user with no matching type is an Open question: add it through product-context, or map it to an existing type.
4. **Build the table**, rows in feature order, types in rank order:

   | Feature | User-types (rank) | Serves | Access |
   |---|---|---|---|
   | View attendees | UT-03 Organiser (1), UT-01 Visitor (2) | UT-03-M2 | Elevated; Anonymous sees count only |

5. **Find the gaps.** For each touched type, each Must-need this feature plausibly bears on is either served (by which feature) or uncovered.
   - Uncovered Must of a target type: **Blocker**.
   - Uncovered Must of a suggested type, or a feature that breaks a Won't: **Major**.
   - Where two types' needs conflict, the higher rank wins; name the conflict and the losing need in the finding.
6. **Walk the journeys** of the top-ranked target types through [ui-interaction.md](ui-interaction.md) "Flows and journeys" (outcomes and context variants), when the feature has a UI or a bot.

Put the table in Findings (or a **Coverage** block right after Findings), and one Check for Done when per served Must, citing its ID: "UT-03-M2: an organiser sees the live attendee count on the event page."
