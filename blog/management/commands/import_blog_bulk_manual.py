from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from django.utils.text import slugify
from blog.models import BlogPost
from django.core.files.base import ContentFile
import requests
import os
from urllib.parse import urlparse
import re
import html


class Command(BaseCommand):
    help = 'Idempotent bulk manual import of authoritative blog posts (no scraping)'

    def handle(self, *args, **options):
        posts = [
            {
                "title": "Craft Spirits vs. Commercial Liquor: What’s Really in Your Glass?",
                "date": "18 July 2025",
                "hero_image_url": "https://img1.wsimg.com/isteam/ip/4e3b58ef-b256-41c7-8a9d-effc89e31648/03afe35c-8f9d-4b8c-9686-5412fdbd86b3.png",
                "content": (
                    "In a world where choice defines lifestyle, the difference between craft spirits and commercial liquor is more than just branding—it’s a matter of quality and experience. As India’s drinking culture evolves, consumers are asking: What am I really drinking? At Ochre Spirits, the answer is clear—premium, locally crafted spirits that honour flavour, integrity, and innovation.\n\n"
                    "The Commercial Liquor Landscape\n"
                    "Commercial liquor dominates the global alcohol market with mass production, standardized recipes, and aggressive marketing. These brands prioritize volume over nuance, often relying on artificial flavoring, high sugar content, and industrial distillation methods. While consistent and widely available, commercial liquors lack the character and craftsmanship that modern consumers crave.\n\n"
                    "In India, many commercial brands use neutral grain spirits diluted with synthetic additives to mimic flavor profiles. The result? A drink that’s palatable but uninspired. For health-conscious and flavor-driven drinkers, this model is increasingly outdated.\n\n"
                    "The Craft Spirit Revolution\n"
                    "Enter craft spirits—small-batch, artisanal alcohol made with care and creativity. At Ochre Spirits, every bottle tells a story. From premium rum India offerings like Nutty Berry Rum to artisanal vodka brands such as Peach & Cherry Vodka, Ochre’s lineup is crafted using locally sourced ingredients and innovative infusions.\n\n"
                    "Unlike commercial liquor, Ochre’s spirits are distilled in limited quantities to preserve quality and flavor complexity. The use of indigenous botanicals like saffron, mango, and citron reflects India’s rich terroir and elevates the drinking experience.\n\n"
                    "Flavor Integrity and Innovation\n"
                    "Flavor integrity is where craft truly shines. Ochre’s spirits are designed to be sipped, savored, and celebrated. The Mango Citron Rum, for instance, balances tropical sweetness with citrus zest, while the Saffron Vodka offers a tart, refreshing profile without relying on syrups or sugar.\n\n"
                    "This innovation extends to mixology. Bartenders across Bengaluru and Goa are turning to Ochre for cocktails that highlight natural ingredients and bold flavors. It’s not just alcohol—it’s an experience.\n\n"
                    "The Verdict: Choose Craft, Choose Character\n"
                    "In the battle of craft vs commercial alcohol, the winner is clear for those who value authenticity, sustainability, and flavor. Ochre Spirits isn’t just redefining what goes into your glass—it’s redefining what it means to drink well.\n\n"
                    "Whether you’re a cocktail enthusiast, a mindful drinker, or someone exploring India’s evolving alcohol scene, Ochre offers a premium alternative that’s rooted in tradition and driven by innovation."
                ),
            },
            {
                "title": "Why Craft Spirits Are Redefining India’s Drinking Culture",
                "date": "11 July 2025",
                "hero_image_url": "https://img1.wsimg.com/isteam/ip/4e3b58ef-b256-41c7-8a9d-effc89e31648/1fa6a6c2-58bd-4893-a9db-083aa73fd503.png",
                "content": (
                    "India’s alcohol industry is experiencing a seismic shift. Once dominated by mass-produced liquors and legacy brands, the market is now embracing a new wave of craft spirits—premium, small-batch alcohol that prioritizes flavor, sustainability, and storytelling. At the heart of this movement is Ochre Spirits.\n\n"
                    "The Rise of Conscious Consumption\n"
                    "Millennials and Gen Z are driving this transformation. According to a 2024 report by IWSR Drinks Market Analysis, younger consumers in India are increasingly choosing premium Indian alcohol brands that align with their values. They’re looking for authenticity, transparency, and innovation. Craft spirits like Ochre’s Saffron Vodka and Mango Citron Rum deliver on all fronts—offering bold flavors made from locally sourced ingredients and produced with eco-conscious methods.\n\n"
                    "This isn’t just about taste—it’s about identity. Consumers want to know where their drink comes from, how it’s made, and what it stands for. Ochre’s commitment to sustainable alcohol production and mindful drinking resonates deeply with this audience.\n\n"
                    "Flavor Meets Innovation\n"
                    "Unlike traditional liquors that rely on artificial additives and high sugar content, Indian craft spirits are embracing natural infusions and artisanal techniques. Ochre’s spirits are crafted in small batches, allowing for greater control over quality and flavor. Their Mango Citron Rum, for example, blends tropical fruit notes with a citrus twist, creating a profile that’s both familiar and refreshingly modern.\n\n"
                    "This kind of flavor innovation is what sets craft spirits apart. It’s not just about drinking—it’s about experiencing. And as cocktail culture in India continues to grow, bartenders and mixologists are turning to brands like Ochre for ingredients that elevate their creations.\n\n"
                    "A Cultural Shift in Every Sip\n"
                    "The rise of craft spirits in India isn’t a passing trend—it’s a cultural shift. It reflects a broader movement toward conscious living, where every choice—from food to fashion to alcohol—is made with intention. Ochre Spirits embodies this ethos, offering products that are not only delicious but also meaningful.\n\n"
                    "As India’s drinking culture evolves, brands like Ochre are setting the tone for what comes next: authenticity over excess, quality over quantity, and connection over consumption."
                ),
            },
        ]

        def download_and_attach_image(post, url):
            if not url:
                return None
            try:
                resp = requests.get(url, timeout=20)
                resp.raise_for_status()
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Failed to download image: {e}"))
                return None

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

        for item in posts:
            title = item["title"]
            raw_date = item["date"]
            hero_image_url = item.get("hero_image_url")
            content = item.get("content", "")

            # Convert plain-text content into structured HTML per rules:
            # - Split on double newlines into blocks
            # - If a block ends WITHOUT terminal punctuation and is followed by other blocks,
            #   treat it as a heading (<h2>)
            # - Otherwise wrap block in <p>
            # - Preserve ordering and escape content
            def convert_plaintext_to_html(text):
                if not text:
                    return ""
                # If content already contains HTML tags, leave as-is
                if any(tag in text for tag in ("<p", "<h", "<div", "<br", "</")):
                    return text

                blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
                out_blocks = []

                for idx, b in enumerate(blocks):
                    # Determine if block ends with terminal punctuation
                    last_char = b.strip()[-1] if b.strip() else ""
                    ends_with_punct = last_char in ".!?;:"

                    # If this block ends without punctuation and is followed by at least one block,
                    # treat as a heading
                    is_heading = (not ends_with_punct) and (idx < len(blocks) - 1)

                    escaped = html.escape(b)
                    if is_heading:
                        out_blocks.append(f"<h2>{escaped}</h2>")
                    else:
                        out_blocks.append(f"<p>{escaped}</p>")

                return "\n".join(out_blocks)

            content = convert_plaintext_to_html(content)

            slug = slugify(title)

            # parse date for creation only
            try:
                dt = datetime.strptime(raw_date, "%d %B %Y")
                created_at = timezone.make_aware(dt)
            except Exception:
                created_at = None

            try:
                post = BlogPost.objects.get(slug=slug)
                post.title = title
                post.content = content
                post.save(update_fields=["title", "content", "updated_at"]) if hasattr(post, "updated_at") else post.save()
                created = False
                self.stdout.write(self.style.SUCCESS(f"Updated BlogPost id={post.id} slug={post.slug}"))
            except BlogPost.DoesNotExist:
                if created_at:
                    post = BlogPost(title=title, slug=slug, content=content, created_at=created_at)
                else:
                    post = BlogPost(title=title, slug=slug, content=content)
                post.save()
                created = True
                self.stdout.write(self.style.SUCCESS(f"Created BlogPost id={post.id} slug={post.slug}"))

            # attach hero image regardless (download + save)
            if hero_image_url:
                cover_path = download_and_attach_image(post, hero_image_url)
                if cover_path:
                    self.stdout.write(self.style.SUCCESS(f"Attached cover_image: {cover_path}"))
                else:
                    self.stdout.write(self.style.WARNING("No cover_image attached"))

            # Final per-item confirmation
            self.stdout.write(self.style.NOTICE(f"FINAL: id={post.id} slug={post.slug} cover_image={getattr(post.cover_image, 'name', None)} created={created}"))
