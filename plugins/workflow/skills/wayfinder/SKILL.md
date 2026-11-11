---
name: wayfinder
description: Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on your issue tracker, and resolve them one at a time until the way to the destination is clear.
disable-model-invocation: true
---

A loose idea has arrived, too big for one agent session, wrapped in fog: the way from here to the **destination** isn't visible yet. Wayfinding finds that way instead of charging at the destination. This skill charts it as a **shared map** on the repo's issue tracker, then works its **decision tickets** (questions whose resolution is a decision, not slices of a build) one at a time until the route is clear.

The destination varies per effort and naming it is the first act of charting, since it shapes every ticket: a spec to hand off, a decision to lock before planning, or a change made in place like a data-structure migration. The map is domain-agnostic: engineering, course content, whatever fits.

## Plan, don't do

Wayfinder **plans**: each ticket resolves a decision, and the map is done when the way is clear and nothing is left to decide. The pull to do the work signals the edge of the map: time to hand off. An effort can override this in its **Notes**; otherwise produce decisions, not deliverables.

## Refer by name

Every map and ticket is an issue with a **name**, its title. In everything the human reads (narration, Decisions-so-far), use the name, wrapping its link, never a bare id, number or slug: a wall of `#42, #43, #44` is illegible.

## The Map

The map is a single issue on the repo's tracker, labelled with the map label (`wayfinder:map` by default) and given the task issue type (`--type`, the tracker doc's **Issue types**): the canonical artifact. Its tickets are child issues. It is an **index**, not a store: it lists the decisions made and links the tickets that hold their detail; a decision lives only in its ticket, and the map gists and links it.

**Tracker:** follow `docs/agents/issue-tracker.md` ("Wayfinding operations" says how this repo expresses the map, child tickets, blocking and frontier queries; its Labels table names the map and type labels, defaulting to the names below). With none, read [no-tracker-doc.md](no-tracker-doc.md) before creating anything.

### The map body

The whole map at low resolution, loaded once per session. Open tickets are not listed: they are open child issues, found by query.

```markdown
## Destination

<what reaching the end of this map looks like: the spec, decision, or change. One or two lines; every session orients to it before choosing a ticket.>

## Notes

<domain; skills every session should consult; standing preferences for this effort>

## Decisions so far

<!-- one line per closed ticket, enough to judge relevance; zoom the link for detail -->

- [<closed ticket title>](link): <one-line gist of the answer>

## Not yet specified

<!-- in-scope fog you can't ticket yet; graduates as the frontier advances -->

## Out of scope

<!-- work ruled beyond the destination; closed, never graduates -->
```

### Tickets

Each ticket is a **child issue** of the map, its body the question, sized to one 100K-token agent session:

```markdown
## Question

<the decision or investigation this ticket resolves>
```

It carries its type label (`wayfinder:<type>` by default): `research`, `prototype`, `interview` or `task`, and, like the map, the task issue type, which is not a label. Besides the claim label and an optional high or low priority label, the map and type labels are the only labels a map and its tickets carry.

A session **claims** a ticket **first**, before any work, as the tracker doc's Claim says; an open ticket without a live claim is unclaimed.

Blocking uses the tracker's **native** dependency relationship, which renders the frontier in the tracker's own UI; only a tracker without it falls back to a body convention. A ticket is **unblocked** when every blocker is closed; the **frontier** is the open, unblocked, unclaimed children, in priority order: high first, then normal (no priority label), then low, map order within each.

The answer is not in the body: record it on resolution. Assets made while resolving a ticket are linked from the issue, not pasted in.

## Ticket types

Every ticket is **HITL** (worked *with* a human who speaks for themselves) or **AFK** (the agent alone). A HITL ticket resolves only through that live exchange; an agent that answers its own interview questions has broken this.

- **Research** (AFK): read documentation, third-party APIs or local resources to surface a fact a decision waits on. A sub-agent briefed with research-this's facts-mode rules as plain text (Chart the map, step 5) or the `research-this` skill in facts mode in the session resolves it. Use when knowledge outside the working directory is required.
- **Prototype** (HITL): raise the discussion's fidelity with a cheap, rough, concrete artifact to react to (outline, stub, UI or logic code) by invoking the `prototype` skill if available; link it as an asset. Use when "how should it look or behave" is the key question.
- **Interview** (HITL): conversation, the default. Invoke `interview`, then `domain-modeling` if available.
- **Task** (HITL or AFK): manual work that must happen before a *decision* can be made (signing up for a service to judge its API, provisioning access, moving data to see its shape). The one type that *does*: it earns its place by unblocking a decision. The agent drives it alone where it can; otherwise it hands the human a precise checklist. The answer records what was done and any facts later tickets depend on (credentials location, new URLs, row counts).

## Fog of war

The map is *deliberately* incomplete: don't chart what you can't yet see. Beyond the live tickets lies the **fog of war**: decisions and investigations you can tell are coming but can't pin down because they hang on open questions. Resolving a ticket clears the fog ahead of it, graduating whatever is now specifiable into fresh tickets, until the way is clear and no tickets remain.

**Not yet specified** holds that dim view: the suspected question, the area to revisit. Everything there is in scope, just not sharp enough to ticket; write it as loosely or fully as the view allows.

**Fog or ticket?** Can you state the question precisely now, not can you answer it now. A sharp question is a ticket even when blocked. If you can't phrase it that sharply, it's fog: don't pre-slice it, since one patch may graduate into several tickets or none. **Not yet specified** excludes what's decided, what's a live ticket, and what's out of scope.

## Out of scope

The destination fixes the scope; work beyond it is **out of scope**, not fog (scope, not sharpness, lands it here). It gets its own map section and never graduates: it returns only if the destination is redrawn, as a fresh effort. When an existing ticket turns out to sit past the destination, **close it** and leave one line in **Out of scope**: the gist, why, and the closed ticket's link. Keep it out of **Decisions so far**, which records the route actually walked.

## Invocation

Two modes. Either way, **resolve at most one ticket per session**, except research tickets.

### Chart the map

The user invokes with a loose idea.

1. **Name the destination.** Invoke `interview`, then `domain-modeling` if available, to pin down the spec, decision or change. The destination fixes the scope, so it is settled first.
2. **Map the frontier.** Interview again, **breadth-first**: fan out across the whole space, surfacing open decisions and first steps takeable now. If this surfaces no fog (the way is clear, the journey fits one session), skip the map: stop and ask the user how to proceed.
3. **Create the map** (with the map label): Destination and Notes filled, Decisions-so-far empty, the fog sketched into **Not yet specified**.
4. **Create the tickets you can specify now** as child issues (each with its type label and `--type` task), then wire blocking edges and cross-references in a **second pass** with real ids (issues need ids first; a placeholder `#<n>` auto-links an unrelated issue). Anything you can't yet specify stays in the fog.
5. **Resolve the research tickets.** Claim each `research` ticket just created and start one sub-agent per ticket in parallel. Sub-agents often can't see skills, so give each a self-contained brief with research-this's facts-mode rules as plain text: the ticket's question; primary sources only (official docs, source code, specs); each claim with its source URL and fetch date; a Gaps section; findings returned as Markdown text, no files written, no git commands (they share your working tree). Record each result as it returns: locally in `plans/<effort>/research/<name>.md` linked from the ticket, on a remote tracker as the resolution comment. Then resolve the ticket as in Work through the map, step 4. Done when every research ticket is closed with its findings recorded.
6. Stop: charting is one session's work and, beyond research tickets, resolves nothing.

### Work through the map

The user invokes with a map (URL or number); a ticket is optional, and without one you pick the next decision.

1. Load the **map**: the low-res view, not every ticket body.
2. Take the ticket the user named, else the first frontier ticket. **Claim it** before any work.
3. Resolve it as its type label names (the body never states the type). **Zoom as needed**: fetch any related or closed ticket's body on demand, and invoke the skills the map's `## Notes` name. If in doubt, `interview`, then `domain-modeling` if available.
4. Record the resolution: post the answer as a **resolution comment**, **close** the issue, **append a context pointer** to Decisions-so-far.
5. Add newly surfaced tickets (create, then wire); graduate any fog the answer made specifiable, clearing it from **Not yet specified**. If a ticket (this one or another) sits beyond the destination, **rule it out of scope** instead of resolving it. If the decision invalidates other parts of the map, update or delete those tickets.

### Hand off

When no tickets remain and the way is clear, the map is done: tell the user to run `/plan-this` on it, which keeps every map decision as settled and plans only the gaps. The user may run unblocked tickets in parallel, so expect other sessions editing the tracker concurrently.
