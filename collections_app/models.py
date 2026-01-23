# collections_app/models.py
from django.db import models
from django.utils.text import slugify


# Backwards-compatible: the old string choices are still supported on existing
# rows via `category`. New installations should use `CollectionCategory` and
# the `category_fk` ForeignKey. We keep the old `category` field for a
# transition period and to make automated data migrations easier.
CATEGORY_CHOICES = [
    ("gin", "Gin"),
    ("vodka", "Vodka"),
    ("limited_edition", "Limited Edition"),
    ("special_release", "Special Release"),
]


class CollectionCategory(models.Model):
    """Admin-managed category for collections.

    Fields:
    - name: human visible name
    - slug: url-friendly unique identifier
    - description: optional admin-facing description
    - is_active: whether to show the category in public filters
    - order: integer to control ordering in the filter bar
    """

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ("order", "name")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CollectionItem(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    excerpt = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="collections/", blank=True, null=True)

    # Deprecated string-based category (kept for migration/back-compat).
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="gin")

    # New admin-managed relation. Nullable so we can migrate existing rows
    # gradually without blocking site operation. Use `category_fk` in templates
    # and front-end data attributes once populated.
    category_fk = models.ForeignKey(
        CollectionCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
    )

    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
