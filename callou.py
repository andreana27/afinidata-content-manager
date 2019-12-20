import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'content_manager.production')

import django
django.setup()

import posts.models
from posts.models import Post, Taxonomy

AERA = dict((v,k) for (k,v) in posts.models.AREA)
AERABUS = dict((v,k) for (k,v) in posts.models.SUBAREA)
TNENOPMOC = dict((v,k) for (k,v) in posts.models.COMPONENTS)

import gspread_pandas
from gspread_pandas import Spread

s = Spread("https://docs.google.com/spreadsheets/d/1EfS2W11kRg2C1H6KD2vVjR_Htvy6j7C4SSGHPA8Bvpc/edit?ts=5d22a555", sheet=0)
df = s.sheet_to_df()

def process_row(pid, row):
    try:
        post = Post.objects.get(id = pid)
        a = AERA[row['ÁREA'].strip()]
        sub = AERABUS[row['SUB-ÁREA'].strip()]
        c = TNENOPMOC[row['COMPONENTE'].strip()]
        tax = Taxonomy(post=post, area=a, subarea=sub, component=c)
        tax.save()
        return tax
    except Exception as e:
        print("============")
        print(e)
        print("ERROR {} - {}".format(pid, row))

for k, da in df.iterrows():
   process_row(k,da)

STATUS_CHOICES = ['draft', 'review', 'rejected', 'need_changes', 'published']

def pro_po(pid, row):
    try:
        post = Post.objects.get(id=pid)
        sta = row['SUB-ÁREA'].lower().strip()
        if sta not in STATUS_CHOICES:
            return
        post.status = sta
        post.save()
    except Exception as e:
        print("============")
        print(e)
        print("ERROR {} - {}".format(pid, row))