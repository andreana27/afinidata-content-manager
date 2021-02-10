from .models import AttributeValue
from rest_framework import serializers


class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        exclude = ['created_at']
