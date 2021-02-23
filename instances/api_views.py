from django.db.models import Q
from rest_framework import filters
from instances import models, serializers
from rest_framework import viewsets, permissions
from django.utils.decorators import method_decorator

class InstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Instance.objects.all()
    serializer_class = serializers.InstanceSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        if self.request.query_params.get('user_id'):
            instances = models.InstanceAssociationUser.objects.values_list('instance', flat=True).all().filter(
                user=self.request.query_params.get('user_id'))

            if not instances:
                return []

            return qs.filter(id__in=instances)

        return qs

class InstancesAttributeViewSet(viewsets.ModelViewSet):
    queryset = models.AttributeValue.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ("$attribute__name","$value")

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.AttributeValueListSerializer

        return serializers.AttributeValueSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        if self.request.query_params.get('attribute_id'):
            return qs.filter(attribute_id=self.request.query_params.get('attribute_id'))

        if self.request.query_params.get('instance_id'):
            return qs.filter(instance_id=self.request.query_params.get('instance_id'))

        return qs
