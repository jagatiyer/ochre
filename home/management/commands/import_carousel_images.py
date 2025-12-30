import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from django.db import models


class Command(BaseCommand):
    help = 'Import images from a folder into CarouselSlide entries'

    def add_arguments(self, parser):
        parser.add_argument('folder', nargs='?', default='Home_carousel_images', help='Folder (relative to BASE_DIR) containing images')

    def handle(self, *args, **options):
        folder = options.get('folder')
        base = getattr(settings, 'BASE_DIR', None) or os.getcwd()
        src_dir = os.path.join(base, folder)

        if not os.path.isdir(src_dir):
            self.stderr.write(self.style.ERROR(f'Folder not found: {src_dir}'))
            return

        from home.models import CarouselSlide

        # determine starting order
        max_order = CarouselSlide.objects.aggregate(models_max=models.Max('display_order'))['models_max']
        if max_order is None:
            max_order = 0
        next_order = max_order + 1

        valid_ext = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif'}

        files = sorted(os.listdir(src_dir))
        imported = 0
        skipped = 0

        for fname in files:
            path = os.path.join(src_dir, fname)
            if not os.path.isfile(path):
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext not in valid_ext:
                skipped += 1
                continue

            # avoid duplicates by filename
            if CarouselSlide.objects.filter(image__icontains=fname).exists():
                self.stdout.write(self.style.WARNING(f'Skipping (exists): {fname}'))
                skipped += 1
                continue

            slide = CarouselSlide()
            slide.is_active = True
            slide.display_order = next_order

            with open(path, 'rb') as f:
                django_file = File(f)
                slide.image.save(fname, django_file, save=False)

            slide.save()
            self.stdout.write(self.style.SUCCESS(f'Imported: {fname} as order {next_order}'))
            next_order += 1
            imported += 1

        self.stdout.write(self.style.SUCCESS(f'Done. Imported: {imported}. Skipped: {skipped}.'))
