# Generated by Django 2.2.10 on 2020-03-25 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programs', '0002_level'),
    ]

    operations = [
        migrations.RenameField(
            model_name='level',
            old_name='range_max',
            new_name='assign_max',
        ),
        migrations.RenameField(
            model_name='level',
            old_name='range_min',
            new_name='assign_min',
        ),
    ]
