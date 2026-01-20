from django.test import Client
import re
c = Client()
urls = ['/', '/story/', '/society/', '/commercials/']
for u in urls:
    r = c.get(u)
    print('URL', u, 'STATUS', r.status_code)
    s = r.content.decode('utf-8')
    if 'logo_leaf.png' in s:
        print('LOGO_IN_PAGE', u)
    else:
        print('LOGO_NOT_IN_PAGE', u)
    m = re.search(r'<nav[^>]*class=["\'].*?navbar.*?["\'][^>]*>(.*?)</nav>', s, re.S)
    if m:
        snippet = m.group(1).strip()[:400]
        print('NAV_SNIPPET_START')
        print(snippet)
        print('NAV_SNIPPET_END')
    else:
        print('NAV_MISSING')
