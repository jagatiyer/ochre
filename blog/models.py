from django.db import models
from django.utils.text import slugify

TAG_CHOICES = [
    ("craft_process", "Craft Process"),
    ("innovation", "Innovation"),
    ("product_story", "Product Story"),
    ("recipes", "Recipes"),
    ("sustainability", "Sustainability"),
    ("news", "News"),
]

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    excerpt = models.CharField(max_length=500, blank=True)

    description = models.TextField(blank=True)
    content = models.TextField(blank=True)

    cover_image = models.ImageField(upload_to="blog/", blank=True, null=True)

    tag = models.CharField(max_length=50, choices=TAG_CHOICES, default="news")

    published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
