# Generated by Django 2.2.13 on 2021-02-02 22:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_sessions', '0022_auto_20210202_2150'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='request_type',
        ),
        migrations.RemoveField(
            model_name='service',
            name='url',
        ),
    ]
