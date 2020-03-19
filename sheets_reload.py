import os
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'content_manager.production')

import django
django.setup()

import logging

import posts.models
from posts.models import Post

import gspread_pandas
from gspread_pandas import Spread


def fix_date_post_dataframe(post: Post, df):
    try:
        min_r = post.min_range
        max_r = post.max_range
        mess = df["meses"]
        reg = r"(\d+)\s*-\s*(\d+).*"
        meses_search = re.search(reg, mess)
        min_d_val = int(meses_search.group(1))
        max_d_val = int(meses_search.group(2))
        if abs(min_r - min_d_val) > 0 or abs(max_r-max_d_val) > 0:
            post.min_range = min_d_val
            post.max_range = max_d_val
            post.save()
            print(f"Fixed post {post.pk} for a date difference {min_r} - {min_d_val}, {max_r}-{max_d_val}")
    except:
        logging.exception("error when setting age ranges to post, key")



def diff_post_dataframe(post: Post, df):
    min_r = post.min_range
    max_r = post.max_range
    mess = df["meses"]
    reg = r"(-?\d+)\s*-\s*(-?\d+).*"
    meses_search = re.search(reg, mess)
    min_d_val = int(meses_search.group(1))
    max_d_val = int(meses_search.group(2))
    # print(df)
    # print(f"min- {min_r} === {min_d_val}")
    # print(f"max- {max_r} === {max_d_val}")
    return (min_r - min_d_val, max_r-max_d_val)

s = Spread(sheet,
           sheet="Base de Datos")
df = s.sheet_to_df()


STATUS_CHOICES = ['draft', 'review', 'rejected', 'need_changes', 'published']

for k, da in df.iterrows():
    print("-----------------")
    if da["STATUS"] == 'rejected':
        continue
    try:
       post = Post.objects.get(id=k)   #id=da["POST ID"])   # id=k
       # print("====")
       # print(fix_date_post_dataframe(post, da))

    except Exception as e:
        logging.exception(f"broken on key {k} - {da}")
        pass
