from django.contrib import admin
from django import forms
from .models import BlogPost

# Use CKEditor5 widget for rich-text editing in the admin content field.
try:
    from django_ckeditor_5.widgets import CKEditor5Widget
except Exception:
    CKEditor5Widget = None


class BlogPostForm(forms.ModelForm):
    if CKEditor5Widget is not None:
        # Use the named 'blog' config defined in settings.py for full toolbar
        content = forms.CharField(widget=CKEditor5Widget(config_name='blog'))

    class Meta:
        model = BlogPost
        fields = "__all__"


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    form = BlogPostForm
    list_display = ("title", "tag", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "description")
    list_filter = ("tag",)

    class Media:
        css = {
            'all': ('admin/ckeditor5_admin.css',)
        }
