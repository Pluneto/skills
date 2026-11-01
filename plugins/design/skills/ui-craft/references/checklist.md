# UI checklist

Run at the end of every Build or Review. Mark each item done, n/a (say why), or gap. Sections 1–3 apply in full to Operate screens and where relevant elsewhere.

## 0. Theme and mode
- [ ] Colours, type, spacing, radius and icons come from the project's existing tokens and components; any new token is named
- [ ] Each screen's surface mode (Operate, Persuade, Read, Experience, Converse) is named and drives its trade-offs
- [ ] Persuade: one message and one primary call to action per screen, real product graphics and proof
- [ ] Read: 60–75 characters a line, clear heading levels, scannable
- [ ] Experience: the signature motion has a `prefers-reduced-motion` fallback
- [ ] Converse: short messages, actions as buttons, every failure answered, acknowledgement within a second

## 1. Data drives the form
- [ ] Each column/field matches its data type (chip, number, avatar, date, text)
- [ ] Finite categories are chips/pills
- [ ] Numbers right-aligned, tabular figures
- [ ] Long text truncated with full value on hover
- [ ] Inactive/archived rows dimmed
- [ ] People shown with avatars
- [ ] Time-based data shown as timeline and/or chart, not only a sorted table
- [ ] Every color maps to meaning (status, severity, category); none decorative
- [ ] Urgent items are the most visually prominent

## 2. Progressive disclosure
- [ ] Each action placed on the explicitness spectrum on purpose
- [ ] Primary action visible; secondary revealed on hover/focus, menu, or popover
- [ ] Small features use popover/drawer, not a new page
- [ ] Destructive actions are not permanently prominent and ask for confirmation or offer undo
- [ ] Onboarding is sequenced (single tooltip, checklist), not one big modal

## 3. Invisible UI inventory
- [ ] Tooltips on all icon-only buttons and ambiguous labels
- [ ] Hover actions (copy cell, row actions, remove)
- [ ] Comment/note indicators on cells or rows
- [ ] Row context menu (copy, comment, insert, delete, link)
- [ ] Column menu (rename, describe, change type, insert, hide, delete)
- [ ] Sort, filter, group builders
- [ ] Share/permissions popover
- [ ] Drawers or side panels for details
- [ ] "What's new" / announcement surface
- [ ] Onboarding checklist or tooltip tour with dismiss
- [ ] Empty, loading, and error states
- [ ] Bulk-selection state (selected count, bulk actions)

## 4. Accessibility and robustness
- [ ] Hover-only actions reachable by keyboard focus and on touch
- [ ] Status never conveyed by color alone
- [ ] Contrast OK on chips and dimmed rows
- [ ] Tooltips and popovers dismissible with Escape and focus-managed
- [ ] Everything operable by keyboard with a visible focus ring; semantic elements before ARIA
- [ ] Targets at least 24×24 px; status updates announced through a live region
- [ ] Reflows at 320 px wide and 200% zoom

## 5. Memorability (n/a for internal/ops tools unless noted)
- [ ] Audience tier identified (consumer / B2B / internal)
- [ ] Key charts paired with interpretation and a next action (all tiers)
- [ ] One signature visual or delight moment, appropriate to the tier
- [ ] Playful states only for consumer products
- [ ] Delight never on critical data; data colors still carry meaning
- [ ] Anything that doesn't earn its place was cut

## 6. No AI tells (SaaS / vibecoded apps)
- [ ] No emojis as icons; one consistent icon set; all icons actually render
- [ ] Small deliberate palette; series and scale colors are clearly distinguishable (dataviz skill followed when available)
- [ ] No repeated summary metrics across pages; no element without an insight or job
- [ ] Visual encodings fit the data type (including uncapped or open-ended values)
- [ ] Simplifying kept function: search, sort, filter work on every list; utility pages are complete
- [ ] Growing collections use scalable structures, not fixed card sets
- [ ] Items show glanceable trend/change where it applies
- [ ] Comparisons are aligned, absence is explicit, non-comparable items are separated
- [ ] Narrative text is short and tied to an action
- [ ] Navigation lean; create/edit flows sized to content with advanced options collapsed
- [ ] Settings/billing structure can absorb new areas; pricing coherent (no cheaper higher tier)
- [ ] Landing page uses real product graphics, not generic icons
