from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from contact.models import ContactSubmission


class Command(BaseCommand):
    help = "Delete resolved inquiries after 90 days and unresolved ones after one year."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report eligible inquiries without deleting them.",
        )

    def handle(self, *args, **options):
        now = timezone.now()
        resolved_cutoff = now - timedelta(days=90)
        unresolved_cutoff = now - timedelta(days=365)

        expired_resolved = ContactSubmission.objects.filter(
            resolved_at__lt=resolved_cutoff
        )
        expired_unresolved = ContactSubmission.objects.filter(
            resolved_at__isnull=True,
            created_at__lt=unresolved_cutoff,
        )

        resolved_count = expired_resolved.count()
        unresolved_count = expired_unresolved.count()
        if options["dry_run"]:
            self.stdout.write(
                f"Dry run: {resolved_count} resolved and "
                f"{unresolved_count} unresolved inquiries are eligible for deletion."
            )
            return

        expired_resolved.delete()
        expired_unresolved.delete()
        self.stdout.write(
            f"Deleted {resolved_count} resolved and "
            f"{unresolved_count} unresolved inquiries."
        )
