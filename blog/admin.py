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

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Inject the BlogPost form widget media into the change form view context.

        This ensures CKEditor JS/CSS for the BlogPost `content` field are present
        even if admin templates or other admin customizations would otherwise
        omit `{{ media }}`. The injection is local to BlogPostAdmin only.
        """
        # Obtain the form class and instantiate it to access its media
        form_class = self.get_form(request, None)
        try:
            form_instance = form_class()
        except Exception:
            form_instance = None

        # Prepare extra_context and inject media from the form if available
        extra_context = {} if extra_context is None else dict(extra_context)
        if form_instance is not None and hasattr(form_instance, 'media'):
            existing_media = extra_context.get('media')
            if existing_media:
                extra_context['media'] = existing_media + form_instance.media
            else:
                extra_context['media'] = form_instance.media

        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

    fields = (
        "title",
        "slug",
        "excerpt",
        "content",
        "cover_image",
        "tag",
        "published",
    )
