from rest_framework import viewsets, permissions, filters
from posts import models, serializers
from django.utils.decorators import method_decorator
from django.db.models import Q


class AreaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Area.objects.all().order_by('-id')
    serializer_class = serializers.AreaSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('id', 'name')
    ordering_fields = ['id', 'name']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))
        
        return qs


class MaterialesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Materiales.objects.all().order_by('-id')
    serializer_class = serializers.MaterialesSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('id', 'name')
    ordering_fields = ['id', 'name']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))
        
        return qs





