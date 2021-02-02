from rest_framework import viewsets, permissions
from attributes import models, serializers
from django.utils.decorators import method_decorator


class AttributeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Attribute.objects.all()
    serializer_class = serializers.AttributeSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))
        return qs

    def list(self, request, *args, **kwargs):
        return super(AttributeViewSet, self).list(request, *args, **kwargs)
