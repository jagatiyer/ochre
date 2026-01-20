#!/usr/bin/env python3
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','ochre.settings')
import django
django.setup()
from allauth.socialaccount.models import SocialApp

apps = SocialApp.objects.all()
print('TOTAL_SOCIALAPPS=', apps.count())
for a in apps:
    print('ID', a.id, 'provider', a.provider, 'name', repr(a.name), 'client_id', repr(a.client_id))
    print('  sites:', [s.id for s in a.sites.all()])
