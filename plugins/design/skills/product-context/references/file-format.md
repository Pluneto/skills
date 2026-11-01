# PRODUCT.md format

One file at the repository root, plain Markdown, no tooling. Headings, IDs and field labels are fixed; wording inside them is free.

## IDs

| Thing | Format | Example | Rule |
|---|---|---|---|
| User-type | `UT-NN` | `UT-03` | Take the **Next user-type ID**, then raise that line by one. Never reused, even after a drop. |
| Requirement | `UT-NN-<M/S/C/W><n>` | `UT-03-M2` | Letter = MoSCoW priority; numbered per type and priority. New ones take the next free number; a dropped number stays unused. |
| Baseline requirement | `BL-<M/S/C/W><n>` | `BL-M1` | Only in the Baseline section. |

IDs are copied verbatim, including when converting a legacy file. Rank is separate from the ID: re-ranking never touches an ID.

## Layout

```markdown
# Product

<!-- Maintained with the design:product-context skill. IDs are permanent: never renumber or reuse them. -->

**What it is:** One or two sentences: what the product does and for whom.
**Next user-type ID:** UT-04

## User-types by rank

| Rank | ID | Name | Access | Must |
|---|---|---|---|---|
| 1 | UT-03 | Organiser | Elevated | 2 |
| 2 | UT-01 | Visitor | Anonymous | 3 |

## Baseline requirements

Every human user-type inherits these. Profiles never repeat them.

| ID | Priority | Requirement |
|---|---|---|
| BL-M1 | Must | Usable with keyboard and screen reader; meets WCAG 2.2 AA. |
| BL-M2 | Must | Works on a phone-sized screen as well as on desktop. |
| BL-M3 | Must | Errors say what went wrong and how to fix it, without losing what the user entered. |

## UT-03 · Organiser

**Rank:** 1
**Description:** A committee member who plans events and needs to know who is coming.
**Goals:**
- Publish an event with all practical details
- Know numbers in time to book the room and food
**Access level:** Elevated
**Contexts:** Desktop; Returning
**Based on:** G-COM-03 Organiser
**Evidence:** supabase/migrations/001_roles.sql:3; README.md:4

### Requirements

| ID | Priority | Requirement |
|---|---|---|
| UT-03-M1 | Must | Can publish an event without help from a developer. |
| UT-03-M2 | Must | Can see an up-to-date attendee count at any time. |
| UT-03-S1 | Should | Can message everyone who signed up. |
| UT-03-W1 | Won't | Handle payments for tickets. |
```

## Field rules

- **Order:** type sections in ID order (stable diffs); the rank table in Rank order.
- **Rank:** 1..n, unique, 1 = the type whose needs win when two conflict. Every type has one; the rank table and each section's **Rank** line agree.
- **Heading:** `## UT-NN · Name`, the name this product uses for them.
- **Description:** one or two sentences: who they are and why they come.
- **Goals:** two to four bullets.
- **Access level:** exactly one of `Anonymous`, `Signed-in`, `Elevated`, `Admin`, `System`.
- **Contexts:** those that apply from: Mobile; Desktop; Assistive tech; Slow/offline network; Language; Low digital confidence; First time; Returning. Contexts are situations, not types: a screen-reader user is a context on a type.
- **Based on:** a glossary ID and name (`references/glossary.md`), or `None (written fresh)`.
- **Evidence:** `path:line` references, `User-specified`, or `Glossary only`.
- **Requirements:** Must 3–5, Should 2–4, Could 1–3, Won't 1–2. Each is a need a feature could satisfy ("Can see which events still have places"), not a feature spec ("Event list with capacity badge"). Priority words `Must`, `Should`, `Could`, `Won't` match the ID letter. Leave out what the Baseline covers.
- **Must count** in the rank table = the number of Must rows in that type's section.

## Checks before writing

- Every `UT-NN` heading appears once in the rank table, and every rank row has a section.
- No ID appears twice; no ID from the previous version is missing unless the user approved its drop.
- **Next user-type ID** is above every `UT-NN` ever used (including dropped ones, which `git log -p -- PRODUCT.md` shows).
