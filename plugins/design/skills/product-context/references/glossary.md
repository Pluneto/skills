# User-type glossary

## Choosing groups

| The product… | Groups |
|---|---|
| Any product | CORE (★ entries are always candidates) |
| Has public pages that inform or persuade: company, portfolio, blog, docs | PUB |
| Has members, events, a club, an association, a forum or a Discord-linked community | COM |
| Sells products with a cart and checkout | SHP |
| Is software customers sign up to and use for their work, often per team or workspace | SAS |
| Connects two sides who transact: buyers and sellers, guests and hosts, clients and providers | MKT |
| Is used by staff of one organisation to run its operations | INT |

A product can take several groups. A club site with a shop takes CORE + PUB + COM + SHP.

## Telling similar types apart

- **Anonymous visitor vs Prospect:** Prospect when the site exists to turn visitors into enquiries or sales. Keep both when some visitors only want information.
- **Registered user vs Member / Customer / Team member:** Registered user is the fallback. Use the more specific type whenever belonging, buying or team use defines the account.
- **Shopper vs Customer:** Shopper is browsing and has not bought; Customer has bought and comes back for orders, returns or reorders.
- **Administrator vs Site owner vs Workspace admin:** Administrator runs the whole product with full control (often the developer or operator). Site owner is a non-technical client who owns a small site. Workspace admin is a customer managing their own team inside a multi-tenant product.
- **Moderator vs Trust & safety reviewer:** Moderator keeps community conversations healthy; Trust & safety reviewer checks listings, accounts and transactions for fraud and rule-breaking.
- **Organiser vs Committee member:** Organiser runs specific events or activities; Committee member governs the association (membership, finances, decisions).
- **Operator vs Approver:** Operator does the work in the tool; Approver signs off on what operators prepared.

---

## CORE: every product

### G-COR-01 · Anonymous visitor ★
- **Who:** Someone who is not signed in, often on a first visit, arriving from search, a shared link or word of mouth.
- **Goals:** understand what this is and who it's for; find one specific piece of information; decide whether to go further.
- **Access level:** Anonymous
- **Contexts:** Mobile; First time; Slow/offline network
- **Repo signals:** public routes, `anon` role, landing or home page, `/about`, `/contact`, auth-middleware exceptions
- **Must:** grasp what the product offers within the first screen; reach key public information without an account; find the next step (contact, sign up, buy).
- **Should:** see who is behind it and why to trust it; land directly on what a shared link pointed to.
- **Could:** preview what signing up unlocks.
- **Won't:** be forced to create an account to read public content.

### G-COR-02 · Registered user
- **Who:** Someone with an account who is not defined by a more specific role. Use only when no Member, Customer or Team member type fits.
- **Goals:** get back to their own data quickly; manage their account.
- **Access level:** Signed-in
- **Contexts:** Returning; Mobile
- **Repo signals:** `authenticated` role, `/account`, `/profile`, `/settings`, a `users` or `profiles` table
- **Must:** sign in and out reliably; see and change their own data; recover access when locked out.
- **Should:** pick up where they left off; control notifications.
- **Could:** export their data.
- **Won't:** see other users' private data.

### G-COR-03 · Administrator ★
- **Who:** The person or small team who configures and runs the whole product, often the developer or the client's technical contact.
- **Goals:** keep the product running and its content correct; manage users and permissions; fix problems fast.
- **Access level:** Admin
- **Contexts:** Desktop; Returning
- **Repo signals:** `admin`, `is_admin`, `superuser`, `service_role`, `/admin`, `/dashboard/settings`, admin-only RLS policies
- **Must:** manage users and their roles; change content and settings without a code deploy; see what changed and who changed it.
- **Should:** spot problems before users report them; undo a mistaken change.
- **Could:** bulk-edit or import data.
- **Won't:** read secrets or passwords in plain text.

### G-COR-04 · Support agent
- **Who:** Staff who answer questions and resolve problems on behalf of users.
- **Goals:** understand a user's problem quickly; fix it or route it; keep the user informed.
- **Access level:** Elevated
- **Contexts:** Desktop; Returning
- **Repo signals:** `support` role, `/support`, tickets or messages tables, impersonation or "view as" code
- **Must:** look up a user and their recent activity; see what the user sees; leave a record of what was done.
- **Should:** fix common issues without a developer; reach the user in the channel they use.
- **Could:** see recurring issues across users.
- **Won't:** change a user's data without leaving a trace.

### G-COR-05 · External system
- **Who:** A non-human actor that reads or writes data on someone's behalf: a payment provider's webhook, a Discord bot, a nightly import.
- **Goals:** exchange data reliably and predictably.
- **Access level:** System
- **Contexts:** none
- **Repo signals:** `/api/webhooks`, cron config, edge functions, service keys, bot tokens
- **Must:** authenticate with its own limited credentials; get clear, stable responses; be retried safely without duplicating effects.
- **Should:** be monitored so failures are noticed.
- **Could:** be throttled independently of human traffic.
- **Won't:** use a human user's credentials.
- Include only when the tool really has a non-human actor in its journeys.

---

## PUB: public, marketing and content sites

### G-PUB-01 · Prospect
- **Who:** A visitor weighing whether to hire, buy from or contact the organisation.
- **Goals:** judge fit and quality; compare with alternatives; get in touch with minimal effort.
- **Access level:** Anonymous
- **Contexts:** Mobile; Desktop; First time
- **Repo signals:** `/contact`, `/pricing`, `/work`, `/portfolio`, quote or contact forms, lead tables, CRM integrations
- **Must:** see relevant work or proof quickly; understand prices or how pricing works; contact the organisation in under a minute.
- **Should:** know what happens after they make contact; find answers to common objections.
- **Could:** book a call directly.
- **Won't:** have to give more details than needed for a first contact.

### G-PUB-02 · Reader / subscriber
- **Who:** Someone who comes for content (articles, news, docs, updates) and may subscribe to get more.
- **Goals:** read or find content; follow new content without checking manually.
- **Access level:** Anonymous
- **Contexts:** Mobile; Returning
- **Repo signals:** `/blog`, `/news`, `/docs`, RSS, CMS collections, newsletter signup, `subscribers` table
- **Must:** read comfortably on any screen; find related or older content; subscribe and unsubscribe easily.
- **Should:** share a piece with one tap.
- **Could:** save content for later.
- **Won't:** hit a paywall or signup wall for public content.

### G-PUB-03 · Content editor
- **Who:** Someone who writes and updates content without touching code.
- **Goals:** publish accurate content quickly; keep existing content up to date.
- **Access level:** Elevated
- **Contexts:** Desktop; Low digital confidence
- **Repo signals:** CMS config (Sanity, Contentful, Payload, Strapi), `editor` or `author` role, `/admin/posts`, draft/published states
- **Must:** create, edit and publish without developer help; preview before publishing; fix a mistake after publishing.
- **Should:** schedule publication; add images that come out right without manual resizing.
- **Could:** see which content performs well.
- **Won't:** be able to break the site layout.

### G-PUB-04 · Site owner
- **Who:** The non-technical owner of a small site who edits occasionally and cares mostly about results.
- **Goals:** keep key facts current (hours, prices, contact details); see whether the site brings in business.
- **Access level:** Admin
- **Contexts:** Low digital confidence; Mobile
- **Repo signals:** single owner account, simple settings page, a hosted CMS, contact-form notification emails
- **Must:** change key facts in minutes without help; receive enquiries reliably; know the site is up and secure.
- **Should:** see simple numbers on visits and enquiries.
- **Could:** add a new page from a template.
- **Won't:** manage hosting, domains or updates themselves.

---

## COM: communities, clubs and memberships

### G-COM-01 · Prospective member
- **Who:** Someone who wants to join or is considering joining.
- **Goals:** find out what membership offers and costs; join with little friction.
- **Access level:** Anonymous
- **Contexts:** Mobile; First time
- **Repo signals:** `/join`, `/membership`, `/signup`, applications table, Discord or OAuth sign-up flow
- **Must:** understand what members get and what it costs; know the steps to join; complete joining on a phone.
- **Should:** see what the community is like (events, photos, members).
- **Could:** try something before joining (an open event).
- **Won't:** wait days without knowing whether the application went through.

### G-COM-02 · Member
- **Who:** Someone who belongs and uses the community's events, content or conversations.
- **Goals:** know what's happening; take part; stay connected with other members.
- **Access level:** Signed-in
- **Contexts:** Mobile; Returning
- **Repo signals:** `member` role, `members` table, membership status or expiry, `/events`, `/members`, Discord guild or role checks
- **Must:** see what's coming up; sign up for activities; manage their own profile and membership.
- **Should:** get reminders that matter without noise; find other members.
- **Could:** see their history (events attended, contributions).
- **Won't:** see other members' private contact details without consent.

### G-COM-03 · Organiser
- **Who:** A member who runs specific events or activities.
- **Goals:** announce events well; know who is coming; communicate changes.
- **Access level:** Elevated
- **Contexts:** Desktop; Mobile; Returning
- **Repo signals:** `organiser`, `organizer`, `host`, `committee` roles, event create/edit routes, attendee or RSVP tables
- **Must:** create and edit events without developer help; see an up-to-date attendee list; tell attendees about changes.
- **Should:** copy a past event; set capacity and a waitlist.
- **Could:** check people in on the day.
- **Won't:** see members' data unrelated to their events.

### G-COM-04 · Moderator
- **Who:** Someone who keeps posts, comments or chats within the rules.
- **Goals:** act on problems quickly and fairly; keep a record.
- **Access level:** Elevated
- **Contexts:** Mobile; Returning
- **Repo signals:** `moderator`, `mod` roles, reports or flags tables, hide/ban/delete actions, audit logs
- **Must:** see reported content in one place; hide or remove content and say why; act against repeat offenders.
- **Should:** see the history of a user or thread before acting.
- **Could:** let trusted members help with flagging.
- **Won't:** delete content without a trace.

### G-COM-05 · Committee member
- **Who:** Someone who governs the association: membership, money, decisions.
- **Goals:** keep membership and records accurate; make and communicate decisions.
- **Access level:** Admin
- **Contexts:** Desktop; Returning
- **Repo signals:** `board`, `committee`, `officer`, `treasurer` roles, membership admin, fees or payments tables, exports
- **Must:** approve, change and end memberships; see who has paid; export lists for official use.
- **Should:** hand over their role cleanly to a successor.
- **Could:** see participation trends.
- **Won't:** keep personal data longer than the association needs it.

---

## SHP: online shops

### G-SHP-01 · Shopper
- **Who:** Someone looking for products, not (yet) a customer.
- **Goals:** find the right product; compare; decide whether to buy.
- **Access level:** Anonymous
- **Contexts:** Mobile; First time
- **Repo signals:** `/products`, `/shop`, `/collections`, product and category tables, search, filters
- **Must:** find products by browsing and searching; see price, availability and delivery cost before checkout; trust the shop with payment.
- **Should:** compare options; see reviews or photos from others.
- **Could:** save a wishlist.
- **Won't:** need an account to buy.

### G-SHP-02 · Customer
- **Who:** Someone who has bought and comes back to buy again or follow up an order.
- **Goals:** check out quickly; track orders; return or reorder.
- **Access level:** Signed-in
- **Contexts:** Mobile; Returning
- **Repo signals:** cart, checkout, orders table, Stripe/Mollie integration, `/orders`, `/account/orders`
- **Must:** pay with a familiar method; know the order went through; track delivery; start a return.
- **Should:** reorder in a few taps.
- **Could:** save addresses and payment methods.
- **Won't:** be charged twice for one order.

### G-SHP-03 · Store manager
- **Who:** Someone who runs the catalogue, prices, stock and orders.
- **Goals:** keep the catalogue accurate; process orders; see sales.
- **Access level:** Admin
- **Contexts:** Desktop; Returning
- **Repo signals:** product admin routes, inventory tables, discount codes, order status workflow
- **Must:** add and edit products and prices; see and update order status; handle refunds.
- **Should:** be warned about low stock.
- **Could:** run promotions.
- **Won't:** see full card details.

### G-SHP-04 · Fulfilment staff
- **Who:** Someone who picks, packs and ships orders.
- **Goals:** know what to ship next; ship correctly; mark it done.
- **Access level:** Elevated
- **Contexts:** Mobile; Returning
- **Repo signals:** packing slips, shipping-label integrations, `fulfilment` or `shipping` statuses
- **Must:** see a clear queue of orders to ship; print or get labels; mark orders shipped so customers are told.
- **Should:** flag problems (out of stock, damaged).
- **Could:** scan items to confirm picks.
- **Won't:** change prices or refunds.

---

## SAS: SaaS and B2B software

### G-SAS-01 · Trial user
- **Who:** Someone testing whether the product solves their problem before paying.
- **Goals:** reach the first useful result quickly; judge whether it's worth paying for.
- **Access level:** Signed-in
- **Contexts:** Desktop; First time
- **Repo signals:** `trial` plan or status, onboarding routes, sample data, plan limits
- **Must:** get to a useful result in the first session; understand what a paid plan adds; keep their work when upgrading.
- **Should:** get help in the product when stuck.
- **Could:** invite a colleague to try it with them.
- **Won't:** be asked for a card before seeing value (unless that's the business model).

### G-SAS-02 · Team member
- **Who:** Someone using the product daily as part of their team's work.
- **Goals:** get their work done fast; collaborate with colleagues.
- **Access level:** Signed-in
- **Contexts:** Desktop; Returning
- **Repo signals:** `member` role within a `workspace`, `organization` or `team` table, per-tenant RLS
- **Must:** do frequent tasks in few steps; see and share what colleagues are working on; trust that data is saved.
- **Should:** be notified about what concerns them only.
- **Could:** customise their own view.
- **Won't:** see other organisations' data.

### G-SAS-03 · Workspace admin
- **Who:** A customer-side person who manages their team's access and settings.
- **Goals:** add and remove people; set up the workspace for the team.
- **Access level:** Admin
- **Contexts:** Desktop
- **Repo signals:** `admin` or `owner` role scoped to a workspace, invites table, workspace settings routes
- **Must:** invite and remove members; set roles; change workspace settings.
- **Should:** see who has access to what.
- **Could:** connect single sign-on.
- **Won't:** change other workspaces.

### G-SAS-04 · Billing owner
- **Who:** The person responsible for paying and for the contract.
- **Goals:** pay correctly; get invoices; control cost.
- **Access level:** Admin
- **Contexts:** Desktop
- **Repo signals:** subscription, plan and invoice tables, Stripe customer portal, `/billing`
- **Must:** change plan and seats; download invoices; update the payment method.
- **Should:** be warned before limits or renewals.
- **Could:** split costs across departments.
- **Won't:** need to contact sales for routine changes.

### G-SAS-05 · Developer / API consumer
- **Who:** A developer connecting their own systems to the product.
- **Goals:** integrate quickly and reliably; debug when something breaks.
- **Access level:** Signed-in
- **Contexts:** Desktop
- **Repo signals:** `/api`, API key tables, OpenAPI specs, SDKs, `/docs/api`, webhook settings
- **Must:** create and revoke API keys; find accurate docs with examples; get clear error messages.
- **Should:** test without touching production data.
- **Could:** see request logs.
- **Won't:** face breaking changes without notice.

### G-SAS-06 · Invited guest
- **Who:** Someone outside the organisation who was invited to see or comment on specific items.
- **Goals:** see what was shared with them; respond; leave.
- **Access level:** Signed-in
- **Contexts:** First time; Mobile
- **Repo signals:** share links, `guest` role, per-item permissions, magic links
- **Must:** open what was shared without a long signup; act on it (comment, approve); see only what was shared.
- **Should:** be notified when it changes.
- **Could:** become a full user later.
- **Won't:** see anything not shared with them.

---

## MKT: marketplaces and booking platforms

### G-MKT-01 · Buyer / booker
- **Who:** Someone looking to buy or book from one of many sellers or providers.
- **Goals:** find a good match; transact safely; resolve problems.
- **Access level:** Signed-in
- **Contexts:** Mobile; First time; Returning
- **Repo signals:** listings, bookings or orders tables, availability calendars, reviews, messaging between parties
- **Must:** search and filter listings; see real availability and the total price; pay safely; reach the seller.
- **Should:** read reviews from past buyers.
- **Could:** save searches and get alerts.
- **Won't:** share contact or payment details directly with sellers outside the platform.

### G-MKT-02 · Seller / provider
- **Who:** Someone offering products, services or spaces through the platform.
- **Goals:** get found; manage requests and availability; get paid.
- **Access level:** Signed-in
- **Contexts:** Mobile; Returning
- **Repo signals:** listing management routes, payouts, Stripe Connect, availability settings
- **Must:** create and manage listings; accept or decline requests; know when and how much they're paid.
- **Should:** reply to buyers quickly.
- **Could:** see how listings perform.
- **Won't:** see buyers' payment details.

### G-MKT-03 · Trust & safety reviewer
- **Who:** Platform staff who check listings, accounts and transactions for fraud and rule-breaking.
- **Goals:** catch bad actors early; resolve disputes fairly.
- **Access level:** Elevated
- **Contexts:** Desktop
- **Repo signals:** verification status, disputes or reports tables, review queues, flags
- **Must:** see flagged items in a queue; suspend listings or accounts with a reason; see a party's history before deciding.
- **Should:** resolve disputes with both sides' evidence.
- **Could:** tune automated flags.
- **Won't:** act without a recorded reason.

---

## INT: internal tools

### G-INT-01 · Operator
- **Who:** Staff who use the tool daily to do the organisation's work: entering, processing, scheduling.
- **Goals:** get through their queue quickly and correctly.
- **Access level:** Elevated
- **Contexts:** Desktop; Returning
- **Repo signals:** internal routes behind SSO, work-queue or status fields, bulk actions, staff roles
- **Must:** see what needs doing next; complete common tasks in few steps; avoid entering the same data twice.
- **Should:** use keyboard shortcuts and bulk actions.
- **Could:** save personal filters.
- **Won't:** change records outside their responsibility.

### G-INT-02 · Approver
- **Who:** Someone who checks and signs off on what operators prepared.
- **Goals:** decide quickly with the right information; keep accountability.
- **Access level:** Elevated
- **Contexts:** Mobile; Desktop
- **Repo signals:** approval or review statuses, `manager` role, sign-off fields, notifications
- **Must:** see what waits for approval; approve or reject with a comment; see who approved what.
- **Should:** approve from a phone.
- **Could:** delegate approvals while away.
- **Won't:** be able to approve their own submissions.

### G-INT-03 · Analyst
- **Who:** Someone who reads data and reports but doesn't change records.
- **Goals:** answer questions with data; share findings.
- **Access level:** Signed-in
- **Contexts:** Desktop
- **Repo signals:** `viewer` or `readonly` role, dashboards, reports routes, CSV exports
- **Must:** filter and view the data they're allowed to see; export it; trust that it's current.
- **Should:** save and share views.
- **Could:** schedule reports.
- **Won't:** edit source records.

### G-INT-04 · Auditor
- **Who:** Someone who verifies that processes and data handling follow the rules.
- **Goals:** reconstruct what happened, when and by whom.
- **Access level:** Elevated
- **Contexts:** Desktop
- **Repo signals:** audit or event-log tables, `auditor` role, retention settings
- **Must:** see a complete, tamper-evident history of changes; filter it by person, record and time; export evidence.
- **Should:** see who has access to what at any moment.
- **Could:** get alerts on unusual activity.
- **Won't:** change any data.
