from milestones.models import Session
from content_manager.settings import BASE_DIR
from messenger_users.models import User
import csv
import os


def run():
    with open(os.path.join(BASE_DIR, 'report.csv'), 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['session', 'child', 'Parent', 'Milestones:'])
        for s in Session.objects.filter(active=False):
            if s.instance_set.exists():
                row_array = [s.uuid]
                i = s.instance_set.first()
                u = i.get_users().first()
                row_array.append(i)
                row_array.append("%s %s" % (u.first_name, u.last_name))
                row_array.append(' ')
                for r in s.response_set.all():
                    row_array.append(r.milestone.code)
                    if r.response == 'done':
                        row_array.append('yes')
                    else:
                        row_array.append('no')

                spamwriter.writerow(row_array)
