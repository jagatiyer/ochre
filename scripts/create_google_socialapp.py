#!/usr/bin/env python3
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE','ochre.settings')
import django
django.setup()
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Load .env into os.environ if present (simple parser)
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                k, v = line.split('=', 1)
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k.strip(), v)
    except Exception:
        pass

# List existing
apps = SocialApp.objects.filter(provider='google')
print('EXISTING_COUNT_BEFORE=', apps.count())
for a in apps:
    print('BEFORE ID', a.id, 'name', a.name, 'client_id=', a.client_id, 'sites=', [s.id for s in a.sites.all()])

# Remove any existing google apps (safety per instruction)
SocialApp.objects.filter(provider='google').delete()
print('DELETED_EXISTING')

# Create exactly one using environment variables
site = Site.objects.get_current()
print('SITE', site.id, site.domain)
client_id = os.environ.get('GOOGLE_CLIENT_ID','')
secret = os.environ.get('GOOGLE_CLIENT_SECRET','')
if not client_id or not secret:
    print('ERROR: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET missing in environment')
    sys.exit(2)

app = SocialApp.objects.create(provider='google', name='Google', client_id=client_id, secret=secret)
app.sites.add(site)
app.save()
print('CREATED ID', app.id, 'client_id_present=', bool(app.client_id), 'secret_present=', bool(app.secret), 'sites=', [s.id for s in app.sites.all()])
print('EXISTING_COUNT_AFTER=', SocialApp.objects.filter(provider='google').count())
