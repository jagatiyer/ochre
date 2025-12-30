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
from django.db import models

# Create your models here.
