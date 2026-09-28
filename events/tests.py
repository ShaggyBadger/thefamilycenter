from datetime import datetime, timezone
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase, override_settings

from .models import EventPage, EventsIndexPage
from pages.wagtail_hooks import require_reviewed_page_content


class EventPageValidationTests(TestCase):
    def test_end_must_follow_start(self):
        event = EventPage(
            title="Sample event",
            slug="sample-event",
            start_datetime=datetime(2026, 10, 24, 11, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 10, 24, 10, tzinfo=timezone.utc),
        )

        with self.assertRaises(ValidationError) as error:
            event.clean()

        self.assertIn("end_datetime", error.exception.message_dict)


class EventPublicationGuardTests(TestCase):
    @override_settings(DEBUG=False)
    def test_unconfirmed_event_cannot_be_published_in_production(self):
        events_index = EventsIndexPage.objects.get(slug="events")
        event = EventPage(
            title="Source event",
            slug="source-event",
            start_datetime=datetime(2026, 11, 21, 11, tzinfo=timezone.utc),
            verification_status=EventPage.NEEDS_CONFIRMATION,
        )
        events_index.add_child(instance=event)
        request = RequestFactory().post("/admin/pages/4/", {})

        with patch("pages.wagtail_hooks.messages.error"):
            response = require_reviewed_page_content(request, event)

        self.assertEqual(response.status_code, 302)
