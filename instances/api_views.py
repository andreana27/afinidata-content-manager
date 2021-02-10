from rest_framework import viewsets, permissions
from instances import models, serializers
from django.utils.decorators import method_decorator


class InstancesAttributeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.AttributeValue.objects.all()
    serializer_class = serializers.AttributeValueSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        if self.request.query_params.get('attribute_id'):
            return qs.filter(attribute_id=self.request.query_params.get('attribute_id'))

        return qs

    def list(self, request, *args, **kwargs):
        return super(InstancesAttributeViewSet, self).list(request, *args, **kwargs)
