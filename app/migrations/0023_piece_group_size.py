# Generated by Django 4.1.4 on 2023-01-23 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_profile_cursed_with_comic_sans'),
    ]

    operations = [
        migrations.AddField(
            model_name='piece',
            name='group_size',
            field=models.IntegerField(default=0),
        ),
    ]
