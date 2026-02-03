from django.shortcuts import render, get_object_or_404

from .models import StaticPage


def staticpage_detail(request, slug):
    page = get_object_or_404(StaticPage, slug=slug, is_published=True)

    # Render isolated static page template that reuses blog classes
    # for typography without pulling in blog UI/context.
    return render(
        request,
        "pages/static_page_detail.html",
        {"page": page}
    )
