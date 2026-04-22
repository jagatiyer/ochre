from django.contrib import admin
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import (
    ShopCategory,
    ShopItem,
    ProductImage,
    UnitType,
    ProductType,
    ProductUnit,
    Cart,
    CartItem,
    ExperienceBooking,
    Order,
    OrderItem,
)


@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


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


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "order")
    ordering = ("order",)


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    class ShopItemForm(forms.ModelForm):
        description = forms.CharField(
            widget=CKEditor5Widget(config_name="blog"),
            required=False,
        )

        class Meta:
            model = ShopItem
            fields = "__all__"

    form = ShopItemForm

    list_display = (
        "title",
        "category",
        "is_experience",
        "is_featured",
        "price",
        "published",
        "created_at",
    )
    list_editable = ("is_featured", "published")
    list_filter = ("category", "is_experience", "is_featured", "published")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at",)

    fields = (
        "title",
        "caption",
        "slug",
        "category",
        "description",
        "image",
        "price",
        "tax_percent",
        "is_experience",
        "is_featured",
        "published",
    )

    inlines = [
        ProductUnitInline,
        ProductImageInline,
    ]


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


# ✅ ORDERS ADMIN (FINAL CLEAN VERSION)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("uuid", "user", "status", "created_at", "total_amount")
    list_filter = ("status", "created_at")
    search_fields = ("user__email",)  # ✅ added
    readonly_fields = ("created_at", "updated_at")

    def get_readonly_fields(self, request, obj=None):
        ro = list(self.readonly_fields)
        if obj and obj.status == obj.STATUS_PAID:
            ro += ["razorpay_order_id", "razorpay_payment_id", "razorpay_signature"]
        return ro


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "qty", "unit_price")