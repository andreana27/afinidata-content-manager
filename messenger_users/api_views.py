from rest_framework import viewsets, permissions
from messenger_users import models, serializers
from django.utils.decorators import method_decorator
from django.db.models import Q


import logging


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        return qs


class UserDataViewSet(viewsets.ModelViewSet):
    queryset = models.UserData.objects.all()
    serializer_class = serializers.UserDataSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        if self.request.query_params.get('user_id'):
            return qs.filter(user_id=self.request.query_params.get('user_id'))

        if self.request.query_params.get('attribute_id'):
            return qs.filter(attribute_id=self.request.query_params.get('attribute_id'))
        
        if self.request.query_params.get('attribute_value') or self.request.query_params.get('attribute_name'):

            a_name = self.request.query_params.get('attribute_name')
            a_value = self.request.query_params.get('attribute_value')

            filter_by = Q( attribute__name__contains = a_name ) if a_name else False
            if a_value:
                filter_by = filter_by & Q( data_value__contains = a_value ) if filter_by else Q( data_value__contains = a_value )
            
            return qs.filter(filter_by)

        return qs
