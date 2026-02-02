from .models import StaticPage


def footer_static_pages(request):
    # Only fetch pages that are marked for footer display and published.
    # Limit loaded fields to avoid pulling the full content field.
    pages = StaticPage.objects.filter(show_in_footer=True, is_published=True).order_by("footer_order").only("title", "slug", "footer_order")
    return {"footer_static_pages": pages}
