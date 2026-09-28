from wagtail import hooks
from wagtail.admin.viewsets.model import ModelViewSet

from .forms import ContactInquiryInboxForm
from .models import ContactSubmission


class ContactInquiryViewSet(ModelViewSet):
    model = ContactSubmission
    name = "contact_inquiries"
    url_prefix = "contact-inquiries"
    menu_label = "Contact inquiries"
    menu_icon = "mail"
    add_to_admin_menu = True
    copy_view_enabled = False
    inspect_view_enabled = True
    inspect_view_fields = (
        "name",
        "email",
        "message",
        "created_at",
        "is_resolved",
        "resolved_at",
    )
    list_display = ("name", "email", "created_at", "is_resolved")
    list_filter = ("is_resolved",)
    search_fields = ("name", "email")
    ordering = ("-created_at",)

    def get_form_class(self, for_update=False):
        return ContactInquiryInboxForm


@hooks.register("register_admin_viewset")
def register_contact_inquiries_viewset():
    return ContactInquiryViewSet()
