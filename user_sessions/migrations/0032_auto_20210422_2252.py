# Generated by Django 3.1.4 on 2021-04-22 22:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_sessions', '0031_intent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reply',
            old_name='attribute',
            new_name='the_attribute',
        ),
    ]