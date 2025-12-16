from django.db import models
from django.utils.text import slugify


class PressArticle(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)

    publication_name = models.CharField(max_length=255)
    date = models.DateField()

    description = models.TextField(blank=True)
    external_link = models.URLField(blank=True)

    featured = models.BooleanField(default=False)

    # Optional cover thumbnail
    cover_image = models.ImageField(upload_to="press/", blank=True, null=True)

    # Full article content for detail page
    content = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]  # Reverse chronological

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} — {self.publication_name}"


class PressKit(models.Model):
    pdf = models.FileField(upload_to="press_kits/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Press Kit"
