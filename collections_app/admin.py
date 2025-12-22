from django.contrib import admin
from .models import CollectionItem
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget


class CollectionItemForm(forms.ModelForm):
    description = forms.CharField(
        widget=CKEditor5Widget(config_name="blog"),
        required=False,
    )

    class Meta:
        model = CollectionItem
        fields = [
            "title",
            "slug",
            "excerpt",
            "description",
            "cover_image",
            "category",
            "published",
        ]


@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    form = CollectionItemForm
    list_display = ("title", "category", "published", "created_at")
    list_filter = ("category", "published")
    search_fields = ("title", "excerpt", "description")
    prepopulated_fields = {"slug": ("title",)}
