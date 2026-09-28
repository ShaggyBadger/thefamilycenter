# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Python 3.14, Django 5.2, Wagtail 8, Django templates, and PostgreSQL in Docker Compose. SQLite is used for direct local CEO-demo work.

## Users

Families and community members in Winston-Salem are the primary audience. Their main job on the site is to find confirmed event information and decide how to attend. Local businesses and supporters are secondary audiences seeking approved ways to support the organization.

## Product Purpose

Provide a trusted, accessible, mobile-first website that makes The Family Center's confirmed events and approved organizational information easy to find and use. Keep current work distinct from future aspirations.

## Positioning

Canonical Wagtail pages hold each event's practical details and action link; the homepage and events index draw from those records so families can plan participation without searching through duplicated or stale event copy.

## Operating Context

The owner and CEO manage events and informational pages through Wagtail. The homepage layout and copy are code-owned; its event listings come from Wagtail records. The CEO is a staff editor below superuser. Local demo content may include legacy-site snapshots and illustrative copy for review; production content is entered separately after approval. The first launch uses external donation and event-registration services.

## Capabilities and Constraints

- The homepage prioritizes event attendance for families and community members; business support is a secondary path.
- Event pages use structured fields for date/time, venue/address, audience, cost, schedule, accessibility, transportation, parking, food, what to bring, images, and an event-specific action.
- Contact inquiries collect only name, email, and message; no sensitive details about children are requested.
- Do not process payments or attendee registration in Django for the first launch.
- Do not copy the SQLite database file into PostgreSQL. Production starts from migrations and receives approved content manually.
- Contact email/sender details, the active status of school-supply work, mission/vision copy, actual events, and partner terms require owner/CEO confirmation.

## Brand Commitments

- The organization is The Family Center, serving Winston-Salem, North Carolina.
- Use `instructions/homepage-preview.html` as visual inspiration, with the event-finding path primary. Its copy, example events, and photos are not approved for production.
- Keep five visual themes selectable after launch. Audience/content alternatives are local-demo comparisons; publish one selected canonical content set.
- Keep public language respectful and do not present unconfirmed programs or legacy claims as current services.

## Evidence on Hand

- `COMMANDERS_INTENT.md` contains the owner-approved project purpose and website-specific intent.
- `instructions/thefamilycenternc-content-inventory.json` is a public-site snapshot captured on 2026-09-25. Its mission/service wording, event details, contact details, and photos require review; some event addresses and service lists conflict.
- `content/demo-site-content.json` contains explicitly unapproved draft copy, CEO-review mission/vision syntheses, and fictional event examples.
- No event records, photos, or organization-approved public page copy have been seeded into Wagtail production content.

## Product Principles

1. Put confirmed event details and the next participation action first for families and community members.
2. Publish only owner/CEO-approved facts and distinguish current work from future aspirations.
3. Keep one canonical Wagtail page per event and derive event listings from those records.
4. Collect the minimum contact information needed and restrict inquiry access.
5. Keep demo alternatives, source snapshots, and unverified media out of production.

## Accessibility & Inclusion

Design mobile-first with semantic HTML, keyboard access, visible focus, reduced-motion support, readable event logistics, and accessible image descriptions. Use respectful language that does not reduce young people or families to hardship.
