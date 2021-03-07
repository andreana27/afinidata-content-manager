from django.db.models import Q
from rest_framework import filters
from instances import models, serializers
from rest_framework import viewsets, permissions, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from messenger_users.models import User

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

    def apply_filter_to_search(self, field, value, condition):
        if condition == 'is':
            query_search = Q(**{f"{field}__icontains": value})
        elif condition == 'is_not':
            query_search = ~Q(**{f"{field}__icontains": value})
        elif condition == 'startswith':
            query_search = Q(**{f"{field}__startswith": value})
        elif condition == 'gt':
            query_search = Q(**{f"{field}__gt": value})
        elif condition == 'lt':
            query_search = Q(**{f"{field}__lt": value})
        return query_search

    def apply_connector_to_search(self, connector, filters, query):
        if connector is None:
            filters = query
        else:
            if connector == 'and':
                filters &= query
            else:
                filters |= query

        return filters

    @action(methods=['POST'], detail=False)
    def advance_search(self, request):
        queryset = models.Instance.objects.order_by('-id').all()
        filtros = request.data['filtros']
        apply_filters = Q()
        next_connector = None
        users = []

        for idx, f in enumerate(filtros):
            data_key = f['data_key']
            value = f['data_value']
            condition = f['condition']
            search_by = f['search_by']

            # TODO: validar si son attributes de instances o de users
            check_attribute_type = 'USER'

            if search_by == 'attribute':
                if check_attribute_type == 'USER':
                    user_filter = Q()
                    qs = User.objects.all().order_by('-id')
                    query = self.apply_filter_to_search('userdata__data_value', value, condition)
                    search = Q(userdata__attribute_id=data_key) & query
                    user_filter = self.apply_connector_to_search(next_connector, user_filter, search)
                    qs = qs.filter(user_filter).values_list('id',flat=True)

                    [users.append(x) for x in qs if x not in users]
                else:
                    query_search = self.apply_filter_to_search('attributevalue__value',value, condition)
                    query = Q(attributes__id=data_key) & query_search
                    apply_filters = self.apply_connector_to_search(next_connector, apply_filters, query)

            next_connector = f['connector']

        if request.query_params.get("search"):
            filter_search = Q()
            params = ['id','name']

            for x in params:
                filter_search |= Q(**{f"{x}__icontains": self.request.query_params.get('search')})
            queryset = queryset.filter(filter_search)

        queryset = queryset.filter(apply_filters)

        if len(users) > 0:
            queryset = queryset.filter(instanceassociationuser__user_id__in=users)

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
