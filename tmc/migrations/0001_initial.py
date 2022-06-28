# Generated by Django 4.0.4 on 2022-06-26 11:12

import address.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('address', '0003_auto_20200830_1851'),
    ]

    operations = [
        migrations.CreateModel(
            name='Correpetitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='HostFamily',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('mobile', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('email', models.EmailField(max_length=254)),
                ('single_rooms', models.PositiveSmallIntegerField()),
                ('double_rooms', models.PositiveSmallIntegerField()),
                ('provides_breakfast', models.BooleanField()),
                ('has_own_bathroom', models.BooleanField()),
                ('has_wifi', models.BooleanField()),
                ('provides_transport', models.BooleanField()),
                ('preferred_gender', models.CharField(blank=True, choices=[('m', 'Male'), ('f', 'Female'), ('n', 'Non-Binary')], max_length=5)),
                ('pets', models.CharField(blank=True, max_length=180)),
                ('practice_allowed', models.BooleanField()),
                ('practice_notes', models.CharField(blank=True, max_length=180)),
                ('smoking_allowed', models.BooleanField()),
                ('notes', models.TextField()),
                ('submitted_at', models.DateTimeField()),
                ('address', address.models.AddressField(on_delete=django.db.models.deletion.CASCADE, to='address.address')),
            ],
        ),
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('name_de_ch', models.CharField(max_length=255, null=True)),
                ('name_en', models.CharField(max_length=255, null=True)),
                ('name_fr_ch', models.CharField(max_length=255, null=True)),
                ('name_it_ch', models.CharField(max_length=255, null=True)),
                ('name_es', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='JuryMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('is_pre', models.BooleanField()),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tmc.instrument')),
            ],
        ),
        migrations.CreateModel(
            name='Inscription',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('gender', models.CharField(choices=[('m', 'Male'), ('f', 'Female'), ('n', 'Non-Binary')], max_length=10, verbose_name='gender')),
                ('given_name', models.CharField(max_length=120, verbose_name='given name')),
                ('surname', models.CharField(max_length=120, verbose_name='surname')),
                ('date_of_birth', models.DateField(verbose_name='date of birth')),
                ('nationality', django_countries.fields.CountryField(max_length=2, verbose_name='nationality')),
                ('mother_tongue', models.CharField(max_length=120, verbose_name='language')),
                ('language_of_correspondence', models.CharField(choices=[('en', 'English'), ('de', 'German')], max_length=120, verbose_name='language of correspond')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='phone')),
                ('email', models.EmailField(max_length=254, verbose_name='e-mail')),
                ('education', models.TextField(max_length=500, verbose_name='education')),
                ('occupation', models.CharField(max_length=60, verbose_name='occupation')),
                ('notes', models.TextField(blank=True, verbose_name='notes')),
                ('emergency_contact', models.CharField(max_length=120, verbose_name='emergency contact')),
                ('emergency_phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='emergency phone')),
                ('emergency_relation', models.CharField(blank=True, max_length=120, verbose_name='emergency relation')),
                ('accomodation_needed', models.BooleanField(verbose_name='accomodation needed')),
                ('is_smoker', models.BooleanField(verbose_name='smoker')),
                ('food_needed', models.BooleanField(verbose_name='need food')),
                ('vegetarian', models.BooleanField(verbose_name='vegetarian')),
                ('allergies', models.CharField(blank=True, max_length=120, verbose_name='allergies')),
                ('submitted_at', models.DateTimeField(auto_now_add=True, verbose_name='submitted')),
                ('address', address.models.AddressField(on_delete=django.db.models.deletion.CASCADE, to='address.address', verbose_name='address')),
                ('host_family', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tmc.hostfamily')),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tmc.instrument', verbose_name='instrument')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='hostfamily',
            name='languages',
            field=models.ManyToManyField(to='tmc.language'),
        ),
    ]
