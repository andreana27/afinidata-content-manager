from rest_framework import serializers
from entities.models import Entity


class EntitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Entity
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
