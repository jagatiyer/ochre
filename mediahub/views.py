from django.shortcuts import render, get_object_or_404
from .models import PressArticle, PressKit


def media_index(request):
    featured = PressArticle.objects.filter(featured=True).order_by("-date")[:5]
    all_press = PressArticle.objects.all().order_by("-date")

    press_kit = PressKit.objects.first()

    context = {
        "featured": featured,
        "all_press": all_press,
        "press_kit": press_kit,
    }
    return render(request, "mediahub/media_list.html", context)


def press_detail(request, slug):
    article = get_object_or_404(PressArticle, slug=slug)
    context = {"article": article}
    return render(request, "mediahub/press_detail.html", context)
