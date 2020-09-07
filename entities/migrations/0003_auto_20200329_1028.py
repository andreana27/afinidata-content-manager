# Generated by Django 2.2.10 on 2020-03-29 10:28

from django.db import migrations


def set_first_entity_permissions_to_company(apps, schema_editor):
    content_type_model = apps.get_model('contenttypes', 'ContentType')
    permission_model = apps.get_model('auth', 'Permission')
    group_model = apps.get_model('auth', 'Group')
    bot_content_type = content_type_model.objects.get(app_label='entities', model='entity')
    permissions = permission_model.objects.filter(content_type=bot_content_type,
                                                  codename__in=['view_entity'])

    groups = group_model.objects.filter(name__in=['company'])

    for group in groups:
        for permission in permissions:
            group_permission = group.permissions.add(permission)
            print(group_permission)


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0002_auto_20200329_0036'),
        ('pages', '0001_initial')
    ]

    operations = [
        migrations.RunPython(set_first_entity_permissions_to_company)
    ]