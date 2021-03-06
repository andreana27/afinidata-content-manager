# Generated by Django 2.2.13 on 2020-08-10 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20200525_2154'),
    ]

    operations = [
        migrations.CreateModel(
            name='Materiales',
            fields=[
                ('id', models.CharField(choices=[('casa', 'Se encuentran en casa'), ('reciclados', 'Reciclados'), ('juguetes', 'Juguetes'), ('ropa', 'Ropa'), ('libreria', 'De librería'), ('exterior', 'Del exterior'), ('alimentos', 'Alimentos'), ('no', 'Sin materiales')], max_length=35, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=140)),
            ],
        ),
        migrations.CreateModel(
            name='Situacional',
            fields=[
                ('id', models.CharField(choices=[('', 'En casa'), ('', 'Al aire libre'), ('', 'En transporte'), ('', 'Día caluroso'), ('', 'Día de frío'), ('', 'Vacaciones'), ('', 'De noche'), ('', 'De día'), ('', 'En toda ocasión')], max_length=35, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=140)),
            ],
        ),
    ]
