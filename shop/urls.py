# shop/urls.py
from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.shop_index, name="shop_index"),
    path("cart/", views.cart_view, name="cart_view"),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/", views.remove_cart_item, name="remove_cart_item"),

    # The missing one ↓↓↓
    path("checkout/", views.checkout_view, name="checkout_view"),

    path("<slug:slug>/", views.product_detail, name="product_detail"),
]
