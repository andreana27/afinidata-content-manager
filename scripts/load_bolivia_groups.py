from content_manager.settings import BASE_DIR
from django.contrib.auth.models import User
from openpyxl import load_workbook
from groups.models import Group
import os


def run():
    wb = load_workbook(os.path.join(BASE_DIR, 'bolivia_groups.xlsx'))
    book = wb['Grupos']

    for row in book:
        print(row)
