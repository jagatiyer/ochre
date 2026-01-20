#!/usr/bin/env python3
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ochre.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth.models import AnonymousUser
from shop.models import ShopCategory, ShopItem, ExperienceBooking
from payments.models import Payment
from payments.views import booking_details, create_order, verify_payment
from django.conf import settings

rf = RequestFactory()

# helper to attach session & messages
def prepare_request(req, session_source=None):
    SessionMiddleware(lambda r: None).process_request(req)
    if session_source is not None:
        # copy session data
        req.session.update(session_source)
    req.session.save()
    try:
        MessageMiddleware(lambda r: None).process_request(req)
    except Exception:
        pass
    return req


def main():
    out = {
        'migrations_applied': True,
        'free_booking': {},
        'paid_booking': {},
        'razorpay_keys_provided': bool(settings.RAZORPAY_TEST_KEYS_PROVIDED),
        'errors': []
    }
    try:
        cat, _ = ShopCategory.objects.get_or_create(name='TestCat', slug='testcat')
        free, _ = ShopItem.objects.get_or_create(title='Free Exp', slug='free-exp', category=cat, defaults={'price':0, 'is_experience':True})
        paid, _ = ShopItem.objects.get_or_create(title='Paid Exp', slug='paid-exp', category=cat, defaults={'price':1000.00, 'is_experience':True})

        # Free booking
        data = {'experience_id': str(free.id), 'date':'2026-02-01', 'time_slot':'10:00', 'customer_name':'Alice','customer_email':'alice@example.com','customer_phone':'999','notes':''}
        req = rf.post('/payments/booking/details/', data)
        req.user = AnonymousUser()
        prepare_request(req)
        resp = booking_details(req)
        out['free_booking']['response_type'] = type(resp).__name__
        fb = ExperienceBooking.objects.filter(customer_email='alice@example.com').order_by('-created_at').first()
        out['free_booking']['exists'] = bool(fb)
        out['free_booking']['id'] = getattr(fb, 'id', None)
        out['free_booking']['status'] = getattr(fb, 'status', None)

        # Paid booking
        data2 = {'experience_id': str(paid.id), 'date':'2026-02-02','time_slot':'11:00','customer_name':'Bob','customer_email':'bob@example.com','customer_phone':'888','notes':''}
        req2 = rf.post('/payments/booking/details/', data2)
        req2.user = AnonymousUser()
        prepare_request(req2)
        resp2 = booking_details(req2)
        out['paid_booking']['response_type'] = type(resp2).__name__
        bid = req2.session.get('booking_id')
        amount = req2.session.get('booking_amount')
        out['paid_booking']['session_booking_id'] = bid
        out['paid_booking']['session_booking_amount'] = amount
        if bid:
            b = ExperienceBooking.objects.get(id=bid)
            out['paid_booking']['created'] = True
            out['paid_booking']['id'] = b.id
            out['paid_booking']['payment_required'] = b.payment_required
            out['paid_booking']['payment_ref_before'] = b.payment_ref
        else:
            out['paid_booking']['created'] = False

        # Create order
        req3 = rf.post('/payments/create_order/')
        req3.user = AnonymousUser()
        prepare_request(req3, session_source=req2.session)
        resp3 = create_order(req3)
        out['create_order'] = {'status_code': getattr(resp3, 'status_code', None)}
        try:
            order_json = json.loads(resp3.content.decode())
            order_id = order_json.get('order_id')
            out['create_order']['order_id'] = order_id
            p = Payment.objects.filter(order_id=order_id).first()
            out['create_order']['payment_created'] = bool(p)
            out['create_order']['payment_status'] = getattr(p, 'status', None) if p else None
            b_link = ExperienceBooking.objects.filter(payment_ref=order_id).first()
            out['create_order']['booking_linked'] = bool(b_link)
            out['create_order']['booking_linked_id'] = getattr(b_link, 'id', None)
            out['create_order']['booking_linked_status'] = getattr(b_link, 'status', None) if b_link else None
        except Exception as e:
            out['create_order']['error'] = str(e)

        # Verify payment
        if out['create_order'].get('order_id'):
            req4 = rf.post('/payments/verify_payment/', {'razorpay_order_id': out['create_order']['order_id'], 'razorpay_payment_id':'pay_123', 'razorpay_signature':'sig'})
            req4.user = AnonymousUser()
            prepare_request(req4)
            resp4 = verify_payment(req4)
            out['verify_payment'] = {'status_code': getattr(resp4, 'status_code', None), 'content': getattr(resp4, 'content', b'').decode()}
            if 'order_id' in out['create_order']:
                p = Payment.objects.filter(order_id=out['create_order']['order_id']).first()
                if p:
                    p.refresh_from_db()
                    out['verify_payment']['payment_status'] = p.status
                    out['verify_payment']['payment_id'] = p.payment_id
                b_after = ExperienceBooking.objects.filter(payment_ref=out['create_order']['order_id']).first()
                out['verify_payment']['booking_status'] = getattr(b_after, 'status', None) if b_after else None

    except Exception as exc:
        out['errors'].append(str(exc))

    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
