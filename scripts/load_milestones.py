from content_manager.settings import BASE_DIR
from milestones.models import Milestone
from openpyxl import load_workbook
from areas.models import Area
import os


def run():
    areas = dict(
        MOTOR=Area.objects.get(name='Motor'),
        SOCIOEMOCIONAL=Area.objects.get(name='Socio emocional'),
        COGNITIVO=Area.objects.get(name='Cognitivo y Lenguaje'),
        LENGUAJE=Area.objects.get(name='Lenguaje')
    )

    wb = load_workbook(os.path.join(BASE_DIR, 'bolivia-hitos.xlsx'))
    book = wb['h']

    for index, row in enumerate(book):
        if index > 0:
            if row[0].value:
                new_milestone = Milestone.objects.create(
                    code=row[0].value,
                    name=row[1].value,
                    description=row[1].value,
                    min=row[2].value,
                    max=row[3].value,
                    value=row[2].value,
                    second_code=row[0].value,
                    secondary_value=row[2].value,
                    source=row[5].value
                )
                new_milestone.areas.add(areas[row[4].value])
                print(new_milestone, new_milestone.areas.all())
