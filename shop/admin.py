from django.contrib import admin
from .models import (
    ShopCategory,
    ShopItem,
    ProductImage,
    UnitType,
    ProductType,      # LEGACY – must stay
    ProductUnit,
    Cart,
    CartItem,
    ExperienceBooking,
    Order,             # LEGACY – must stay
    OrderItem,         # LEGACY – must stay
)


# ---------------------------
# Category
# ---------------------------
@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


# ---------------------------
# Product Units (inline)
# ---------------------------
class ProductUnitInline(admin.TabularInline):
    model = ProductUnit
    extra = 1
    fields = (
        "unit_type",
        "label",
        "value",
        "price",
        "is_default",
        "is_active",
    )


# ---------------------------
# Product Gallery Images (inline)
# ---------------------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "order")
    ordering = ("order",)


# ---------------------------
# Products
# ---------------------------
@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_experience", "price", "published")
    list_filter = ("category", "is_experience", "published")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at",)

    # ✅ THIS is why the image field now shows
    fields = (
        "title",
        "slug",
        "category",
        "description",
        "image",          # MAIN IMAGE
        "price",
        "tax_percent",
        "is_experience",
        "published",
    )

    inlines = [
        ProductUnitInline,
        ProductImageInline,
    ]


# ---------------------------
# Experience Bookings
# ---------------------------
@admin.register(ExperienceBooking)
class ExperienceBookingAdmin(admin.ModelAdmin):
    list_display = (
        "experience",
        "customer_name",
        "customer_email",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("customer_name", "customer_email")
    readonly_fields = ("created_at", "updated_at")


# ---------------------------
# LEGACY MODELS (DO NOT REMOVE)
# ---------------------------
@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(UnitType)
class UnitTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "updated_at")
    readonly_fields = ("updated_at",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "product_unit", "qty", "unit_price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at", "total")
    list_filter = ("status",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "qty", "unit_price")
