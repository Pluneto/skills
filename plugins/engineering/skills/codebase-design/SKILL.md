---
name: codebase-design
description: Shared vocabulary for designing deep modules. Use when the user wants to design or improve a module's interface, find deepening opportunities, decide where a seam goes, make code more testable or AI-navigable, or when another skill needs the deep-module vocabulary.
---

# Codebase Design

Design **deep modules**: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface. Callers get leverage, maintainers get locality.

The vocabulary and the tests below are fixed, because other skills, reports and module names share them. How you apply them to the code in front of you is your own judgement: decide the design, and state the reason.

## Vocabulary

Use these terms exactly, in designs, reports and names.

**Module**: anything with an interface and an implementation, at any scale: a function, class, package, or tier-spanning slice. _Avoid_: unit, component, service.

**Interface**: everything a caller must know to use the module correctly: the type signature, and also invariants, ordering constraints, error modes, required configuration and performance characteristics. _Avoid_: API, signature (both name only the type-level surface).

**Implementation**: the code inside a module.

**Depth**: leverage at the interface: how much behaviour a caller or test can exercise per unit of interface they have to learn. **Deep** is a lot of behaviour behind a small interface; **shallow** is an interface nearly as complex as the implementation. Depth is leverage, not a ratio of implementation lines to interface lines, which would reward padding.

**Seam** _(Michael Feathers)_: a place where behaviour can be altered without editing in that place; the location where a module's interface lives. Where the seam goes is its own decision, separate from what sits behind it. _Avoid_: boundary (taken by DDD's bounded context).

**Adapter**: a concrete thing that satisfies an interface at a seam. It names the role (the slot filled), whatever its size: a Postgres repo and an in-memory fake are both adapters.

**Leverage**: what callers get from depth: one implementation pays back across N call sites and M tests.

**Locality**: what maintainers get from depth: change, bugs and knowledge concentrate in one place. Fix once, fixed everywhere.

## Tests for a design

- **Deletion test.** Imagine the module deleted. If the complexity vanishes, it was a pass-through; if it reappears across N callers, the module earns its keep.
- **The interface is the test surface.** Callers and tests cross the same seam. Wanting to test past the interface means the module has the wrong shape.
- **Two adapters make a seam.** One adapter is a hypothetical seam, plain indirection; a seam is real when something varies across it (typically production and test).
- **Depth belongs to the interface.** A deep module may be built from small swappable parts with internal seams its own tests use; those stay out of the interface.
- **Design it twice.** When an interface's shape is open, the first idea is rarely the best. Produce designs that differ in kind (smallest possible interface, most flexible, common caller made trivial, ports and adapters), each worked out without sight of the others (separate sub-agents stop them converging), then compare them on depth, locality and seam placement and choose one or a hybrid.

## Dependencies decide how a deepened module is tested

| Dependency | Examples | Seam and tests |
|---|---|---|
| In-process | pure computation, in-memory state | Merge the modules and test through the new interface. No adapter. |
| Local-substitutable | Postgres via PGLite, in-memory filesystem | Test with the stand-in running. The seam stays internal. |
| Remote but owned | your own services over a network | A port at the seam; the module owns the logic, the transport is an injected adapter (HTTP in production, in-memory in tests). |
| True external | Stripe, Twilio | Injected port; tests supply a mock adapter. |

After deepening, **replace, don't layer**: write tests at the new interface that assert observable outcomes, and delete the old tests on the shallow modules they cover. A test that must change when the implementation changes is testing past the interface.
