# Generated by Django 2.2.10 on 2020-04-01 20:32

from django.db import migrations


def permission_add_code_to_company(apps, schema_editor):
    content_type_model = apps.get_model('contenttypes', 'ContentType')
    permission_model = apps.get_model('auth', 'Permission')
    group_model = apps.get_model('auth', 'Group')
    content_type, created = content_type_model.objects.get_or_create(app_label='groups', model='code')
    permissions = permission_model.objects.filter(content_type=content_type,
                                                  codename__in=['add_code'])

    print(permissions)

    groups = group_model.objects.filter(name__in=['company'])

    for group in groups:
        for permission in permissions:
            group_permission = group.permissions.add(permission)
            print(group_permission)


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0011_add_third_permissions_to_company'),
    ]

    operations = [
        migrations.RunPython(permission_add_code_to_company)
    ]
