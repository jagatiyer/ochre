from django.test import Client
import json, traceback

c = Client()
try:
    resp = c.get('/payments/create-order/')
    print('STATUS', resp.status_code)
    body = resp.content.decode('utf-8')
    print('BODY', body)
    try:
        data = json.loads(body)
        print('PARSED_KEYS', list(data.keys()) if isinstance(data, dict) else type(data))
        order_id = None
        if isinstance(data, dict):
            if 'order' in data and isinstance(data['order'], dict) and 'id' in data['order']:
                order_id = data['order']['id']
            elif 'order_id' in data:
                order_id = data['order_id']
            elif 'id' in data:
                order_id = data['id']
            if 'key' in data:
                print('KEY_PRESENT')
    except Exception:
        print('JSON_PARSE_FAILED')
        traceback.print_exc()
    if 'order_id' in locals() and order_id:
        try:
            from payments.models import Payment
            p = Payment.objects.get(order_id=order_id)
            print('DB', p.order_id, p.status, p.amount, p.currency, p.payment_id, p.signature)
        except Exception as e:
            print('DB_LOOKUP_ERROR', e)
except Exception:
    traceback.print_exc()
