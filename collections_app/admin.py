from django.contrib import admin
from .models import CollectionItem, CollectionCategory
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
            "category_fk",
            "published",
            "display_order",
        ]


@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    form = CollectionItemForm
    list_display = ("title", "display_order", "category_fk", "published", "created_at")
    list_editable = ("display_order",)
    list_filter = ("category_fk", "published")
    search_fields = ("title", "excerpt", "description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("display_order",)
    fieldsets = (
        (None, {
            'fields': (
                'title', 'slug', 'excerpt', 'description', 'cover_image',
                'category_fk', 'published', 'display_order'
            )
        }),
    )


@admin.register(CollectionCategory)
class CollectionCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "order")
    list_editable = ("is_active", "order")
    prepopulated_fields = {"slug": ("name",)}
