from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import BlogPost
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.utils.text import get_valid_filename
import uuid
from django.http import HttpResponseBadRequest
from django.conf import settings


# ============================================================
# BLOG LIST PAGE
# ============================================================

def blog_list(request):
    """
    Initial blog list page.
    Loads ONLY the first row (2 posts for now).
    """

    # Use explicit ?filter= parameter; default to 'all'
    filter_value = request.GET.get("filter", "all")

    if filter_value == "all":
        qs = BlogPost.objects.filter(published=True).order_by("-created_at")
        active_filter = "all"
    else:
        qs = BlogPost.objects.filter(published=True).order_by("-created_at").filter(tag=filter_value)
        active_filter = filter_value

    posts = qs[:2]
    total_count = qs.count()

    return render(request, "blog/blog_list.html", {
        "posts": posts,
        "total_count": total_count,
        "tags": BlogPost.TAG_CHOICES,
        "active_filter": active_filter,
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


@staff_member_required
@require_POST
def tinymce_upload(request):
    """Receive image upload from TinyMCE and return JSON with `location` key.

    Expects file field named `image`.
    """
    upload = request.FILES.get('image')
    if not upload:
        return HttpResponseBadRequest('No image uploaded')

    # Sanitize filename and add UUID prefix to avoid collisions
    filename = get_valid_filename(upload.name)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    save_path = f"blog/{unique_name}"

    # Save using default storage (will place under MEDIA_ROOT)
    saved_name = default_storage.save(save_path, upload)
    url = default_storage.url(saved_name)

    # Return URL that editors expect. TinyMCE expects `location`, CKEditor5 expects `url`.
    return JsonResponse({'location': url, 'url': url})
