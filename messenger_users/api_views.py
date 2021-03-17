from django.db.models import Q, Exists
from django.utils.decorators import method_decorator
from rest_framework import filters
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from messenger_users import models, serializers
from instances.models import Instance
from groups.models import ProgramAssignation, AssignationMessengerUser
from programs.models import Program
from attributes.models import Attribute
from datetime import datetime, timedelta, time
import re


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.User.objects.all().order_by('-id')
    serializer_class = serializers.UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=id', 'username', 'first_name', 'last_name', '=bot_id', '=channel_id', '$created_at']

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

    def apply_connector_to_search(self, connector, queryset, query):
        # apply connector & or | to search
        if connector is None:
            queryset = query
        else:
            if connector == 'and':
                queryset = queryset & query
            else:
                queryset = queryset | query
        return queryset

    @action(methods=['POST'], detail=False)
    def advance_search(self, request):
        filtros = request.data['filtros']
        next_connector = None
        date_filter = Q()
        filter_search = Q()
        queryset = models.User.objects.all()

        for idx, f in enumerate(filtros):
            data_key = f['data_key']
            value = f['data_value']
            condition = f['condition']
            search_by = f['search_by']
            check_attribute_type = 'INSTANCE'

            if search_by == 'attribute':
                # check if attribute belongs to user o instance
                attribute = Attribute.objects.get(pk=data_key)

                if attribute.entity_set.filter(id__in=[4, 5]).exists():
                    check_attribute_type = 'USER'

                if condition == 'is_set' or condition == 'not_set':
                    if check_attribute_type == 'USER':
                        if condition == 'is_set':
                            # validar is set attribute
                            qs = models.User.objects.filter(userdata__attribute_id=data_key)
                            queryset = self.apply_connector_to_search(next_connector, queryset, qs)

                        if condition == 'not_set':
                            # validar not set attribute
                            qs = models.User.objects.exclude(userdata__attribute_id=data_key)
                            queryset = self.apply_connector_to_search(next_connector, queryset, qs)
                    else:
                        if condition == 'is_set':
                            qs = models.User.objects.filter(
                                instanceassociationuser__instance__attributevalue__attribute_id=data_key)

                        if condition == 'not_set':
                            qs = models.User.objects.exclude(
                                instanceassociationuser__instance__attributevalue__attribute_id=data_key)

                        queryset = self.apply_connector_to_search(next_connector, queryset, qs)

                else:
                    if check_attribute_type == 'INSTANCE':
                        # filter by attribute instance
                        s = Q(instanceassociationuser__instance__attributevalue__attribute_id=data_key) & \
                            self.apply_filter_to_search('instanceassociationuser__instance__attributevalue__value',
                                                        value, condition)
                        qs = models.User.objects.filter(s)
                    else:
                        # filter by attribute user
                        s = Q(userdata__attribute_id=data_key) & \
                            self.apply_filter_to_search('userdata__data_value', value, condition)
                        qs = models.User.objects.filter(s)

                    queryset = self.apply_connector_to_search(next_connector, queryset, qs)

            elif search_by == 'program':
                # filter by program
                s = self.apply_filter_to_search('assignationmessengeruser__group__programassignation__program_id',
                                                value, condition)
                qs = models.User.objects.filter(s)
                queryset = self.apply_connector_to_search(next_connector, queryset, qs)

            elif search_by == 'channel':
                # filter by channel
                s = self.apply_filter_to_search('channel_id', value, condition)
                qs = models.User.objects.filter(s)
                queryset = self.apply_connector_to_search(next_connector, queryset, qs)

            elif search_by == 'group':
                # filter by group
                s = self.apply_filter_to_search('assignationmessengeruser__group_id', value, condition)
                qs = models.User.objects.filter(s)
                queryset = self.apply_connector_to_search(next_connector, queryset, qs)

            elif search_by == 'dates':
                date_from = datetime.combine(datetime.strptime(f['date_from'], '%Y-%m-%d'), time.min) - timedelta(days=1)
                date_to = datetime.combine(datetime.strptime(f['date_to'], '%Y-%m-%d'), time.max) - timedelta(days=1)

                if date_from and date_to:
                    if data_key == 'created_at':
                        date_filter = Q(created_at__gte=date_from, created_at__lte=date_to)

                    if data_key == 'last_seen':
                        date_filter = Q(last_seen__gte=date_from, last_seen__lte=date_to)

            next_connector = f['connector']

        if request.query_params.get("search"):
            # search by queryparams
            params = ['id','username','first_name','last_name','bot_id','channel_id','created_at']

            for x in params:
                filter_search |= Q(**{f"{x}__icontains": self.request.query_params.get('search')})

        queryset = queryset.filter(date_filter).filter(filter_search).distinct()
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
            qs = qs.filter(user_id=self.request.query_params.get('user_id'))

        if self.request.query_params.get('attribute_id'):
            qs = qs.filter(attribute_id=self.request.query_params.get('attribute_id'))

        return qs

    """
        return the value of the specific attribute 
    """
    @action(methods=['get'], detail=False, url_path='get_base_date', url_name='get_base_date')
    def base_date(self, request, *args, **kwgars):
        try:
            base_date = False
            qs = self.get_queryset()
            
            if qs.exists():
                base_date = qs.values_list('data_value', flat=True).first()
                try:
                    found = False
                    recognized_formats ={
                        '(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})': '%Y-%m-%dT%H:%M:%S',
                        '(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})': '%Y-%m-%d %H:%M:%S',
                        '(\d{2})-(\d{2})-(\d{4})': '%d-%m-%Y',
                        '(\d{2})/(\d{2})/(\d{4})': '%d/%m/%Y',
                        '(\d{2})\.(\d{2})\.(\d{4})': '%d.%m.%Y'
                    }
                    
                    for pattern, date_format in recognized_formats.items():
                        match = re.search(pattern, base_date)
                        if match:
                            base_date = datetime.strptime(match.group(), date_format)
                            base_date = base_date.strftime('%Y-%m-%dT%H:%M:%S%z')
                            found = True
                            break

                    if found == False:
                       return Response({'ok':False, 'message':'value could not be parsed to datetime'},status=HTTP_500_INTERNAL_SERVER_ERROR) 
                   
                except ValueError:
                    return Response({'ok':False, 'message':'value could not be parsed to datetime'},status=HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'ok':True, 'base_date': base_date})
        except Exception as err:
            return Response({'ok':False, 'message':str(err)},status=HTTP_500_INTERNAL_SERVER_ERROR)
