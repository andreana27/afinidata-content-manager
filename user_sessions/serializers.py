from rest_framework import serializers
from sessions.models import Session


class SessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Session
        fields = ['id', 'name']
