---
name: to-tickets
description: Break a saved plan, a planned issue, a spec, or the current conversation into tracer-bullet tickets, each declaring its blocking edges, as local files under plans/ or issues on the repo's tracker. For work that spans sessions or parallel agents.
disable-model-invocation: true
---

# To Tickets

Break a plan, spec or conversation into **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it.

**Tracker:** follow `docs/agents/issue-tracker.md` (setup-pluneto-skills writes it): it says where tickets go and which labels mark them. When the repo has none, read [no-tracker-doc.md](no-tracker-doc.md) and ask its tracker question before publishing, also for an agreed plan file: no plan says where its tickets go.

## Process

### 1. Gather context

Work from the conversation. If the user passes a reference (a `plan-*.md` path, a spec path, an issue number or URL), fetch and read all of it, with comments. A plan from plan-this is agreed: its decisions are settled, and its milestones, done-when checks and Needs from you are the starting material for the slices. An issue with the planned label is such a plan: read it from its plan comment (the one holding `Created <date> with /plan-this`). An issue with the draft label is not planned yet: stop and point to `/plan-this issues <n>`.

Read the tracker, so step 3 can find tickets that already cover the work:

- **GitHub**: every open issue (`gh issue list --state open --limit 1000 --json number,title,labels,assignees,body`) plus issues closed in the last 30 days (`--state closed --search "closed:>=<date 30 days ago>"`). Keep the first ~300 characters of each body. Leave out issues with the draft or planned label, and any closed issue whose comments say `planned in #<parent>` (step 3 sees those comments when it reads a candidate): they are plans, not work, so never a duplicate, done or append target. When 1000 come back the list is cut off: in step 3 also run 2-3 `gh search issues "<phrasing>" --state open` per draft.
- **Local**: every ticket file under `plans/*/tickets/`, whatever its `Status:`.

Optionally explore the codebase to learn its current state: use the project's glossary vocabulary in titles, respect ADRs in the area, and look for prefactoring that makes the change easy ("make the change easy, then make the easy change").

### 2. Draft vertical slices

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a COMPLETE path through every layer (schema, API, UI, tests): vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is one deliverable a single agent finishes in one session while it hands cheap work (searches, test runs, mechanical edits, a well-specified sub-feature) to sub-agents: slices sharing files or an area (one module, skill or feature folder, not a whole package) merge into one ticket
- Keep slices apart only for a real blocking edge, a different Who (agent or human), a hotspot both would edit (a file many tickets change, such as a shared registry or lockfile), so no one long ticket holds it, or work that would outgrow one such session; each part stays vertical
- Any prefactoring comes first

</vertical-slice-rules>

Give each ticket its **blocking edges**: the tickets that must complete before it can start; none means it can start immediately.

Mark each ticket **agent** or **human**. **Human** when the user must do its core work (a console step, a decision, a physical action); **agent** otherwise, also when the agent only needs the user's go or one reply along the way, which you name under **Needs you** in the ticket. For an agreed plan file, take the split from its "Needs from you" section.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change (rename a column, retype a shared symbol) whose **blast radius** spans the codebase, so one edit breaks thousands of call sites and no vertical slice lands green. Sequence it as **expand–contract**: first expand (add the new form beside the old so nothing breaks); then migrate call sites in batches sized by blast radius (per package or directory), each batch its own ticket blocked by the expand, CI green throughout because the old form still exists; finally contract (delete the old form) in a ticket blocked by every batch. When even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket; green is promised only there.

### 3. Check the tracker for matches

First merge drafts that deliver the same outcome into one, with both sets of acceptance criteria.

Then for each draft, shortlist the step 1 tickets that look like the same work, read each candidate in full (GitHub: body and comments; local: the whole file), and sort the closest with the **outcome test**:

- **duplicate**: finishing the existing ticket would also deliver this draft.
- **overlap**: the existing ticket delivers part of the draft; the rest is missing.
- **related**: same area, different outcome.
- **new**: no candidate passes. The source issue (when the source is an existing issue) is never a candidate.

Between two classes, take the weaker one (related over overlap, overlap over duplicate): the user confirms each match in step 4, and a weaker class loses no work.

Record the existing ticket's state. **Claimed**: on GitHub an assignee, the `in-progress` label, or a `claimed by` comment with no `released:` comment after it (the tracker doc's claim rule); locally `Status: claimed`. **Done**: closed (GitHub) or `Status: resolved` (local). **Open**: anything else.

| Class | Existing ticket | Action in step 5 |
|---|---|---|
| duplicate | open or claimed | skip the draft; point to the existing ticket |
| duplicate | done | skip the draft; report "already done in <ticket>" |
| overlap | open | **append**: add the missing acceptance criteria to the existing ticket |
| overlap | claimed or done | **delta ticket**: a ticket for only the missing part, blocked by the existing one when it is claimed, with a `Related:` line when it is done |
| related | any | create the draft with a `Related: <ticket>` line, or a blocked-by edge on the existing ticket when the draft needs it done first |
| new | | create the draft |

Claimed tickets are never rewritten and done tickets never reopened: someone else owns them. When a skipped draft blocked another draft, point that edge at the existing ticket (drop it when that ticket is done).

Done when every draft has a class, a target ticket (or "new") and an action.

### 4. Quiz the user

When the source is an agreed plan file, skip the breakdown questions (not the tracker question): its interview settled the work. Show the breakdown (the list below) in one message and go on to step 5, except when step 3 found a match: then ask the match question first.

Otherwise present the breakdown as a numbered list; for each ticket show **Title**, **Who** (agent or human), **Priority** (the source issue's priority label, else normal; the user may change it), **Blocked by**, **What it delivers** (the end-to-end behaviour it makes work) and **Match** (class, existing ticket and action, `overlap #12 → append`, or `new`).

**Match question**, whenever step 3 found a match, also for an agreed plan: one question asking the user to confirm the matched rows, naming any to reject; a rejected match turns that draft back into a new ticket.

Then ask: Does the granularity feel right (too coarse or fine)? Does each ticket depend only on tickets that genuinely gate it? Should any be merged or split? Iterate until the user approves.

### 5. Publish the tickets

Run each draft's action: make the appends, then publish the tickets to create (new, related and delta).

**Append**: just before writing, re-read the existing ticket's claim state; if it is now claimed, create a delta ticket instead. Add this section to the end of its body, keeping everything above it:

```
## Added from <source plan, spec or issue> (<YYYY-MM-DD>)

- [ ] Missing acceptance criterion
```

On GitHub, save the body (`gh issue view <n> --json body --jq .body`), add the section and write it back with `gh issue edit <n> --body-file <file>`; locally, append it to the ticket file.

How to publish depends on the tracker; the tickets are the same either way, only the blocking edges' shape changes:

- **Local files**: one file per ticket (never one combined file) at `plans/<feature-slug>/tickets/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first), using the template below. `Who:` says agent or human; `Blocked by:` lists the numbers it depends on.
- **GitHub Issues**: one issue per ticket in dependency order (blockers first), so each can reference real issue numbers. Give each the tracker doc's agent or human label, its type as the doc's **Issue types** says (`--type`, chosen per ticket), and its priority label from the breakdown, and use native blocking (the doc's **Blocking**), falling back to the "Blocked by" section only where unavailable. If the source was an existing issue, make each ticket its sub-issue (the doc's operation) with the source's milestone (`--milestone`).

Leave any parent issue open and unchanged, except: once a planned source's tickets exist, remove its planned label. A `Related:` line goes at the top of the body, under the title; a local edge or `Related:` line to a ticket in another folder names its path.

Finish with the published list (number or file, title, agent/human, blocked by), one line per appended or skipped draft naming its existing ticket, the counts (`created N, merged N, skipped N`: merged counts appends, skipped counts duplicates), and the exact line to run next:

- `/build-this <tickets folder>` or `/build-this issues <first>-<last>` (bare numbers: T3's composer turns a typed `#<n>` into a pull-request chip): one session works them in blocker order, skipping human tickets.
- On GitHub, when two or more agent tickets can run at once, also offer `/dispatch`, which takes ownership of them and finishes them with parallel workers.

<local-ticket-template>

# <NN>: <Ticket title>

Who: agent | human
Blocked by: the numbers of the tickets that gate this one, or None
Status: open

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective, not a layer-by-layer list.

**Needs you:** the step where an agent ticket waits on the user (a go, a reply), or omit.

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

</local-ticket-template>

<issue-template>

The agent or human label carries Who; the body has no Who line.

## Parent

A reference to the parent issue on the tracker (only if the source was an existing issue).

## What to build

The end-to-end behaviour this ticket makes work, from the user's perspective, not layer-by-layer.

## Needs you

The step where an agent ticket waits on the user (a go, a reply). Omit when none.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by

- A reference to each blocking ticket, or "None (can start immediately)". Omit when blockers were set as native edges.

</issue-template>

In either form, avoid file paths and code snippets: they go stale. Exception: a prototype's snippet that encodes a decision more precisely than prose (state machine, reducer, schema, type shape) is inlined, trimmed to the decision-rich parts, with a note that it came from a prototype.
