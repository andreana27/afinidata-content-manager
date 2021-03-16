from .models import AttributeValue, Instance
from rest_framework import serializers
from attributes.serializers import AttributeSerializer

class InstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instance
        fields = '__all__'


class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = '__all__'

class AttributeValueListSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(read_only=True, many=False)

    class Meta:
        model = AttributeValue
        fields = ('id','value','attribute','instance')
