import os
import json
import hmac
import hashlib
import random
from django.test import Client

c = Client()
print('Calling create-order...')
r = c.get('/payments/create-order/')
print('create-order status:', r.status_code)
print('create-order body:', r.content.decode('utf-8'))
try:
    data = json.loads(r.content.decode('utf-8'))
    order_id = data.get('order_id') or data.get('order', {}).get('id')
except Exception as e:
    print('Failed parsing create-order JSON:', e)
    order_id = None

from payments.models import Payment

if order_id:
    try:
        p = Payment.objects.get(order_id=order_id)
        print('DB before verify:', p.order_id, p.status)
    except Payment.DoesNotExist:
        print('Payment row not found for', order_id)

    # simulate razorpay payment id
    payment_id = f'pay_test_{random.randint(100000,999999)}'
    secret = os.environ.get('RAZORPAY_KEY_SECRET')
    if not secret:
        print('RAZORPAY_KEY_SECRET not in env')
    else:
        msg = f"{order_id}|{payment_id}".encode()
        signature = hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()
        print('Simulated payment_id:', payment_id)
        print('Calculated signature:', signature)

        # POST to verify
        resp = c.post('/payments/verify/', {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })
        print('verify status:', resp.status_code)
        print('verify body:', resp.content.decode('utf-8'))

        # check DB
        try:
            p = Payment.objects.get(order_id=order_id)
            print('DB after verify:', p.order_id, p.status, p.payment_id, p.signature)
        except Exception as e:
            print('DB lookup after verify failed:', e)
else:
    print('No order_id returned; abort')
