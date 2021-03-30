from django_filters import rest_framework as filters
from entities.models import Entity

class EntityFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Entity
        fields = ('name','description')