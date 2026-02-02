from django.contrib import admin
from .models import StaticPage


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "show_in_footer", "footer_order", "is_published")
    list_filter = ("show_in_footer", "is_published")
    search_fields = ("title", "slug", "content")
    ordering = ("footer_order", "-publish_date")
    fields = ("title", "slug", "content", "is_published", "publish_date", "show_in_footer", "footer_order")
