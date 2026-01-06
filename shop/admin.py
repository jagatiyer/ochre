from django.contrib import admin
from .models import (
    ShopCategory,
    ShopItem,
    ExperienceBooking,
    UnitType,
    ProductType,
    ProductUnit,
    ProductImage,
)


@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class ProductUnitInline(admin.TabularInline):
    model = ProductUnit
    extra = 1
    fields = ("unit_type", "label", "value", "price", "is_default", "is_active")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "order")
    ordering = ("order",)


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_experience", "price", "published")
    list_filter = ("category", "is_experience", "published")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at",)

    # ✅ IMAGE FIELD IS INCLUDED HERE
    fields = (
        "title",
        "slug",
        "category",
        "description",
        "image",
        "price",
        "is_experience",
        "published",
    )

    inlines = [ProductUnitInline, ProductImageInline]


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
