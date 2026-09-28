from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class HomePage(Page):
    """Wagtail site-tree root; the public homepage is a standard Django view."""

    REVIEW_STATUS_CHOICES = [
        ("needs_review", "Needs owner/CEO review"),
        ("approved", "Approved for publication"),
    ]

    max_count = 1
    subpage_types = ["events.EventsIndexPage"]
    is_previewable = False

    hero_heading = models.CharField(max_length=180, blank=True)
    hero_body = RichTextField(blank=True)
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_image_caption = models.CharField(max_length=160, blank=True)
    community_pillar_title = models.CharField(max_length=100, blank=True)
    community_pillar_body = RichTextField(blank=True)
    practical_support_pillar_title = models.CharField(max_length=100, blank=True)
    practical_support_pillar_body = RichTextField(blank=True)
    future_direction_pillar_title = models.CharField(max_length=100, blank=True)
    future_direction_pillar_body = RichTextField(blank=True)
    review_status = models.CharField(
        max_length=20, choices=REVIEW_STATUS_CHOICES, default="needs_review"
    )
    source_reference = models.CharField(max_length=250, blank=True)
    editor_notes = models.TextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel("hero_heading"),
        FieldPanel("hero_body"),
        FieldPanel("hero_image"),
        FieldPanel("hero_image_caption"),
        MultiFieldPanel(
            [
                FieldPanel("community_pillar_title"),
                FieldPanel("community_pillar_body"),
                FieldPanel("practical_support_pillar_title"),
                FieldPanel("practical_support_pillar_body"),
                FieldPanel("future_direction_pillar_title"),
                FieldPanel("future_direction_pillar_body"),
            ],
            heading="Pillars",
        ),
        FieldPanel("review_status"),
        FieldPanel("source_reference"),
        FieldPanel("editor_notes"),
    ]



