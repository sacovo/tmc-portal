# Generated by Django 4.0.4 on 2022-06-26 15:02

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import tmc.models


class Migration(migrations.Migration):

    dependencies = [
        ('tmc', '0003_inscription_passport_inscription_photo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscription',
            name='passport',
            field=models.FileField(blank=True, upload_to='documents/'),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='photo',
            field=models.ImageField(blank=True, upload_to='photos/'),
        ),
        migrations.CreateModel(
            name='RequiredRecording',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=600)),
                ('slug', models.SlugField()),
                ('nr', models.IntegerField()),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tmc.instrument')),
            ],
        ),
        migrations.CreateModel(
            name='Recording',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recording', models.FileField(upload_to=tmc.models.recording_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'mkv'])])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('requirement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tmc.requiredrecording')),
                ('uploader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tmc.instrument')),
            ],
        ),
    ]
