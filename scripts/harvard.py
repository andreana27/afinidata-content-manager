from programs.models import ProgramMilestoneValue
from content_manager.settings import BASE_DIR
import csv
import os


def run():
    with open(os.path.join(BASE_DIR, 'harvard-milestones.csv'), newline='') as csvfile:
        filereader = csv.reader(csvfile, delimiter=',')
        for row in filereader:
            pms = ProgramMilestoneValue.objects.filter(milestone__second_code=row[0])
            if pms.exists():
                pm = pms.first()
                pm.min = row[1]
                pm.max = row[2]
                pm.save()
                print(pm.milestone.code, pm.min, pm.max, pm.milestone.min, pm.milestone.max)
