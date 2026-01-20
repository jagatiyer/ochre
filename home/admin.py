from django.contrib import admin
from django import forms
from .models import CarouselSlide, HomePageVideo, HomeContentSection


class HomePageVideoForm(forms.ModelForm):
	class Meta:
		model = HomePageVideo
		fields = '__all__'

	def clean(self):
		cleaned = super().clean()
		video = cleaned.get('video')
		embed_url = cleaned.get('embed_url')
		embed_html = cleaned.get('embed_html')
		# Ensure at most one source is provided.
		sources = [bool(video), bool(embed_url), bool(embed_html)]
		if sum(1 for s in sources if s) > 1:
			raise forms.ValidationError('Provide only one video source: upload OR embed URL OR embed HTML.')
		if not any(sources):
			raise forms.ValidationError('Provide a video file or an embed URL / embed HTML.')
		return cleaned


@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'is_active', 'display_order', 'auto_slide_seconds')
	list_editable = ('is_active', 'display_order', 'auto_slide_seconds')
	ordering = ('display_order',)
	search_fields = ('title',)


@admin.register(HomePageVideo)
class HomePageVideoAdmin(admin.ModelAdmin):
	form = HomePageVideoForm
	list_display = ('__str__', 'is_active', 'order', 'created_at')
	list_editable = ('is_active', 'order')
	ordering = ('order',)
	search_fields = ('title',)
	fieldsets = (
		(None, {
			'fields': ('title', 'order', 'is_active')
		}),
		('Video Source (choose one)', {
			'fields': ('video', 'embed_url', 'embed_html'),
			'description': 'Provide either an uploaded video file, an embed URL (YouTube/Vimeo), or raw embed HTML (iframe). Do not provide more than one source.'
		}),
	)

@admin.register(HomeContentSection)
class HomeContentSectionAdmin(admin.ModelAdmin):
	list_display = ('title', 'image_position', 'order', 'is_active')
	list_editable = ('image_position', 'order')
	ordering = ('order',)
	search_fields = ('title',)

