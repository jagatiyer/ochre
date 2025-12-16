# shop/cart_utils.py
from decimal import Decimal
from django.conf import settings
from .models import Cart, CartItem, ShopItem

SESSION_KEY = "cart"  # {'<product_id>': qty, ...}

def get_session_cart(request):
    return request.session.get(SESSION_KEY, {})

def save_session_cart(request, cart_dict):
    request.session[SESSION_KEY] = cart_dict
    request.session.modified = True

def add_to_session_cart(request, product_id, qty=1):
    cart = get_session_cart(request)
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + int(qty)
    save_session_cart(request, cart)
    return cart

def remove_from_session_cart(request, product_id):
    cart = get_session_cart(request)
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        save_session_cart(request, cart)
    return cart

def session_cart_to_items(request):
    """Return list of dicts with product and qty for rendering."""
    cart = get_session_cart(request)
    product_ids = [int(i) for i in cart.keys()] if cart else []
    products = ShopItem.objects.filter(id__in=product_ids, published=True)
    mapping = {p.id: p for p in products}
    rows = []
    for pid_str, qty in cart.items():
        pid = int(pid_str)
        p = mapping.get(pid)
        if not p:  # product removed/unpublished
            continue
        rows.append({"product": p, "qty": qty, "line_total": (p.price or 0) * int(qty)})
    return rows

def merge_session_cart_to_user(request, user):
    """Create or get Cart for user and merge session cart items in DB."""
    session_cart = get_session_cart(request)
    if not session_cart:
        return
    cart, _ = Cart.objects.get_or_create(user=user)
    for pid_str, qty in session_cart.items():
        pid = int(pid_str)
        try:
            product = ShopItem.objects.get(id=pid, published=True)
        except ShopItem.DoesNotExist:
            continue
        ci, created = CartItem.objects.get_or_create(cart=cart, product=product,
                                                     defaults={"qty": qty, "unit_price": product.price or 0})
        if not created:
            ci.qty = ci.qty + qty
            ci.unit_price = product.price or ci.unit_price
            ci.save()
    # clear session cart
    request.session[SESSION_KEY] = {}
    request.session.modified = True
