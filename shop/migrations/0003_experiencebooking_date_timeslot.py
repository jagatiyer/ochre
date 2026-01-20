# Generated ad-hoc migration to add date and time_slot to ExperienceBooking
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_shopitem_is_featured'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiencebooking',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='experiencebooking',
            name='time_slot',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
