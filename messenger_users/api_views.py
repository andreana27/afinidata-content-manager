import logging
from django.db.models import Q
from rest_framework import filters
from rest_framework import viewsets, permissions
from messenger_users import models, serializers
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters

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

    @action(methods=['POST'], detail=False)
    def advance_search(self, request):
        queryset = models.User.objects.order_by('-id').all()
        filtros = request.data['filtros']
        apply_filters = Q()
        next_connector = None

        for idx, f in enumerate(filtros):
            #attribute
            if f['search_by'] == 'attribute':
                # validar si son attributes de instances o de users
                # el queryset inicial va a depender de que tipo de attributes son (user o instance)

                # Si son attribute de instances
                # consultar las instances filtrado por el attribute enviado igual
                # a (***api_view de instances)

                # si son attributes de users continuo con lo que existe.
                field_name = 'userdata__data_value'

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
                apply_filters = Q(userdata__data_key=f['data_key']) & query_search
            else:
                if next_connector == 'and':
                    apply_filters &= Q(userdata__data_key=f['data_key']) & query_search
                else:
                    apply_filters |= Q(userdata__data_key=f['data_key']) & query_search

            next_connector = f['connector']

        if request.query_params.get("search"):
            filter_search = Q()
            params = ['id','username','first_name','last_name','bot_id','channel_id']

            for x in params:
                filter_search |= Q(**{f"{x}__icontains": self.request.query_params.get('search')})
            queryset = queryset.filter(filter_search)

        # aplico los filtros al query secundario
        queryset = queryset.filter(apply_filters)

        # al query anterior le aplico el metodo .values_list('id', flat=True)
        # luego filtro el queryset principal User o Instances basado en los ids
        # User.objects.filters(instanceassociationuser__in=ids) or
        # Instances.objects.filters(instanceassociationuser__in=ids) or
        # y este ultimo query es el que va al pagination
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
