# Briefing a child

A child agent starts with nothing but its brief, so the brief stands alone. Write it in your own words; it is complete when the child could finish without asking you anything. It carries:

- **The outcome and its check:** the milestone (or the search, check or fix), its Done when with the exact command, and the plan file or ticket to read for the goal, Constraints and the Decisions that bear on it.
- **Its ground:** the checkout and branch, the files or area it owns, what is already built that it depends on, and what other workers are touching.
- **Its latitude:** engineering deviations are its to make and report; a user-level deviation (see the skill's Deviations) is reported back, never decided. It is unattended: it asks no one, marks what only the user can supply `TODO(user)` and names secrets by variable only.
- **Its limits:** it stops before anything hard to undo or outside the workspace and lists it as held. Say plainly whether it commits, and that it leaves the plan's ticks and Build log to you.
- **Method:** skills worth loading, by name when the child can load skills, else as file paths or pasted lines.
- **The report you want back**, short enough to read without filling your context (about 150 words, no code): status (done or blocked), the check and its result, files changed, deviations, user-level questions, items held or owed, the commit if any.

Then verify: re-run the check yourself or through a cheap child that changes nothing, and read the diff when the work is subtle.
