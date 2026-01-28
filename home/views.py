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
    # featured products: prefer explicit featured flag if present, otherwise fall back to recent published products
    shop_fields = [f.name for f in ShopItem._meta.get_fields()]
    featured_qs = ShopItem.objects.filter(published=True)
    if 'is_featured' in shop_fields:
        featured_qs = featured_qs.filter(is_featured=True)
    elif 'featured' in shop_fields:
        featured_qs = featured_qs.filter(featured=True)
    else:
        # no explicit featured flag — show recent non-experience published items
        featured_qs = featured_qs.exclude(is_experience=True)

    # NOTE: Featured product selection:
    # - If the project uses an explicit `is_featured` flag, admins expect
    #   the item to appear immediately after toggling the flag. Ordering
    #   purely by `created_at` can hide older products that are newly
    #   marked featured (they'll be sorted by original creation time).
    #
    # Minimal, non-invasive approach: when `is_featured` exists, order
    # by primary key descending to provide a deterministic, recent-first
    # ordering for featured items (avoids adding fields/migrations).
    # For a robust solution, add an `updated_at` timestamp to `ShopItem`
    # and order by it when prioritising admin edits.
    if 'is_featured' in shop_fields:
        featured_products = featured_qs.select_related('category').order_by('-pk')[:8]
    else:
        featured_products = featured_qs.select_related('category').order_by('-created_at')[:8]
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
