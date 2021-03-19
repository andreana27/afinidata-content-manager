from .models import UserData, User, Child, ChildData
from rest_framework import serializers
import requests
import os


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        # exclude = ['created_at']


class UserConversationSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField('get_profile_pic')
    last_message = serializers.SerializerMethodField('get_last_message')
    bot_id = serializers.SerializerMethodField('get_bot_id')
    bot_channel_id = serializers.SerializerMethodField('get_bot_channel_id')
    user_channel_id = serializers.SerializerMethodField('get_user_channel_id')

    def get_profile_pic(self, obj):
        pictures = obj.userdata_set.filter(attribute__name='profile_pic')
        if pictures.exists():
            profile_pic = pictures.last().data_value
        else:
            return ''
        return profile_pic

    def get_last_message(self, obj):
        user_channels = obj.userchannel_set.all()
        last_message = 'Sin mensajes del webhook'
        if user_channels.exists():
            bot_id = user_channels.last().bot_id
            bot_channel_id = user_channels.last().bot_channel_id
            user_channel_id = user_channels.last().user_channel_id
            WEBHOOK_URL = os.getenv("WEBHOOK_DOMAIN_URL")
            response = requests.get('%s/bots/%s/channel/%s/get_conversation/?user_channel_id=%s' %
                                    (WEBHOOK_URL, bot_id, bot_channel_id, user_channel_id))
            if response.status_code == 200:
                data = response.json()['data']
                if len(data) > 0:
                    last_message = data[0]['content']
                else:
                    last_message = ''
        return last_message

    def get_bot_id(self, obj):
        user_channels = obj.userchannel_set.all()
        if user_channels.exists():
            bot_id = user_channels.last().bot_id
        else:
            return ''
        return bot_id

    def get_bot_channel_id(self, obj):
        user_channels = obj.userchannel_set.all()
        if user_channels.exists():
            bot_channel_id = user_channels.last().bot_channel_id
        else:
            return ''
        return bot_channel_id

    def get_user_channel_id(self, obj):
        user_channels = obj.userchannel_set.all()
        if user_channels.exists():
            user_channel_id = user_channels.last().user_channel_id
        else:
            return ''
        return user_channel_id

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'last_seen',
                  'user_channel_id', 'bot_channel_id', 'bot_id', 'profile_pic', 'last_message']


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        exclude = ['created']


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        exclude = ['created']


class ChildDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChildData
        exclude = ['timestamp']
