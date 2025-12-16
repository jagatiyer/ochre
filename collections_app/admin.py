from django.contrib import admin
from .models import CollectionItem

@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "published", "created_at")
    list_filter = ("category", "published")
    search_fields = ("title", "excerpt", "description")
    prepopulated_fields = {"slug": ("title",)}
