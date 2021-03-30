from rest_framework import serializers
from user_sessions.models import Session, BotSessions


class SessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Session
        fields = ['id', 'name']


class BotSessionsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BotSessions
        fields = ['id', 'session_id', 'bot_id', 'session_type']

        