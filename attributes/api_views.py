from rest_framework import viewsets, permissions
from attributes import models, serializers
from django.utils.decorators import method_decorator
from entities.models import Entity
from instances.models import Instance
from attributes import models as modelAttribute
from messenger_users.models import User
from rest_framework.response import Response
from .paginations import LimitOffsetPagination
from rest_framework.decorators import action
from attributes import serializers as attrSerializers
from .filters import AttrFilter

class AttributeViewSet(viewsets.ModelViewSet):

    queryset = models.Attribute.objects.all()
    serializer_class = serializers.AttributeSerializer
    pagination_class = LimitOffsetPagination
    filterset_class = AttrFilter

    def paginate_queryset(self, queryset, view=None):

        if self.request.query_params.get('pagination') == 'off':
            return None

        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_queryset(self):

        qs = super().get_queryset()

        if (self.request.query_params.get('id') and self.request.query_params.get('type')
        and self.request.query_params.get('type') in ['user', 'instance']):

            t_type = Instance if self.request.query_params.get('type') == 'instance' else User
            target = t_type.objects.get(id = self.request.query_params.get('id'))

            if not target or not target.entity:
                return []

            attribute_ids = Entity.objects.values_list('attributes', flat=True).filter(id = target.entity.id)
            return qs.filter(id__in = attribute_ids)

        if self.request.query_params.get('attribute_type'):
            return qs.filter(type=self.request.query_params.get('attribute_type'))

        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        return qs

    def list(self, request, *args, **kwargs):
        return super(AttributeViewSet, self).list(request, *args, **kwargs)

    def update(self, request, pk=None):

        name = self.request.data.get("name")
        type = self.request.data.get("type")
        attribute_view = self.request.data.get("attribute_view")

        update_attr = self.get_object()

        update_attr.name = name
        update_attr.type = type
        update_attr.attribute_view = attribute_view

        update_attr.save()

        serializer_context = {
            'request': request,
        }

        serializer = serializers.AttributeSerializer(instance=update_attr,context=serializer_context)
        return Response(serializer.data)
