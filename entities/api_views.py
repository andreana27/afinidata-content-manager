from rest_framework import viewsets, permissions
from entities import models, serializers
from attributes import models as modelAttribute
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from attributes import serializers as attrSerializers
from .paginations import LimitOffsetPagination
from django_filters import rest_framework as filters
from .filters import EntityFilter

class EntityViewSet(viewsets.ModelViewSet):

    queryset = models.Entity.objects.all()
    serializer_class = serializers.EntitySerializer
    pagination_class = LimitOffsetPagination
    filterset_class = EntityFilter

    def create(self, request, *args, **kwargs):
        data = request.data

        new_entity = models.Entity.objects.create(name=data["name"], description=data["description"])
        new_entity.save()

        for attribute in data["attributes"]:
            attribute_obj = modelAttribute.Attribute.objects.get(name=attribute["name"])
            new_entity.attributes.add(attribute_obj)

        serializer = serializers.EntitySerializer(new_entity)

        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        return super(EntityViewSet, self).list(request, *args, **kwargs)
    
    def update(self, request, pk=None):

        name = self.request.data.get("name")
        description = self.request.data.get("description")
        attributes = self.request.data.get("attributes")

        update_entity = self.get_object()

        if name is not None:
            update_entity.name = name

        if description is not None:
            update_entity.description = description

        update_entity.attributes.set([])

        update_entity.save()

        if attributes is not None:
            for attribute in attributes:
                attribute_obj = modelAttribute.Attribute.objects.get(id=attribute["id"]) 
                update_entity.attributes.add(attribute_obj)

        update_entity.save()

        serializer_context = {
            'request': request,
        }

        serializer = serializers.EntitySerializer(instance=update_entity,context=serializer_context)
        return Response(serializer.data)