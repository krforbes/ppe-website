# Generated by Django 4.1.4 on 2023-01-19 22:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_schedule_availability_schedule_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='availability_updated',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='last updated availability'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='pref_updated',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='last updated preferences'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='schedule',
            name='availability_reset',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='last reset availability'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='schedule',
            name='pref_reset',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='last reset preferences'),
            preserve_default=False,
        ),
    ]