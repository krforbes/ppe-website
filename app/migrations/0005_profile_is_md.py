# Generated by Django 4.1.4 on 2023-01-05 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_profile_alter_piece_arrangers_alter_piece_performers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_md',
            field=models.BooleanField(default=False),
        ),
    ]
