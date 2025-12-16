# shop/models.py
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

User = settings.AUTH_USER_MODEL


# ---------------------------
# Product / Category models
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
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["slug", "published"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            # naive slug; ensure uniqueness externally if necessary
            self.slug = slugify(self.title)[:255]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def price_display(self):
        if self.price is None:
            return ""
        return f"₹ {self.price:.2f}"


# ---------------------------
# Persistent Cart models
# ---------------------------
class Cart(models.Model):
    """
    One cart per user (optional). Anonymous users use session cart.
    """
    user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.CASCADE, related_name="cart"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return f"Cart(user={self.user})" if self.user else "Cart(anonymous)"

    def items_count(self):
        return self.items.aggregate(total=models.Sum("qty"))["total"] or 0

    def subtotal(self):
        """
        Sum of line totals (price * qty) before taxes/discounts.
        """
        rows = self.items.all()
        total = Decimal("0.00")
        for it in rows:
            total += it.line_total()
        return total

    def total_tax(self):
        """
        Compute tax assuming each CartItem.unit_price already excludes tax and
        each ShopItem has tax_percent defined. (This is a simple approach.)
        """
        tax = Decimal("0.00")
        for it in self.items.select_related("product"):
            tax += (it.unit_price * it.qty) * (it.product.tax_percent or Decimal("0.00")) / Decimal("100.00")
        return tax.quantize(Decimal("0.01"))

    def total(self):
        return (self.subtotal() + self.total_tax()).quantize(Decimal("0.01"))


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(ShopItem, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    # unit_price is a snapshot of product.price at the time of add-to-cart
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.qty}× {self.product.title}"

    def line_total(self):
        return (self.unit_price * Decimal(self.qty)).quantize(Decimal("0.01"))


# ---------------------------
# Orders / OrderItem models
# ---------------------------
class Order(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending"  # awaiting payment
    STATUS_PAID = "paid"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = (
        (STATUS_DRAFT, "Draft"),
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_PENDING)
    # Snapshot fields (store totals at time of order)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    # payment reference (gateway id, etc.)
    payment_ref = models.CharField(max_length=255, blank=True, null=True)
    # free-form JSON field for metadata if you need it (requires Django 3.1+)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Order #{self.pk} — {self.status}"

    def recalc_from_items(self):
        """
        Recalculate subtotal/tax/total from related OrderItem rows.
        Use this after creating/updating OrderItem rows.
        """
        subtotal = Decimal("0.00")
        tax_total = Decimal("0.00")
        for it in self.items.all():
            subtotal += it.line_total()
            tax_total += (it.unit_price * it.qty) * (it.tax_percent or Decimal("0.00")) / Decimal("100.00")
        self.subtotal = subtotal.quantize(Decimal("0.01"))
        self.tax_total = Decimal(tax_total).quantize(Decimal("0.01"))
        self.total = (self.subtotal + self.tax_total).quantize(Decimal("0.01"))
        self.save(update_fields=["subtotal", "tax_total", "total"])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(ShopItem, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)  # snapshot of title
    qty = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)  # snapshot price
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    # any extra metadata like "experience_date" can be saved here
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        # no unique_together — same product can appear multiple times for complex orders
        ordering = ("id",)

    def __str__(self):
        return f"{self.qty}× {self.title} (Order #{self.order_id})"

    def line_total(self):
        return (self.unit_price * Decimal(self.qty)).quantize(Decimal("0.01"))
