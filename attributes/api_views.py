from rest_framework import viewsets, permissions
from attributes import models, serializers
from utilities.permission_decorator import validates_permission
from django.utils.decorators import method_decorator


class AttributeViewSet(viewsets.ModelViewSet):
    queryset = models.Attribute.objects.all()
    serializer_class = serializers.AttributeSerializer

    def list(self, request, *args, **kwargs):
        return super(AttributeViewSet, self).list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super(AttributeViewSet, self).update(request, *args, **kwargs)
