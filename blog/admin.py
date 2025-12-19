from django.contrib import admin
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    content = forms.CharField(
        widget=CKEditor5Widget(config_name="blog"),
        required=False
    )

    class Meta:
        model = BlogPost
        fields = "__all__"


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    form = BlogPostForm
    fields = (
        "title",
        "slug",
        "excerpt",
        "content",
        "cover_image",
        "tag",
        "published",
    )

    class Media:
        # Include a tiny inspector script scoped to BlogPost admin only. The
        # real CKEditor assets are injected via the form media in
        # `changeform_view`, this file only helps us detect which plugins are
        # present in the build (logged to the browser console).
        js = ["admin/js/ckeditor_inspect.js"]
        css = {
            'all': ('blog/admin_blog_light.css',)
        }

    # Auto-populate slug from title in the admin (scoped to BlogPost only)
    prepopulated_fields = {"slug": ("title",)}
