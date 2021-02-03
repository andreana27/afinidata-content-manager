from messenger_users.models import User
from content_manager.settings import BASE_DIR
from openpyxl import load_workbook
import os


def update_bot(bot_id):
    # file uri
    file_url = os.path.join(BASE_DIR, 'users.xlsx')
    # get workbook
    wb = load_workbook(filename=file_url)
    # get worksheet
    ws = wb['Hoja 1']

    # iterate rows in worksheet
    for i, row in enumerate(ws.rows, start=1):
        if User.objects.filter(id=row[0].value).exists():
            user = User.objects.get(id=row[0].value)
            user.bot_id = bot_id
            user.save()
            print(row[0].value)

    wb.template = False
    wb.save(file_url)


update_bot(11)
