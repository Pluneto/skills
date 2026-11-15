---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a GLOSSARY.md, or recording or editing an ADR.
---

# Domain Modeling

The domain model is the project's agreed language and its hard-to-reverse decisions. It lives in two places that other skills read: `GLOSSARY.md` for terms and `docs/adr/` for decisions. This skill is for changing the model; reading it needs no skill.

**Done when** every domain term the work relied on has one meaning, the glossary states it, and the code, the glossary and what the user said agree, with any remaining disagreement named in your report.

## Sharpening the model

Look for what makes the language unreliable: a term used against its glossary definition, one word covering two concepts, two words for one concept, a stated rule the code contradicts. Probe relationships between concepts with concrete edge-case scenarios, since a boundary only shows where a scenario crosses it.

Settle each one yourself:

- **Facts** (what the code does, what the glossary says, how the term is used across the repo) you look up.
- **Meaning only the user holds** (which of two concepts they intend, a rule the code doesn't encode): with the user in the conversation, put the conflict to them in one concrete question ("the code cancels whole Orders, you describe partial cancellation: which holds?"). Running unattended, take the reading the code supports, write it down, and list it under Assumptions in your report.

Write each change to the model in the turn it is settled, so the files never lag the conversation.

## GLOSSARY.md

The file layout and entry format are fixed, because other skills find and parse them.

- **Single context** (most repos): one `GLOSSARY.md` at the repo root.
- **Several contexts**: `GLOSSARY-MAP.md` at the root links each context's own `GLOSSARY.md` (`- [Ordering](./src/ordering/GLOSSARY.md): receives and tracks customer orders`) and, under `## Relationships`, says how contexts relate (`- **Ordering → Fulfillment**: Ordering emits OrderPlaced; Fulfillment starts picking`). Work in the context the topic belongs to.
- Create a file when there is a first term to put in it.

```md
# {Context name}

{One or two sentences: what this context is and why it exists.}

## Language

**Order**:
A customer's request to buy one or more products.
_Avoid_: Purchase, transaction
```

An entry is one canonical term, one or two sentences saying what it *is*, and the rejected synonyms under `_Avoid_`. The glossary holds domain concepts only: general programming concepts and implementation details live elsewhere. Subheadings group terms once clusters appear.

## ADRs

An ADR records that a decision was made and why. Write one when all three hold, and skip it when any is missing:

1. **Hard to reverse**: changing course later has a real cost.
2. **Surprising without context**: a future reader would wonder why it was done this way, or would "fix" it.
3. **A real trade-off**: there were genuine alternatives and specific reasons for the choice.

Typical cases: technology with lock-in, a deliberate deviation from the obvious path, a constraint the code cannot show, an alternative rejected for a non-obvious reason.

Location and numbering are fixed: `docs/adr/NNNN-slug.md`, the next number after the highest present (a context's own decisions go in `<context>/docs/adr/`). The content is a title and one to three sentences of context, decision and reason. Add a `Status` frontmatter (`proposed | accepted | deprecated | superseded by ADR-NNNN`), considered options or consequences only when a reader needs them.
