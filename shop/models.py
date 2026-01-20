from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.text import slugify
import uuid

User = settings.AUTH_USER_MODEL


# ---------------------------
# Categories
# ---------------------------
class ShopCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Shop categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ---------------------------
# Products
# ---------------------------
class ShopItem(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.ForeignKey(
        ShopCategory, related_name="shopitem", on_delete=models.CASCADE
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    is_experience = models.BooleanField(default=False)
    image = models.ImageField(upload_to="shop/", blank=True, null=True)

    # ✅ FEATURED FLAG (NEW)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["slug", "published"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:255]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    # ---- helpers used in templates ----
    def has_units(self):
        return self.units.filter(is_active=True).exists()

    def active_units(self):
        return self.units.filter(is_active=True).order_by("-is_default", "id")

    def default_unit(self):
        return self.units.filter(is_active=True, is_default=True).first()

    def price_display(self):
        return f"₹ {self.price:.2f}" if self.price else ""


# ---------------------------
# Product Gallery Images
# ---------------------------
class ProductImage(models.Model):
    product = models.ForeignKey(
        ShopItem,
        related_name="gallery_images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to="shop/gallery/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return f"{self.product.title} image {self.order}"


# ---------------------------
# Units
# ---------------------------
class UnitType(models.Model):
    name = models.CharField(max_length=50)
    code = models.SlugField(unique=True, max_length=30)

    def __str__(self):
        return self.name


class ProductUnit(models.Model):
    product = models.ForeignKey(
        ShopItem,
        related_name="units",
        on_delete=models.CASCADE,
    )
    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)
    label = models.CharField(max_length=50)
    value = models.CharField(max_length=20, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.is_default:
            ProductUnit.objects.filter(product=self.product).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} – {self.label}"


# ---------------------------
# LEGACY Product Type (DO NOT DELETE)
# ---------------------------
class ProductType(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ---------------------------
# Cart
# ---------------------------
class Cart(models.Model):
    user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.CASCADE, related_name="cart"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return f"Cart({self.user})" if self.user else "Cart(anonymous)"

    def items_count(self):
        return sum(item.qty for item in self.items.all())

    def subtotal(self):
        return sum(item.line_total() for item in self.items.all())

    def total_tax(self):
        return sum(
            item.line_total() * (item.tax_percent / Decimal("100"))
            for item in self.items.all()
        )

    def total(self):
        return self.subtotal() + self.total_tax()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(ShopItem, on_delete=models.CASCADE)
    product_unit = models.ForeignKey(
        ProductUnit, null=True, blank=True, on_delete=models.SET_NULL
    )
    qty = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("cart", "product", "product_unit")

    def __str__(self):
        return f"{self.qty} × {self.product}"

    def line_total(self):
        return (self.unit_price or Decimal("0.00")) * self.qty

    @property
    def tax_percent(self):
        return self.product.tax_percent if self.product else Decimal("0.00")


# ---------------------------
# Experience Bookings
# ---------------------------
class ExperienceBooking(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_PAID = "paid"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_PAID, "Paid"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    experience = models.ForeignKey(
        ShopItem,
        on_delete=models.CASCADE,
        related_name="experience_bookings",
        limit_choices_to={"is_experience": True},
    )

    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30, blank=True)

    notes = models.TextField(blank=True)
    metadata = models.JSONField(blank=True, null=True)

    status = models.CharField(
        max_length=24,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    payment_required = models.BooleanField(default=False)
    payment_ref = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Booking #{self.pk}"


# ---------------------------
# Orders
# ---------------------------
class Order(models.Model):
    """Order model for shop payments.

    Keep a UUID for external references while retaining DB integer PK
    compatibility to avoid invasive migrations elsewhere.
    """

    STATUS_CREATED = "created"
    STATUS_PAYMENT_PENDING = "payment_pending"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (STATUS_CREATED, "Created"),
        (STATUS_PAYMENT_PENDING, "Payment pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_FAILED, "Failed"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_CREATED)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=6, default="INR")

    # Razorpay integration fields
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    payment_ref = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Order {self.uuid} (user={self.user})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(ShopItem, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    qty = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    metadata = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.qty} × {self.title}"
