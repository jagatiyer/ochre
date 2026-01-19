from django.contrib import admin
from django import forms
from django.utils.html import format_html

from .models import CommercialVideo


class CommercialVideoForm(forms.ModelForm):
	class Meta:
		model = CommercialVideo
		fields = '__all__'

	def clean(self):
		cleaned = super().clean()
		has_file = bool(cleaned.get('video'))
		has_url = bool(cleaned.get('embed_url'))
		has_html = bool(cleaned.get('embed_html'))
		provided = sum([has_file, has_url, has_html])
		if provided == 0:
			raise forms.ValidationError('Provide one source: upload file, embed URL, or embed HTML.')
		if provided > 1:
			raise forms.ValidationError('Please provide only one of: upload file, embed URL, or embed HTML.')
		return cleaned

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# make `order` optional in the admin form (use model default when saving)
		if 'order' in self.fields:
			self.fields['order'].required = False


@admin.register(CommercialVideo)
class CommercialVideoAdmin(admin.ModelAdmin):
	form = CommercialVideoForm
	list_display = ('title', 'is_active', 'order', 'created_at', 'preview')
	list_editable = ('is_active', 'order')
	ordering = ('order',)
	readonly_fields = ('preview',)

	def preview(self, obj):
		if not obj:
			return ''
		if obj.embed_html:
			return format_html('<div style="max-width:360px">{}</div>', format_html(obj.embed_html))
		if obj.embed_url:
			return format_html('<video controls style="max-width:360px; height:200px; object-fit:cover;"><source src="{}"></video>', obj.embed_url)
		if obj.video:
			try:
				url = obj.video.url
			except Exception:
				url = ''
			return format_html('<video controls style="max-width:360px; height:200px; object-fit:cover;"><source src="{}"></video>', url)
		return ''

	preview.short_description = 'Preview'
