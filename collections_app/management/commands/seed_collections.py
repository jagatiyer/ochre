# collections_app/management/commands/seed_collections.py

from django.core.management.base import BaseCommand
from collections_app.models import CollectionItem
from django.utils.text import slugify

class Command(BaseCommand):
    help = "Seed initial Ochre Collection Items"

    def handle(self, *args, **kwargs):
        items = [
            {
                "title": "Saffron Infused Gin",
                "excerpt": "Our signature expression—floral, exotic, and unmistakably Ochre.",
                "description": "Crafted using premium juniper, fresh citrus, and handpicked Kashmiri saffron. A silky, aromatic gin celebrating Indian botanicals.",
                "category": "gin",
            },
            {
                "title": "Himalayan Juniper Gin",
                "excerpt": "A crisp, mountain-inspired gin with bright herbal freshness.",
                "description": "Made with wild Himalayan juniper berries, coriander, and fresh lemon zest. Perfect for refreshing highballs and gin tonics.",
                "category": "gin",
            },
            {
                "title": "Cold-Distilled Citrus Vodka",
                "excerpt": "Vibrant, clean, and bursting with natural citrus oils.",
                "description": "Distilled slowly at low temperatures to preserve delicate citrus aromatics. Light, smooth, and exceptionally mixable.",
                "category": "vodka",
            },
            {
                "title": "Smoked Oak Vodka",
                "excerpt": "A bold, barrel-touched vodka with warm spice and caramel notes.",
                "description": "Oak-rested and gently smoked, this vodka was created for complex cocktails and sipping over ice.",
                "category": "vodka",
            },
            {
                "title": "Limited Edition Saffron Reserve",
                "excerpt": "A rare, collectible gin aged with saffron threads and toasted spices.",
                "description": "Rich, golden, and aromatic. Only 500 bottles produced yearly. A celebration of India’s most precious spice.",
                "category": "limited_edition",
            },
            {
                "title": "Master Distiller’s Special Release",
                "excerpt": "A seasonal expression highlighting innovative distillation techniques.",
                "description": "Crafted with experimental botanicals, unique cask finishes, and boundary-pushing flavour design.",
                "category": "special_release",
            },
        ]

        for item in items:
            obj, created = CollectionItem.objects.get_or_create(
                title=item["title"],
                defaults={
                    "slug": slugify(item["title"]),
                    "excerpt": item["excerpt"],
                    "description": item["description"],
                    "category": item["category"],
                    "published": True,
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {obj.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Already exists: {obj.title}"))

        self.stdout.write(self.style.SUCCESS("\nAll collection items seeded successfully!"))
