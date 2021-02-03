from messenger_users.models import User
from instances.models import Instance, InstanceAssociationUser
from content_manager.settings import BASE_DIR
from openpyxl import load_workbook
import os


def create_instances():
    # file uri
    file_url = os.path.join(BASE_DIR, 'users.xlsx')
    # get workbook
    wb = load_workbook(filename=file_url)
    # get worksheet
    ws = wb['Hoja 1']

    # iterate rows in worksheet
    for i, row in enumerate(ws.rows, start=1):
        if i > 1:
            user_id = row[0].value
            user_reg = row[0].value
            bot_id = row[1].value
            childName = row[4].value
            birthday = row[5].value
            childDOB = row[6].value
            if (i % 1000) == 0:
                print(i, ':', user_id)
            if User.objects.filter(id=user_id).exists():
                user = User.objects.get(id=user_id)
                new_instance = Instance(user_id=user_id, entity_id=1, name=childName)
                assignation = InstanceAssociationUser.objects.get_or_create(user_id=user_id, instance=new_instance)
                user.userdata_set.update_or_create(data_key='instance', attribute_id=330,
                                                   defaults={'data_value': new_instance.id})
                user.userdata_set.update_or_create(data_key='user_reg', attribute_id=210,
                                                   defaults={'data_value': user_reg})
                user.userdata_set.update_or_create(data_key='birthday', attribute_id=191,
                                                   defaults={'data_value': birthday})
                user.userdata_set.update_or_create(data_key='childDOB', attribute_id=341,
                                                   defaults={'data_value': childDOB})
                user.userdata_set.update_or_create(data_key='childName', attribute_id=212,
                                                   defaults={'data_value': childName})
                user.bot_id = bot_id
                user.save()

    wb.template = False
    wb.save(file_url)


create_instances()
