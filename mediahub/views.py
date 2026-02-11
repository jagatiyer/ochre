from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import PressArticle, PressKit
from django.utils.dateformat import format as dateformat


def media_index(request):
    featured = PressArticle.objects.filter(featured=True).order_by("-date")[:5]
    # Serve only the first page (10 items) initially
    PAGE_SIZE = 10
    all_press = PressArticle.objects.all().order_by("-date")[:PAGE_SIZE]

    press_kit = PressKit.objects.first()

    context = {
        "featured": featured,
        "all_press": all_press,
        "press_page_size": PAGE_SIZE,
        "press_kit": press_kit,
    }
    return render(request, "mediahub/media_list.html", context)


def load_more_press(request):
    """AJAX endpoint: returns the next page of press articles as JSON.

    Query params:
      - page: integer (1-based). page=1 corresponds to the first page.
    """
    try:
        page = int(request.GET.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    PAGE_SIZE = 10
    start = (page - 1) * PAGE_SIZE
    end = page * PAGE_SIZE
    qs = PressArticle.objects.all().order_by("-date")[start:end]

    articles = []
    for a in qs:
        articles.append({
            "title": a.title,
            "publication_name": a.publication_name,
            "date": dateformat(a.date, "F j, Y"),
            "cover_image_url": a.cover_image.url if getattr(a, "cover_image", None) and getattr(a.cover_image, "url", None) else None,
            "slug": a.slug,
        })

    # Determine if there are more items beyond this page
    total = PressArticle.objects.count()
    has_more = end < total

    return JsonResponse({"articles": articles, "has_more": has_more})


def press_detail(request, slug):
    article = get_object_or_404(PressArticle, slug=slug)
    context = {"article": article}
    return render(request, "mediahub/press_detail.html", context)
