# Generated by Django 2.2.5 on 2020-10-26 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bots', '0011_auto_20200918_2119'),
    ]

    operations = [
        migrations.AddField(
            model_name='bot',
            name='url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
