# SaaS redesign lessons (one case study, optional recipes)

These are patterns from a single redesign. Treat them as options to consider, not rules: pick the form that fits the data, product and audience (donut vs bar, map vs table, tabs vs sections, modal vs flyout, plan count and naming, palette).

Source: "5 SaaS UI/UX mistakes that SCREAM you Vibe Code" (https://www.youtube.com/watch?v=PDcQJOPby1k), redesign of a vibecoded URL shortener ("LinkGuard"). These notes are everything this skill has from it. Observations from the video, not independently verified.

## Before -> after
- Emoji icons (check, clipboard, eye, calendar, link) -> thin line icons.
- Dark blue + multicolor icon chips -> dark green monochrome, sparklines in KPI cards.
- Same four KPIs on dashboard, usage, analytics -> two KPIs on the dashboard only.
- Gradient letter avatar + Sign Out in sidebar -> "My Account" card opening a popover (Settings, Sign Out).
- Link rows with Analytics/QR/Delete buttons and text chips -> URL + check + copy icon left, date center, "27 clicks" + kebab menu right.
- Create-link flyout -> modal; advanced options (custom domain, password) collapsed; added description.
- Usage page with four KPI tiles + five plan cards -> Settings with Usage/Billing/Account tabs, two-column usage with donuts, four plans (Business renamed Enterprise), billing email + payment method.
- Analytics bar chart -> multi-line chart with Aggregate/Individual toggle, device donut, source and browser tables, hex-dot world map with country table.
- Landing page with generic icons -> skewed link-card hero, edited analytics screenshot, strikethrough pricing.

## Pricing pattern
Reference points the video cites: Resend and Supabase pricing pages (Free / Pro "Most Popular" / Team / Enterprise "Custom", "From" price, "Everything in X, plus:" lists).

## Recipes that worked in this case (use when they fit)
- Usage: two-column layout with small donuts per meter; uncapped meters shown as a count marked Unlimited.
- Settings: tabs (Usage / Billing / Account) so new areas slot in.
- Pricing: up to four plans, big monthly price, strikethrough discount, next-tier benefits, top tier named Enterprise.
- Analytics: Aggregate/Individual toggle, device donut, source/browser tables, shaded world map beside a country table.
- Create flow: modal with advanced options collapsed when a flyout would be sparse.
- Palette: one hue family plus one accent, color carried through data rather than buttons and icons.
- Icons: one set (Phosphor, Lucide), inline SVG.
