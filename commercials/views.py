from django.shortcuts import render
from .models import CommercialVideo


def index(request):
    commercials = CommercialVideo.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'commercials/index.html', {
        'commercials': commercials,
        'current': 'commercials',
    })
