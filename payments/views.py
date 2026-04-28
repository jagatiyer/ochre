from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
import razorpay
import logging

from shop.models import Order
from shop.utils.invoice import generate_invoice

logger = logging.getLogger(__name__)


def send_order_email(order):
    print("REACHED EMAIL BLOCK")
    if not order.user or not order.user.email: # Check for user and email
        print("NO EMAIL FOUND") # Log if no email is found
        return # Exit early if no recipient email

    print("USER EMAIL:", order.user.email) # Log the recipient email
    
    subject = f"Ochre Order Confirmation - {order.uuid}"

    # Use a static message as per instructions
    message = "Your order has been successfully placed."

    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER # Sender email
    recipient = [order.user.email] # Recipient is strictly the user's email

    email = EmailMessage(subject, message, from_email, recipient)

    # Attach invoice if it exists
    if order.invoice_file and hasattr(order.invoice_file, "path"):
        try:
            email.attach_file(order.invoice_file.path)
            print("ATTACHMENT OK")
        except Exception as e:
            print("ATTACHMENT ERROR:", str(e))

    try:
        email.send(fail_silently=False)
        print("SMTP SEND OK")
    except Exception as e:
        print("EMAIL ERROR:", str(e)) # Log here to avoid duplication in verify()
        raise e

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
    print("===== VERIFY HIT =====")
    print(request.POST)

    payment_id = request.POST.get("razorpay_payment_id")
    rp_order_id = request.POST.get("razorpay_order_id")
    signature = request.POST.get("razorpay_signature")
    order_internal_id = request.POST.get("order_internal_id")

    if not (payment_id and rp_order_id and signature and order_internal_id):
        return HttpResponseBadRequest("Missing required fields")

    order = get_object_or_404(Order, uuid=order_internal_id)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # ensure the posted razorpay_order_id matches the one created for this Order
    if order.razorpay_order_id and rp_order_id != order.razorpay_order_id:
        order.status = Order.STATUS_FAILED
        order.save()
        logger.warning("Posted razorpay_order_id does not match order record: %s != %s", rp_order_id, order.razorpay_order_id)
        return JsonResponse({"ok": False, "error": "order_id_mismatch"}, status=400)

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': rp_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
        print("SIGNATURE VERIFIED")
    except Exception as e:
        # signature verification failed
        order.status = Order.STATUS_FAILED
        order.save()
        print("SIGNATURE FAILED:", str(e))
        return JsonResponse({"ok": False, "error": "signature_verification_failed"}, status=400)

    # success
    order.razorpay_payment_id = payment_id
    order.razorpay_signature = signature
    order.payment_ref = payment_id
    order.status = Order.STATUS_PAID
    order.save()

    try:
        generate_invoice(order)
        print("INVOICE OK")
    except Exception as e:
        print("INVOICE ERROR:", str(e))

    # Clear cart safely
    if order.user and hasattr(order.user, "cart"):
        try:
            order.user.cart.items.all().delete()
        except Exception:
            logger.exception("Cart clear failed")

    # Send email
    try:
        send_order_email(order)
    except Exception as e:
        print("EMAIL ERROR:", str(e))
    else: # Only print "EMAIL OK" if no exception was raised by send_order_email
        print("EMAIL OK")

    # SMS (leave as-is)
    try:
        send_order_sms(order)
    except Exception:
        logger.exception("send_order_sms hook failed")

    return JsonResponse({"ok": True})
