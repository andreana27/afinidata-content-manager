from .models import AttributeValue, Instance
from rest_framework import serializers


class InstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instance
        exclude = ['created_at']


class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        exclude = ['created_at']
