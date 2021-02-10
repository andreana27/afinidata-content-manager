from rest_framework import viewsets, permissions
from messenger_users import models, serializers
from django.utils.decorators import method_decorator

import logging


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

        return qs
