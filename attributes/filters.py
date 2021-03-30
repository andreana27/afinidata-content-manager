from django_filters import rest_framework as filters
from entities.models import Attribute

class AttrFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Attribute
        fields = ('name',)