from django.core.management.base import BaseCommand
from django.utils import timezone
from blog.models import BlogPost
from datetime import timedelta

POSTS = [
    {
        "title": "The Art of Slow Distillation",
        "tag": "craft_process",
        "excerpt": "Why slow distillation brings unmatched purity and flavour.",
        "description": "A deep look into why slow, controlled distillation results in richer aromas and superior spirits.",
        "content": "Full long-form article here about craft distillation processes...",
    },
    {
        "title": "Innovation in Modern Craft Spirits",
        "tag": "innovation",
        "excerpt": "Where tradition meets cutting-edge science.",
        "description": "How modern tools and techniques are transforming India’s craft spirits movement.",
        "content": "Full article on innovation and technology...",
    },
    {
        "title": "The Story Behind Our Signature Botanical Blend",
        "tag": "product_story",
        "excerpt": "A flavour profile inspired by nature.",
        "description": "A narrative about how Ochre selects and perfects its botanical blends.",
        "content": "Full product story article...",
    },
    {
        "title": "3 Signature Cocktails You Can Make at Home",
        "tag": "recipes",
        "excerpt": "Simple, elegant, and delicious.",
        "description": "Easy, bartender-approved cocktails using craft spirits.",
        "content": "Full recipe list...",
    },
    {
        "title": "Our Commitment to Sustainability",
        "tag": "sustainability",
        "excerpt": "Crafting responsibly, for the future.",
        "description": "How Ochre reduces waste, sources local, and prioritises green processes.",
        "content": "Full sustainability article...",
    },
    {
        "title": "Ochre Wins Gold at International Spirits Awards 2025",
        "tag": "news",
        "excerpt": "A proud moment for India’s craft spirit movement.",
        "description": "Our latest recognition at a global platform.",
        "content": "Full news article...",
    },
]


class Command(BaseCommand):
    help = "Seeds initial blog posts"

    def handle(self, *args, **kwargs):
        base_time = timezone.now()

        for i, data in enumerate(POSTS):
            # Spread posts across past 6 days
            created_time = base_time - timedelta(days=5 - i)

            post, created = BlogPost.objects.get_or_create(
                title=data["title"],
                defaults={
                    "excerpt": data["excerpt"],
                    "description": data["description"],
                    "content": data["content"],
                    "tag": data["tag"],
                    "published": True,
                }
            )

            # If it already existed, update fields
            if not created:
                post.excerpt = data["excerpt"]
                post.description = data["description"]
                post.content = data["content"]
                post.tag = data["tag"]
                post.published = True
                post.save()

            # Manually set created_at after creation
            BlogPost.objects.filter(id=post.id).update(created_at=created_time)

            self.stdout.write(self.style.SUCCESS(f"Seeded: {post.title}"))

        self.stdout.write(self.style.SUCCESS("All blog posts seeded successfully!"))
