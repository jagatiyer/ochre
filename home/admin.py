from django.contrib import admin
from .models import CarouselSlide


@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'is_active', 'display_order', 'auto_slide_seconds')
	list_editable = ('is_active', 'display_order', 'auto_slide_seconds')
	ordering = ('display_order',)
	search_fields = ('title',)

