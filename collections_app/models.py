# collections_app/models.py
from django.db import models
from django.utils.text import slugify

CATEGORY_CHOICES = [
    ("gin", "Gin"),
    ("vodka", "Vodka"),
    ("limited_edition", "Limited Edition"),
    ("special_release", "Special Release"),
]

class CollectionItem(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    excerpt = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="collections/", blank=True, null=True)

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="gin")
    
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
