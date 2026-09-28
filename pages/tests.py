from datetime import timedelta
from unittest.mock import patch

from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone

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
        self.assertContains(response, "A community that shows up for its young people.")
        self.assertContains(response, "Winston-Salem Community Events")
        self.assertContains(response, 'name="robots" content="noindex,nofollow"')

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

    @override_settings(DEBUG=False)
    def test_homepage_only_shows_public_ready_events_outside_local_preview(self):
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

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Unconfirmed Gathering")
        self.assertNotContains(response, "Missing Event Action")
        self.assertContains(response, "No upcoming events are listed right now.")

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
