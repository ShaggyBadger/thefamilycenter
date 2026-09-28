from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import ContactInquiryForm
from .models import ContactSubmission


def contact_view(request):
    if request.method == "POST":
        form = ContactInquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
            return redirect("contact")
        messages.error(request, "Something went wrong. Please try again.")
    else:
        form = ContactInquiryForm()

    return render(
        request,
        "contact/form.html",
        {"form": form, "submission_count": ContactSubmission.objects.count()},
    )
