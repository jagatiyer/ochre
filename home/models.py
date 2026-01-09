from django.db import models


class CarouselSlide(models.Model):
    image = models.ImageField(upload_to='carousel/')
    title = models.CharField(max_length=200, blank=True)
    cta_text = models.CharField(max_length=100, blank=True)
    cta_url = models.CharField(max_length=400, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    auto_slide_seconds = models.IntegerField(default=5)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.title or f"Slide {self.pk}"


class HomePageVideo(models.Model):
    title = models.CharField(max_length=255, blank=True)
    video = models.FileField(upload_to='home/videos/')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return self.title or f"HomeVideo {self.pk}"
from django.db import models

# Create your models here.


class HomeContentSection(models.Model):
    POSITION_LEFT = 'left'
    POSITION_RIGHT = 'right'
    IMAGE_POSITION_CHOICES = [
        (POSITION_LEFT, 'Left'),
        (POSITION_RIGHT, 'Right'),
    ]

    title = models.CharField(max_length=255)
    body = models.TextField()
    image = models.ImageField(upload_to='home/sections/')
    image_position = models.CharField(max_length=5, choices=IMAGE_POSITION_CHOICES)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return self.title or f"HomeContentSection {self.pk}"
