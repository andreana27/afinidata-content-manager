from django.db.models import Q
from rest_framework import filters
from instances import models, serializers
from rest_framework import viewsets
from rest_framework.decorators import action
# from rest_framework.response import Response
# from django.utils.decorators import method_decorator
from rest_framework.pagination import PageNumberPagination
# from rest_framework import filters
from messenger_users.models import User
from groups.models import ProgramAssignation, AssignationMessengerUser
from attributes.models import Attribute
from datetime import datetime, timedelta, time

from instances.models import AttributeValue


class InstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Instance.objects.all()
    serializer_class = serializers.InstanceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=id', 'name']

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

    @action(methods=['GET'], detail=True)
    def get_possible_values(self, request, pk=None):
        queryset = AttributeValue.objects.filter(attribute_id=pk).values('value').distinct()
        pagination = PageNumberPagination()
        pagination.page_size = 10
        pagination.page_query_param = 'pagenumber'
        qs = pagination.paginate_queryset(queryset, request)
        serializer = serializers.AttributeValueFilterPosibleVal(qs, many=True)
        return pagination.get_paginated_response(serializer.data)

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
        queryset = super().get_queryset()
        filtros = request.data['filtros']
        apply_filters = Q()
        next_connector = None

        for idx, f in enumerate(filtros):
            data_key = f['data_key']
            value = f['data_value']
            condition = f['condition']
            search_by = f['search_by']
            check_attribute_type = 'INSTANCE'

            if search_by == 'attribute':
                attribute = Attribute.objects.get(pk=data_key)

                # check if attribute belongs to user o instance
                if attribute.entity_set.filter(id__in=[4, 5]).exists():
                    check_attribute_type = 'USER'

                if condition == 'is_set' or condition == 'not_set':
                    if condition == 'is_set':
                        # validar is set attribute
                        if check_attribute_type == 'USER':
                            users = User.objects.filter(Q(userdata__attribute_id=data_key))
                            q = Q(instanceassociationuser__user_id__in=users)
                            apply_filters = self.apply_connector_to_search(next_connector, apply_filters, q)
                        else:
                            q = Q(attributevalue__attribute_id=data_key)
                            apply_filters = self.apply_connector_to_search(next_connector, apply_filters, q)

                    if condition == 'not_set':
                        # validar not set attribute
                        if check_attribute_type == 'USER':
                            users = User.objects.filter(~Q(userdata__attribute_id=data_key))
                            q = Q(instanceassociationuser__user_id__in=users)
                            apply_filters = self.apply_connector_to_search(next_connector, apply_filters, q)
                        else:
                            q = ~Q(attributevalue__attribute_id=data_key)
                            apply_filters = self.apply_connector_to_search(next_connector, apply_filters, q)
                else:
                    if check_attribute_type == 'USER':
                        # filter by attribute user
                        s = self.apply_filter_to_search('userdata__data_value', value, condition)
                        qs = User.objects.filter(s)  # .values_list('id',flat=True)
                        query = Q(instanceassociationuser__user_id__in=qs)
                        apply_filters = self.apply_connector_to_search(next_connector, apply_filters, query)
                    else:
                        # filter by attribute instance
                        query_search = self.apply_filter_to_search('attributevalue__value', value, condition)
                        query = Q(attributes__id=data_key) & query_search
                        apply_filters = self.apply_connector_to_search(next_connector, apply_filters, query)

            elif search_by == 'program':
                # filter by program
                s = self.apply_filter_to_search('program__id', value, condition)
                qs = ProgramAssignation.objects.filter(s).values_list('user_id', flat=True).exclude(user_id__isnull=True)
                query = Q(instanceassociationuser__user_id__in=list(qs))
                apply_filters = self.apply_connector_to_search(next_connector, apply_filters, query)

            elif search_by == 'channel':
                # filter by channel
                s = self.apply_filter_to_search('channel_id', value, condition)
                qs = User.objects.filter(s).order_by('-id').values_list('id', flat=True)
                query = Q(instanceassociationuser__user_id__in=list(qs))
                apply_filters = self.apply_connector_to_search(next_connector, apply_filters, query)

            elif search_by == 'group':
                # filter by group
                s = self.apply_filter_to_search('group__id', value, condition)
                qs = AssignationMessengerUser.objects.filter(s).values_list('user_id', flat=True).exclude(user_id__isnull=True).distinct()
                query_group = Q(instanceassociationuser__user_id__in=list(qs))
                apply_filters = self.apply_connector_to_search(next_connector, apply_filters, query_group)

            elif search_by == 'dates':
                # filter by dates
                date_from = datetime.combine(datetime.strptime(f['date_from'], '%Y-%m-%d'), time.min) - timedelta(days=1)
                date_to = datetime.combine(datetime.strptime(f['date_to'], '%Y-%m-%d'), time.max) - timedelta(days=1)
                if date_from and date_to:
                    if data_key == 'created_at':
                        queryset = queryset.filter(created_at__gte=date_from, created_at__lte=date_to)

            next_connector = f['connector']

        if request.query_params.get("search"):
            # string search on datatable
            filter_search = Q()
            params = ['id', 'name']

            for x in params:
                filter_search |= Q(**{f"{x}__icontains": self.request.query_params.get('search')})
            queryset = queryset.filter(filter_search)

        queryset = queryset.filter(apply_filters)
        pagination = PageNumberPagination()
        qs = pagination.paginate_queryset(queryset, request)
        serializer = serializers.InstanceSerializer(qs, many=True)
        return pagination.get_paginated_response(serializer.data)


class InstancesAttributeViewSet(viewsets.ModelViewSet):
    queryset = models.AttributeValue.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ("$attribute__name", "$value")

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
