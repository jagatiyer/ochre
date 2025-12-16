# shop/views.py
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .models import ShopItem, ShopCategory, Cart, CartItem
from .cart_utils import (
    add_to_session_cart,
    remove_from_session_cart,
    session_cart_to_items,
    get_session_cart,
)


def _is_ajax_request(request):
    """
    Modern AJAX detection for Django 4+ (request.is_ajax() removed).
    Checks standard X-Requested-With header from both request.headers and META.
    """
    return (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
    )


# ---------------------------
# SHOP LIST / INDEX
# ---------------------------
def shop_index(request):
    """
    Shop index with two tabs: products / experiences.
    - Query param `tab` : "products" or "experiences" (default products)
    - Optional query param `category` : category slug to filter items
    """
    tab = request.GET.get("tab", "products")
    if tab not in ("products", "experiences"):
        tab = "products"
    selected_tab = "products" if tab == "products" else "experiences"
    is_experience = selected_tab == "experiences"

    # category filter (optional)
    category_slug = request.GET.get("category")
    categories = ShopCategory.objects.all()

    items_qs = ShopItem.objects.filter(is_experience=is_experience, published=True).select_related("category")

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


# ---------------------------
# PRODUCT DETAIL
# ---------------------------
def product_detail(request, slug):
    item = get_object_or_404(ShopItem, slug=slug, published=True)
    context = {"item": item}
    return render(request, "shop/product_detail.html", context)


# ---------------------------
# ADD TO CART (AJAX-friendly)
# ---------------------------
@require_POST
def add_to_cart(request):
    """
    POST params:
      - product_id
      - qty (optional, defaults to 1)
    Behavior:
      - For authenticated users: persist to DB Cart / CartItem.
      - For anonymous users: persist in session via cart_utils.add_to_session_cart.
    Returns:
      - JsonResponse when AJAX request, otherwise redirect back to shop index.
    """
    product_id = request.POST.get("product_id")
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

    # Persist to DB if authenticated
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        ci, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"qty": qty, "unit_price": product.price or Decimal("0.00")},
        )
        if not created:
            ci.qty = ci.qty + qty
            # snapshot latest price if you prefer; otherwise keep existing
            ci.unit_price = product.price or ci.unit_price
            ci.save()
    else:
        add_to_session_cart(request, product.id, qty)

    # compute a lightweight cart_count to return
    if request.user.is_authenticated:
        cart_count = cart.items_count() if cart else 0
    else:
        session_cart = get_session_cart(request)
        cart_count = sum(int(v) for v in session_cart.values()) if session_cart else 0

    # JSON response for AJAX
    if _is_ajax_request(request):
        return JsonResponse({"ok": True, "message": "Added to cart", "cart_count": cart_count})

    # fallback: redirect back to product or shop
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("shop:shop_index")
    return redirect(next_url)


# ---------------------------
# REMOVE CART ITEM (AJAX-friendly)
# ---------------------------
@require_POST
def remove_cart_item(request):
    """
    POST params:
      - product_id
    Works for both authenticated and anonymous users.
    """
    product_id = request.POST.get("product_id")
    if not product_id:
        return HttpResponseBadRequest("Missing product_id")

    if request.user.is_authenticated:
        cart = getattr(request.user, "cart", None)
        if cart:
            CartItem.objects.filter(cart=cart, product_id=product_id).delete()
    else:
        remove_from_session_cart(request, product_id)

    # compute cart_count
    if request.user.is_authenticated:
        cart = getattr(request.user, "cart", None)
        cart_count = cart.items_count() if cart else 0
    else:
        session_cart = get_session_cart(request)
        cart_count = sum(int(v) for v in session_cart.values()) if session_cart else 0

    if _is_ajax_request(request):
        return JsonResponse({"ok": True, "cart_count": cart_count})

    # fallback redirect to cart page
    return redirect("shop:cart_view")


# ---------------------------
# CART PAGE (view)
# ---------------------------
# ---------------------------
# CART PAGE (view)
# ---------------------------
def cart_view(request):
    """
    Renders a clean cart summary:
    - items (rows of product, qty, line_total)
    - subtotal
    - gst (18%)
    - grand_total
    """

    if request.user.is_authenticated:
        cart = getattr(request.user, "cart", None)
        items = []
        subtotal = Decimal("0.00")

        if cart:
            for ci in cart.items.select_related("product").all():
                line_total = ci.line_total()
                items.append({
                    "product": ci.product,
                    "qty": ci.qty,
                    "unit_price": ci.unit_price,
                    "line_total": line_total,
                })
                subtotal += line_total

    else:
        # SESSION CART
        items_raw = session_cart_to_items(request)
        items = []
        subtotal = Decimal("0.00")

        for row in items_raw:
            items.append({
                "product": row["product"],
                "qty": row["qty"],
                "unit_price": row["product"].price or Decimal("0.00"),
                "line_total": row["line_total"],
            })
            subtotal += row["line_total"]

    # --- Tax & grand total ---
    gst = subtotal * Decimal("0.18")      # 18% GST
    gst = gst.quantize(Decimal("0.01"))   # round to 2 decimals

    grand_total = subtotal + gst

    context = {
        "items": items,
        "subtotal": subtotal,
        "gst": gst,
        "grand_total": grand_total,
    }

    return render(request, "shop/cart.html", context)



# ---------------------------
# CHECKOUT VIEW (requires login)
# ---------------------------
@login_required
def checkout_view(request):
    """
    Minimal checkout view — requires authentication.
    On GET: show checkout form (billing/shipping info).
    On POST: validate cart and create Order (not implemented here).
    For now this ensures an authenticated user and non-empty cart.
    """
    cart = getattr(request.user, "cart", None)
    if not cart or not cart.items.exists():
        # No cart / no items => redirect to shop
        return redirect("shop:shop_index")

    # For now, just render a placeholder checkout template you can expand.
    # You will implement order creation and payment integration here.
    context = {
        "cart": cart,
        "items": cart.items.select_related("product").all(),
        "subtotal": cart.subtotal(),
        "tax_total": cart.total_tax(),
        "total": cart.total(),
    }
    return render(request, "shop/checkout.html", context)
