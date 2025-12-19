import logging
import os
from urllib.parse import urljoin, urlparse

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

import requests
from bs4 import BeautifulSoup

from blog.models import BlogPost

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import blog posts from https://ochrespirits.com/media-%26-blogs (supports --dry-run)'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Do not save anything — just report')
        parser.add_argument('--source', type=str, default='https://ochrespirits.com/media-%26-blogs', help='Source URL')
        parser.add_argument('--single-url', type=str, help='Run import for a single post URL (use with --dry-run for safe testing)')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        source = options['source']

        self.stdout.write(self.style.NOTICE('Starting import (dry-run=%s) from %s' % (dry_run, source)))

        session = requests.Session()

        to_process = []
        visited_page_urls = set()
        page_url = source

        single_url = options.get('single_url')
        if single_url:
            to_process = [single_url]
            page_url = None

        # Follow 'load more' / pagination if present. This is best-effort: we look for
        # rel="next" links and for buttons/links with data-url or href that looks like pagination.
        while page_url and page_url not in visited_page_urls:
            visited_page_urls.add(page_url)
            self.stdout.write('Fetching: %s' % page_url)
            try:
                r = session.get(page_url, timeout=20)
                r.raise_for_status()
            except Exception as exc:
                self.stderr.write('Failed to fetch %s: %s' % (page_url, exc))
                break

            soup = BeautifulSoup(r.text, 'html.parser')

            # Find article links — heuristic: anchors inside list/grid with class contains 'post' or 'article'
            anchors = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                # ignore nav, anchor-only hrefs
                if href.startswith('#'):
                    continue
                text = (a.get_text() or '').strip()
                # Heuristic: link that contains child with class 'card' or 'article' or article title heading
                parent = a.parent
                parent_classes = ' '.join(parent.get('class') or []) if parent else ''
                if ('post' in parent_classes or 'article' in parent_classes or 'card' in parent_classes) or ('blog' in href) or (len(text) > 10 and '/' in href):
                    anchors.append(urljoin(page_url, href))

            # Deduplicate and add
            for link in anchors:
                if link not in to_process:
                    to_process.append(link)

            # Attempt to find a 'load more' or rel=next
            next_url = None
            rel_next = soup.find('link', rel='next')
            if rel_next and rel_next.get('href'):
                next_url = urljoin(page_url, rel_next['href'])
            else:
                # look for button/link with class load-more or show-more
                btn = soup.find(lambda t: t.name in ('a', 'button') and t.get('class') and any('load' in c or 'more' in c or 'show' in c for c in t.get('class')))
                if btn and btn.get('data-url'):
                    next_url = urljoin(page_url, btn['data-url'])
                elif btn and btn.get('href'):
                    next_url = urljoin(page_url, btn['href'])

            if next_url and next_url not in visited_page_urls:
                page_url = next_url
            else:
                # try to find numeric pagination links
                pager = soup.find('a', href=True, text=lambda t: t and t.strip().isdigit())
                if pager:
                    next_url = urljoin(page_url, pager['href'])
                    if next_url not in visited_page_urls:
                        page_url = next_url
                        continue
                break

        # Now process candidate post URLs. Filter unique slugs
        imported = 0
        skipped = 0
        failed = 0
        processed_slugs = set()

        for url in to_process:
            try:
                r = session.get(url, timeout=20)
                r.raise_for_status()
            except Exception as exc:
                self.stderr.write('Failed to fetch post %s: %s' % (url, exc))
                failed += 1
                continue

            soup = BeautifulSoup(r.text, 'html.parser')

            # Heuristics to find title, date, excerpt, content
            title_tag = soup.find(['h1', 'h2'])
            title = title_tag.get_text().strip() if title_tag else None
            if not title:
                self.stderr.write('Skipping %s — no title found' % url)
                failed += 1
                continue

            # slug from URL last path segment
            path = urlparse(url).path
            raw_slug = os.path.basename(path.rstrip('/'))
            # Ensure we create a safe slug (only allowed chars) — slugify both raw slug and fallback to title
            slug = slugify(raw_slug) if raw_slug else slugify(title)
            if slug in processed_slugs:
                continue

            # idempotent check
            if BlogPost.objects.filter(slug=slug).exists():
                self.stdout.write('Skipping existing: %s (%s)' % (title, slug))
                skipped += 1
                processed_slugs.add(slug)
                continue

            # date — try meta property
            created_at = None
            date_meta = soup.find('meta', {'property': 'article:published_time'}) or soup.find('time')
            if date_meta:
                created_at = date_meta.get('content') or date_meta.get_text()

            # excerpt — first paragraph under article or meta description
            excerpt = None
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                excerpt = meta_desc['content']
            else:
                p = soup.find('p')
                excerpt = p.get_text().strip() if p else ''

            # content — locate the article container precisely using site-specific selectors
            content_container = None
            selectors = ['article', '.blog-post-content', '.blog-content', '.entry-content', '.post-content', '.article-content', '.post', '.content']
            for sel in selectors:
                if sel.startswith('.'):
                    found = soup.select_one(sel)
                else:
                    found = soup.find(sel)
                if found and len(found.get_text(strip=True)) > 50:
                    content_container = found
                    break

            # Fallback: try to find the largest <div> or <article> by text length
            if not content_container:
                candidates = soup.find_all(['article', 'div'], limit=10)
                best = None
                best_len = 0
                for c in candidates:
                    l = len(c.get_text(strip=True))
                    if l > best_len:
                        best_len = l
                        best = c
                if best_len > 50:
                    content_container = best

            if content_container:
                # sanitize content: remove scripts, iframes, styles, noscript and unwanted wrappers
                for bad in content_container.select('script, iframe, style, noscript'):
                    bad.decompose()

                # remove header/footer/nav inside container
                for tag in content_container.select('header, nav, footer'):
                    tag.decompose()

                # remove elements likely to be cookie banners / external widgets
                for sel in ['.cookie', '.cookie-banner', '.consent', '.gdpr', '.site-footer', '.powered-by', '.wix', '.godaddy', '.cookie-consent', '.cookie-notice']:
                    for el in content_container.select(sel):
                        el.decompose()

                # sanitize images: remove width/height attributes and inline width/height styles
                for img in content_container.select('img'):
                    if img.has_attr('width'):
                        del img['width']
                    if img.has_attr('height'):
                        del img['height']
                    if img.has_attr('style'):
                        # remove width/height from style
                        styles = [s.strip() for s in img['style'].split(';') if s.strip()]
                        styles = [s for s in styles if not s.split(':',1)[0].strip() in ('width','height')]
                        if styles:
                            img['style'] = ';'.join(styles)
                        else:
                            del img['style']

                content_html = str(content_container)
            else:
                content_html = ''

            # Find primary image: look for og:image or first img in content
            cover_image_url = None
            og_image = soup.find('meta', {'property': 'og:image'})
            if og_image and og_image.get('content'):
                cover_image_url = urljoin(url, og_image['content'])
            else:
                img = content_container.find('img') if content_container else None
                if img and img.get('src'):
                    cover_image_url = urljoin(url, img['src'])

            # Dry-run: only log and show extracted HTML for single-url
            self.stdout.write('Found post: %s (%s)' % (title, slug))

            if dry_run:
                self.stdout.write('DRY RUN — would import: %s (slug=%s) cover_image=%s' % (title, slug, cover_image_url))
                # If single-url, output the extracted (sanitized) HTML for inspection
                if single_url:
                    self.stdout.write('--- EXTRACTED SANITIZED HTML START ---')
                    self.stdout.write(content_html or '[EMPTY]')
                    self.stdout.write('--- EXTRACTED SANITIZED HTML END ---')
                processed_slugs.add(slug)
                continue

            # Create BlogPost instance
            try:
                post = BlogPost(title=title, slug=slug, excerpt=excerpt or '', content=content_html, published=True)

                # parse created_at into datetime if possible
                if created_at:
                    try:
                        from dateutil import parser as dateparser
                        post.created_at = dateparser.parse(created_at)
                    except Exception:
                        # leave as default
                        pass

                # Save without image first to get file storage
                post.save()

                # handle cover image
                if cover_image_url:
                    try:
                        img_resp = session.get(cover_image_url, timeout=20)
                        img_resp.raise_for_status()
                        img_name = os.path.basename(urlparse(cover_image_url).path) or '%s.jpg' % slug
                        media_path = os.path.join('blog_imports', slug, img_name)
                        post.cover_image.save(media_path, ContentFile(img_resp.content), save=True)
                    except Exception as iexc:
                        self.stderr.write('Failed to download cover image %s: %s' % (cover_image_url, iexc))

                # TODO: replace image URLs inside content to point to local media if required — left as future step

                imported += 1
                processed_slugs.add(slug)
                self.stdout.write(self.style.SUCCESS('Imported: %s' % title))
            except Exception as exc:
                self.stderr.write('Failed to import %s: %s' % (title, exc))
                failed += 1

        self.stdout.write(self.style.SUCCESS('Import complete — imported=%d skipped=%d failed=%d' % (imported, skipped, failed)))
