from content_manager.settings import BASE_DIR
from milestones.models import Milestone
from groups.models import MilestoneRisk
from programs.models import Program
import csv
import os


def run():
    program = Program.objects.get(id=1)

    with open(os.path.join(BASE_DIR, 'risks.csv'), newline='') as csvfile:
        filereader = csv.reader(csvfile, delimiter=',')
        for row in filereader:
            m = Milestone.objects.get(second_code=row[0])
            risk_0 = MilestoneRisk.objects.create(milestone=m, program=program, value=row[1], percent_value=0)
            risk_1 = MilestoneRisk.objects.create(milestone=m, program=program, value=row[2], percent_value=50)
            risk_2 = MilestoneRisk.objects.create(milestone=m, program=program, value=row[3], percent_value=100)
            print(risk_0, risk_1, risk_2)
