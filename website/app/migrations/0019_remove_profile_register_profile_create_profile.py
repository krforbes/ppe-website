# Generated by Django 4.1.4 on 2023-01-22 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_remove_profile_is_md_remove_profile_reset_code_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='register',
        ),
        migrations.AddField(
            model_name='profile',
            name='create_profile',
            field=models.BooleanField(default=True),
        ),
    ]
