from rest_framework import viewsets, permissions
from entities import models, serializers
from django.utils.decorators import method_decorator


class EntityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Entity.objects.all()
    serializer_class = serializers.EntitySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))
        return qs

    def list(self, request, *args, **kwargs):
        return super(EntityViewSet, self).list(request, *args, **kwargs)
