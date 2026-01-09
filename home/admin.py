from django.contrib import admin
from .models import CarouselSlide, HomePageVideo, HomeContentSection


@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'is_active', 'display_order', 'auto_slide_seconds')
	list_editable = ('is_active', 'display_order', 'auto_slide_seconds')
	ordering = ('display_order',)
	search_fields = ('title',)


@admin.register(HomePageVideo)
class HomePageVideoAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'is_active', 'order', 'created_at')
	list_editable = ('is_active', 'order')
	ordering = ('order',)
	search_fields = ('title',)

@admin.register(HomeContentSection)
class HomeContentSectionAdmin(admin.ModelAdmin):
	list_display = ('title', 'image_position', 'order', 'is_active')
	list_editable = ('image_position', 'order')
	ordering = ('order',)
	search_fields = ('title',)

