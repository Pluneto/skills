---
name: improve-codebase-architecture
description: Survey a codebase for deepening opportunities and return verified, ranked candidates with the top one designed, ready for /plan-this.
disable-model-invocation: true
---

# Improve Codebase Architecture

Find where the architecture causes friction and propose **deepening opportunities**: refactors that turn shallow modules into deep ones, for testability and AI-navigability. Run it from start to finish on your own judgement, without questions to the user. It proposes and changes nothing in the repo.

## What you build on

- **`codebase-design`** (invoke it; in Claude Code, call the Skill tool with `codebase-design`): the vocabulary (module, interface, depth, seam, adapter, leverage, locality) and the design tests. Use its terms exactly in everything you report.
- **`GLOSSARY.md`**: the domain names. Say "the Order intake module", in the project's words.
- **ADRs in `docs/adr/`**: decisions already made. Raise a candidate that contradicts one only when the friction justifies reopening it, and mark it as such.

## Where to look

A direction the user named (a module, a subsystem, a pain point) is the scope. Otherwise weight the areas that keep changing in the commit history: deepening pays off through future changes, so hot spots come first, and the net widens only when the history shows none.

Friction is what you experience while reading: one concept spread over many small modules, an interface nearly as complex as its implementation, pure functions extracted for testability while the bugs live in how they are called, modules leaking across their seams, code that is untested or hard to test through its current interface.

## Done when

- **Every candidate is verified in the code by you**: the files read, the callers checked, the deletion test applied. A sub-agent's finding is a lead until you have confirmed it.
- **Each candidate states** the files involved, the friction, the change, the gain in leverage, locality and tests, its dependency category, and a strength: `Strong`, `Worth exploring` or `Speculative`.
- **The top recommendation is designed**: the deepened module's interface, where its seam sits, its adapters, and which tests replace which. Where the interface's shape is open, design it twice.
- **It ends in a goal for `/plan-this`**: what to build, the constraints, and the decisions already taken here.
- **Open questions** carry the choices that belong to the user (reopening an ADR, a change in behaviour users would notice, how much to take on): numbered, the recommended option first and marked, a one-line pro and con per option. The design proceeds on the recommended options.

The form of the report is yours: pick what makes the structure clearest to the reader, with a before/after diagram wherever prose would not show the change.

When the user later rejects a candidate for a reason a future review would need, record it as an ADR with `domain-modeling`, so the next survey leaves it alone.
