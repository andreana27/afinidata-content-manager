from rest_framework import serializers
from bots.models import Interaction, UserInteraction


class InteractionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interaction
        fields = ['id', 'name', 'description']


class UserInteractionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserInteraction
        fields = ['id','interaction', 'bot_id', 'user', 'value', 'created_at', 'updated_at']


