# profile/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import ProfileForm

@login_required
def profile_view(request):
    """
    Simple profile page that displays user info and links to edit.
    """
    user = request.user
    context = {"user": user}
    return render(request, "account/profile.html", context)


@login_required
def profile_edit(request):
    """
    Edit basic user details (first_name, last_name, email).
    Uses ProfileForm in profile/forms.py.
    """
    user = request.user

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile:profile")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ProfileForm(instance=user)

    return render(request, "account/profile_edit.html", {"form": form})
