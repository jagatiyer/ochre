# views for home app
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import CarouselSlide, HomePageVideo, HomeContentSection, HomeSectionHeader
from shop.models import ShopItem


def index(request):
    # Limit homepage carousel to maximum 5 active slides ordered by display_order
    slides = CarouselSlide.objects.filter(is_active=True).order_by('display_order')[:5]
    context = {
        'carousel_slides': slides,
    }
    # featured products: STRICT logic
    # Only show products explicitly marked as featured by admin
    featured_products = (
        ShopItem.objects
        .filter(published=True, is_featured=True)
        .select_related('category')
        .order_by('-id')[:8]
    )
    context['featured_products'] = featured_products
    # home videos: only active, ordered by `order`, limit 6
    home_videos = HomePageVideo.objects.filter(is_active=True).order_by('order')[:6]
    context['home_videos'] = home_videos
    # home content sections (admin-managed blocks)
    home_content_sections = HomeContentSection.objects.filter(is_active=True).order_by('order')
    context['home_content_sections'] = home_content_sections
    # global header configuration for home sections (singleton)
    context['home_section_header'] = HomeSectionHeader.objects.first()
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
