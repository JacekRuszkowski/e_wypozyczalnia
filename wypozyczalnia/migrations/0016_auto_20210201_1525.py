# Generated by Django 3.1.1 on 2021-02-01 14:25

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('wypozyczalnia', '0015_auto_20210129_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='copies',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='return_date',
            field=models.DateTimeField(default=datetime.datetime(
                2021, 2, 15, 14, 25, 27, 430070, tzinfo=utc)),
        ),
    ]
