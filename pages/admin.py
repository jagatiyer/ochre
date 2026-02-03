from django.contrib import admin
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import StaticPage


class StaticPageForm(forms.ModelForm):
    content = forms.CharField(
        widget=CKEditor5Widget(config_name="blog"),
        required=False
    )

    class Meta:
        model = StaticPage
        fields = "__all__"


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    form = StaticPageForm
    list_display = ("title", "slug", "show_in_footer", "footer_order", "is_published")
    list_filter = ("show_in_footer", "is_published")
    search_fields = ("title", "slug", "content")
    ordering = ("footer_order", "-publish_date")
    fields = ("title", "slug", "content", "is_published", "publish_date", "show_in_footer", "footer_order")
