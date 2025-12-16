from django.shortcuts import render, get_object_or_404
from .models import BlogPost, TAG_CHOICES

def blog_list(request):
    posts = BlogPost.objects.filter(published=True).order_by("-created_at")

    context = {
        "posts": posts,
        "active_tag": "all",
        "tags": TAG_CHOICES,
    }
    return render(request, "blog/blog_list.html", context)

def blog_by_tag(request, tag):
    posts = BlogPost.objects.filter(tag=tag, published=True).order_by("-created_at")

    context = {
        "posts": posts,
        "active_tag": tag,
        "tags": TAG_CHOICES,
    }
    return render(request, "blog/blog_list.html", context)

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    return render(request, "blog/blog_detail.html", {"post": post})
