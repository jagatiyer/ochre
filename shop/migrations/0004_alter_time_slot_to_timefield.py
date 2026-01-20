from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_experiencebooking_date_timeslot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiencebooking',
            name='time_slot',
            field=models.TimeField(null=True, blank=True),
        ),
    ]
