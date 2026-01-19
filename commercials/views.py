from django.shortcuts import render
from .models import CommercialVideo


def index(request):
    videos = CommercialVideo.objects.filter(is_active=True).order_by('order')
    return render(request, 'commercials/index.html', {
        'videos': videos,
        'current': 'commercials',
    })
