# Generated by Django 3.1.4 on 2021-04-22 22:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attributes', '0005_attribute_attribute_view'),
        ('user_sessions', '0032_auto_20210422_2252'),
    ]

    operations = [
        migrations.AddField(
            model_name='reply',
            name='attribute',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='attributes.attribute'),
        ),
    ]
