from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from wagtail import hooks

from events.models import EventPage
from pages.models import HomePage


@hooks.register("before_publish_page")
def require_reviewed_page_content(request, page):
    if settings.DEBUG:
        return None

    page = page.specific
    if isinstance(page, HomePage) and page.review_status != "approved":
        messages.error(request, "Owner/CEO approval is required before publishing this page.")
        return redirect("wagtailadmin_pages:edit", page.pk)

    if isinstance(page, EventPage) and not page.is_public_ready:
        messages.error(
            request,
            "Confirm the event details and a working action before publishing.",
        )
        return redirect("wagtailadmin_pages:edit", page.pk)

    return None
