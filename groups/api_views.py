from django.db.models import Q
from rest_framework import filters
from rest_framework import viewsets, permissions
from groups import models, serializers
from django.utils.decorators import method_decorator


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Group.objects.all().order_by('id')
    serializer_class = serializers.GroupSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))
       
        if self.request.query_params.get('search'):
            search = self.request.query_params.get('search')
            qs = qs.filter(
                Q(id__icontains=search) | 
                Q(name__icontains=search)
            )

        return qs

