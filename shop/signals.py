# shop/signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .cart_utils import merge_session_cart_to_user

@receiver(user_logged_in)
def on_user_login(sender, user, request, **kwargs):
    merge_session_cart_to_user(request, user)
