# shop/cart_utils.py
from decimal import Decimal
from django.conf import settings
from .models import Cart, CartItem, ShopItem, ProductUnit

SESSION_KEY = "cart"  # {'<product_id>' or '<product_id>|<unit_id>': qty, ...}

def get_session_cart(request):
    return request.session.get(SESSION_KEY, {})

def save_session_cart(request, cart_dict):
    request.session[SESSION_KEY] = cart_dict
    request.session.modified = True

def add_to_session_cart(request, product_id, qty=1, product_unit_id=None):
    cart = get_session_cart(request)
    if product_unit_id:
        key = f"{product_id}|{product_unit_id}"
    else:
        key = str(product_id)
    cart[key] = cart.get(key, 0) + int(qty)
    save_session_cart(request, cart)
    return cart

def remove_from_session_cart(request, product_id, product_unit_id=None):
    cart = get_session_cart(request)
    key = f"{product_id}|{product_unit_id}" if product_unit_id else str(product_id)
    if key in cart:
        del cart[key]
        save_session_cart(request, cart)
    return cart

def session_cart_to_items(request):
    """Return list of dicts with product, optional product_unit, qty and line_total for rendering."""
    cart = get_session_cart(request)
    rows = []
    if not cart:
        return rows

    product_keys = []
    unit_keys = {}
    for key in cart.keys():
        try:
            if "|" in key:
                pid_str, unit_str = key.split("|", 1)
                pid = int(pid_str)
                uid = int(unit_str)
                product_keys.append(pid)
                unit_keys.setdefault(pid, []).append(uid)
            else:
                pid = int(key)
                product_keys.append(pid)
        except (ValueError, TypeError):
            # skip malformed session keys
            continue

    products = ShopItem.objects.filter(id__in=product_keys, published=True)
    products_map = {p.id: p for p in products}

    # preload units for relevant products
    unit_ids = []
    for vals in unit_keys.values():
        for v in vals:
            try:
                unit_ids.append(int(v))
            except (ValueError, TypeError):
                continue
    units = ProductUnit.objects.filter(id__in=unit_ids, is_active=True) if unit_ids else []
    units_map = {u.id: u for u in units}

    for key, qty in cart.items():
        try:
            if "|" in key:
                pid_str, unit_str = key.split("|", 1)
                pid = int(pid_str)
                uid = int(unit_str)
                p = products_map.get(pid)
                u = units_map.get(uid)
                if not p or not u:
                    continue
                line_total = (u.price or 0) * int(qty)
                rows.append({"product": p, "product_unit": u, "qty": qty, "line_total": line_total})
            else:
                pid = int(key)
                p = products_map.get(pid)
                if not p:
                    continue
                line_total = (p.price or 0) * int(qty)
                rows.append({"product": p, "product_unit": None, "qty": qty, "line_total": line_total})
        except (ValueError, TypeError):
            # skip malformed cart entries
            continue

    return rows

def merge_session_cart_to_user(request, user):
    """Create or get Cart for user and merge session cart items in DB."""
    session_cart = get_session_cart(request)
    if not session_cart:
        return
    cart, _ = Cart.objects.get_or_create(user=user)
    for key, qty in session_cart.items():
        try:
            if "|" in key:
                pid_str, uid_str = key.split("|", 1)
                pid = int(pid_str)
                uid = int(uid_str)
            else:
                pid = int(key)
                uid = None
        except (ValueError, TypeError):
            # skip malformed keys
            continue

        try:
            product = ShopItem.objects.get(id=pid, published=True)
        except ShopItem.DoesNotExist:
            continue

        if uid:
            try:
                unit = ProductUnit.objects.get(id=uid, product=product, is_active=True)
            except ProductUnit.DoesNotExist:
                unit = None
        else:
            unit = None

        defaults = {"qty": qty, "unit_price": (unit.price if unit else (product.price or 0)), "product_unit": unit}
        ci, created = CartItem.objects.get_or_create(cart=cart, product=product, product_unit=unit, defaults=defaults)
        if not created:
            ci.qty = ci.qty + qty
            ci.unit_price = defaults["unit_price"] or ci.unit_price
            ci.save()
    # clear session cart
    request.session[SESSION_KEY] = {}
    request.session.modified = True
