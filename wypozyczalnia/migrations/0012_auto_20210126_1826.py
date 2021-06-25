# Generated by Django 3.1.3 on 2021-01-26 17:26

import datetime
import django.core.validators
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('wypozyczalnia', '0011_auto_20210126_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='return_date',
            field=models.DateTimeField(default=datetime.datetime(
                2021, 2, 9, 17, 26, 45, 130339, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(
                5), django.core.validators.MinValueValidator(0)]),
        ),
    ]
