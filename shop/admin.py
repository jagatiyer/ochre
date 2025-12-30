from django.contrib import admin
from .models import ShopCategory, ShopItem, ExperienceBooking, UnitType, ProductType, ProductUnit

# Admin guidance:
# Workflow for configuring product units:
# 1) Create UnitType entries (one-time) such as "Volume" or "Size".
# 2) Create or open a ShopItem in the admin.
# 3) Under the ShopItem, use the "ProductUnit" inline to add sellable units for that product.
# 4) Provide a clear Label and set the Unit Price for each ProductUnit.
# 5) Mark exactly one ProductUnit as the Default unit for that product.
# 6) Save and verify on the public site the correct selector and price are shown.


@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_experience", "price", "published")
    list_filter = ("category", "is_experience", "published")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at",)
    fields = ("title", "slug", "category", "description", "price", "is_experience", "published")
    inlines = []


class ProductUnitInline(admin.TabularInline):
    model = ProductUnit
    extra = 1
    fields = ("unit_type", "label", "value", "price", "is_default", "is_active")
    readonly_fields = ()


# attach inline to admin after inline definition
ShopItemAdmin.inlines = [ProductUnitInline]


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
