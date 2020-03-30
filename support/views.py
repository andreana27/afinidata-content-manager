from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.urls import reverse

import json
import traceback
import requests

@csrf_exempt
def index(request):
    return HttpResponse('hey')


@csrf_exempt
def chatfuel(request):
    url_part = ''
    attributes = [dict(attribute_name = '',
                       attribute_value = '')]
    for attribute_name, attribute_value in attributes:
        url_part += f'{attribute_name}={attribute_value}&'
    bot_id = '5e4cdf014b1fd70001e9384b'
    user_id = '3650968864944027'
    token = 'mELtlMAHYqR0BvgEiMq8zVek3uYUK3OJMbtyrdNPTrQB9ndV0fM7lWTFZbM4MZvD'
    block_name = 'subscribe_sequence'
    #tag = ''&chatfuel_message_tag={tag}
    url = f'''https://api.chatfuel.com/bots/{bot_id}/users/{user_id}/send?chatfuel_token={token}&chatfuel_block_name={block_name}&{url_part}'''
    r = requests.post(url)
    return HttpResponse(r.text)
