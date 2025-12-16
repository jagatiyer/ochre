from django.contrib import admin
from .models import PressArticle, PressKit


@admin.register(PressArticle)
class PressArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "publication_name", "date", "featured")
    list_filter = ("featured", "publication_name", "date")
    search_fields = ("title", "publication_name")


@admin.register(PressKit)
class PressKitAdmin(admin.ModelAdmin):
    list_display = ("pdf", "uploaded_at")
