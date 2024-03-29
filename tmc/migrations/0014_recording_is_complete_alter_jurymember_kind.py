# Generated by Django 4.1.3 on 2022-11-13 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tmc', '0013_jurymember_bank_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='recording',
            name='is_complete',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='jurymember',
            name='kind',
            field=models.CharField(blank=True, max_length=120, verbose_name='function TMC'),
        ),
    ]
