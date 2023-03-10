# Generated by Django 4.1.4 on 2023-01-22 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_alter_schedule_availability_reset_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='create_profile',
        ),
        migrations.AlterField(
            model_name='schedule',
            name='availability_reset',
            field=models.DateTimeField(verbose_name='last reset availability'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='pref_reset',
            field=models.DateTimeField(verbose_name='last reset preferences'),
        ),
    ]
