from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
import razorpay
import logging

from shop.models import Order

logger = logging.getLogger(__name__)


def send_order_email(order):
    """Send a simple order confirmation email. Non-blocking; errors are logged."""
    subject = f"Order received: {order.uuid}"
    message = f"Thank you for your order. Order id: {order.uuid}\nAmount: {order.total_amount} {order.currency}\nStatus: {order.status}"
    from_email = settings.EMAIL_HOST_USER or settings.CONTACT_EMAIL or "noreply@example.com"
    recipient = [order.user.email] if order.user and getattr(order.user, 'email', None) else [settings.CONTACT_EMAIL]
    try:
        send_mail(subject, message, from_email, recipient, fail_silently=True)
    except Exception as e:
        logger.exception("send_order_email failed: %s", e)


def send_order_sms(order):
    """Placeholder SMS hook for MSG91 or similar. Non-blocking."""
    try:
        # Intentionally a stub; integrate MSG91 or other provider when keys available.
        logger.info("send_order_sms stub called for order %s", order.uuid)
    except Exception:
        logger.exception("send_order_sms failed")


@require_POST
def verify(request):
    """Verify Razorpay payment signature and update Order status.

    Expected POST fields: razorpay_payment_id, razorpay_order_id, razorpay_signature, order_internal_id
    """
    payment_id = request.POST.get("razorpay_payment_id")
    rp_order_id = request.POST.get("razorpay_order_id")
    signature = request.POST.get("razorpay_signature")
    order_internal_id = request.POST.get("order_internal_id")

    if not (payment_id and rp_order_id and signature and order_internal_id):
        return HttpResponseBadRequest("Missing required fields")

    order = get_object_or_404(Order, uuid=order_internal_id)

    if not settings.RAZORPAY_TEST_KEYS_PROVIDED:
        order.status = Order.STATUS_FAILED
        order.save()
        return JsonResponse({"ok": False, "error": "Razorpay keys not configured"}, status=500)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # ensure the posted razorpay_order_id matches the one created for this Order
    if order.razorpay_order_id and rp_order_id != order.razorpay_order_id:
        order.status = Order.STATUS_FAILED
        order.save()
        logger.warning("Posted razorpay_order_id does not match order record: %s != %s", rp_order_id, order.razorpay_order_id)
        return JsonResponse({"ok": False, "error": "order_id_mismatch"}, status=400)

    try:
        client.utility.verify_payment_signature(
            {"razorpay_order_id": rp_order_id, "razorpay_payment_id": payment_id, "razorpay_signature": signature}
        )
    except Exception as e:
        # signature verification failed
        order.status = Order.STATUS_FAILED
        order.save()
        logger.exception("Razorpay signature verification failed: %s", e)
        return JsonResponse({"ok": False, "error": "signature_verification_failed"}, status=400)

    # success
    order.razorpay_payment_id = payment_id
    order.razorpay_signature = signature
    order.status = Order.STATUS_PAID
    order.save()

    # Fire non-blocking hooks
    try:
        send_order_email(order)
    except Exception:
        logger.exception("send_order_email hook failed")

    try:
        send_order_sms(order)
    except Exception:
        logger.exception("send_order_sms hook failed")

    return JsonResponse({"ok": True})
