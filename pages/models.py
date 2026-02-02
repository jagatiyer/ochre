from django.db import models
from django.urls import reverse


class StaticPage(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    publish_date = models.DateTimeField(null=True, blank=True)

    # Footer controls
    show_in_footer = models.BooleanField(
        default=False,
        help_text="If enabled, this page will appear in the site footer."
    )
    # Backwards-compatibility DB column: keep `add_to_footer` present
    # so existing DB rows (pre-migration) do not cause NOT NULL errors.
    # This field is ignored by templates/context processors which use
    # `show_in_footer`.
    add_to_footer = models.BooleanField(default=False)
    footer_order = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        help_text="Controls the order of this page in the footer (lower comes first).",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["footer_order", "-publish_date", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("pages:detail", args=[self.slug])
