# Generated by Django 4.1.3 on 2023-01-02 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tmc', '0019_piece_round_setlist_selection_piece_set_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='piece',
            name='name',
            field=models.CharField(default='asdfa', max_length=300),
            preserve_default=False,
        ),
    ]
