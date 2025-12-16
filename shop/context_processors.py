# shop/context_processors.py
from decimal import Decimal
from .cart_utils import get_session_cart
from .models import Cart

def cart_count(request):
    """
    Adds `cart_count` (int) to every template context.
    Works for authenticated users (DB Cart) and anonymous (session).
    Always returns an int (0 if none).
    """
    try:
        if request.user.is_authenticated:
            # Try to get related cart (adjust to your model relationship)
            cart = getattr(request.user, "cart", None)
            if cart:
                return {"cart_count": int(cart.items_count())}
            # fallback: try Cart model lookup
            cart_obj = Cart.objects.filter(user=request.user).first()
            if cart_obj:
                return {"cart_count": int(cart_obj.items_count())}
            return {"cart_count": 0}
        else:
            session_cart = get_session_cart(request)  # should return dict {product_id: qty}
            if not session_cart:
                return {"cart_count": 0}
            # sum quantities and return integer
            total = sum(int(v) for v in session_cart.values())
            return {"cart_count": int(total)}
    except Exception:
        # Very defensive: never blow up template rendering
        return {"cart_count": 0}
