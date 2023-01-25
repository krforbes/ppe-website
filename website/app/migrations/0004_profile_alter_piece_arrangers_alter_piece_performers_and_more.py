# Generated by Django 4.1.4 on 2023-01-05 05:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0003_rename_piece_text_piece_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='piece',
            name='arrangers',
            field=models.ManyToManyField(related_name='arranged', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='piece',
            name='performers',
            field=models.ManyToManyField(related_name='playing', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Person',
        ),
    ]
