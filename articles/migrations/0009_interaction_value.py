# Generated by Django 2.2.13 on 2020-09-09 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0008_articletranslate_language_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='interaction',
            name='value',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
