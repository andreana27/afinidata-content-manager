from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from messenger_users.models import User

import json
import traceback
import requests

@login_required(login_url='/login/')
def index(request):
    return render(request, 'support/index.html')


@csrf_exempt
def chatfuel(request):
    def get_fb_user_id(user_id):
        return User.objects.get(id=user_id).last_channel_id
    #https://contentmanager.afinidata.com/utilities/child_months/?date=14/06/1989
    vars = ['child_dob', 'childDOBinput', 'childDOB', 'favorite_birthday']
    url_part = ''
    date_of_birth = request.POST.get("dob")
    attributes = dict()
    for v in vars:
        attributes[v] = date_of_birth
    r = requests.get(request.build_absolute_uri(reverse('utilities:get_months')),
                     params = dict(date = date_of_birth))
    cm = json.loads(r.text)['set_attributes']['childMonths']
    attributes['childMonths'] = cm
    for attribute_name, attribute_value in attributes.items():
        url_part += f'{attribute_name}={attribute_value}&'
    #Afini Tutor
    bot_id = '5e4cdf014b1fd70001e9384b'
    token = 'mELtlMAHYqR0BvgEiMq8zVek3uYUK3OJMbtyrdNPTrQB9ndV0fM7lWTFZbM4MZvD'
    #Afini normal
    if request.POST.get("bot") == "1":
        bot_id = '58bcd41ee4b0d01fda181a35'
        token = 'vnbqX6cpvXUXFcOKr5RHJ7psSpHDRzO1hXBY8dkvn50ZkZyWML3YdtoCnKH7FSjC'
    fb_user_id = get_fb_user_id(request.POST.get("user_id"))#'3650968864944027'
    block_name = request.POST.get("block_name")
    #tag = ''&chatfuel_message_tag={tag}
    url = f'''https://api.chatfuel.com/bots/{bot_id}/users/{fb_user_id}/send?chatfuel_token={token}&chatfuel_block_name={block_name}&{url_part}'''
    r = requests.post(url)
    return render(request, 'support/result.html', dict(message = json.loads(r.text)))
