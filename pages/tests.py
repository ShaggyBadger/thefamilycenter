import json
import re
from datetime import timedelta
from unittest.mock import patch

from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone
from wagtail.models import Site

from events.models import EventPage, EventsIndexPage
from .models import HomePage
from .wagtail_hooks import require_reviewed_page_content


class WagtailPublicPageTests(TestCase):
    @override_settings(DEBUG=True)
    def test_homepage_is_served_from_the_site_root(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, "home")
        self.assertTemplateUsed(response, "pages/home_page.html")
        self.assertContains(response, "The Family Center")
        self.assertContains(response, "No upcoming events are listed right now.")
        self.assertContains(response, "Helping students enter high school ready to thrive.")
        self.assertContains(response, "Building strong foundations")
        self.assertContains(response, "Growing skills and confidence")
        self.assertContains(response, "Student Readiness in Winston-Salem")
        self.assertContains(response, "The Family Center’s purpose is to prepare")
        self.assertContains(response, "Local preview · Event details are for review")
        self.assertContains(response, 'name="robots" content="noindex,nofollow"')

    def test_local_robots_disallow_crawling_and_hide_the_sitemap(self):
        robots_response = self.client.get("/robots.txt")

        self.assertEqual(robots_response.status_code, 200)
        self.assertContains(robots_response, "User-agent: *")
        self.assertContains(robots_response, "Disallow: /")
        self.assertEqual(self.client.get("/sitemap.xml").status_code, 404)

    @override_settings(
        DEBUG=False,
        DJANGO_SITE_INDEXABLE=True,
        PUBLIC_SITE_URL="https://thefamilycenternc.org",
    )
    def test_indexable_homepage_has_local_seo_metadata_and_organization_schema(self):
        response = self.client.get("/")
        html = response.content.decode()
        schema_match = re.search(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<link rel="canonical" href="https://thefamilycenternc.org/">',
            html=False,
        )
        self.assertContains(response, 'property="og:type" content="website"')
        self.assertNotContains(response, 'name="robots" content="noindex,nofollow"')
        self.assertNotContains(response, "Local preview")
        self.assertIsNotNone(schema_match)

        schema = json.loads(schema_match.group(1))
        self.assertEqual(schema["@type"], "NGO")
        self.assertEqual(schema["name"], "The Family Center")
        self.assertEqual(schema["areaServed"]["name"], "Winston-Salem")

    @override_settings(
        DEBUG=False,
        DJANGO_SITE_INDEXABLE=True,
        PUBLIC_SITE_URL="https://thefamilycenternc.org",
        ALLOWED_HOSTS=["thefamilycenternc.org"],
    )
    def test_production_robots_and_sitemap_use_the_public_domain(self):
        robots_response = self.client.get(
            "/robots.txt", secure=True, HTTP_HOST="thefamilycenternc.org"
        )
        site = Site.objects.get(is_default_site=True)
        site.hostname = "thefamilycenternc.org"
        site.port = 443
        site.save(update_fields=["hostname", "port"])

        sitemap_response = self.client.get(
            "/sitemap.xml", secure=True, HTTP_HOST="thefamilycenternc.org"
        )

        self.assertContains(
            robots_response, "Sitemap: https://thefamilycenternc.org/sitemap.xml"
        )
        self.assertEqual(sitemap_response.status_code, 200)
        self.assertContains(sitemap_response, "https://thefamilycenternc.org/")

    @override_settings(DEBUG=True)
    def test_homepage_features_the_next_live_wagtail_event(self):
        events_index = EventsIndexPage.objects.get(slug="events")
        event = EventPage(
            title="Family Resource Day",
            slug="family-resource-day",
            summary="A gathering for families.",
            start_datetime=timezone.now() + timedelta(days=10),
            venue_name="Community Hall",
            call_to_action_label="Register",
            call_to_action_url="https://example.test/register",
        )
        events_index.add_child(instance=event)
        event.save_revision().publish()

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["featured_event"])
        self.assertContains(response, "Family Resource Day")
        self.assertContains(response, "Community Hall")
        self.assertContains(response, "View event details")
        self.assertContains(response, "Local preview · details need confirmation")

    @override_settings(DEBUG=False)
    def test_confirmed_events_without_ctas_are_public_outside_local_preview(self):
        events_index = EventsIndexPage.objects.get(slug="events")
        events = [
            EventPage(
                title="Unconfirmed Gathering",
                slug="unconfirmed-gathering",
                start_datetime=timezone.now() + timedelta(days=10),
                call_to_action_label="Register",
                call_to_action_url="https://example.test/register",
            ),
            EventPage(
                title="Missing Event Action",
                slug="missing-event-action",
                start_datetime=timezone.now() + timedelta(days=11),
                verification_status=EventPage.VERIFIED,
            ),
        ]
        for event in events:
            events_index.add_child(instance=event)
            event.save_revision().publish()

        response = self.client.get("/")
        index_response = self.client.get("/events/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Unconfirmed Gathering")
        self.assertContains(response, "Missing Event Action")
        self.assertEqual(
            response.context["featured_event"].title, "Missing Event Action"
        )
        self.assertEqual(index_response.status_code, 200)
        self.assertNotContains(index_response, "Unconfirmed Gathering")
        self.assertContains(index_response, "Missing Event Action")

    def test_events_index_has_an_accurate_empty_state(self):
        response = self.client.get("/events/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upcoming events")
        self.assertContains(response, "No upcoming events are listed right now.")

    def test_event_page_renders_its_structured_details_and_action(self):
        events_index = EventsIndexPage.objects.get(slug="events")
        event = EventPage(
            title="Family Resource Day",
            slug="family-resource-day",
            summary="A community gathering for families.",
            start_datetime=timezone.now() + timedelta(days=10),
            venue_name="Community Hall",
            address="10 Main Street",
            cost="Free",
            call_to_action_label="Register",
            call_to_action_url="https://example.test/register",
        )
        events_index.add_child(instance=event)
        event.save_revision().publish()

        response = self.client.get("/events/family-resource-day/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Family Resource Day")
        self.assertContains(response, "Community Hall")
        self.assertContains(response, "Register")

    @override_settings(DEBUG=False)
    def test_unapproved_homepage_cannot_be_published_in_production(self):
        homepage = HomePage.objects.get(slug="home", depth=2)
        request = RequestFactory().post("/admin/pages/3/", {})

        with patch("pages.wagtail_hooks.messages.error"):
            response = require_reviewed_page_content(request, homepage)

        self.assertEqual(response.status_code, 302)
