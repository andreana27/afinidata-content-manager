from django.db.models import Q
from rest_framework import filters
from instances import models, serializers
from rest_framework import viewsets, permissions, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters

class InstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Instance.objects.all()
    serializer_class = serializers.InstanceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=id','name']

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

    @action(methods=['POST'], detail=False)
    def advance_search(self, request):
        queryset = models.Instance.objects.order_by('-id').all()
        filtros = request.data['filtros']
        apply_filters = Q()
        next_connector = None

        for idx, f in enumerate(filtros):
            #attribute
            if f['search_by'] == 'attribute':
                field_name = 'attributevalue__value'

            # TODO: segment
            # TODO: blocks
            # TODO: sequence

            if f['condition'] == 'is':
                query_search = Q(**{f"{field_name}__icontains": f["data_value"]})
            elif f['condition'] == 'is_not':
                query_search = ~Q(**{f"{field_name}__icontains": f["data_value"]})
            elif f['condition'] == 'startswith':
                query_search = Q(**{f"{field_name}__startswith": f["data_value"]})
            elif f['condition'] == 'gt':
                query_search = Q(**{f"{field_name}__gt": f["data_value"]})
            elif f['condition'] == 'lt':
                query_search = Q(**{f"{field_name}__lt": f["data_value"]})

            if next_connector is None:
                apply_filters = Q(attributes__id=f['data_key']) & query_search
            else:
                if next_connector == 'and':
                    apply_filters &= Q(attributes__id=f['data_key']) & query_search
                else:
                    apply_filters |= Q(attributes__id=f['data_key']) & query_search

            next_connector = f['connector']

        queryset = queryset.filter(apply_filters)
        pagination = PageNumberPagination()
        qs = pagination.paginate_queryset(queryset, request)
        serializer = serializers.InstanceSerializer(qs, many=True)
        return pagination.get_paginated_response(serializer.data)

class InstancesAttributeViewSet(viewsets.ModelViewSet):
    queryset = models.AttributeValue.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ("$attribute__name","$value")

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.AttributeValueListSerializer

        return serializers.AttributeValueSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        if self.request.query_params.get('attribute_id'):
            return qs.filter(attribute_id=self.request.query_params.get('attribute_id'))

        if self.request.query_params.get('instance_id'):
            return qs.filter(instance_id=self.request.query_params.get('instance_id'))

        return qs
