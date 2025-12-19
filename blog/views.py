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

    # Optional tag filter (from ?tag=slug)
    tag = request.GET.get("tag")

    qs = BlogPost.objects.filter(published=True).order_by("-created_at")
    if tag:
        qs = qs.filter(tag=tag)

    posts = qs[:2]
    total_count = qs.count()

    return render(request, "blog/blog_list.html", {
        "posts": posts,
        "total_count": total_count,
        "tags": BlogPost.TAG_CHOICES,
        "current_tag": tag,
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

    qs = BlogPost.objects.filter(published=True).order_by("-created_at")

    posts = qs[offset:offset + limit]
    total = qs.count()

    data = []

    from bs4 import BeautifulSoup

    for post in posts:
        # determine image: prefer cover_image, else first inline image in content
        image_url = ""
        if post.cover_image:
            try:
                image_url = post.cover_image.url
            except Exception:
                image_url = ""
        else:
            try:
                soup = BeautifulSoup(post.content or "", "html.parser")
                img = soup.find("img")
                if img and img.get("src"):
                    image_url = img.get("src")
            except Exception:
                image_url = ""

        data.append({
            "title": post.title,
            "slug": post.slug,
            "excerpt": post.excerpt,
            "image": image_url,
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
