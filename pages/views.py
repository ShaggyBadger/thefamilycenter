from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from functools import partial
from wagtail.models import Site

from events.models import EventPage, EventsIndexPage


def home(request):
    """Render the code-owned homepage with current Wagtail event content."""
    site = Site.find_for_request(request)
    site_root = site.root_page.specific if site else None
    events_index_page = None
    featured_event = None
    upcoming_events = EventPage.objects.none()

    if site_root:
        events_index_page = (
            site_root.get_children()
            .type(EventsIndexPage)
            .live()
            .specific()
            .first()
        )
        if events_index_page:
            events = EventPage.objects.live().descendant_of(events_index_page)
            if not settings.DEBUG:
                events = events.filter(
                    verification_status=EventPage.VERIFIED,
                    call_to_action_label__gt="",
                    call_to_action_url__gt="",
                )
            upcoming_events = events.filter(
                start_datetime__gte=timezone.localtime()
            ).order_by("start_datetime")
            featured_event = upcoming_events.first()
            if featured_event:
                upcoming_events = upcoming_events.exclude(pk=featured_event.pk)[:3]
            else:
                upcoming_events = EventPage.objects.none()

    return render(
        request,
        "pages/home_page.html",
        {
            "page": site_root,
            "is_homepage": True,
            "seo_title": "The Family Center | Winston-Salem Community Events",
            "meta_description": (
                "Find upcoming events from The Family Center in Winston-Salem, "
                "North Carolina, and the details you need to plan your visit."
            ),
            "events_index_page": events_index_page,
            "featured_event": featured_event,
            "upcoming_events": upcoming_events,
        },
    )


def page_view(request, slug):
    """Render a static content page."""
    return render(request, f"pages/{slug}.html", {"slug": slug})


page_views = {
    "about": partial(page_view, slug="about"),
    "what-we-do": partial(page_view, slug="what-we-do"),
    "business-partnerships": partial(page_view, slug="business-partnerships"),
    "contact": partial(page_view, slug="contact"),
}
