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
    path("my-orders/", views.my_orders, name="my_orders"),
    path("order/invoice/<uuid:order_uuid>/", views.download_invoice, name="download_invoice"),
    path("check-availability/", views.check_availability, name="check_availability"),
    path("experience/book/", views.experience_booking_create, name="experience_booking_create"),

    path("<slug:slug>/", views.product_detail, name="product_detail"),
]
