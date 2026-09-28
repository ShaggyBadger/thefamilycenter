from django import forms

from .models import ContactSubmission


class ContactInquiryForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ("name", "email", "message")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "message": forms.Textarea(attrs={"rows": 5, "placeholder": "Tell us what's on your mind…"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ("name", "email", "message"):
            self.fields[field_name].required = True
            self.fields[field_name].widget.attrs.update({"class": "contact-form__input"})
        self.fields["message"].widget.attrs["class"] = "contact-form__input contact-form__textarea"


class ContactInquiryInboxForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ("name", "email", "message", "is_resolved")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ("name", "email", "message"):
            self.fields[field_name].disabled = True
