from django.shortcuts import render
from messenger_users.models import User, UserData
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from messenger_users.forms import CreateUserFormModel
import random
import string
import logging

logger = logging.getLogger(__name__)

## FIXME: convert to django rest views.

'''Creates user from a request.'''
@csrf_exempt
def new_user(request):

    if request.method == 'POST':

        ### TODO: Split in functions, should not be named new_user smth like refresh session (?)

        found_user = None
        try:
            found_user = User.objects.get(last_channel_id=request.POST['messenger user id'])
            logger.info('user id found')
        except:
            logger.error('user could not be found from messenger user id')

        if found_user:
            return JsonResponse(dict(
                            set_attributes=dict(
                                hasLoggedIn=True
                            ),
                            messages=[]
                        ))

        else:
            logger.info('Creating New User')
            user = dict(bot_id=None, last_channel_id=None, backup_key=None)
            user['last_channel_id'] = request.POST['messenger user id']
            text = "".join([random.choice(string.ascii_letters) for i in list(range(10))]) # Should either be a friendlier "random-ish" str or a shorter hash.
            user['backup_key'] = request.POST['parentName'] + request.POST['parentLastname'] + '.' + text
            user['bot_id'] = request.POST['bot_id']
            user_to_save = User(**user)
            user_to_save.save()

            user_to_update = User.objects.filter(last_channel_id=request.POST['messenger user id'])
            user_to_update.update(username=request.POST['parentName'] + str(user_to_save.pk))

            UserData.objects.create(user=user_to_save, data_key='parentName', data_value=request.POST['parentName'])
            UserData.objects.create(user=user_to_save, data_key='parentLastname', data_value=request.POST['parentLastname'])
            UserData.objects.create(user=user_to_save, data_key='channel_first_name', data_value=request.POST['first name'])
            UserData.objects.create(user=user_to_save, data_key='channel_last_name', data_value=request.POST['last name'])

            return JsonResponse(dict(
                            set_attributes=dict(
                                username=request.POST['parentName'] + str(user_to_save.pk),
                                backup_key=user['backup_key'],
                                user_id=user_to_save.pk
                            ),
                            messages=[]
                        ))
    else:
        logger.error("New user only POST valid.")
        raise Http404('Not auth')


@csrf_exempt
def add_attribute(request, channel_id):

    users = User.objects.filter(channel_id=channel_id)
    user = None
    if users:
        user = users[0]
    else:
        users = User.objects.filter(last_channel_id=channel_id)
        if users:
            user = users[0]

    if request.method == 'POST':
        if not user:
            return JsonResponse(dict(status="error", error="User not exists with channel id: {}".format(channel_id)))
        else:
            results = []
            for param in request.POST:
                UserData.objects.create(
                    user=user,
                    data_key=str(param),
                    data_value=str(request.POST[param])
                )
                results.append(dict(attribute=param, value=request.POST[param]))
            print(request.POST)
            return JsonResponse(dict(status="finished", data=dict(user_id=user.pk, added_attributes=results)))
    else:
        return JsonResponse(dict(hello='world'))


@csrf_exempt
def by_username(request, username):
    print(username)
    if request.method == 'POST':
        return JsonResponse(dict(status='error', error='Invalid method'))
    else:
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            logger.error("No username")
            return JsonResponse(dict(status='error', error=str(e)))

        return JsonResponse(dict(
                                set_attributes=dict(
                                    user_id=user.pk
                                ),
                                messages=[]
                            ))
