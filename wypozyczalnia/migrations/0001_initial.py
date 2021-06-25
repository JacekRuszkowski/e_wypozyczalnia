# Generated by Django 3.1.3 on 2020-12-02 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('parent_category', models.ForeignKey(blank=True, null=True,
                 on_delete=django.db.models.deletion.CASCADE, to='wypozyczalnia.category')),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
                'ordering': ('name',),
                'unique_together': {('slug', 'parent_category')},
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('author', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('pages', models.CharField(max_length=50)),
                ('image', models.ImageField(
                    default='default.jpg', upload_to='book_images')),
                ('copies', models.IntegerField()),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('category', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='wypozyczalnia.category')),
            ],
        ),
    ]
