# Generated by Django 3.1.4 on 2021-04-20 22:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messenger_users', '0026_auto_20210324_2145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userchannel',
            name='last_seen',
        ),
        migrations.CreateModel(
            name='Interaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.IntegerField(choices=[(1, 'last user message'), (2, 'last channel interaction')], default=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user_channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='messenger_users.userchannel')),
            ],
        ),
    ]
