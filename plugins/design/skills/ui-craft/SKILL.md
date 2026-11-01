---
name: ui-craft
description: Build or restyle UI that looks deliberate, not AI-generated - dashboards, admin panels and data tables, landing and pricing pages, docs and reading pages, playful consumer screens, chat interfaces. Reads the existing theme first, then applies data-driven layout, progressive disclosure, the invisible UI (states, tooltips, menus), WCAG 2.2 AA build rules and fixes for vibecoded tells. Use when building, restyling or critiquing a UI, or making an app look professional.
argument-hint: "[path or description of the UI]"
---

# UI craft

UIs are easy to style and hard to orchestrate. Apply these rules in any stack. `$ARGUMENTS` may be a path to existing UI or a description of what to build.

Read [contract.md](contract.md) first: who decides and the output shape.

## Mode

- **Review**: existing code, a path or a screenshot is given. Audit it against the rules and [references/checklist.md](references/checklist.md), and report findings by severity with concrete fixes.
- **Build**: otherwise. Take the data, the users and the main action from the plan, `PRODUCT.md` and the code. State what you assumed; choices that are the user's (the audience tier, a visible change of look) go into Open questions, and under a build or autopilot you take the recommended option.

Either way, finish by running the checklist and stating what is covered and what is left out on purpose.

## 0. Read what exists

Before choosing a colour, size or component, read the project's design sources: Tailwind config, CSS variables or theme file, a component library in use, a `DESIGN.md` or design glossary, and two or three existing pages. Build with those tokens and components; add a token only when nothing fits, and name it in the output. Done when you can name the palette, type scale, spacing step, radius and icon set you will use, and where each came from.

## 1. Pick the surface mode

Every screen has one main job; name its mode and let it set the trade-offs.

| Mode | For | Optimise |
|---|---|---|
| **Operate** | dashboards, admin panels, data tables, tools | density, speed of repeated tasks, scanning (sections 2–4 in full) |
| **Persuade** | landing, pricing, sign-up | one message and one primary call to action per screen, proof (real product shots, real numbers), trust |
| **Read** | docs, articles, event and detail pages | type: 60–75 characters a line, clear heading levels, scannable lists, generous line height |
| **Experience** | games, portfolios, playful consumer moments | one signature visual or motion, with a `prefers-reduced-motion` fallback |
| **Converse** | chat UIs, bot replies, notifications | short messages, the action as a button, an answer to every failure, acknowledgement within a second |

## 2. Let the data drive the form

Start from the data: its types, cardinality and dimensions.

- **Finite categories** (department, status, severity) become chips or pills, coloured only when colour carries meaning.
- **Numbers** are right-aligned with tabular figures (`text-align: right; font-variant-numeric: tabular-nums`).
- **Long text** is truncated with an ellipsis and a full-value tooltip.
- **Inactive rows** are dimmed and still readable.
- **People** get avatars next to their names.
- **Time-based data** (logs, activity, history) becomes a timeline or a chart, beside or above the table.
- **Colour is information**: the loudest colour is for urgent or critical; everything else stays quiet.

## 3. Progressive disclosure

Place each action on the **spectrum of explicitness** by frequency, importance and space: (1) always visible with a label (global primary actions), (2) visible icon only, (3) revealed on hover and focus with a tooltip (secondary: remove, copy), (4) behind a menu, popover or drawer (rare).

- The primary action inside a popover or panel comes first and is visible.
- Secondary and destructive actions appear when the user looks for them; destructive ones confirm or offer undo.
- Small features open in a popover or drawer rather than a new page.
- Onboarding is sequenced: one tooltip at the key action, then the next, or a small checklist.

## 4. Design the invisible UI

A working UI is mostly UI not visible at rest: hover actions, tooltips for icons and ambiguous labels, row and column menus, popovers, drawers, sort, filter and group builders, onboarding, and the **empty, loading, error and success states** of every view. The full inventory is in the checklist. Tooltips are the piece most often missing.

## 5. Accessibility as you build

- Semantic elements first (`button`, `a`, `label`, headings, landmarks); ARIA only to fill gaps.
- Everything works by keyboard with a visible focus ring; hover-revealed actions also appear on `:focus-within`, and touch gets a menu or long-press path.
- Contrast: text 4.5:1 (large 3:1), controls and focus rings 3:1, checked on chips, dimmed rows and over images.
- Status pairs colour with an icon or label. Targets at least 24×24 px. Status updates go to a live region.
- Layout reflows at 320 px wide and 200% zoom.

## 6. Look deliberate

AI-generated UIs share tells that read as untrustworthy. Make these decisions on purpose, choosing the form that fits the data, product and audience:

- **One interface icon set** (inline SVG), checked to render; emoji as icons is the loudest tell.
- **A small, hand-picked palette** from the project's tokens, where each colour has a meaning. Data series and categories use clearly distinguishable hues; sequential scales interpolate between two distinct colours.
- **Each view has one job.** Every element yields an insight or an action; summary metrics live on one page.
- **Simplify by disclosure, keeping every capability.** Lists keep working search, sort and filter; account and settings pages stay complete.
- **Structures scale**: growing collections live in a searchable, sortable list, with a small trend and the change versus the last period where items have performance over time.
- **Comparisons compare**: aligned rows, a consistent form, absence shown as a muted mark.
- **Short narrative** tied to an action. **Lean navigation**: core destinations only, account actions in a popover, create and edit forms sized to their content with advanced options collapsed.
- **Settings and billing** in sections new areas can slot into; pricing where each higher tier costs more and says what it adds.
- **Landing pages** use real product graphics.

Optional recipes from one redesign: [references/saas-redesign-lessons.md](references/saas-redesign-lessons.md).

## 7. Make it memorable

Gut check: would someone screenshot this, and why? Pair each key chart with its interpretation and the next action. Scale the signature moment to the audience: **consumer**, a distinctive visual or a playful empty or success state; **B2B**, at most one signature visual; **internal or ops**, insight, action and restraint only. Delight stays off critical data. Examples: [references/memorable-dashboards.md](references/memorable-dashboards.md).

## Charts

When the `dataviz` skill is available, load it before the first line of chart code and follow it. Otherwise: pick the chart from the question (trend → line, part of a capped whole → bar or a single proportional bar, comparison → sorted bars), label axes and units, start bar axes at zero, use at most five distinguishable hues plus grey for "other", and check them in both light and dark themes.

## Output

- **Build**: working code, plus a short note in the contract's shape: Assumptions (including the tokens used and any added), the disclosure level of each action, the hidden UI included, the signature moment (or why none), the checklist result, and Open questions. Before finishing, click through search, sort and filter and confirm icons render.
- **Review**: the contract's output shape; each finding names the rule it breaks and a specific fix.
