from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from shop.models import ShopCategory, ShopItem
from django.utils.text import slugify

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

        created_cats = []
        for name in categories:
            cat, _ = ShopCategory.objects.get_or_create(name=name)
            created_cats.append(cat)
        self.stdout.write("Categories created.")

        # create a few products for product categories (non-experience)
        samples = [
            {
                "title": "Ochre Signature T-Shirt (Pack of 3)",
                "category": ShopCategory.objects.get(name="T-SHIRTS"),
                "description": "Premium cotton pack — three colours included.",
                "price": "1999.00",
                "is_experience": False,
            },
            {
                "title": "Ochre Glassware Gift Set",
                "category": ShopCategory.objects.get(name="GLASSWARE"),
                "description": "Two crystal tumblers and tasting guide.",
                "price": "3499.00",
                "is_experience": False,
            },
            {
                "title": "Cocktail Mix Pack — Citrus",
                "category": ShopCategory.objects.get(name="COCKTAIL-MIX-PACKETS"),
                "description": "Ready-to-mix syrup packs for your home bar.",
                "price": "999.00",
                "is_experience": False,
            },
            {
                "title": "Party Mixers Box (Sparkling + Tonic)",
                "category": ShopCategory.objects.get(name="MIXERS-PARTY-BOXES"),
                "description": "A curated box with sparkling water, tonic & soda.",
                "price": "1499.00",
                "is_experience": False,
            },
        ]

        for s in samples:
            ShopItem.objects.get_or_create(
                title=s["title"],
                defaults={
                    "category": s["category"],
                    "description": s["description"],
                    "price": s["price"],
                    "is_experience": s["is_experience"],
                },
            )
        self.stdout.write("Products created.")

        # create three experiences (is_experience=True)
        exp_cat, _ = ShopCategory.objects.get_or_create(name="EXPERIENCES")
        experiences = [
            {
                "title": "Ochre Signature Mixology Session",
                "category": exp_cat,
                "description": "90–120 minute immersive team mixology session.",
                "is_experience": True,
            },
            {
                "title": "Curated Dining & Tasting Experience",
                "category": exp_cat,
                "description": "Intimate chef-and-mixologist-led tasting for up to 6 guests.",
                "is_experience": True,
            },
            {
                "title": "Private Mixology Service",
                "category": exp_cat,
                "description": "At-home private mixology for your event.",
                "is_experience": True,
            },
        ]

        for e in experiences:
            ShopItem.objects.get_or_create(
                title=e["title"],
                defaults={
                    "category": e["category"],
                    "description": e["description"],
                    "is_experience": True,
                },
            )
        self.stdout.write("Experiences created.")
        self.stdout.write(self.style.SUCCESS("Seeding complete."))
