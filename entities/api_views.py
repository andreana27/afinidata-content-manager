import json

from django_filters import rest_framework as filters
from django.utils.decorators import method_decorator
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import api_view

from entities import models, serializers
from attributes import models as modelAttribute
from attributes import serializers as attrSerializers
from .paginations import LimitOffsetPagination
from .filters import EntityFilter


class EntityViewSet(viewsets.ModelViewSet):
    queryset = models.Entity.objects.all().order_by('-id')
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

    @action(methods=['POST'], detail=False, url_path='add_attributes', url_name='add_attributes')
    def add_attributes(self, request, *args, **kwgars):
        try:
            if len(request.POST) > 0:
                data = request.POST
            else:
                data = json.loads(request.body)

            if not data:
                return Response(dict(request_status=500, request_error='Invalid parameters'))

            for entry in data:
                entity = self.queryset.filter(id=entry['entity'])
                if entity.exists():
                    entity = entity.last()
                    for attribute_id in entry['attributes']:
                        attribute = modelAttribute.Attribute.objects.filter(id=attribute_id)
                        if attribute.exists():
                            entity.attributes.add(attribute.last())
                
            return Response(dict(request_status=200))
        except Exception as err:
            return Response(dict(request_status=500, request_error=str(err)))

