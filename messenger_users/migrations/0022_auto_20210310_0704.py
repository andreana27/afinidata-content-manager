# Generated by Django 2.2.13 on 2021-03-10 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger_users', '0021_auto_20201222_1842'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_seen',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='userchannel',
            name='last_seen',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
