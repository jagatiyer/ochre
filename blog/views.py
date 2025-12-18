from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import BlogPost


# ============================================================
# BLOG LIST PAGE
# ============================================================

def blog_list(request):
    """
    Initial blog list page.
    Loads ONLY the first row (2 posts for now).
    """

    all_posts = (
        BlogPost.objects
        .filter(published=True)
        .order_by("-created_at")
    )

    posts = all_posts[:2]  # first row only
    total_count = all_posts.count()

    return render(request, "blog/blog_list.html", {
        "posts": posts,
        "total_count": total_count,
        "tags": BlogPost.TAG_CHOICES,
    })


# ============================================================
# LOAD MORE POSTS (AJAX)
# ============================================================

def blog_list_more(request):
    """
    Returns more blog posts as JSON.
    Used by the 'Show More' button.
    """

    offset = int(request.GET.get("offset", 0))
    limit = 2  # one row = 2 posts

    qs = (
        BlogPost.objects
        .filter(published=True)
        .order_by("-created_at")
    )

    posts = qs[offset:offset + limit]
    total = qs.count()

    data = []

    for post in posts:
        data.append({
            "title": post.title,
            "slug": post.slug,
            "excerpt": post.excerpt,
            "image": post.cover_image.url if post.cover_image else "",
        })

    return JsonResponse({
        "posts": data,
        "next_offset": offset + limit,
        "has_more": offset + limit < total,
    })


# ============================================================
# BLOG DETAIL PAGE
# ============================================================

def blog_detail(request, slug):
    """
    Individual blog detail page.
    """

    post = get_object_or_404(
        BlogPost,
        slug=slug,
        published=True
    )

    recent_posts = (
        BlogPost.objects
        .filter(published=True)
        .exclude(id=post.id)
        .order_by("-created_at")[:5]
    )

    return render(request, "blog/blog_detail.html", {
        "post": post,
        "recent_posts": recent_posts,
        "categories": BlogPost.TAG_CHOICES,
    })
