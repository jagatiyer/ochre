from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf import settings
import os
from .models import BlogPost


class TinyMCEAdminWidget(forms.Textarea):
        class Media:
            js = ()

        def render(self, name, value, attrs=None, renderer=None):
                html = super().render(name, value, attrs, renderer)
                final_id = (attrs or {}).get("id")
                selector = f"#{final_id}" if final_id else f"textarea[name=\"{name}\"]"

                # Determine TinyMCE API key from settings or env; use 'no-api-key' only in DEBUG
                api_key = getattr(settings, 'TINYMCE_API_KEY', None) or os.environ.get('TINYMCE_API_KEY')
                if not api_key and getattr(settings, 'DEBUG', False):
                        api_key = 'no-api-key'

                # Build script tag if key is available (or placeholder used for DEBUG)
                if api_key:
                        script_tag = f"<script src=\"https://cdn.tiny.cloud/1/{api_key}/tinymce/6/tinymce.min.js\"></script>"
                else:
                        script_tag = '<!-- TinyMCE not loaded: TINYMCE_API_KEY missing -->'

                # TinyMCE init script: enables headings, bold/italic/underline, links, lists, blockquote, image upload
                init_js = f"""
{script_tag}
<script>
document.addEventListener('DOMContentLoaded', function() {{
    if (typeof tinymce === 'undefined') return;
    tinymce.init({{
        selector: '{selector}',
        plugins: 'lists link image code advlist autolink',
        toolbar: 'formatselect | bold italic underline | bullist numlist | blockquote | link | image | undo redo',
        menubar: false,
        statusbar: false,
        branding: false,
        images_upload_url: '{reverse('blog:tinymce_upload')}',
        images_upload_handler: function (blobInfo, success, failure) {{
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '{reverse('blog:tinymce_upload')}');
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            // Add CSRF token
            function getCookie(name) {{
                var value = "; " + document.cookie;
                var parts = value.split("; " + name + "=");
                if (parts.length === 2) return parts.pop().split(';').shift();
            }}
            var csrftoken = getCookie('csrftoken');
            if (csrftoken) xhr.setRequestHeader('X-CSRFToken', csrftoken);
            xhr.onload = function() {{
                if (xhr.status !== 200) {{
                    failure('HTTP Error: ' + xhr.status);
                    return;
                }}
                var json = JSON.parse(xhr.responseText);
                if (!json || typeof json.location != 'string') {{
                    failure('Invalid JSON: ' + xhr.responseText);
                    return;
                }}
                success(json.location);
            }};
            var formData = new FormData();
            formData.append('image', blobInfo.blob(), blobInfo.filename());
            xhr.send(formData);
        }}
    }});
}});
</script>
"""

                return mark_safe(html + init_js)


class BlogPostForm(forms.ModelForm):
        content = forms.CharField(widget=TinyMCEAdminWidget())

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
