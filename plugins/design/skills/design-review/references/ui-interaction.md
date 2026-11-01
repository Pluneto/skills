# UI and interaction

Screens, flows, forms, accessibility and wording, reviewed as the people who will use them. For how to build the UI (layout, colour, disclosure, the AI-tells), ui-craft is the build-phase skill; this file is the review.

## Flows and journeys

A journey is one way a user-type moves through the feature: **intent → arrival → use → outcome**. For each target user-type's main intent (highest rank first, from `PRODUCT.md` when it exists):

1. **Main path.** The most common way in and the shortest path to success. Count the steps and decisions; each one should earn its place.
2. **Arrivals that change the start.** A shared link that lands on a detail page, arriving signed out, a notification deep link. Each must land somewhere that works, with the sign-in detour returning the user to where they were going.
3. **Outcomes other than success**, wherever they can realistically happen, at the point where they are most likely or most costly:
   - **Partial**: progress saved but not done (draft, waitlist, pending approval). Can they see it and come back to it?
   - **Abandoned**: they leave by choice. Is anything lost? Is the way back obvious?
   - **Error**: a system or validation failure. Does the message say what happened and how to fix it, keeping what they entered?
   - **Blocked**: not allowed or not eligible (wrong role, full, deadline passed). Do they learn why, and what they can do instead, before investing effort?
4. **Context variants.** For each context on the type (Mobile; Desktop; Assistive tech; Slow/offline network; Language; Low digital confidence; First time; Returning), ask: does it change the path or the outcome? Only a yes is a finding (a drag-and-drop step a keyboard user can't complete; a table unreadable at phone width).

## Screens and states

- Every view has a designed **empty**, **loading**, **error** and **success** state, plus **partial** where data can be incomplete. An empty state says what goes here and offers the first action.
- **Destructive or costly actions** are confirmed in proportion to their cost, and undoable where possible (undo beats "are you sure?").
- **Forms**: a visible label per field, the format shown up front, validation inline after the field is left, errors next to the field and summarised at the top, input kept on error, sensible defaults, no asking twice for what the product knows (WCAG 3.3.7).
- **Feedback** for every action within about a second: a state change, a toast, a spinner on the control that started it.
- **Consistency**: the same action has the same name, place and look everywhere; patterns match what the rest of the app already does.

## Accessibility (WCAG 2.2 AA)

- Everything works by **keyboard**, in a logical order, with a **visible focus** that is never hidden behind sticky headers (2.4.11).
- Text contrast at least **4.5:1** (3:1 for large text); controls, focus rings and meaningful graphics at least **3:1** against what's next to them.
- **Colour is never the only signal**: status also has a label or icon.
- Targets at least **24×24 px** (2.5.8); any drag has a single-pointer alternative (2.5.7).
- Every control has an **accessible name** that matches its visible label; images have alt text (empty for decoration); headings and landmarks give the structure.
- Content **reflows** at 320 px wide and at 200% zoom without losing anything.
- **Status messages** (saved, error, results updated) are announced to screen readers (an ARIA live region).
- Sign-in needs no memory or transcription test (3.3.8): allow paste and password managers.
- Motion respects `prefers-reduced-motion`; nothing flashes more than three times a second.

## UX copy

Read every label, button, message and empty state as a first-time user:

- **Buttons say what happens** ("Sign up for event", "Delete clip"), not "OK" or "Submit".
- **Error messages** say what went wrong and how to fix it, in plain words, without blame or codes alone.
- **Terms match the product's glossary** and stay the same across screens (not "sign-up" here and "registration" there).
- **Facts are true and current**: counts, dates, prices and states the copy states match what the system does (a "places left" that ignores the waitlist is a bug).
- Plain language a non-native speaker follows; sentence case; dates, times and numbers in the user's locale.
- Empty and success states say what to do next.

## Typical Checks for Done when

- "Every action in the flow is reachable and operable by keyboard alone, with visible focus."
- "Signing up for a full event shows why and offers the waitlist, before any form is filled in."
- "axe (or Lighthouse accessibility) reports no violations on the new pages."
