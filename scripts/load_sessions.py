from user_sessions.models import Session, RedirectBlock, SessionType
from areas.models import Area
from content_manager.settings import BASE_DIR
from openpyxl import load_workbook
import os


def load_sessions():
    # file uri
    file_url = os.path.join(BASE_DIR, 'sessions.xlsx')
    # get workbook
    wb = load_workbook(filename=file_url)
    # get worksheet
    ws = wb['Hoja 1']

    # iterate rows in worksheet
    for i, row in enumerate(ws.rows, start=1):
        # exclude title
        if i != 1:
            # check if session not exist
            if not row[0].value:
                # create session
                session = Session.objects.create(name=row[1].value, min=row[5].value, max=row[6].value)
                # set session ID in file
                row[0].value = session.pk
            # session exists here
            else:
                # get session in platform
                session = Session.objects.get(id=row[0].value)
                # get name and value in sheet
                row_name = row[1].value
                row_min = row[5].value
                row_max = row[6].value
                # verify if session name or value change in BD
                if session.name != row_name or session.min != row_min or session.max != row_max:
                    session.name = row_name
                    session.min = row_min
                    session.max = row_max
                    # change values for session
                    session.save()
            print("Session:", session.pk, session.name)
            # Add Type
            new_type, created = SessionType.objects.get_or_create(name=row[2].value)
            session.session_type = new_type
            session.save()
            # Add Areas
            if row[4].value:
                areas = row[4].value.split(', ')
                for new_area in areas:
                    area, created = Area.objects.get_or_create(name=new_area)
                    session.areas.add(area)
            for index, cell in enumerate(row):
                # verify if cell is not in flow
                if index > 6:
                    # get position
                    position = index - 7
                    # split values
                    if cell.value:
                        text = cell.value.split('\n\n')
                        # choice field type
                        if text[0].strip() == 'TEXT':
                            field_type = 'text'
                        elif text[0].strip() == 'REPLIES':
                            field_type = 'quick_replies'
                        else:
                            field_type = 'save_values_block'
                        print(field_type)
                        # filter position in worksheet
                        filter_fields = session.field_set.filter(position=position)
                        # check if position has not exists in worksheet
                        if not filter_fields.exists():
                            # if not exist field create
                            field = session.field_set.create(field_type=field_type, position=position)
                        else:
                            # if exist get the field
                            print('exists')
                            field = filter_fields.first()

                        # check field type in field is text
                        if field.field_type == 'text':
                            # get messages
                            messages = text[1:]
                            # loop in existents messages
                            for message in field.message_set.all():
                                # delete existent message
                                message.delete()
                            # add file messages
                            for message in messages:
                                if message.strip() != '':
                                    new_message = field.message_set.create(text=message)
                                    print(new_message.pk, 'message created.')

                        # check field type in field is replies
                        if field.field_type == 'quick_replies':
                            # get replies
                            replies = text[1:]
                            # delete existent replies
                            for reply in field.reply_set.all():
                                reply.delete()
                            # add new replies
                            for reply in replies:
                                # split values
                                reply_values = reply.split(', ')
                                # check if reply has label
                                if len(reply_values) > 0:
                                    new_reply = field.reply_set.create(label=reply_values[0])
                                    # check if reply has attribute
                                    if len(reply_values) > 1:
                                        new_reply.attribute = reply_values[1]
                                    # check if has value
                                    if len(reply_values) > 2:
                                        new_reply.value = reply_values[2]
                                    # check if has block
                                    if len(reply_values) > 3:
                                        new_reply.redirect_block = reply_values[3]
                                    # save new values
                                    new_reply.save()

                        # check if field type is save values block
                        if field.field_type == 'save_values_block':
                            # get block
                            block = text[1]
                            filter_blocks = RedirectBlock.objects.filter(field_id=field.pk)
                            if filter_blocks.exists():
                                print(field.redirectblock)
                                # delete redirect block
                                field.redirectblock.delete()
                            # create block
                            new_block = RedirectBlock.objects.create(field=field, block=block)
                            print('New block: ', new_block.pk)

    wb.template = False
    wb.save(file_url)


load_sessions()
