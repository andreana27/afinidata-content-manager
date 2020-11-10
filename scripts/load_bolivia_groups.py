from content_manager.settings import BASE_DIR
from django.contrib.auth.models import User
from programs.models import Program
from openpyxl import load_workbook
from groups.models import Group
from bots.models import Bot
import os


def run():
    wb = load_workbook(os.path.join(BASE_DIR, 'bolivia_groups.xlsx'))
    book = wb['Grupos']

    for index, row in enumerate(book):
        if index > 0:
            new_group = Group.objects.create(name=row[0].value)
            if row[1].value:
                parents = Group.objects.filter(name=row[1].value)
            else:
                parents = Group.objects.filter(id=50)
            if parents.exists():
                new_group.parent = parents.first()
                new_group.save()
            if row[2].value:
                new_group.code_set.create(code=row[2].value)
            if row[3].value:
                users = User.objects.filter(username=row[3].value)
                if users.exists():
                    new_group.rolegroupuser_set.create(user=users.first(), role='administrator')
            if row[4].value:
                users = User.objects.filter(username=row[4].value)
                if users.exists():
                    new_group.rolegroupuser_set.create(user=users.first(), role='administrator')
            programs = Program.objects.filter(name='Unicef Bolivia panmanitos')
            if programs.exists():
                new_group.programassignation_set.create(program=programs.first())
            bots = Bot.objects.filter(name='Afini Pilot Perú y Bolivia')
            if bots.exists():
                new_group.botassignation_set.create(bot=bots.first())
            print(new_group)
