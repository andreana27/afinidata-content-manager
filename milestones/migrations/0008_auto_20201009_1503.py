# Generated by Django 2.2.5 on 2020-10-09 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('milestones', '0007_auto_20200916_1632'),
    ]

    operations = [
        migrations.AddField(
            model_name='milestone',
            name='max',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='milestone',
            name='min',
            field=models.FloatField(default=0, null=True),
        ),
    ]
