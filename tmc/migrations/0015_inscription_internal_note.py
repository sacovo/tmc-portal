# Generated by Django 4.1.3 on 2022-11-25 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tmc', '0014_recording_is_complete_alter_jurymember_kind'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='internal_note',
            field=models.CharField(blank=True, max_length=120),
        ),
    ]