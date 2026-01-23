from django.db import migrations


def forwards(apps, schema_editor):
    CollectionItem = apps.get_model('collections_app', 'CollectionItem')
    CollectionCategory = apps.get_model('collections_app', 'CollectionCategory')

    # Gather existing legacy category strings
    legacy_values = CollectionItem.objects.values_list('category', flat=True).distinct()
    slugified = {}

    for val in legacy_values:
        if not val:
            continue
        # Create a category with the same slug as the legacy value and a
        # human-friendly name. If the legacy value already looks like a
        # slug, use title-casing for name.
        name = val.replace('_', ' ').title()
        slug = val
        cat, created = CollectionCategory.objects.get_or_create(slug=slug, defaults={'name': name})
        slugified[val] = cat

    # Map items to the newly created categories
    for legacy_val, category_obj in slugified.items():
        CollectionItem.objects.filter(category=legacy_val).update(category_fk=category_obj)


def reverse(apps, schema_editor):
    # Leave category_fk populated; reversing this migration is a no-op.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('collections_app', '0003_create_collectioncategory_and_fk'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse),
    ]
