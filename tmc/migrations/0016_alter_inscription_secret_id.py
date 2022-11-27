# Generated by Django 4.1.3 on 2022-11-27 20:24

from django.db import migrations, models
import tmc.models


class Migration(migrations.Migration):

    dependencies = [
        ('tmc', '0015_inscription_internal_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscription',
            name='secret_id',
            field=models.CharField(default=tmc.models.generate_secret_id, max_length=8),
        ),
    ]