---
name: product-context
description: PRODUCT.md, the repo's ranked user-types (role + goal) with MoSCoW needs under permanent IDs. Use when planning anything with users, roles or permissions and the repo has no PRODUCT.md, or to add, edit or rank user-types. Converts a legacy UX/User_Types.md.
---

# Product context

Keeps `PRODUCT.md` at the repo root: who the product is for, as **ranked user-types**. A user-type is a role + goal (what someone may do, and why they come); situations such as phone use or a screen reader are **contexts** on a type, never extra types. design-review checks coverage against these types, and plans, code and migrations cite their IDs.

Read [contract.md](contract.md) first: who decides, the output shape, and the ID rules. Read [references/file-format.md](references/file-format.md) before drafting, and [references/glossary.md](references/glossary.md) (about 30 generic user-types by product kind) when drafting new types.

## Modes

- **Draft** (the default, and the only mode while planning): return the proposed file and the Open questions. Writes nothing.
- **Apply**: write an approved draft. Runs when a caller says Apply (a plan milestone "Apply PRODUCT.md from Decisions …", or the standalone flow after interview), with the draft and the answers in hand.

## Draft

1. **Find what exists.** `PRODUCT.md` at the root means an update. Otherwise a `UX/User_Type*.md` means a legacy conversion (see Legacy). Otherwise it is new. Done when you know which, and for an update, which types the goal touches.
2. **Gather evidence** (new types only). Read the README, `CLAUDE.md`/`AGENTS.md`, any glossary or persona doc, and the role and permission definitions: grep for roles, `is_admin`, `admin`, row-level security policies, and route folders such as `/admin` or `/account`. Keep a `path:line` for each candidate. Done when every candidate has evidence, is named in the goal, or is a ★ CORE glossary entry.
3. **Match each candidate to the glossary**: the product kind through "Choosing groups", then one entry through "Repo signals" and "Telling similar types apart". Name the type as the repo does. Two candidates with the same access level and goals are one type.
4. **Write the profiles** per file-format.md, starting from the glossary entry; detail from the repo or the goal beats generic glossary text. New types take IDs from **Next user-type ID**. For an edit or drop, grep the repo for each touched ID and list the hits in Findings.
5. **Rank every type**: 1 is the type whose needs win when two conflict. Propose an order from the product's purpose, how many people each type is and how often they come. The order is an Open question unless the user already gave it.
6. **Check** against file-format.md's "Checks before writing". Done when every check passes.
7. **Return** in the contract's output shape, with the proposed file (new or converted) or the changed sections as before → after under a **Draft** heading right after Findings. Findings include roles in the code with no type, types with no evidence, and ID hits from step 4. Decisions for the plan carry one row: `Apply PRODUCT.md | <n> types as drafted, ranks per Open question 1 | <why>`. Typical Open questions: the rank order; which drafted types to add, drop or merge (one question: "All as drafted (Recommended)" or name the changes); a type resting only on guesswork.

## Apply

1. Take the latest draft and fold in the answers (from the plan's Decisions, the interview, or the recommended options when unattended).
2. Write `PRODUCT.md`. For a legacy conversion, delete the old `UX/User_Types.md` (and `UX/` when nothing else is left in it); list any other `UX/` files in the output, unchanged.
3. Point every reference to the old file at `PRODUCT.md`: `grep -rn "User_Types" --exclude-dir=node_modules --exclude-dir=.git .`
4. **Prove no ID was lost**: run the command below on the old version (`git show HEAD:<old path>`, or the old file) and on `PRODUCT.md`, and diff the two lists. Done when the diff shows only the drops the user approved, and file-format.md's checks pass.

```bash
grep -oE '\b(UT-[0-9]+(-[MSCW][0-9]+)?|BL-[MSCW][0-9]+)\b' <file> | sort -u
```

## Legacy UX/User_Types.md

Convert it verbatim: each `## UT-NN` section keeps every field and requirement row word for word, and gains a **Rank** line. Drop the `ux:` comment markers, the "Mapped features" blocks and the Index (the rank table replaces it). `<!-- ux:last-ut: N -->` becomes `**Next user-type ID:** UT-<N+1>`. The Baseline section moves as it is. The converted file is the Draft, and the rank order is its Open question.
