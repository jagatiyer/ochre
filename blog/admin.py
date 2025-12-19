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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # 🔥 FORCE widget media injection
        if hasattr(form, "media"):
            self.media = self.media + form.media

        return form

    fields = (
        "title",
        "slug",
        "excerpt",
        "content",
        "cover_image",
        "tag",
        "published",
    )
