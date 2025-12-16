from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from mediahub.models import PressArticle, PressKit
from datetime import date


class Command(BaseCommand):
    help = "Seeds sample press articles + press kit"

    def handle(self, *args, **options):

        SAMPLE_ARTICLES = [
            {
                "title": "Ochre Spirits Wins Gold at International Spirits Awards",
                "publication_name": "The Economic Times",
                "date": date(2025, 11, 15),
                "description": (
                    "Our flagship whiskey receives top honors at this year's "
                    "prestigious international competition."
                ),
                "content": "<p>Full article content for Gold Award...</p>",
                "external_link": "",
                "featured": True,
            },
            {
                "title": "The Art of Modern Distilling: A Feature on Ochre",
                "publication_name": "Forbes India",
                "date": date(2025, 10, 28),
                "description": (
                    "A deep dive into Ochre’s innovative approach to traditional distillation."
                ),
                "content": "<p>Full article content for Modern Distilling...</p>",
                "external_link": "",
                "featured": True,
            },
            {
                "title": "Innovation Meets Tradition at Ochre Spirits",
                "publication_name": "Business Standard",
                "date": date(2025, 9, 20),
                "description": (
                    "How Ochre is redefining craft spirits through modern innovation."
                ),
                "content": "<p>Full article content for Innovation Meets Tradition...</p>",
                "external_link": "",
                "featured": False,
            },
        ]

        self.stdout.write(self.style.WARNING("Creating sample press articles..."))

        for data in SAMPLE_ARTICLES:
            article, created = PressArticle.objects.get_or_create(
                title=data["title"],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Added: {article.title}"))
            else:
                self.stdout.write(f"• Already exists: {article.title}")

        self.stdout.write(self.style.SUCCESS("Press articles seeded."))

        # ------------------------------------------------------------------

        self.stdout.write(self.style.WARNING("Creating Press Kit..."))

        if not PressKit.objects.exists():
            kit = PressKit.objects.create()
            kit.pdf.save("press_kit.pdf", ContentFile(b"Sample press kit PDF file"))
            self.stdout.write(self.style.SUCCESS("✓ Press Kit created."))
        else:
            self.stdout.write("• Press Kit already exists.")

        self.stdout.write(self.style.SUCCESS("\nSeeding complete!"))
