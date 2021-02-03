from messenger_users.models import User
from instances.models import Instance, InstanceAssociationUser
from content_manager.settings import BASE_DIR
from openpyxl import load_workbook
import os


def set_datavalue(user, attribute_name, attribute_id, value):
    user_data = user.userdata_set.filter(data_key=attribute_name, attribute_id=attribute_id)
    if user_data.exists():
        user_data = user_data.last()
        user_data.data_value = value
        user_data.save()
    else:
        user.userdata_set.create(data_key=attribute_name, attribute_id=attribute_id, data_value=value)
    user.save()


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
            user_reg = row[1].value
            bot_id = row[2].value
            childName = row[5].value
            birthday = row[6].value
            childDOB = row[7].value
            print(user_id)
            if (i % 1000) == 0:
                print('-------------------', i, '-------------------')
            if User.objects.filter(id=user_id).exists():
                user = User.objects.get(id=user_id)
                new_instance = Instance.objects.filter(entity_id=1, name=childName)
                if new_instance.exists():
                    new_instance = new_instance.last()
                else:
                    new_instance = Instance(entity_id=1, name=childName)
                    new_instance.save()
                assignation = InstanceAssociationUser.objects.get_or_create(user_id=user_id, instance=new_instance)
                set_datavalue(user, 'instance', 330, new_instance.id)
                set_datavalue(user, 'user_reg', 210, user_reg)
                set_datavalue(user, 'birthday', 191, birthday)
                set_datavalue(user, 'childDOB', 341, childDOB)
                set_datavalue(user, 'childName', 212, childName)
                user.bot_id = bot_id
                user.save()

    wb.template = False
    wb.save(file_url)


create_instances()
