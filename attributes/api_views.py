from rest_framework import viewsets, permissions
from attributes import models, serializers
from django.utils.decorators import method_decorator
from entities.models import Entity
from instances.models import Instance
from messenger_users.models import User


class AttributeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Attribute.objects.all()
    serializer_class = serializers.AttributeSerializer

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

        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        return qs

    def list(self, request, *args, **kwargs):
        return super(AttributeViewSet, self).list(request, *args, **kwargs)
