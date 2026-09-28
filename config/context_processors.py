from django.conf import settings
from wagtail.models import Site


def site_is_indexable():
    return (
        not settings.DEBUG
        and settings.DJANGO_SITE_INDEXABLE
        and bool(settings.PUBLIC_SITE_URL)
    )


def site_navigation(request):
    site = Site.find_for_request(request)
    site_root = site.root_page.specific if site else None
    events_index_page = None
    site_menu_pages = None
    site_footer_pages = None
    if site_root:
        from events.models import EventsIndexPage

        site_menu_pages = site_root.get_children().live().in_menu()
        events_index_page = (
            site_root.get_children()
            .type(EventsIndexPage)
            .live()
            .specific()
            .first()
        )
        site_footer_pages = []
    return {
        "site_root": site_root,
        "site_events_index_page": events_index_page,
        "site_menu_pages": site_menu_pages,
        "site_footer_pages": site_footer_pages,
        "is_local_preview": settings.DEBUG,
        "search_indexing_enabled": site_is_indexable(),
    }
