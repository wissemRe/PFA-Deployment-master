# Generated by Django 3.2.3 on 2021-05-28 21:55

from django.db import migrations, models

import authentification.models


class Migration(migrations.Migration):
    dependencies = [
        ('authentification', '0002_auto_20210528_2238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(blank=True, default='', upload_to=authentification.models.user_directory_path),
        ),
    ]
