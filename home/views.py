# views for home app
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import CarouselSlide


def index(request):
    # Limit homepage carousel to maximum 5 active slides ordered by display_order
    slides = CarouselSlide.objects.filter(is_active=True).order_by('display_order')[:5]
    context = {
        'carousel_slides': slides,
    }
    return render(request, "home/index.html", context)
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
