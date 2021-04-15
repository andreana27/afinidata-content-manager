import json
import re
import dateutil.parser
from datetime import datetime, timedelta, time
from django.db.models import Q, Exists
from django.db.models.aggregates import Max
from django.utils import timezone
from django.utils.decorators import method_decorator
from rest_framework import filters, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR

from messenger_users import models, serializers
from instances.models import Instance
from groups.models import ProgramAssignation, AssignationMessengerUser
from programs.models import Program
from attributes.models import Attribute

from messenger_users.models import UserData


class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all().order_by('-id')
    serializer_class = serializers.UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=id', 'username', 'first_name', 'last_name', '=bot_id', '=channel_id', '$created_at']
    http_method_names = ['get', 'patch', 'options', 'head', 'post']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        return qs

    @action(methods=['GET'], detail=True)
    def get_possible_values(self, request, pk=None):
        queryset = UserData.objects.filter(attribute_id=pk).values('data_value').distinct()
        pagination = PageNumberPagination()
        pagination.page_size = 10
        pagination.page_query_param = 'pagenumber'
        qs = pagination.paginate_queryset(queryset, request)
        serializer = serializers.UserDataFilterPosibleVal(qs, many=True)
        return pagination.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=False, url_path='last_seen', url_name='last_seen')
    def get_last_seen(self, request, *args, **kwgars):
        try:
            if 'sender' not in request.GET and 'id' not in request.GET:
                return Response({'request_status':400, 'error':'Wrong parameters'})

            result = False
            filter_search = Q(id=request.GET['id']) if 'id' in request.GET else Q(last_channel_id=request.GET['sender'])
            last_seen = models.User.objects.filter(filter_search).values_list('last_seen', flat=True)
            if last_seen.exists():
                result = last_seen.last()
            
            if isinstance(result, bool):
                return Response({'request_status':404, 'error':'Sender could not be found'})

            if 'inwindow' in request.GET:
                if not result: 
                    result = False
                else:
                    result = (timezone.now() - result).days < 1
            
            return Response({'request_status':200, 'result':result})
        except Exception as err:
            return Response({'request_status':500, 'error':str(err)})

    @action(methods=['POST'], detail=False, url_path='update_last_seen', url_name='update_last_seen')
    def update_last_seen(self, request, *args, **kwgars):
        try:
            if len(request.POST) > 0:
                data = request.POST.dict()
            else:
                data = json.loads(request.body)

            if 'user_channel_id' not in data or 'bot_id' not in data or 'bot_channel_id' not in data:
                return Response({'request_status':400, 'error':'Wrong parameters'})

            user_channel = models.UserChannel.objects.filter(   bot_id=data['bot_id'], 
                                                                bot_channel_id=data['bot_channel_id'], 
                                                                user_channel_id=data['user_channel_id'])
            
            if user_channel.exists():
                user_channel.update(last_seen=timezone.now())
                models.User.objects.filter(id=user_channel.last().user.id).update(last_seen=timezone.now())
                
                return Response({'request_status':200})

            return Response({'request_status':404, 'error':'user_channel could not be found'})
        
        except Exception as err:
            return Response({'request_status':500, 'error':str(err)})

    def apply_filter_to_search(self, field, value, condition, numeric=False):
        # apply condition to search
        if condition == 'is':
            if numeric:
                query_search = Q(**{f"{field}": value})
            else:
                query_search = Q(**{f"{field}__icontains": value})
        elif condition == 'is_not':
            if numeric:
                query_search = ~Q(**{f"{field}": value})
            else:
                query_search = ~Q(**{f"{field}__icontains": value})
        elif condition == 'startswith':
            if numeric:
                query_search = Q(**{f"{field}": value})
            else:
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
                                                value, condition, numeric=True)
                qs = models.User.objects.filter(s)
                queryset = self.apply_connector_to_search(next_connector, queryset, qs)

            elif search_by == 'channel':
                # filter by channel
                s = self.apply_filter_to_search('userchannel__channel_id', value, condition, numeric=True)
                qs = models.User.objects.filter(s)
                queryset = self.apply_connector_to_search(next_connector, queryset, qs)

            elif search_by == 'group':
                # filter by group and by parent group
                s = self.apply_filter_to_search('assignationmessengeruser__group_id', value, condition, numeric=True)
                s2 = self.apply_filter_to_search('assignationmessengeruser__group__parent_id',
                                                 value, condition, numeric=True)
                qs = models.User.objects.filter(s | s2)
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
            params = ['username','first_name','last_name','created_at']

            for x in params:
                filter_search |= Q(**{f"{x}__icontains": self.request.query_params.get('search')})
            if self.request.query_params.get('search').isnumeric():
                filter_search |= Q(id=self.request.query_params.get('search'))
                filter_search |= Q(bot_id=self.request.query_params.get('search'))
                filter_search |= Q(channel_id=self.request.query_params.get('search'))

        queryset = queryset.filter(date_filter).filter(filter_search).distinct()
        pagination = PageNumberPagination()
        qs = pagination.paginate_queryset(queryset, request)
        serializer = serializers.UserSerializer(qs, many=True)
        return pagination.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=False)
    def user_conversations(self, request):
        queryset = models.User.objects.all().order_by('-last_seen')
        # Filter by bot if necessary
        if request.query_params.get("bot_id"):
            queryset = queryset.filter(userchannel__bot_id=self.request.query_params.get('bot_id')).distinct()
        if request.query_params.get("live_chat"):
            if self.request.query_params.get('live_chat') == 'True':
                queryset = queryset.filter(userchannel__live_chat=self.request.query_params.get('live_chat')).distinct()
            else:
                date = datetime.now() - timedelta(days=30)
                queryset = queryset.filter(userchannel__livechat__created_at__gte=date).distinct()
        # Filter by name
        filter_search = Q()
        if request.query_params.get("search"):
            # search by queryparams
            params = ['username', 'first_name', 'last_name']
            for x in params:
                filter_search |= Q(**{f"{x}__icontains": self.request.query_params.get('search')})
            if self.request.query_params.get('search').isnumeric():
                filter_search |= Q(id=self.request.query_params.get('search'))
            queryset = queryset.filter(filter_search)
        pagination = PageNumberPagination()
        pagination.page_size = 20
        qs = pagination.paginate_queryset(queryset, request)
        serializer = serializers.UserConversationSerializer(qs, many=True)
        return pagination.get_paginated_response(serializer.data)


class UserDataViewSet(viewsets.ModelViewSet):
    queryset = models.UserData.objects.all()
    serializer_class = serializers.UserDataSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ("$data_key", "$data_value")

    def paginate_queryset(self, queryset, view=None):

        if self.request.query_params.get('pagination') == 'off':
            return None

        return self.paginator.paginate_queryset(queryset, self.request, view=self)


    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        if self.request.query_params.get('user_id'):
            qs = qs.filter(user_id=self.request.query_params.get('user_id'))
            last_attributes = qs.values('attribute_id').annotate(max_id=Max('id'))
            qs = qs.filter(id__in=[x['max_id'] for x in last_attributes])

        if self.request.query_params.get('attribute_id'):
            qs = qs.filter(attribute_id=self.request.query_params.get('attribute_id'))

        if self.request.query_params.get('attribute_name'):
            qs = qs.filter(attribute__name=self.request.query_params.get('attribute_name'))

        return qs.order_by('-id')

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
                        '(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(\.\d+)?(?:Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])': '%Y-%m-%dT%H:%M:%S%Z',
                        '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?': '%Y-%m-%dT%H:%M:%S',
                        '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?': '%Y-%m-%d %H:%M:%S',
                        '(\d{2})-(\d{2})-(\d{4})': '%d-%m-%Y',
                        '(\d{2})/(\d{2})/(\d{4})': '%d/%m/%Y',
                        '(\d{2})\.(\d{2})\.(\d{4})': '%d.%m.%Y'
                    }
                    
                    for pattern, date_format in recognized_formats.items():
                        match = re.search(pattern, base_date)
                        if match:
                            if date_format[-1].lower() == 'z':
                                base_date = dateutil.parser.isoparse(match.group())
                            else:
                                base_date = datetime.strptime(match.group(), date_format)
                            base_date = base_date.isoformat()
                            found = True
                            break

                    if found == False:
                       return Response({'ok':False, 'message':'value could not be parsed to datetime'})

                except ValueError:
                    return Response({'ok':False, 'message':'value could not be parsed to datetime'})

            return Response({'ok':True, 'base_date': base_date})
        except Exception as err:
            return Response({'ok':False, 'message':str(err)})


class UserChannelSet(viewsets.ModelViewSet):
    queryset = models.UserChannel.objects.all().order_by('-id')
    serializer_class = serializers.UserChannelSerializer
    http_method_names = ['get', 'post', 'patch', 'options', 'head']

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.query_params.get('detail'):
            self.serializer_class = serializers.DetailedUserChannelSerializer

        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        if self.request.query_params.get('user_channel_id'):
            qs = qs.filter(user_channel_id=self.request.query_params.get('user_channel_id'))

        if self.request.query_params.get('bot_id'):
            qs = qs.filter(bot_id=self.request.query_params.get('bot_id'))

        if self.request.query_params.get('channel_id'):
            qs = qs.filter(channel_id=self.request.query_params.get('channel_id'))

        if self.request.query_params.get('bot_channel_id'):
            qs = qs.filter(bot_channel_id=self.request.query_params.get('bot_channel_id'))

        return qs

    def create(self, request, *args, **kwargs):
        created = super(UserChannelSet, self).create(request, *args, **kwargs)
        return Response({'request_status': 'done', 'data': created.data}) 