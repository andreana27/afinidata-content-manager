import logging
from django.db.models import Q, Exists
from rest_framework import filters
from rest_framework import viewsets, permissions
from messenger_users import models, serializers
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from instances.models import Instance
from groups.models import ProgramAssignation, AssignationMessengerUser
from programs.models import Program
from attributes.models import Attribute
from datetime import datetime, timedelta, time


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.User.objects.all().order_by('-id')
    serializer_class = serializers.UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=id','username','first_name','last_name','=bot_id','=channel_id','$created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        return qs

    def apply_filter_to_search(self, field, value, condition):
        # apply condition to search
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
        # apply connector & or | to search
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
                # check if attribute belongs to user o instance
                attribute = Attribute.objects.get(pk=data_key)

                if attribute.entity_set.filter(id__in=[4,5]).exists():
                    check_attribute_type = 'USER'

                if condition == 'is_set' or condition == 'not_set':
                    if check_attribute_type == 'USER':
                        if condition == 'is_set':
                            # validar is set attribute
                            q = Q(userdata__attribute_id=data_key)
                            apply_filters = self.apply_connector_to_search(next_connector, apply_filters, q)

                        if condition == 'not_set':
                            # validar not set attribute
                            q = ~Q(userdata__attribute_id=data_key)
                            apply_filters = self.apply_connector_to_search(next_connector, apply_filters, q)
                    else:
                        if condition == 'is_set':
                            instances = Instance.objects.filter(Q(attributevalue__attribute_id=data_key))

                        if condition == 'not_set':
                            instances = Instance.objects.filter(~Q(attributevalue__attribute_id=data_key))

                        q = Q(instanceassociationuser__instance_id__in=instances)
                        apply_filters = self.apply_connector_to_search(next_connector, apply_filters, q)

                else:
                    if check_attribute_type == 'INSTANCE':
                        # filter by attribute instance
                        s = Q(attributes__id=data_key) & self.apply_filter_to_search('attributevalue__value',value,condition)
                        qs = Instance.objects.filter(s) #.values_list('id', flat=True)
                        query = Q(instanceassociationuser__instance_id__in=qs)
                        apply_filters = self.apply_connector_to_search(next_connector, apply_filters, query)
                    else:
                        # filter by attribute user
                        query_search = self.apply_filter_to_search('userdata__data_value',value, condition)
                        query_attr_user = Q(userdata__attribute_id=data_key) & query_search
                        apply_filters = self.apply_connector_to_search(next_connector, apply_filters, query_attr_user)


            elif search_by == 'program':
                # filter by program
                s = self.apply_filter_to_search('id',value, condition)
                programs = Program.objects.filter( s ).values_list('id')

                program_assignation = ProgramAssignation.objects.filter(
                    program_id__in=list(programs)
                ).values_list('group_id')

                users = AssignationMessengerUser.objects.filter(
                    group_id__in=list(program_assignation)
                )
                query = Q(id__in=users)
                apply_filters = self.apply_connector_to_search(next_connector, apply_filters, query)

            elif search_by == 'channel':
                # filter by channel
                s = self.apply_filter_to_search('channel_id',value, condition)
                query = Q(s)
                apply_filters = self.apply_connector_to_search(next_connector, apply_filters, query)

            elif search_by == 'group':
                # filter by group
                s = self.apply_filter_to_search('group__id',value, condition)
                qs = AssignationMessengerUser.objects.filter(s).values_list('user_id', flat=True).exclude(user_id__isnull=True).distinct()
                query = Q(id__in=qs)
                apply_filters = self.apply_connector_to_search(next_connector, apply_filters, query)

            elif search_by == 'dates':
                date_from = datetime.combine(datetime.strptime(f['date_from'],'%Y-%m-%d'), time.min)
                date_to = datetime.combine(datetime.strptime(f['date_to'],'%Y-%m-%d'), time.max)

                if date_from and date_to:
                    if data_key == 'created_at':
                        queryset = queryset.filter(created_at__gte=date_from,created_at__lte=date_to)

                    if data_key == 'last_seen':
                        queryset = queryset.filter(last_seen__gte=date_from, last_seen__lte=date_to)

            next_connector = f['connector']

        if request.query_params.get("search"):
            # search by queryparams
            filter_search = Q()
            params = ['id','username','first_name','last_name','bot_id','channel_id','created_at']

            for x in params:
                filter_search |= Q(**{f"{x}__icontains": self.request.query_params.get('search')})

            queryset = queryset.filter(filter_search)

        queryset = queryset.filter(apply_filters)
        print(queryset.query)
        pagination = PageNumberPagination()
        qs = pagination.paginate_queryset(queryset, request)
        serializer = serializers.UserSerializer(qs, many=True)
        return pagination.get_paginated_response(serializer.data)

class UserDataViewSet(viewsets.ModelViewSet):
    queryset = models.UserData.objects.all()
    serializer_class = serializers.UserDataSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ("$data_key", "$data_value")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        if self.request.query_params.get('user_id'):
            return qs.filter(user_id=self.request.query_params.get('user_id'))

        if self.request.query_params.get('attribute_id'):
            return qs.filter(attribute_id=self.request.query_params.get('attribute_id'))

        return qs
