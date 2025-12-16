from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactSubmission


def contact_page(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        # Save to DB
        ContactSubmission.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
        )

        # Success toast
        messages.success(request, "Message Sent Successfully!")

        # Clear form (redirect)
        return redirect("contact_page")

    return render(request, "contact/contact_page.html")
