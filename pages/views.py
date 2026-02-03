from django.shortcuts import render, get_object_or_404

from .models import StaticPage
from blog.models import BlogPost


def staticpage_detail(request, slug):
    page = get_object_or_404(StaticPage, slug=slug, is_published=True)

    # Match the blog detail view's context so templates/CSS that rely on
    # these page-level variables behave the same for static pages.
    recent_posts = (
        BlogPost.objects
        .filter(published=True)
        .order_by("-created_at")[:5]
    )

    context = {
        "post": page,
        "recent_posts": recent_posts,
        "categories": BlogPost.TAG_CHOICES,
        "is_static_page": True,
    }

    return render(request, "blog/blog_detail.html", context)
