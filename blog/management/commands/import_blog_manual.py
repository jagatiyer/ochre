from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from django.utils.text import slugify
from blog.models import BlogPost
from django.core.files.base import ContentFile
import requests
from urllib.parse import urlparse


class Command(BaseCommand):
    help = 'Idempotent manual import of a single blog post (Example 1)'

    def handle(self, *args, **options):
        # Authoritative Example 1 values
        title = "Craft Spirits vs. Commercial Liquor: What’s Really in Your Glass?"
        raw_date = "18 july 2025"
        hero_image_url = (
            "https://img1.wsimg.com/isteam/ip/4e3b58ef-b256-41c7-8a9d-effc89e31648/03afe35c-8f9d-4b8c-9686-5412fdbd86b3.png"
            "/:/cr=t:0%25,l:0%25,w:100%25,h:100%25/rs=w:1280"
        )
        content = (
            "In a world where choice defines lifestyle, the difference between craft spirits and commercial "
            "liquor is more than just branding—it’s a matter of quality and experience. As India’s drinking "
            "culture evolves, consumers are asking: What am I really drinking? At Ochre Spirits, the answer is "
            "clear—premium, locally crafted spirits that honour flavour, integrity, and innovation.\n\n"
            "The Commercial Liquor Landscape\n"
            "Commercial liquor dominates the global alcohol market with mass production, standardized "
            "recipes, and aggressive marketing. These brands prioritize volume over nuance, often relying on "
            "artificial flavoring, high sugar content, and industrial distillation methods. While consistent and "
            "widely available, commercial liquors lack the character and craftsmanship that modern consumers "
            "crave.\n\n"
            "In India, many commercial brands use neutral grain spirits diluted with synthetic additives to mimic "
            "flavor profiles. The result? A drink that’s palatable but uninspired. For health-conscious and "
            "flavor-driven drinkers, this model is increasingly outdated.\n\n"
            "The Craft Spirit Revolution\n"
            "Enter craft spirits—small-batch, artisanal alcohol made with care and creativity. At Ochre Spirits, "
            "every bottle tells a story. From premium rum India offerings like Nutty Berry Rum to artisanal "
            "vodka brands such as Peach & Cherry Vodka, Ochre’s lineup is crafted using locally sourced "
            "ingredients and innovative infusions.\n\n"
            "Unlike commercial liquor, Ochre’s spirits are distilled in limited quantities to preserve quality and "
            "flavor complexity. The use of indigenous botanicals like saffron, mango, and citron reflects India’s "
            "rich terroir and elevates the drinking experience.\n\n"
            "Flavor Integrity and Innovation\n"
            "Flavor integrity is where craft truly shines. Ochre’s spirits are designed to be sipped, savored, and "
            "celebrated. The Mango Citron Rum, for instance, balances tropical sweetness with citrus zest, while "
            "the Saffron Vodka offers a tart, refreshing profile without relying on syrups or sugar.\n\n"
            "This innovation extends to mixology. Bartenders across Bengaluru and Goa are turning to Ochre for "
            "cocktails that highlight natural ingredients and bold flavors. It’s not just alcohol—it’s an "
            "experience.\n\n"
            "The Verdict: Choose Craft, Choose Character\n"
            "In the battle of craft vs commercial alcohol, the winner is clear for those who value authenticity, "
            "sustainability, and flavor. Ochre Spirits isn’t just redefining what goes into your glass—it’s "
            "redefining what it means to drink well.\n\n"
            "Whether you’re a cocktail enthusiast, a mindful drinker, or someone exploring India’s evolving alcohol "
            "scene, Ochre offers a premium alternative that’s rooted in tradition and driven by innovation."
        )

        # Build slug
        slug = slugify(title)

        # Parse created date
        try:
            dt = datetime.strptime(raw_date, "%d %B %Y")
            created_at = timezone.make_aware(dt)
        except Exception:
            created_at = None

        def download_and_attach_image(post, url):
            if not url:
                return None
            try:
                resp = requests.get(url, timeout=20)
                resp.raise_for_status()
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Failed to download image: {e}"))
                return None

            # Derive filename
            path = urlparse(url).path
            _, ext = os.path.splitext(path)
            if not ext:
                ext = ".jpg"
            filename = f"{post.slug}{ext}"

            try:
                post.cover_image.save(filename, ContentFile(resp.content), save=True)
                return post.cover_image.name
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Failed to save cover_image: {e}"))
                return None

        # Idempotent upsert by slug: update if exists, otherwise create
        try:
            post = BlogPost.objects.get(slug=slug)
            post.title = title
            post.content = content
            # Do not overwrite created_at for existing records
            post.save()
            created = False
            self.stdout.write(self.style.SUCCESS(f"Updated BlogPost id={post.id} slug={post.slug}"))
        except BlogPost.DoesNotExist:
            if created_at:
                post = BlogPost(title=title, slug=slug, content=content, created_at=created_at)
            else:
                post = BlogPost(title=title, slug=slug, content=content)
            post.save()
            # ensure created_at preserved if provided
            if created_at:
                try:
                    post.created_at = created_at
                    post.save(update_fields=["created_at"])
                except Exception:
                    pass
            created = True
            self.stdout.write(self.style.SUCCESS(f"Created BlogPost id={post.id} slug={post.slug}"))

        # Download and attach hero image (if provided)
        if hero_image_url:
            cover_path = download_and_attach_image(post, hero_image_url)
            if cover_path:
                self.stdout.write(self.style.SUCCESS(f"Attached cover_image: {cover_path}"))
            else:
                self.stdout.write(self.style.WARNING("No cover_image attached"))

        # Final confirmation output
        self.stdout.write(
            self.style.NOTICE(
                f"FINAL: id={post.id} slug={post.slug} cover_image={getattr(post.cover_image, 'name', None)} created={created}"
            )
        )
