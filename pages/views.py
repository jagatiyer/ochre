from django.shortcuts import render, get_object_or_404

from .models import StaticPage


def staticpage_detail(request, slug):
    page = get_object_or_404(StaticPage, slug=slug, is_published=True)

    # Reuse blog detail template by providing the same variable name `post`.
    context = {
        "post": page,
        "recent_posts": [],
        "categories": [],
        "is_static_page": True,
    }
    return render(request, "blog/blog_detail.html", context)
