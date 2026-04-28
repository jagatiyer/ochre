from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
import razorpay
import logging

from shop.models import Order

logger = logging.getLogger(__name__)


# ============================================================
# EMAIL
# ============================================================

def send_order_email(order):
    logger.info("EMAIL: start for order %s", order.uuid)

    if not order.user or not order.user.email:
        logger.warning("EMAIL: no recipient for order %s", order.uuid)
        return

    subject = f"Ochre Order Confirmation - {order.uuid}"
    message = f"""
Hi {order.full_name or "Customer"},

Thank you for your order with Ochre.

Your payment has been successfully received.

----------------------------------------
ORDER DETAILS
----------------------------------------
Order ID: {order.uuid}
Amount Paid: ₹{order.total_amount}
Payment Reference: {order.payment_ref}

----------------------------------------
SHIPPING DETAILS
----------------------------------------
Name: {order.full_name}
Phone: {order.phone}
Address:
{order.shipping_address}

----------------------------------------

What happens next?

• Your order is being processed
• You will receive a dispatch email with tracking details
• Invoice will be shared at dispatch

Regards,  
Ochre Team
"""

    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
    recipient = [order.user.email]

    email = EmailMessage(subject, message, from_email, recipient)

    try:
        email.send(fail_silently=False)
        logger.info("EMAIL: sent successfully for order %s", order.uuid)
    except Exception as e:
        logger.exception("EMAIL FAILED for order %s: %s", order.uuid, e)
        raise


def send_dispatch_email(order):
    logger.info("EMAIL: start dispatch for order %s", order.uuid)

    if not order.user or not order.user.email:
        logger.warning("EMAIL: no recipient for dispatch %s", order.uuid)
        return

    subject = f"Your Ochre Order has been Dispatched - {order.uuid}"
    message = f"""
Hi {order.full_name},

Your order has been dispatched.

----------------------------------------
ORDER DETAILS
----------------------------------------
Order ID: {order.uuid}
Invoice Number: {order.invoice_number or "To be assigned"}

----------------------------------------
TRACKING DETAILS
----------------------------------------
Tracking ID: {order.tracking_id or 'N/A'}
Carrier: {order.carrier_name or 'N/A'}

----------------------------------------

Your invoice is attached with this email.

Regards,  
Ochre Team
"""

    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
    recipient = [order.user.email]

    email = EmailMessage(subject, message, from_email, recipient)

    if order.invoice_file and hasattr(order.invoice_file, "path"):
        email.attach_file(order.invoice_file.path)

    try:
        email.send(fail_silently=False)
        logger.info("EMAIL: dispatch sent successfully for order %s", order.uuid)
    except Exception as e:
        logger.exception("EMAIL FAILED for dispatch order %s: %s", order.uuid, e)
        raise


def send_delivery_email(order):
    logger.info("EMAIL: start delivery for order %s", order.uuid)

    if not order.user or not order.user.email:
        return

    subject = f"Order Delivered - {order.uuid}"
    message = f"""
Hi {order.full_name},

Your order has been successfully delivered.

We hope you enjoy your purchase.

Regards,  
Ochre Team
"""

    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
    recipient = [order.user.email]

    email = EmailMessage(subject, message, from_email, recipient)

    try:
        email.send(fail_silently=False)
        logger.info("EMAIL: delivery sent successfully for order %s", order.uuid)
    except Exception as e:
        logger.exception("EMAIL FAILED for delivery order %s: %s", order.uuid, e)
        raise


# ============================================================
# SMS (stub)
# ============================================================

def send_order_sms(order):
    try:
        logger.info("SMS stub for order %s", order.uuid)
    except Exception:
        logger.exception("SMS failed")


# ============================================================
# VERIFY PAYMENT
# ============================================================

@require_POST
def verify(request):
    logger.info("VERIFY HIT: %s", request.POST)

    payment_id = request.POST.get("razorpay_payment_id")
    rp_order_id = request.POST.get("razorpay_order_id")
    signature = request.POST.get("razorpay_signature")
    order_internal_id = request.POST.get("order_internal_id")

    if not (payment_id and rp_order_id and signature and order_internal_id):
        return HttpResponseBadRequest("Missing required fields")

    order = get_object_or_404(Order, uuid=order_internal_id)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    # ============================================================
    # ORDER VALIDATION
    # ============================================================

    if order.razorpay_order_id and rp_order_id != order.razorpay_order_id:
        order.status = Order.STATUS_FAILED
        order.save()

        logger.warning(
            "Order mismatch: %s != %s",
            rp_order_id,
            order.razorpay_order_id
        )

        return JsonResponse(
            {"ok": False, "error": "order_id_mismatch"},
            status=400
        )

    # ============================================================
    # SIGNATURE VERIFY
    # ============================================================

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": rp_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        })
        logger.info("SIGNATURE VERIFIED for order %s", order.uuid)

    except Exception as e:
        order.status = Order.STATUS_FAILED
        order.save()

        logger.exception("SIGNATURE FAILED for order %s: %s", order.uuid, e)

        return JsonResponse(
            {"ok": False, "error": "signature_verification_failed"},
            status=400
        )

    # ============================================================
    # SUCCESS → MARK PAID
    # ============================================================

    order.razorpay_payment_id = payment_id
    order.razorpay_signature = signature
    order.payment_ref = payment_id
    order.status = Order.STATUS_PAID
    order.save()

    logger.info("ORDER MARKED PAID: %s", order.uuid)

    # ============================================================
    # 🚨 IMPORTANT: NO INVOICE HERE
    # ============================================================

    # Invoice will be generated later by admin at dispatch

    # ============================================================
    # CLEAR CART
    # ============================================================

    if order.user and hasattr(order.user, "cart"):
        try:
            order.user.cart.items.all().delete()
        except Exception:
            logger.exception("Cart clear failed for order %s", order.uuid)

    # ============================================================
    # EMAIL (CONFIRMATION ONLY)
    # ============================================================

    try:
        send_order_email(order)
    except Exception:
        logger.exception("EMAIL FAILED at verify for order %s", order.uuid)

    # ============================================================
    # SMS
    # ============================================================

    try:
        send_order_sms(order)
    except Exception:
        logger.exception("SMS hook failed for order %s", order.uuid)

    return JsonResponse({"ok": True})