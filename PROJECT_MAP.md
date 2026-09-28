# Project Map

Last reviewed: 2026-09-26

Use this page to find the main parts of the repository. Update it whenever an app, package, or major responsibility is added, moved, or renamed.

## Current repository structure

The project now has a Django/Wagtail 8 foundation: a custom user model, a code-owned Django homepage, Wagtail informational and event page types, contact-submission storage, and a Wagtail site tree. The local Docker preview is seeded with existing-site copy and event records marked for owner/CEO review; it is noindex and is not production content.

| Path | Responsibility |
| --- | --- |
| `COMMANDERS_INTENT.md` | Owner-approved project-wide purpose and guiding direction. |
| `manage.py` | Django command-line entry point. |
| `config/` | Project configuration: settings, Wagtail/Django URL routes, a site-navigation context processor, and ASGI/WSGI entry points. |
| `accounts/` | Custom Django user model established before organization-specific app migrations. |
| `pages/` | Code-owned Django homepage view, Wagtail site-tree root, and standard informational page type. |
| `events/` | Wagtail event index and canonical per-event page model with structured details. |
| `contact/` | Minimal contact inquiry model, retention cleanup command, and limited Wagtail inbox viewset. |
| `templates/` | Shared accessible site shell and templates for the Django homepage, Wagtail content pages, event index, and event pages. |
| `static/css/site.css` | Initial responsive design tokens and public-site styles; supports later theme variants. |
| `compose.yaml` | Local Docker Compose services: Django development server and PostgreSQL. |
| `content/demo-site-content.json` | Page-keyed local demo draft with CEO-review mission/vision drafts and clearly marked fictional event examples. |
| `pages/management/commands/seed_local_preview.py` | Explicit DEBUG-only command to seed the local Wagtail preview from the local existing-site inventory; never seeds production. |
| `instructions/homepage-preview.html` | Local-only visual concept reference; its copy, sample events, and photos are not approved production content. |
| `Dockerfile` | Image used for the Django development container. |
| `requirements.txt` | Django 5.2, Wagtail 8.0, and the PostgreSQL driver. |
| `db-wagtail.sqlite3` | New local SQLite database for Wagtail development; ignored by Git. The former `db.sqlite3` is preserved separately. |
| `README.md` | Start-here page with local run instructions and links to project documentation. |
| `instructions/` | Local-only guidance, planning notes, and source inventory; ignored by Git. |

## Remaining implementation direction

- Finish the CEO's restricted event-editor permissions and the contact-inbox permission group.
- Add the partners app after eligibility and sponsorship terms are settled.
- Build the five visual themes and the local content/audience comparison controls.
- Add the public contact submission flow after confirming the organization sender/provider and notification address.
- Load only owner/CEO-approved public facts, pages, events, and media.

See [DECISION_LOG.md](DECISION_LOG.md) for the status of these choices. Check the actual code before treating planned structure as implemented.
