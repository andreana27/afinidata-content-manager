from rest_framework import serializers
from programs.models import Program, AttributeType, Attributes
from attributes.models import Attribute
from entities.models import Entity


class AttributesSerializer(serializers.ModelSerializer):

    attribute = serializers.PrimaryKeyRelatedField(queryset=Attribute.objects.all())
    attribute_type = serializers.PrimaryKeyRelatedField(queryset=AttributeType.objects.all())

    class Meta:
        model = Attributes
        fields = ['id', 'attribute', 'attribute_type', 'weight', 'threshold', 'label', 'created_at', 'updated_at']
        depth = 2


class AttributeTypeSerializer(serializers.ModelSerializer):

    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all())
    entity = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all())
    attributes_set = AttributesSerializer(read_only=True, many=True)

    class Meta:
        model = Attributes
        fields = ['id', 'program', 'entity', 'name', 'description', 'weight', 'attributes_set', 'created_at', 'updated_at']
        depth = 1


class ProgramSerializer(serializers.ModelSerializer):

    attribute_type_set = AttributesSerializer(read_only=True, many=True)

    class Meta:
        model = Program
        fields = ['id', 'name', 'description', 'attribute_type_set', 'created_at', 'updated_at']
