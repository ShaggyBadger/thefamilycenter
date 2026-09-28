import json
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.html import format_html, format_html_join, strip_tags
from django.utils.text import slugify

from events.models import EventPage, EventsIndexPage
from pages.models import HomePage


class Command(BaseCommand):
    help = "Seed the local Wagtail preview from the existing-site JSON snapshot."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-inventory",
            default=str(settings.BASE_DIR / "instructions/thefamilycenternc-content-inventory.json"),
            help="Local-only JSON inventory captured from the existing public site.",
        )
        parser.add_argument(
            "--demo-content",
            default=str(settings.BASE_DIR / "content/demo-site-content.json"),
            help="JSON file containing the CEO-review mission and vision drafts.",
        )
        parser.add_argument(
            "--confirm-local-preview",
            action="store_true",
            help="Confirm that unapproved source content is being added to the local preview only.",
        )
        parser.add_argument(
            "--refresh",
            action="store_true",
            help="Refresh records previously created by this command; leave other content untouched.",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("This command is disabled when DEBUG is false.")
        if not options["confirm_local_preview"]:
            raise CommandError(
                "Pass --confirm-local-preview to add unapproved source data to the local preview."
            )

        inventory_path = Path(options["source_inventory"])
        demo_path = Path(options["demo_content"])
        if not inventory_path.is_file():
            raise CommandError(f"Source inventory not found: {inventory_path}")
        if not demo_path.is_file():
            raise CommandError(f"Demo content JSON not found: {demo_path}")

        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        demo_content = json.loads(demo_path.read_text(encoding="utf-8"))
        source_pages = {page["key"]: page for page in inventory["pages"]}
        demo_pages = demo_content["pages"]
        source_site = inventory["inventory_metadata"]["source_site"]
        captured_on = inventory["inventory_metadata"]["captured_on"]

        with transaction.atomic():
            homepage = HomePage.objects.get(slug="home", depth=2)
            events_index = EventsIndexPage.objects.get(slug="events", depth=3)
            focus_areas = next(
                section
                for section in demo_pages["home"]["sections"]
                if section["type"] == "focus_areas"
            )["items"]
            seeded_pages = self._seed_homepage(
                homepage,
                source_pages["home"],
                focus_areas,
                source_site,
                captured_on,
                options["refresh"],
            )

            about_body, about_notes = self._about_content(
                source_pages["home"], demo_pages["about"]
            )
            seeded_pages += self._seed_standard_page(
                homepage,
                slug="about",
                title="About",
                source_reference=f"{source_site}/ (mission and vision snapshot)",
                body=about_body,
                editor_notes=about_notes,
                show_in_menus=True,
                refresh=options["refresh"],
            )

            work_body, work_notes = self._services_content(source_pages)
            seeded_pages += self._seed_standard_page(
                homepage,
                slug="what-we-do",
                title="What We Do",
                source_reference=f"{source_site}/our-services (service lists captured {captured_on})",
                body=work_body,
                editor_notes=work_notes,
                show_in_menus=True,
                refresh=options["refresh"],
            )

            business_body, business_notes = self._business_content(demo_pages)
            seeded_pages += self._seed_standard_page(
                homepage,
                slug="business-partnerships",
                title="Business Partnerships",
                source_reference="content/demo-site-content.json (planning draft)",
                body=business_body,
                editor_notes=business_notes,
                show_in_menus=True,
                refresh=options["refresh"],
            )

            contact_body, contact_notes = self._contact_content(
                inventory["organization_contact_as_published"], captured_on
            )
            seeded_pages += self._seed_standard_page(
                homepage,
                slug="contact",
                title="Contact",
                source_reference=f"{source_site}/contact (captured {captured_on})",
                body=contact_body,
                editor_notes=contact_notes,
                show_in_menus=True,
                refresh=options["refresh"],
            )

            donate_body, donate_notes = self._donation_content(inventory, captured_on)
            seeded_pages += self._seed_standard_page(
                homepage,
                slug="donate",
                title="Donate",
                source_reference=f"{source_site}/ (donation snapshot captured {captured_on})",
                body=donate_body,
                editor_notes=donate_notes,
                show_in_menus=False,
                show_in_footer=True,
                refresh=options["refresh"],
            )

            seeded_events = sum(
                self._seed_event(events_index, event_data, captured_on, options["refresh"])
                for event_data in inventory.get("events", [])
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Local review preview seeded or refreshed: {seeded_pages} pages and "
                f"{seeded_events} source events. No source photos were imported."
            )
        )
        self.stdout.write(
            "All imported pages are marked for review; local preview pages are noindex."
        )

    def _seed_homepage(self, page, source_page, focus_areas, source_site, captured_on, refresh):
        hero = next(
            section for section in source_page["sections"] if section["type"] == "hero"
        )
        source_reference = f"{source_site}/ (captured {captured_on})"
        if page.source_reference:
            if page.source_reference != source_reference or not refresh:
                return 0
        elif (
            page.hero_heading
            or page.hero_body
            or page.hero_image_id
            or page.hero_image_caption
            or page.community_pillar_body
            or page.practical_support_pillar_body
            or page.future_direction_pillar_body
        ):
            return 0

        pillars = {
            "bring the community together": ("community_pillar_title", "community_pillar_body"),
            "meet immediate needs": ("practical_support_pillar_title", "practical_support_pillar_body"),
            "build toward ongoing youth development": (
                "future_direction_pillar_title",
                "future_direction_pillar_body",
            ),
        }
        page.hero_heading = hero.get("heading", "")
        page.hero_body = hero.get("subheading", "")
        for item in focus_areas:
            title_field, body_field = pillars[item["title"].casefold()]
            setattr(page, title_field, item["title"])
            setattr(page, body_field, item["summary"])
        page.review_status = "needs_review"
        page.source_reference = source_reference
        page.editor_notes = (
            "Legacy homepage copy captured from the public-site inventory and planning focus areas "
            "from content/demo-site-content.json. Confirm current-work statements before publication. "
            "Linked photos were omitted because reuse permission is unconfirmed."
        )
        self._publish_local_preview_page(page)
        return 1

    def _seed_standard_page(
        self,
        parent,
        *,
        slug,
        title,
        source_reference,
        body,
        editor_notes,
        show_in_menus,
        refresh,
        show_in_footer=False,
    ):
        return 0

    def _seed_event(self, events_index, event_data, captured_on, refresh):
        event_date = date.fromisoformat(event_data["date"])
        timezone_name = event_data.get("time_zone") or "America/New_York"
        event_timezone = ZoneInfo(timezone_name)
        start_time = time.fromisoformat(event_data.get("start_time") or "00:00")
        start_datetime = datetime.combine(event_date, start_time, tzinfo=event_timezone)
        end_datetime = None
        if event_data.get("end_time"):
            end_datetime = datetime.combine(
                event_date,
                time.fromisoformat(event_data["end_time"]),
                tzinfo=event_timezone,
            )

        title = event_data["title"]
        event_slug = f"{slugify(title)}-{event_date.isoformat()}"
        source_reference = (
            f"public_site_snapshot:{captured_on}:{event_date.isoformat()}:{slugify(title)}"
        )
        event = EventPage.objects.child_of(events_index).filter(slug=event_slug).first()
        is_new = event is None
        if event:
            if event.source_reference != source_reference or not refresh:
                return 0
        else:
            event = EventPage(title=title, slug=event_slug)

        description = event_data.get("description", "")
        address = (
            event_data.get("address_as_published")
            or event_data.get("address_as_published_in_listing")
            or ""
        )
        notes = [
            f"Existing public-site snapshot captured {captured_on}; source section: "
            f"{event_data.get('source_location', 'events listing')}.",
            "Confirm date, time, venue, audience, cost, and participation action before publication.",
        ]
        if event_data.get("address_conflict"):
            notes.append(event_data["address_conflict"])
        if not event_data.get("registration_or_event_url"):
            notes.append("No registration or event-action URL was present in the source snapshot.")

        event.title = title
        event.summary = strip_tags(description).strip()[:180]
        event.start_datetime = start_datetime
        event.end_datetime = end_datetime
        event.venue_name = event_data.get("venue", "") or ""
        event.address = address
        event.cost = event_data.get("ticket_price_text", "") or ""
        event.details = description
        event.call_to_action_label = ""
        event.call_to_action_url = event_data.get("registration_or_event_url") or ""
        event.verification_status = EventPage.NEEDS_CONFIRMATION
        event.source_reference = source_reference
        event.review_notes = " ".join(notes)
        if is_new:
            events_index.add_child(instance=event)
        self._publish_local_preview_page(event)
        return 1

    @staticmethod
    def _about_content(home_page, demo_about_page):
        home_sections = home_page["sections"]
        legacy_mission = next(section["body"] for section in home_sections if section["type"] == "mission")
        legacy_vision = next(section["body"] for section in home_sections if section["type"] == "vision")
        draft = next(
            section
            for section in demo_about_page["sections"]
            if section["type"] == "mission_vision_working_copy"
        )
        body = format_html(
            "<h2>Mission · CEO review draft</h2><p>{}</p>"
            "<h2>Vision · CEO review draft</h2><p>{}</p>",
            draft["mission_body"],
            draft["vision_body"],
        )
        editor_notes = format_html(
            "Legacy homepage mission (historical reference): {}\n\n"
            "Legacy homepage vision (historical reference): {}\n\n"
            "Do not publish these source statements without explicit owner/CEO approval.",
            legacy_mission,
            legacy_vision,
        )
        return body, str(editor_notes)

    @staticmethod
    def _services_content(source_pages):
        homepage = source_pages["home"]
        homepage_items = next(
            section["items"]
            for section in homepage["sections"]
            if section["type"] == "service_teasers"
        )
        services_items = source_pages["our_services"]["services"]
        homepage_list = format_html_join(
            "",
            "<li><strong>{}</strong>: {}</li>",
            ((item["title"], item["body"]) for item in homepage_items),
        )
        services_list = format_html_join(
            "",
            "<li><strong>{}</strong>: {}</li>",
            ((item["title"], item["body"]) for item in services_items),
        )
        body = format_html(
            "<p>The legacy website contains conflicting lists. These are shown for reconciliation, "
            "not as a confirmed list of current services.</p>"
            "<h2>Homepage list</h2><ul>{}</ul>"
            "<h2>Our Services page list</h2><ul>{}</ul>",
            homepage_list,
            services_list,
        )
        return body, "Ask the CEO which offerings are active and reconcile the two source lists before publication."

    @staticmethod
    def _business_content(demo_pages):
        page = demo_pages["business-partnerships"]
        hero = next(section for section in page["sections"] if section["type"] == "hero")
        options = next(
            section for section in page["sections"] if section["type"] == "partnership_options"
        )
        items = format_html_join(
            "",
            "<li>{}</li>",
            ((item["title"],) for item in options["items"]),
        )
        body = format_html(
            "<p>{}</p><h2>Possible ways to connect</h2><ul>{}</ul>"
            "<p>These draft options need CEO confirmation.</p>",
            hero["body"],
            items,
        )
        notes = "; ".join(
            f"{item['title']}: {item['availability']}" for item in options["items"]
        )
        return body, f"Draft heading: {hero['heading']}. Verify each proposed option. {notes}"

    @staticmethod
    def _contact_content(contact_details, captured_on):
        body = format_html(
            "<p>These values were copied from the public-site snapshot captured {}. "
            "Confirm each one before public use.</p><h2>Contact details as published</h2><ul>"
            "<li><strong>Phone:</strong> {}</li><li><strong>Email:</strong> {}</li>"
            "<li><strong>Mailing address:</strong> {}</li></ul>",
            captured_on,
            contact_details["phone"],
            contact_details["email"],
            contact_details["mailing_address"],
        )
        return body, contact_details.get("address_note", "")

    @staticmethod
    def _donation_content(inventory, captured_on):
        donation_url = inventory["organization_contact_as_published"].get("donation_url", "")
        body = format_html(
            "<p>The existing site links to an external donation provider. "
            "Confirm the destination, nonprofit/tax wording, and gift-use information before adding a live action.</p>"
            "<p>Source snapshot captured {}.</p>",
            captured_on,
        )
        return body, f"Legacy donation URL for confirmation (not linked from the page): {donation_url}"

    @staticmethod
    def _publish_local_preview_page(page):
        revision = page.save_revision(user=None, log_action=False)
        revision.publish(user=None, log_action=False, skip_permission_checks=True)
