# Generated by Django 2.2.5 on 2020-09-09 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('areas', '0008_auto_20200908_0651'),
        ('milestones', '0004_auto_20200320_1851'),
    ]

    operations = [
        migrations.AddField(
            model_name='milestone',
            name='areas',
            field=models.ManyToManyField(to='areas.Area'),
        ),
        migrations.AlterField(
            model_name='milestone',
            name='area',
            field=models.IntegerField(null=True),
        ),
    ]
