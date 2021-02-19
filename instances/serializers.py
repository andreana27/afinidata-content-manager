from .models import AttributeValue, Instance
from rest_framework import serializers
from attributes.serializers import AttributeSerializer


class InstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instance
        exclude = ['created_at']


class AttributeValueSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(read_only=False, many=False)

    class Meta:
        model = AttributeValue
        exclude = ['created_at']
