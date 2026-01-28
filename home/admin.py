from django.contrib import admin
from .models import CarouselSlide, HomePageVideo, HomeContentSection
from .models import HomeSectionHeader


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
	fields = (
		'header',
		'title',
		'body',
		'image',
		'image_position',
		'order',
		'is_active',
		'created_at',
	)
	readonly_fields = ('created_at',)


@admin.register(HomeSectionHeader)
class HomeSectionHeaderAdmin(admin.ModelAdmin):
	list_display = ('top_label', 'title')
	fields = ('top_label', 'title', 'description')
	ordering = ('-id',)
	search_fields = ('title', 'top_label')

