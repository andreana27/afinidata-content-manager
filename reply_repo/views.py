from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from reply_repo import models
import json
#from posts.models import Post, Interaction
#from messenger_users.models import User, UserData

@csrf_exempt
def index(request):
    def _prepare_message(message):
        message = message[0]
        extra_items = None
        try:
            extra_items = json.loads(message.extra_items)
        except:
            extra_items = {}
        r2 = dict(text=message.content)
        r2.update(extra_items)
        result = dict(messages=[r2])
        return result
    '''{
     "messages": [
       {"text": "Welcome to the Example!"},
       {"text": "What are you up to?",
       "quick_replies": [
        {
          "title":"Loved it!",
          "block_names": ["Block 1", "Block 2"]
        },
        {
          "title":"Not really...",
          "url": "https://google.com",
          "type":"json_plugin_url"
        },
     ]
    }'''
    data = json.loads(request.body)
    if not data['locale']:
        raise Http404
    if not data['block_id']:
        raise Http404
    d = data['locale'].split('_')
    if len(d) != 2:
        raise Http404
    language = d[0]
    region = d[1]
    #First try with locale
    message = models.Message.objects.filter(
            block_id = data['block_id']
        ).filter(
            full_locale = data['locale']
        )
    message = list(message)
    #Else try with language
    if len(message) > 0:
        result = _prepare_message(message)
        return JsonResponse(result)
    if not message:
        message = models.Message.objects.filter(
                block_id = data['block_id']
            ).filter(
                language = language
            )
    message = list(message)
    #Else default to english
    if len(message) > 0:
        result = _prepare_message(message)
        return JsonResponse(result)
    if not message:
        message = models.Message.objects.filter(
                block_id = data['block_id']
            ).filter(
                language = 'en'
            )
    message = list(message)
    if len(message) > 0:
        result = _prepare_message(message)
        return JsonResponse(result)
    if not message:
        message = 'Error - No block found in english for block_id %s and locale %s.' % (data['block_id'],
        data['locale'])
    return JsonResponse(dict(messages=[dict(text=message)]))
