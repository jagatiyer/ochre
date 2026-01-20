import os,sys,json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','ochre.settings')
import django
django.setup()
from commercials.admin import CommercialVideoForm
from commercials.models import CommercialVideo
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.conf import settings
from shop.models import ShopItem

results = {}

# ADMIN: validate form logic
try:
    f1 = CommercialVideoForm(data={'title':'upl','description':'d'}, files={'video': SimpleUploadedFile('vid.mp4', b'0'*1024, content_type='video/mp4')})
    valid1 = f1.is_valid()
    f2 = CommercialVideoForm(data={'title':'url','embed_url':'https://example.com/video.mp4'})
    valid2 = f2.is_valid()
    f3 = CommercialVideoForm(data={'title':'html','embed_html':'<iframe src="https://player.example.com/embed/abc"></iframe>'})
    valid3 = f3.is_valid()
    f4 = CommercialVideoForm(data={'title':'bad','embed_url':'https://a','embed_html':'<iframe></iframe>'})
    valid4 = f4.is_valid()
    results['admin_validations'] = (valid1, valid2, valid3, not valid4)
    results['admin_errors'] = {
        'f1': getattr(f1, 'errors', None),
        'f2': getattr(f2, 'errors', None),
        'f3': getattr(f3, 'errors', None),
        'f4': getattr(f4, 'errors', None),
    }
except Exception as e:
    results['admin_error'] = str(e)

# ADMIN: create sample records (model save)
try:
    CommercialVideo.objects.all().delete()
    cv1 = CommercialVideo.objects.create(title='uploaded', description='u', video=None, embed_url='', embed_html='')
    cv2 = CommercialVideo.objects.create(title='embedurl', description='v', video=None, embed_url='https://example.com/video.mp4', embed_html='')
    cv3 = CommercialVideo.objects.create(title='embedhtml', description='w', video=None, embed_url='', embed_html='<iframe src="https://player.example.com/embed/abc"></iframe>')
    results['admin_created_count'] = CommercialVideo.objects.count()
except Exception as e:
    results['admin_create_error'] = str(e)

# FRONTEND checks
c = Client()
try:
    resp = c.get('/commercials/')
    results['commercials_status'] = resp.status_code
    body = resp.content.decode('utf-8')
    results['commercials_has_title'] = 'Commercials' in body
    results['commercials_has_grid'] = 'products-scroll' in body or 'collection-card' in body
    results['commercials_h1_count'] = body.count('<h1>')
except Exception as e:
    results['commercials_error'] = str(e)

try:
    resp2 = c.get('/')
    results['home_status'] = resp2.status_code
    b2 = resp2.content.decode('utf-8')
    results['home_has_story_content'] = 'story-content' in b2
except Exception as e:
    results['home_error'] = str(e)

# Footer checks
try:
    static_logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo_leaf.png')
    results['footer_logo_exists'] = os.path.exists(static_logo_path)
    results['footer_has_social'] = 'fa-instagram' in body or 'social-connect' in body or 'fa-instagram' in b2
except Exception as e:
    results['footer_error'] = str(e)

# Booking UX
try:
    # Create minimal category if needed
    cat = None
    from shop.models import ShopCategory
    if ShopCategory.objects.exists():
        cat = ShopCategory.objects.first()
    else:
        cat = ShopCategory.objects.create(name='AutoCat')
    # Free and paid experiences (use unique slugs)
    import uuid
    si_free = ShopItem.objects.create(title='Free Exp', slug=f'free-exp-{uuid.uuid4().hex[:8]}', category=cat, price=0, is_experience=True, published=True)
    si_paid = ShopItem.objects.create(title='Paid Exp', slug=f'paid-exp-{uuid.uuid4().hex[:8]}', category=cat, price=1000, is_experience=True, published=True)
    # POST booking start
    start_url = f'/payments/booking/start/{si_free.id}/'
    resp_free_post = c.post(start_url, data={'customer_name':'Test','customer_email':'t@example.com','customer_phone':'123','date':'2026-01-20','time_slot':'10:00','notes':''}, follow=True)
    results['free_booking_status'] = resp_free_post.status_code
    results['free_booking_final_path'] = resp_free_post.request.get('PATH_INFO')
    start_url_paid = f'/payments/booking/start/{si_paid.id}/'
    resp_paid_post = c.post(start_url_paid, data={'customer_name':'P','customer_email':'p@example.com','customer_phone':'123','date':'2026-01-21','time_slot':'11:00','notes':''}, follow=True)
    results['paid_booking_status'] = resp_paid_post.status_code
    results['paid_booking_final_path'] = resp_paid_post.request.get('PATH_INFO')
    # product detail
    pd = c.get(f'/shop/{si_paid.slug}/')
    results['book_now_text'] = 'BOOK NOW' in pd.content.decode('utf-8')
    results['back_link_top'] = 'top-back' in pd.content.decode('utf-8')
except Exception as e:
    results['booking_error'] = str(e)
    # attempt to continue


out_path = os.path.join(os.path.dirname(__file__), 'ui_checks_out.json')
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print('WROTE', out_path)
