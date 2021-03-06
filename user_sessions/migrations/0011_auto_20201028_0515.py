# Generated by Django 2.2.13 on 2020-10-28 05:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_sessions', '0010_auto_20201028_0419'),
        ('messenger_users', '0021_auto_20201222_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interaction',
            name='instance_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='instances.Instance'),
        ),
        migrations.AlterField(
            model_name='interaction',
            name='user_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='messenger_users.User'),
        ),
    ]
