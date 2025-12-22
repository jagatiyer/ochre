from django.contrib import admin
from .models import PressArticle, PressKit
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget


class PressArticleForm(forms.ModelForm):
    description = forms.CharField(
        widget=CKEditor5Widget(config_name="blog"),
        required=False,
    )

    content = forms.CharField(
        widget=CKEditor5Widget(config_name="blog"),
        required=False,
    )

    class Meta:
        model = PressArticle
        fields = [
            "title",
            "slug",
            "publication_name",
            "date",
            "description",
            "external_link",
            "featured",
            "cover_image",
            "content",
        ]


@admin.register(PressArticle)
class PressArticleAdmin(admin.ModelAdmin):
    form = PressArticleForm
    list_display = ("title", "publication_name", "date", "featured")
    list_filter = ("featured", "publication_name", "date")
    search_fields = ("title", "publication_name")


@admin.register(PressKit)
class PressKitAdmin(admin.ModelAdmin):
    list_display = ("pdf", "uploaded_at")
