import json
from functools import partial

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from wagtail.contrib.sitemaps.views import sitemap as wagtail_sitemap
from wagtail.models import Site

from config.context_processors import site_is_indexable
from events.models import EventPage, EventsIndexPage


def robots_txt(request):
    if not site_is_indexable():
        return HttpResponse(
            "User-agent: *\nDisallow: /\n",
            content_type="text/plain; charset=utf-8",
        )

    sitemap_url = f"{settings.PUBLIC_SITE_URL}{reverse('sitemap')}"
    return HttpResponse(
        f"User-agent: *\nAllow: /\n\nSitemap: {sitemap_url}\n",
        content_type="text/plain; charset=utf-8",
    )


def sitemap_xml(request):
    if not site_is_indexable():
        return HttpResponseNotFound()
    return wagtail_sitemap(request)


def _organization_schema(public_site_url):
    organization = {
        "@context": "https://schema.org",
        "@type": "NGO",
        "name": "The Family Center",
        "description": (
            "A Winston-Salem nonprofit focused on preparing elementary- and "
            "middle-school students to enter high school ready to thrive."
        ),
        "areaServed": {
            "@type": "City",
            "name": "Winston-Salem",
            "containedInPlace": {
                "@type": "State",
                "name": "North Carolina",
            },
        },
    }
    if public_site_url:
        organization["url"] = public_site_url
        organization["@id"] = f"{public_site_url}/#organization"

    # Escape HTML-significant characters before marking serialized JSON as safe.
    schema_json = json.dumps(organization).replace("&", "\\u0026")
    schema_json = schema_json.replace("<", "\\u003c").replace(">", "\\u003e")
    return mark_safe(schema_json)


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
                if site_root.hero_image_id:
                    upcoming_events = upcoming_events[:4]
                else:
                    upcoming_events = upcoming_events.exclude(
                        pk=featured_event.pk
                    )[:3]
            else:
                upcoming_events = EventPage.objects.none()

    search_indexing_enabled = site_is_indexable()
    public_site_url = settings.PUBLIC_SITE_URL if search_indexing_enabled else ""
    meta_description = (
        "The Family Center is a Winston-Salem nonprofit focused on helping "
        "elementary- and middle-school students enter high school ready to thrive."
    )

    return render(
        request,
        "pages/home_page.html",
        {
            "page": site_root,
            "is_homepage": True,
            "seo_title": "The Family Center | Student Readiness in Winston-Salem",
            "meta_description": meta_description,
            "canonical_url": (
                f"{public_site_url}{request.path}" if public_site_url else ""
            ),
            "organization_schema_json": (
                _organization_schema(public_site_url)
                if search_indexing_enabled
                else ""
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
