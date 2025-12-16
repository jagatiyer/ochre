from django.core.management.base import BaseCommand
from django.utils.text import slugify
from shop.models import ShopCategory, ShopItem


class Command(BaseCommand):
    help = "Seed shop categories, products and experiences"

    def handle(self, *args, **options):
        categories = [
            "T-SHIRTS",
            "COFFEE-MUGS",
            "GLASSWARE",
            "BARTENDING-KIT",
            "HIP-FLASK",
            "COCKTAIL-MIX-PACKETS",
            "MIXERS-PARTY-BOXES",
            "EXPERIENCES",
        ]

        # --------------------
        # Categories (slug-safe)
        # --------------------
        category_map = {}

        for name in categories:
            slug = slugify(name)

            cat, created = ShopCategory.objects.get_or_create(
                slug=slug,
                defaults={"name": name},
            )

            category_map[name] = cat

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {name}"))
            else:
                self.stdout.write(f"Category already exists: {name}")

        self.stdout.write(self.style.SUCCESS("Categories ready."))

        # --------------------
        # Products (non-experience)
        # --------------------
        samples = [
            {
                "title": "Ochre Signature T-Shirt (Pack of 3)",
                "category_name": "T-SHIRTS",
                "description": "Premium cotton pack — three colours included.",
                "price": "1999.00",
                "is_experience": False,
            },
            {
                "title": "Ochre Glassware Gift Set",
                "category_name": "GLASSWARE",
                "description": "Two crystal tumblers and tasting guide.",
                "price": "3499.00",
                "is_experience": False,
            },
            {
                "title": "Cocktail Mix Pack — Citrus",
                "category_name": "COCKTAIL-MIX-PACKETS",
                "description": "Ready-to-mix syrup packs for your home bar.",
                "price": "999.00",
                "is_experience": False,
            },
            {
                "title": "Party Mixers Box (Sparkling + Tonic)",
                "category_name": "MIXERS-PARTY-BOXES",
                "description": "A curated box with sparkling water, tonic & soda.",
                "price": "1499.00",
                "is_experience": False,
            },
        ]

        for s in samples:
            slug = slugify(s["title"])
            category = category_map[s["category_name"]]

            obj, created = ShopItem.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": s["title"],
                    "category": category,
                    "description": s["description"],
                    "price": s["price"],
                    "is_experience": s["is_experience"],
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created product: {obj.title}"))
            else:
                self.stdout.write(f"Product already exists: {obj.title}")

        self.stdout.write(self.style.SUCCESS("Products ready."))

        # --------------------
        # Experiences
        # --------------------
        exp_cat = category_map["EXPERIENCES"]

        experiences = [
            {
                "title": "Ochre Signature Mixology Session",
                "description": "90–120 minute immersive team mixology session.",
            },
            {
                "title": "Curated Dining & Tasting Experience",
                "description": "Intimate chef-and-mixologist-led tasting for up to 6 guests.",
            },
            {
                "title": "Private Mixology Service",
                "description": "At-home private mixology for your event.",
            },
        ]

        for e in experiences:
            slug = slugify(e["title"])

            obj, created = ShopItem.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": e["title"],
                    "category": exp_cat,
                    "description": e["description"],
                    "is_experience": True,
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created experience: {obj.title}"))
            else:
                self.stdout.write(f"Experience already exists: {obj.title}")

        self.stdout.write(self.style.SUCCESS("Shop seeding completed successfully."))

