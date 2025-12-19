from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf import settings
import os
from .models import BlogPost

# Prefer the CKEditor5 widget from `django-ckeditor-5`. If it's not installed for
# some reason, fall back to a plain textarea so the admin remains usable.
try:
    from ckeditor.widgets import CKEditor5Widget
except Exception:
    CKEditor5Widget = forms.Textarea


class BlogPostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget())

    class Meta:
        model = BlogPost
        fields = "__all__"


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
        form = BlogPostForm
        list_display = ("title", "tag", "created_at")
        prepopulated_fields = {"slug": ("title",)}
        search_fields = ("title", "excerpt")
        list_filter = ("tag",)

        class Media:
            css = {
                'all': ('admin/ckeditor5_admin.css',)
            }

        def get_readonly_fields(self, request, obj=None):
            # Ensure 'content' is never returned as a readonly field even if
            # other code/configuration marks some fields readonly.
            fields = list(super().get_readonly_fields(request, obj))
            if 'content' in fields:
                fields.remove('content')
            return tuple(fields)

        def get_form(self, request, obj=None, **kwargs):
            # Ensure the form field itself is not rendered disabled by admin
            form = super().get_form(request, obj, **kwargs)
            if hasattr(form, 'base_fields') and 'content' in form.base_fields:
                try:
                    form.base_fields['content'].disabled = False
                except Exception:
                    pass
            return form
