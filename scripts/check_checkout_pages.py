#!/usr/bin/env python3
import os,sys,re,json
sys.path.insert(0,os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE','ochre.settings')
import django
django.setup()
from django.test import Client

c = Client()
# Seed session cart
s = c.session
s['cart'] = [{'sku':'SKU1','name':'Test Item','price':12345,'qty':2},{'sku':'SKU2','name':'Widget','price':2500,'qty':1}]
s.save()

report = {'pages':{}}

# helper
def check_url(path):
    r = c.get(path)
    html = r.content.decode('utf-8')
    return r.status_code, html

# Checkout address
status, html = check_url('/payments/checkout/address/')
report['pages']['checkout_address'] = {
    'status': status,
    'has_checkout_container': 'checkout-container' in html,
    'has_checkout_form_left': 'checkout-form-left' in html,
    'has_order_summary': 'checkout-order-summary' in html,
    'has_contact_form': 'contact-form' in html,
    'has_form_row': 'form-row' in html,
    'has_cn_shop_button': bool(re.search(r'class="[^\"]*cn[^\"]*shop', html)),
    'has_summary_li_data': 'data-price' in html and 'data-qty' in html,
    'has_summary_total_el': 'id="summary-total"' in html,
}

# Cart
status2, html2 = check_url('/payments/cart/')
report['pages']['cart'] = {'status': status2, 'has_checkout_link': 'checkout/address' in html2}

# Checkout review
status3, html3 = check_url('/payments/checkout/review/')
m = re.search(r'Total:\s*₹([0-9,.]+)', html3)
report['pages']['checkout_review'] = {'status': status3, 'server_total': m.group(1) if m else None}

# CSS checks
css_path = os.path.join(os.getcwd(),'static','style.css')
css_text = ''
try:
    with open(css_path,'r') as f:
        css_text = f.read()
except Exception as e:
    css_text = ''
report['css'] = {'contains_scope': '.checkout-address-page' in css_text, 'contains_media': '@media (max-width: 900px)' in css_text}

# expected total
expected_paise = sum(item['price']*item['qty'] for item in s['cart'])
report['expected_total_rupees'] = f"{expected_paise/100:.2f}"

# determine pass/fail
report['results'] = {}
report['results']['checkout_address_layout'] = (report['pages']['checkout_address']['status']==200 and report['pages']['checkout_address']['has_checkout_container'] and report['pages']['checkout_address']['has_order_summary'])
report['results']['mobile_css_present'] = report['css']['contains_media']
report['results']['typography_grouping'] = (report['pages']['checkout_address']['has_contact_form'] and report['pages']['checkout_address']['has_form_row'])
report['results']['cta_button'] = report['pages']['checkout_address']['has_cn_shop_button']
report['results']['client_side_summary_data'] = (report['pages']['checkout_address']['has_summary_li_data'] and report['pages']['checkout_address']['has_summary_total_el'] and report['css']['contains_scope'])
report['results']['cart_page'] = (report['pages']['cart']['status']==200 and report['pages']['cart']['has_checkout_link'])
report['results']['checkout_review'] = (report['pages']['checkout_review']['status']==200 and report['pages']['checkout_review']['server_total'] is not None)
report['results']['checkout_review_total_match'] = (report['pages']['checkout_review']['server_total'] is not None and report['pages']['checkout_review']['server_total'].replace(',','')==report['expected_total_rupees'])

print(json.dumps(report, indent=2))
