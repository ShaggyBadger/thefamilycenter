from datetime import datetime, timedelta, timezone as datetime_timezone
from io import StringIO
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import ContactInquiryInboxForm
from .models import ContactSubmission


class PruneContactSubmissionsTests(TestCase):
    @patch("contact.management.commands.prune_contact_submissions.timezone.now")
    def test_prunes_resolved_and_overdue_open_inquiries(self, mocked_now):
        now = datetime(2026, 9, 26, 12, tzinfo=datetime_timezone.utc)
        mocked_now.return_value = now

        resolved_old = ContactSubmission.objects.create(
            name="Resolved", email="resolved@example.test", message="Resolved inquiry"
        )
        ContactSubmission.objects.filter(pk=resolved_old.pk).update(
            created_at=now - timedelta(days=150),
            is_resolved=True,
            resolved_at=now - timedelta(days=91),
        )
        resolved_recent = ContactSubmission.objects.create(
            name="Recent", email="recent@example.test", message="Recent resolution"
        )
        ContactSubmission.objects.filter(pk=resolved_recent.pk).update(
            created_at=now - timedelta(days=100),
            is_resolved=True,
            resolved_at=now - timedelta(days=89),
        )
        open_old = ContactSubmission.objects.create(
            name="Open", email="open@example.test", message="Unresolved inquiry"
        )
        ContactSubmission.objects.filter(pk=open_old.pk).update(
            created_at=now - timedelta(days=366)
        )

        output = StringIO()
        call_command("prune_contact_submissions", stdout=output)

        self.assertFalse(ContactSubmission.objects.filter(pk=resolved_old.pk).exists())
        self.assertTrue(ContactSubmission.objects.filter(pk=resolved_recent.pk).exists())
        self.assertFalse(ContactSubmission.objects.filter(pk=open_old.pk).exists())

    @patch("contact.management.commands.prune_contact_submissions.timezone.now")
    def test_dry_run_keeps_eligible_inquiries(self, mocked_now):
        now = datetime(2026, 9, 26, 12, tzinfo=datetime_timezone.utc)
        mocked_now.return_value = now
        inquiry = ContactSubmission.objects.create(
            name="Old", email="old@example.test", message="Old inquiry"
        )
        ContactSubmission.objects.filter(pk=inquiry.pk).update(
            created_at=now - timedelta(days=366)
        )

        call_command("prune_contact_submissions", dry_run=True, stdout=StringIO())

        self.assertTrue(ContactSubmission.objects.filter(pk=inquiry.pk).exists())

    @override_settings(DEBUG=False)
    def test_local_source_seed_is_refused_outside_debug(self):
        with self.assertRaises(CommandError):
            call_command(
                "seed_local_preview",
                confirm_local_preview=True,
                source_inventory="/does/not/need/to/exist.json",
                demo_content="/does/not/need/to/exist.json",
                stdout=StringIO(),
            )


class WagtailContactInboxTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="ceo-editor",
            password="unused-test-password",
            is_staff=True,
        )
        permissions = Permission.objects.filter(
            content_type__app_label="contact",
            codename__in=("view_contactsubmission", "change_contactsubmission"),
        )
        admin_access = Permission.objects.get(
            content_type__app_label="wagtailadmin",
            codename="access_admin",
        )
        self.user.user_permissions.add(*permissions, admin_access)
        self.inquiry = ContactSubmission.objects.create(
            name="Family Member",
            email="family@example.test",
            message="Please share event details.",
        )
        self.client.force_login(self.user)

    def test_staff_with_view_permission_can_review_inquiries(self):
        response = self.client.get(reverse("contact_inquiries:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Family Member")
        self.assertNotContains(response, "Please share event details.")
        self.assertFalse(admin.site.is_registered(ContactSubmission))
        add_response = self.client.get(
            reverse("contact_inquiries:add"), follow=True
        )
        self.assertEqual(add_response.status_code, 200)
        self.assertTrue(add_response.redirect_chain)

        delete_response = self.client.get(
            reverse("contact_inquiries:delete", args=[self.inquiry.pk]),
            follow=True,
        )
        self.assertEqual(delete_response.status_code, 200)
        self.assertTrue(delete_response.redirect_chain)

    def test_staff_can_edit_resolution_but_not_inquiry_content(self):
        response = self.client.get(
            reverse("contact_inquiries:edit", args=[self.inquiry.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please share event details.")
        self.assertContains(response, 'name="is_resolved"')
        self.assertContains(response, 'name="message"')
        self.assertContains(response, "disabled")

    def test_inbox_form_ignores_tampered_inquiry_content(self):
        form = ContactInquiryInboxForm(
            data={
                "name": "Changed name",
                "email": "changed@example.test",
                "message": "Changed message",
                "is_resolved": "on",
            },
            instance=self.inquiry,
        )

        self.assertTrue(form.is_valid())
        updated = form.save()

        self.assertEqual(updated.name, "Family Member")
        self.assertEqual(updated.email, "family@example.test")
        self.assertEqual(updated.message, "Please share event details.")
        self.assertTrue(updated.is_resolved)
        self.assertIsNotNone(updated.resolved_at)
