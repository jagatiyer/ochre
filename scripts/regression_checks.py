#!/usr/bin/env python3
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE','ochre.settings')

import django
django.setup()

from django.test import Client

c = Client()
paths = ['/', '/shop/', '/commercials/', '/accounts/login/']
out = {}
for p in paths:
    r = c.get(p)
    out[p] = {'status_code': r.status_code, 'content_snippet': r.content.decode()[:800]}

import json
print(json.dumps(out, indent=2))
