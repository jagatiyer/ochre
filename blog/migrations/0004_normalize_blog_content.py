from django.db import migrations


def migrate_description_to_content(apps, schema_editor):
    BlogPost = apps.get_model("blog", "BlogPost")

    for post in BlogPost.objects.all():
        if (not post.content or post.content.strip() == "") and post.description:
            post.content = post.description
            post.save(update_fields=["content"])


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0003_alter_blogpost_options_blogpost_excerpt_and_more"),
    ]

    operations = [
        migrations.RunPython(migrate_description_to_content),
    ]

