from django.contrib import admin
from django import forms
from django.contrib import messages
from django.utils import timezone
from django_ckeditor_5.widgets import CKEditor5Widget
import logging

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

from payments.views import send_dispatch_email, send_delivery_email
from shop.utils.invoice import generate_invoice

logger = logging.getLogger(__name__)


# ---------------------------
# CATEGORY
# ---------------------------
@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


# ---------------------------
# INLINES
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


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "order")
    ordering = ("order",)


# ---------------------------
# SHOP ITEM
# ---------------------------
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
        "allowed_pincodes",
    )

    inlines = [
        ProductUnitInline,
        ProductImageInline,
    ]


# ---------------------------
# EXPERIENCE BOOKING
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
# PRODUCT TYPES
# ---------------------------
@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(UnitType)
class UnitTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


# ---------------------------
# CART
# ---------------------------
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "updated_at")
    readonly_fields = ("updated_at",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "product_unit", "qty", "unit_price")


# ---------------------------
# DISPATCH ACTION
# ---------------------------
def mark_as_dispatched(modeladmin, request, queryset):
    for order in queryset:

        if order.status != Order.STATUS_PAID:
            continue

        if not order.full_name or not order.billing_address:
            modeladmin.message_user(
                request,
                f"Order {order.uuid} missing customer details",
                level=messages.WARNING
            )
            continue

        if not order.tracking_id:
            modeladmin.message_user(
                request,
                f"Order {order.uuid} missing tracking ID",
                level=messages.ERROR
            )
            continue

        if not order.invoice_number:
            modeladmin.message_user(
                request,
                f"Order {order.uuid} missing invoice number",
                level=messages.ERROR
            )
            continue

        # Prevent duplicate invoice numbers
        if Order.objects.filter(invoice_number=order.invoice_number).exclude(id=order.id).exists():
            modeladmin.message_user(
                request,
                f"Invoice number {order.invoice_number} already used",
                level=messages.ERROR
            )
            continue

        # ✅ Generate invoice FIRST
        if not order.invoice_file:
            generate_invoice(order)
            logger.info("INVOICE GENERATED: %s", order.uuid)

        # ✅ Mark dispatched
        order.status = Order.STATUS_DISPATCHED
        order.dispatch_date = timezone.now()
        order.save()

        # ✅ Send email with invoice
        try:
            send_dispatch_email(order)
        except Exception as e:
            logger.error("EMAIL FAILED for Order %s: %s", order.uuid, e)
            modeladmin.message_user(
                request,
                f"Order {order.uuid} marked dispatched, but notification email failed to send.",
                level=messages.WARNING
            )

        logger.info("ORDER DISPATCHED: %s", order.uuid)


mark_as_dispatched.short_description = "Mark selected as Dispatched"


# ---------------------------
# DELIVERY ACTION
# ---------------------------
def mark_as_delivered(modeladmin, request, queryset):
    for order in queryset:

        if order.status != Order.STATUS_DISPATCHED:
            continue

        order.status = Order.STATUS_DELIVERED
        order.save()

        send_delivery_email(order)

        logger.info("DELIVERED: %s", order.uuid)


mark_as_delivered.short_description = "Mark selected as Delivered"


# ---------------------------
# ORDER ADMIN
# ---------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "user",
        "status",
        "invoice_number",
        "tracking_id",
        "created_at",
        "total_amount",
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__email",)
    readonly_fields = ("uuid", "created_at", "updated_at")

    fields = (
        "uuid",
        "user",
        "status",

        # 🔹 dispatch + invoice inputs
        "invoice_number",
        "tracking_id",
        "carrier_name",

        # 🔹 customer details
        "full_name",
        "phone",
        "billing_address",
        "shipping_address",
        "gst_number",

        # 🔹 financials
        "total_amount",

        # 🔹 system
        "invoice_file",
        "dispatch_date",
        "created_at",
        "updated_at",
    )

    actions = [mark_as_dispatched, mark_as_delivered]

    def get_readonly_fields(self, request, obj=None):
        ro = list(self.readonly_fields)
        if obj and obj.status == obj.STATUS_PAID:
            ro += ["razorpay_order_id", "razorpay_payment_id", "razorpay_signature"]
        return ro


# ---------------------------
# ORDER ITEMS
# ---------------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "qty", "unit_price")