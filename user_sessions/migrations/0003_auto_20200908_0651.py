# Generated by Django 2.2.13 on 2020-09-08 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('areas', '0008_auto_20200908_0651'),
        ('user_sessions', '0002_interaction_text'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='topics',
        ),
        migrations.AddField(
            model_name='session',
            name='areas',
            field=models.ManyToManyField(to='areas.Area'),
        ),
    ]