# Generated by Django 2.2.10 on 2020-03-04 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger_users', '0003_auto_20200304_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='backup_key',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
    ]
