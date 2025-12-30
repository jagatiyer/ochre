# shop/views.py

from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from .models import ShopItem, ShopCategory, Cart, CartItem, ExperienceBooking, ProductUnit
from .cart_utils import (
    add_to_session_cart,
    remove_from_session_cart,
    session_cart_to_items,
    get_session_cart,
)


def _is_ajax_request(request):
    """
    Modern AJAX detection for Django 4+.
    """
    return (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
    )


# ============================================================
# SHOP INDEX
# ============================================================

def shop_index(request):
    tab = request.GET.get("tab", "products")
    if tab not in ("products", "experiences"):
        tab = "products"

    selected_tab = tab
    is_experience = selected_tab == "experiences"

    category_slug = request.GET.get("category")
    categories = ShopCategory.objects.all()

    items_qs = ShopItem.objects.filter(published=True).select_related("category")

    if category_slug:
        items_qs = items_qs.filter(category__slug=category_slug)

    items = items_qs.order_by("-created_at")

    context = {
        "selected_tab": selected_tab,
        "categories": categories,
        "items": items,
        "items_count": items.count(),
        "active_category_slug": category_slug or "all",
    }
    return render(request, "shop/shop_index.html", context)


# ============================================================
# PRODUCT DETAIL
# ============================================================

def product_detail(request, slug):
    item = get_object_or_404(ShopItem, slug=slug, published=True)
    return render(request, "shop/product_detail.html", {"item": item})


# ============================================================
# ADD TO CART
# ============================================================

@require_POST
def add_to_cart(request):
    product_id = request.POST.get("product_id")
    product_unit_id = request.POST.get("product_unit_id")
    qty_raw = request.POST.get("qty", 1)

    if not product_id:
        return HttpResponseBadRequest("Missing product_id")

    try:
        qty = int(qty_raw)
        if qty < 1:
            raise ValueError()
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Invalid qty")

    product = get_object_or_404(ShopItem, id=product_id, published=True)

    # validate product_unit if provided
    product_unit = None
    if product_unit_id:
        try:
            product_unit = product.units.get(id=product_unit_id, is_active=True)
        except ProductUnit.DoesNotExist:
            return HttpResponseBadRequest("Invalid product_unit_id")

    # ---------------- AUTHENTICATED USER ----------------
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)

        defaults = {"qty": qty, "unit_price": (product_unit.price if product_unit else (product.price or Decimal("0.00"))), "product_unit": product_unit}
        ci, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            product_unit=product_unit,
            defaults=defaults,
        )

        if not created:
            ci.qty += qty
            ci.unit_price = defaults["unit_price"] or ci.unit_price
            ci.save()

        cart_count = cart.items_count()

    # ---------------- ANONYMOUS USER ----------------
    else:
        add_to_session_cart(request, product.id, qty, product_unit_id=product_unit_id)
        session_cart = get_session_cart(request)
        cart_count = sum(int(v) for v in session_cart.values()) if session_cart else 0

    # AJAX response
    if _is_ajax_request(request):
        return JsonResponse({
            "ok": True,
            "message": "Added to cart",
            "cart_count": cart_count,
        })

    # Non-AJAX fallback
    next_url = (
        request.POST.get("next")
        or request.META.get("HTTP_REFERER")
        or reverse("shop:shop_index")
    )
    # Add success message for non-AJAX cart additions
    messages.success(request, "Item added to cart successfully.")
    return redirect(next_url)


# ============================================================
# REMOVE CART ITEM
# ============================================================

@require_POST
def remove_cart_item(request):
    product_id = request.POST.get("product_id")
    product_unit_id = request.POST.get("product_unit_id")
    if not product_id:
        return HttpResponseBadRequest("Missing product_id")

    if request.user.is_authenticated:
        cart = getattr(request.user, "cart", None)
        if cart:
            if product_unit_id:
                CartItem.objects.filter(cart=cart, product_id=product_id, product_unit_id=product_unit_id).delete()
            else:
                CartItem.objects.filter(cart=cart, product_id=product_id).delete()
            cart_count = cart.items_count()
        else:
            cart_count = 0
    else:
        remove_from_session_cart(request, product_id, product_unit_id=product_unit_id)
        session_cart = get_session_cart(request)
        cart_count = sum(int(v) for v in session_cart.values()) if session_cart else 0

    if _is_ajax_request(request):
        return JsonResponse({"ok": True, "cart_count": cart_count})

    return redirect("shop:cart_view")


# ============================================================
# CART PAGE (PUBLIC)
# ============================================================

def cart_view(request):
    items = []
    subtotal = Decimal("0.00")

    # ---------------- AUTHENTICATED ----------------
    if request.user.is_authenticated:
        cart = getattr(request.user, "cart", None)
        if cart:
            for ci in cart.items.select_related("product", "product_unit").all():
                line_total = ci.line_total()
                items.append({
                    "product": ci.product,
                    "product_unit": getattr(ci, "product_unit", None),
                    "qty": ci.qty,
                    "unit_price": ci.unit_price,
                    "line_total": line_total,
                })
                subtotal += line_total

    # ---------------- SESSION CART ----------------
    else:
        items_raw = session_cart_to_items(request)
        for row in items_raw:
            items.append({
                "product": row["product"],
                "product_unit": row.get("product_unit"),
                "qty": row["qty"],
                "unit_price": (row.get("product_unit").price if row.get("product_unit") else (row["product"].price or Decimal("0.00"))),
                "line_total": row["line_total"],
            })
            subtotal += row["line_total"]

    gst = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))
    grand_total = subtotal + gst

    context = {
        "items": items,
        "subtotal": subtotal,
        "gst": gst,
        "grand_total": grand_total,
    }

    return render(request, "shop/cart.html", context)


# ============================================================
# CHECKOUT (AUTH REQUIRED)
# ============================================================

@login_required(login_url="account_login")
def checkout_view(request):
    cart = getattr(request.user, "cart", None)

    if not cart or not cart.items.exists():
        return redirect("shop:shop_index")

    context = {
        "cart": cart,
        "items": cart.items.select_related("product").all(),
        "subtotal": cart.subtotal(),
        "tax_total": cart.total_tax(),
        "total": cart.total(),
    }

    return render(request, "shop/checkout.html", context)


@require_POST
def experience_booking_create(request):
    """Handle creation of ExperienceBooking via POST from product detail booking form.

    Expects: experience_id, customer_name, customer_email, customer_phone (opt), notes (opt)
    """
    experience_id = request.POST.get("experience_id")
    customer_name = request.POST.get("customer_name")
    customer_email = request.POST.get("customer_email")
    customer_phone = request.POST.get("customer_phone", "")
    notes = request.POST.get("notes", "")

    if not experience_id or not customer_name or not customer_email:
        return HttpResponseBadRequest("Missing required booking fields")

    experience = get_object_or_404(ShopItem, id=experience_id, is_experience=True)

    booking = ExperienceBooking.objects.create(
        experience=experience,
        user=request.user if request.user.is_authenticated else None,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        notes=notes,
        status=ExperienceBooking.STATUS_PENDING,
        payment_required=False,
    )

    # Add success message and redirect back to product detail with a success flag
    messages.success(request, "Your booking request has been received. We will contact you shortly.")
    return redirect(f"{reverse('shop:product_detail', args=[experience.slug])}?booked=1")
