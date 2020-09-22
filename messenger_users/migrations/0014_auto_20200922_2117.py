# Generated by Django 2.2.13 on 2020-09-22 21:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0003_auto_20200329_1028'),
        ('languages', '0013_language_auto_translate'),
        ('licences', '0001_initial'),
        ('messenger_users', '0013_auto_20200907_0540'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='entity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='entities.Entity'),
        ),
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='languages.Language'),
        ),
        migrations.AddField(
            model_name='user',
            name='license',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='licences.License'),
        ),
    ]
