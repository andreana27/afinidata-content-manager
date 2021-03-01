from django.db.models import Q
from rest_framework import viewsets, permissions, filters
from groups import models, serializers
from django.utils.decorators import method_decorator


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Group.objects.all().order_by('id')
    serializer_class = serializers.GroupSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('id', 'name')
    ordering_fields = ['id', 'name']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        return qs

