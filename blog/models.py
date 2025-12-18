from django.db import models


class BlogPost(models.Model):
    TAG_CHOICES = [
        ("culture", "Culture"),
        ("craft", "Craft"),
        ("sustainability", "Sustainability"),
        ("news", "News"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="blog/", blank=True, null=True)

    tag = models.CharField(
        max_length=50,
        choices=TAG_CHOICES,
        blank=True
    )

    published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
