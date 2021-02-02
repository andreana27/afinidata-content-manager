from rest_framework import serializers
from user_sessions.models import Session


class SessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Session
        fields = ['id', 'name']
