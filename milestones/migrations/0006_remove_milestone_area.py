# Generated by Django 2.2.5 on 2020-09-10 00:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('milestones', '0005_auto_20200909_2313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='milestone',
            name='area',
        ),
    ]