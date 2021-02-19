from rest_framework import viewsets, permissions
from instances import models, serializers
from django.utils.decorators import method_decorator
from django.db.models import Q


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
    serializer_class = serializers.AttributeValueSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        if self.request.query_params.get('attribute_id'):
            return qs.filter(attribute_id=self.request.query_params.get('attribute_id'))

        if self.request.query_params.get('instance_id'):
            return qs.filter(instance_id=self.request.query_params.get('instance_id'))

        if self.request.query_params.get('attribute_value') or self.request.query_params.get('attribute_name'):

            a_name = self.request.query_params.get('attribute_name')
            a_value = self.request.query_params.get('attribute_value')

            filter_by = Q( attribute__name__contains = a_name ) if a_name else False
            if a_value:
                filter_by = filter_by & Q( value__contains = a_value ) if filter_by else Q( value__contains = a_value )
            
            return qs.filter(filter_by)

        return qs
