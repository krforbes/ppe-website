# Generated by Django 4.1.4 on 2023-01-24 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_piece_group_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='has_cat',
            field=models.BooleanField(default=False),
        ),
    ]
