from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ShopCategory,
    ShopItem,
    ExperienceBooking,
    UnitType,
    ProductType,
    ProductUnit,
    ProductImage,
)


class ProductUnitInline(admin.TabularInline):
    model = ProductUnit
    extra = 1
    fields = ("unit_type", "label", "value", "price", "is_default", "is_active")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "order", "preview")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;object-fit:contain;" />',
                obj.image.url
            )
        return "—"


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_experience", "price", "published")
    list_filter = ("category", "is_experience", "published")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at",)
    fields = (
        "title",
        "slug",
        "category",
        "description",
        "price",
        "tax_percent",
        "is_experience",
        "image",
        "published",
    )
    inlines = [ProductUnitInline, ProductImageInline]


@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ExperienceBooking)
class ExperienceBookingAdmin(admin.ModelAdmin):
    list_display = (
        "experience",
        "customer_name",
        "customer_email",
        "status",
        "payment_required",
        "created_at",
    )
    list_filter = ("status", "payment_required")
    search_fields = ("customer_name", "customer_email")
    readonly_fields = ("created_at", "updated_at", "payment_ref")


admin.site.register(UnitType)
admin.site.register(ProductType)
admin.site.register(ProductUnit)
