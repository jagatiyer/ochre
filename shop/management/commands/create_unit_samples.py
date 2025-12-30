from django.core.management.base import BaseCommand
from decimal import Decimal
from shop.models import UnitType, ShopItem, ProductUnit, ShopCategory

class Command(BaseCommand):
    help = 'Create sample UnitTypes, products, and ProductUnits for testing'

    def handle(self, *args, **options):
        vol, _ = UnitType.objects.get_or_create(code='volume', defaults={'name':'Volume'})
        size, _ = UnitType.objects.get_or_create(code='size', defaults={'name':'Size'})

        cat, _ = ShopCategory.objects.get_or_create(name='Sample', defaults={'slug':'sample'})

        # Product with volume units
        p1, created = ShopItem.objects.get_or_create(slug='sample-volume-product', defaults={
            'title':'Sample Volume Product', 'category':cat, 'price':Decimal('0.00'), 'published':True
        })
        # UnitType is assigned to ProductUnit rows; do not set on ShopItem
        ProductUnit.objects.update_or_create(product=p1, label='500 ml', defaults={'unit_type':vol, 'value':'500', 'price':Decimal('120.00'), 'is_default':True, 'is_active':True})
        ProductUnit.objects.update_or_create(product=p1, label='750 ml', defaults={'unit_type':vol, 'value':'750', 'price':Decimal('170.00'), 'is_default':False, 'is_active':True})

        # Product with size units
        p2, created = ShopItem.objects.get_or_create(slug='sample-size-product', defaults={
            'title':'Sample Size Product', 'category':cat, 'price':Decimal('0.00'), 'published':True
        })
        # UnitType is assigned to ProductUnit rows; do not set on ShopItem
        ProductUnit.objects.update_or_create(product=p2, label='Small', defaults={'unit_type':size, 'value':'S', 'price':Decimal('90.00'), 'is_default':True, 'is_active':True})
        ProductUnit.objects.update_or_create(product=p2, label='Large', defaults={'unit_type':size, 'value':'L', 'price':Decimal('150.00'), 'is_default':False, 'is_active':True})

        self.stdout.write(self.style.SUCCESS('Sample products and units created/updated.'))