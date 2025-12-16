from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, "home/index.html")
# append to home/views.py


@login_required
def profile(request):
    """
    Minimal user profile page.
    Keeps things intentionally simple so you can expand later.
    """
    user = request.user
    display_name = user.get_full_name() or user.username

    context = {
        "user": user,
        "display_name": display_name,
    }
    return render(request, "accounts/profile.html", context)
