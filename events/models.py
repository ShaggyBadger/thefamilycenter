from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index


class EventsIndexPage(Page):
    """Parent page for event records and upcoming/past listings."""

    parent_page_types = ["pages.HomePage"]
    subpage_types = ["events.EventPage"]

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]

    def get_context(self, request):
        context = super().get_context(request)
        now = timezone.localtime()
        events = EventPage.objects.live().descendant_of(self)
        if not settings.DEBUG:
            events = events.filter(verification_status=EventPage.VERIFIED)
            events = events.exclude(call_to_action_label="").exclude(
                call_to_action_url=""
            )
        context["upcoming_events"] = events.filter(
            Q(end_datetime__gte=now)
            | Q(end_datetime__isnull=True, start_datetime__gte=now)
        ).order_by("start_datetime")
        context["past_events"] = events.filter(
            Q(end_datetime__lt=now)
            | Q(end_datetime__isnull=True, start_datetime__lt=now)
        ).order_by("-start_datetime")
        return context


class EventPage(Page):
    """One canonical, editor-managed page for each confirmed event."""

    NEEDS_CONFIRMATION = "needs_confirmation"
    VERIFIED = "confirmed"
    VERIFICATION_STATUS_CHOICES = [
        (NEEDS_CONFIRMATION, "Needs detail confirmation"),
        (VERIFIED, "Details confirmed"),
    ]

    parent_page_types = ["events.EventsIndexPage"]
    subpage_types = []

    summary = models.CharField(max_length=280, blank=True)
    start_datetime = models.DateTimeField(db_index=True)
    end_datetime = models.DateTimeField(blank=True, db_index=True, null=True)
    venue_name = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    eligibility = models.TextField(blank=True)
    cost = models.CharField(max_length=120, blank=True)
    schedule = RichTextField(blank=True)
    details = RichTextField(blank=True)
    food = RichTextField(blank=True)
    what_to_bring = RichTextField(blank=True)
    accessibility = RichTextField(blank=True)
    transportation = RichTextField(blank=True)
    parking = RichTextField(blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    call_to_action_label = models.CharField(max_length=80, blank=True)
    call_to_action_url = models.URLField(blank=True)
    verification_status = models.CharField(
        max_length=24,
        choices=VERIFICATION_STATUS_CHOICES,
        default=NEEDS_CONFIRMATION,
        db_index=True,
    )
    source_reference = models.CharField(max_length=250, blank=True)
    review_notes = models.TextField(blank=True)
    map_url = models.URLField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel("summary"),
        FieldPanel("start_datetime"),
        FieldPanel("end_datetime"),
        FieldPanel("venue_name"),
        FieldPanel("address"),
        FieldPanel("map_url"),
        FieldPanel("eligibility"),
        FieldPanel("cost"),
        FieldPanel("schedule"),
        FieldPanel("details"),
        FieldPanel("food"),
        FieldPanel("what_to_bring"),
        FieldPanel("accessibility"),
        FieldPanel("transportation"),
        FieldPanel("parking"),
        FieldPanel("image"),
        FieldPanel("call_to_action_label"),
        FieldPanel("call_to_action_url"),
        FieldPanel("verification_status"),
        FieldPanel("source_reference"),
        FieldPanel("review_notes"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("summary"),
        index.SearchField("details"),
    ]

    def clean(self):
        super().clean()
        if (
            self.start_datetime
            and self.end_datetime
            and self.end_datetime <= self.start_datetime
        ):
            raise ValidationError(
                {"end_datetime": "The end date and time must be after the start."}
            )

    @property
    def is_public_ready(self):
        return bool(
            self.verification_status == self.VERIFIED
            and self.call_to_action_label.strip()
            and self.call_to_action_url.strip()
        )
