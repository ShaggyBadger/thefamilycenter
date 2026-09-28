# Technical Decision Log

Record project-wide technical choices here. Status labels distinguish an agreed direction from a decision already implemented. Update the status when code catches up with planning or a decision changes.

## D-001: Wagtail for public editorial content

- **Status:** Updated; Wagtail foundation implemented, approved content pending
- **Date:** 2026-09-26 (revised; original decision 2026-09-25)
- **Decision:** Use Wagtail for event pages and approved informational content. Render the public homepage with a code-owned Django view and template; it reads event records from Wagtail. Keep the Wagtail homepage model as the site-tree root so existing event and editorial URLs remain stable.
- **Reason:** A bespoke homepage can be designed and iterated directly in templates and CSS, while Wagtail remains focused on the content that staff update frequently, especially events.
- **Framework target:** Wagtail 8.0 with the current Python 3.14.7 and Django 5.2.x baseline. Official compatibility tables list this combination. An isolated local smoke test with Django 5.2.17, Wagtail 8.0, and Wagtail Transfer 0.11 passed Django's system check and loaded both Wagtail and transfer migrations; a full content/media round trip has not been tested.

## D-002: Django templates render Wagtail pages

- **Status:** Starter templates implemented; visual design and final themes pending
- **Date:** 2026-09-25
- **Decision:** Use Django templates, Tailwind CSS, and Alpine.js for the public site. Wagtail page-type templates extend the shared `base.html` and fill its named `{% block content %}`; do not inject a whole template through a generic `{{ content }}` variable.
- **Editor model:** Developers define page types, fields, reusable block types, and their templates. Editors manage page content and compose from approved blocks; the experience is structured, not an unrestricted visual canvas.

## D-003: Events are canonical Wagtail landing pages

- **Status:** Event page model and initial listing behavior implemented; content workflow pending
- **Date:** 2026-09-26
- **Decision:** Create one canonical Wagtail page for each event, with structured dates/times, venue, short summary, details, and an editor-configured action. Editors fill the event-specific values when creating each event. Populate upcoming lists from event dates, allow optional featuring, and place ended events in a past-events list while retaining their public pages by default. Publish only confirmed event details and a real action link.
- **Registration:** Start with an external registration or contact URL as appropriate. Built-in registration and attendee-data collection are not currently planned.

## D-004: Design and test mobile-first

- **Status:** Agreed; pending implementation
- **Date:** 2026-09-25
- **Decision:** Design the phone experience first, prioritizing readable content, clear actions, event details, accessibility, and loading performance; then enhance the layout for larger screens.
- **Reason:** The owner expects many visitors to use phones, so the mobile experience is the primary design target rather than a later responsive adjustment.

## D-005: Five presentation themes for the CEO demo

- **Status:** Agreed direction; pending visual design and implementation
- **Date:** 2026-09-26
- **Decision:** Prepare five site themes that can be selected by an administrator through one global Wagtail setting, both in the local CEO demo and after launch. Themes change presentation only; they share the same content, URLs, audience, and SEO behavior.
- **Implementation note:** Define complete semantic tokens and check contrast/accessibility across themes. Theme selection and avatar/content-concept selection are separate controls.

## D-006: Content concepts for local presentation

- **Status:** Agreed direction; pending CEO review
- **Date:** 2026-09-26
- **Decision:** Include the audience/content alternatives under consideration in the local CEO demo. After the CEO selects a direction, establish one canonical public content set and remove unselected content alternatives before launch. These content choices remain separate from the visual-theme setting in D-005.
- **Reason:** The site should not expose duplicate SEO pages or let a demo setting accidentally change production content.

## D-007: Initial content promotion to PostgreSQL

- **Status:** Agreed direction for initial launch; pending implementation
- **Date:** 2026-09-26
- **Decision:** Initialize production PostgreSQL from the approved Django migrations, then create the CEO-approved launch pages directly in the production Wagtail admin. Do not copy or rsync the SQLite database file to the Linode server: PostgreSQL cannot use a SQLite database file, and copying it would move the entire database rather than just approved public content.
- **Reason:** The initial public site has a limited set of pages, so direct Wagtail entry avoids adding a hosted staging source and transfer workflow before they are needed.
- **Admin accounts:** Agreed: create a fresh production superuser and separate production staff/admin accounts in PostgreSQL during deployment. Assign least-privilege roles and do not migrate local admin credentials, sessions, or development-user data.
- **Future tooling:** Wagtail Transfer may be evaluated later if repeated content promotion justifies a hosted, reachable source. Its installed app and migrations passed a local smoke test with Wagtail 8.0, but its published package classifiers list Wagtail 6 and 7, not Wagtail 8; test a full page/dependency/media round trip before adopting it. Approved media is managed separately from database records and should be uploaded only after rights/consent checks.
- **Safety:** If an automated import is adopted later, require an explicit target, dependency/collision checks, idempotent behavior, and tests against disposable SQLite/PostgreSQL databases. Obtain explicit confirmation before any remote or production write.

## D-008: Staff-only accounts for the first launch

- **Status:** Agreed direction; custom user model implemented, production staff setup pending
- **Date:** 2026-09-25
- **Decision:** Use a custom Django user model established before the first organization-specific migrations. Initially create the owner as superuser and a separate CEO account that can edit and publish Wagtail content. Do not enable public sign-up at launch; consider public accounts only when a concrete user-facing need is approved.
- **Permissions:** Keep the CEO account below superuser; add other Wagtail editors only if requested, using least-privilege groups.

## D-009: Separate apps by responsibility

- **Status:** Accounts, pages, events, and contact foundations started; partners app and remaining workflows pending
- **Date:** 2026-09-25
- **Decision:** Keep distinct responsibilities in cohesive Django apps rather than combining unrelated behavior. Organize page types by content domain; the homepage is a page type, not automatically its own app. Use Wagtail's built-in admin, adding a project app only for genuine custom admin behavior.
- **Initial direction:** Use separate `pages`, `events`, `accounts`, `contact`, and `partners` apps. The `pages` app owns the homepage and standard information page types; `events` owns event pages and date behavior; `accounts` owns the custom user model; `contact` owns stored inquiries, notifications, and retention; `partners` owns business supporter profiles and the no-account approval workflow. Defer dedicated payment/donation and program apps until those workflows are approved and have behavior beyond editorial pages.

## D-010: Project Commander's Intent

- **Status:** Approved by the owner
- **Date:** 2026-09-25
- **Decision:** Use the one-paragraph statement in `COMMANDERS_INTENT.md` as the durable guiding intent for the site project. Every substantial plan must include a concise intent consistent with it, and the owner must explicitly approve the intent before implementation begins.

## D-011: Contact inquiries for the first launch

- **Status:** Inquiry model and restricted Wagtail inbox foundation implemented; public email and sender/provider pending confirmation
- **Date:** 2026-09-26
- **Decision:** The public form collects only name, email, and message. Store submissions until resolved; notify the CEO only. Give the CEO and owner access through a limited Wagtail inbox for reviewing and resolving inquiries, without granting the CEO general Django-model admin access. Delete resolved submissions after 90 days and unresolved submissions after one year at the latest. Show the form plus an organization-controlled public email once the CEO confirms the address.
- **Privacy:** Do not solicit sensitive information about children through a general contact form. Define deletion, backups, CSRF/spam protection, and notification-failure handling before implementation.

## D-012: Image approval before upload

- **Status:** Agreed direction; pending implementation
- **Date:** 2026-09-25
- **Decision:** Upload only photos with confirmed reuse permission and any required subject/guardian consent, especially photos of young people. The CEO may publish approved uploaded images directly under their Wagtail editor permissions.

## D-013: Local and production database roles

- **Status:** Agreed direction; pending implementation
- **Date:** 2026-09-25
- **Decision:** Use SQLite for local CEO demo/content authoring, Docker Compose PostgreSQL running locally for PostgreSQL rehearsal, and Linode PostgreSQL for production. Do not use an SSH tunnel to make the production database the routine target for local development.

## D-014: First-launch payments and measurement

- **Status:** Agreed direction; pending owner configuration and implementation
- **Date:** 2026-09-25
- **Decision:** Use external donation and event-registration links at first launch; do not process payments or store card data in Django. Plan for Google Analytics and Search Console using owner-provided access, and do not add advertising pixels unless separately approved and reflected in the privacy approach.

## D-015: Technical SEO and browser identity baseline

- **Status:** Agreed direction; pending implementation
- **Date:** 2026-09-25
- **Decision:** Treat unique page titles/descriptions, canonicals, an XML sitemap, environment-aware robots/noindex rules, accurate structured data, redirects, approved favicons, and social preview metadata as launch requirements. Keep demo/staging content out of search and include only published canonical pages in the sitemap.
- **Note:** Favicons support recognition and browser usability; they are not a direct search-ranking factor. SEO work should focus on accurate, useful content and sound technical indexing, without promising rankings.

## D-016: Primary audience and event participation

- **Status:** Agreed direction; pending implementation
- **Date:** 2026-09-26
- **Decision:** Families and community members are the primary audience. The site's primary job is to make it easy for them to find and attend events. Businesses and supporters remain secondary audiences. Keep About and What We Do as separate pages.
- **Event experience:** Use the homepage and Events index to make upcoming events easy to find; each event has its own canonical Wagtail page and event-specific action, such as registration or another confirmed way to participate.

## D-017: Accuracy of public organization claims

- **Status:** Agreed publication rule; factual details pending confirmation
- **Date:** 2026-09-26
- **Decision:** Publish organization facts and mission/vision wording only after owner/CEO approval. The approved service area supplied for the plan is Winston-Salem, North Carolina. There are not yet approved public mission or vision statements; prepare the synthesized drafts in `content/demo-site-content.json` for CEO review, using the legacy website copy only as historical source material. The status of school-supply support is unconfirmed; no ongoing youth programs are currently identified. Do not present unverified or aspirational work as a current service.
- **Events:** Follow the confirmed-details-only rule in D-003. Unapproved sample events and placeholder logistics remain private demo content.

## D-018: Business-partner recognition at launch

- **Status:** Agreed initial direction; profile eligibility and sponsorship terms pending CEO discussion
- **Date:** 2026-09-26
- **Decision:** Include profiles for approved business partners. A basic profile may show the approved business name, logo, website link, and a neutral acknowledgment; when relevant, identify the specific event the business sponsors. The CEO and business contact must approve the exact event-sponsor wording. Do not publish unapproved tiers, donation amounts, or benefits. Business contacts do not receive site accounts.

## D-019: Plan-specific Commander's Intent

- **Status:** Approved by the owner; foundation implementation started
- **Date:** 2026-09-26
- **Decision:** Build a mobile-first Django site for Winston-Salem families and community members, using Wagtail for events and approved informational content. Make confirmed events easy to find and attend, clearly separate approved current work from future aspirations, and give staff secure tools to manage content and inquiries.

## D-020: Homepage preview as a visual reference

- **Status:** Implemented
- **Date:** 2026-09-26
- **Decision:** Use the existing brand palette and typography to build a distinctive, code-owned homepage focused on finding events. The old concept is inspiration for layout only, not approved copy, event data, or image permissions. Render live event details from Wagtail records and include informational links only when the corresponding pages are live and approved.
