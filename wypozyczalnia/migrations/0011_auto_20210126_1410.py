# Generated by Django 3.1.5 on 2021-01-26 13:10

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('wypozyczalnia', '0010_auto_20210122_1833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to='wypozyczalnia.category'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='return_date',
            field=models.DateTimeField(default=datetime.datetime(
                2021, 2, 9, 13, 10, 47, 48958, tzinfo=utc)),
        ),
    ]
