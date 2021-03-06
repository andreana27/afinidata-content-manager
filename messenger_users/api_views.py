import logging
from django.db.models import Q
from rest_framework import filters
from rest_framework import viewsets, permissions
from messenger_users import models, serializers
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from instances.models import Instance
from groups.models import ProgramAssignation, AssignationMessengerUser

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=id','username','first_name','last_name','=bot_id','=channel_id']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

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

    @action(methods=['POST'], detail=False)
    def advance_search(self, request):
        queryset = models.User.objects.order_by('-id').all()
        filtros = request.data['filtros']
        apply_filters = Q()
        next_connector = None
        instances = []

        for idx, f in enumerate(filtros):
            # TODO: validar si son attributes de instances o de users
            check_attribute_type = 'USER'
            data_key = f['data_key']
            value = f['data_value']
            condition = f['condition']

            if f['search_by'] == 'attribute':
                if check_attribute_type == 'INSTANCE':
                    # filter by attribute instance
                    instance_filter = Q()
                    qs = Instance.objects.order_by('-id').all()
                    query_search = self.apply_filter_to_search('attributevalue__value', value, condition)

                    if next_connector is None:
                        instance_filter = Q(attributes__id=data_key) & query_search
                    else:
                        if next_connector == 'and':
                            instance_filter &= Q(attributes__id=data_key) & query_search
                        else:
                            instance_filter |= Q(attributes__id=data_key) & query_search

                    qs = qs.filter(instance_filter).values_list('id',flat=True)

                    for x in qs:
                        if x not in instances:
                            instances.append(x)
                else:
                    # filter by attribute user
                    query_search = self.apply_filter_to_search('userdata__data_value',value, condition)

                    if next_connector is None:
                        apply_filters = Q(userdata__attribute_id=data_key) & query_search
                    else:
                        if next_connector == 'and':
                            apply_filters &= Q(userdata__attribute_id=data_key) & query_search
                        else:
                            apply_filters |= Q(userdata__attribute_id=data_key) & query_search

            elif f['search_by'] == 'program':
                # filter by program
                programs_users = ProgramAssignation.objects.filter(program=value).values_list('user_id',flat=True).exclude(user_id__isnull=True)
                query_program = Q(id__in=programs_users)

                if next_connector is None:
                    apply_filters = query_program
                else:
                    if next_connector == 'and':
                        apply_filters &= query_program
                    else:
                        apply_filters |= query_program

            elif f['search_by'] == 'channel':
                # filter by channel
                query_channel = Q(channel_id=value)

                if next_connector is None:
                    apply_filters = query_channel
                else:
                    if next_connector == 'and':
                        apply_filters &= query_channel
                    else:
                        apply_filters |= query_channel

            elif f['search_by'] == 'group':
                # filter by group
                groups_users = AssignationMessengerUser.objects.filter(group=value).values_list('user_id', flat=True).exclude(user_id__isnull=True).distinct()
                query_group = Q(id__in=groups_users)

                if next_connector is None:
                    apply_filters = query_group
                else:
                    if next_connector == 'and':
                        apply_filters &= query_group
                    else:
                        apply_filters |= query_group

            next_connector = f['connector']

        if request.query_params.get("search"):
            filter_search = Q()
            params = ['id','username','first_name','last_name','bot_id','channel_id']

            for x in params:
                filter_search |= Q(**{f"{x}__icontains": self.request.query_params.get('search')})
            queryset = queryset.filter(filter_search)

        queryset = queryset.filter(apply_filters)
        if len(instances) > 0:
            queryset = queryset.filter(instanceassociationuser__in=instances)

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
