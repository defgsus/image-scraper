# Generated by Django 3.2 on 2021-07-01 13:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('image_scraper', '0002_change_verbose_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageRateModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Create at')),
                ('updated_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Create at')),
                ('user', models.CharField(max_length=32, verbose_name='Rating username')),
                ('rate', models.SmallIntegerField(verbose_name='Integer rating value')),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='image_scraper.imagemodel', verbose_name='Rated image')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]