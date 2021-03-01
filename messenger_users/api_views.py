from django.db.models import Q
from rest_framework import viewsets, permissions, filters
from messenger_users import models, serializers
from django.utils.decorators import method_decorator

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.User.objects.all().order_by('id')
    serializer_class = serializers.UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('id', 'username', 'first_name', 'last_name', 'assignationmessengeruser__group__name')
    ordering_fields = ['id', 'username', 'first_name', 'last_name']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        return qs

class UserDataViewSet(viewsets.ModelViewSet):
    queryset = models.UserData.objects.all().order_by('user_id')
    serializer_class = serializers.UserDataSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ("$data_key", "$data_value")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            qs = qs.filter(id=self.request.query_params.get('id'))

        if self.request.query_params.get('user_id'):
            qs = qs.filter(user_id=self.request.query_params.get('user_id'))

        if self.request.query_params.get('attribute_id'):
            qs = qs.filter(attribute_id=self.request.query_params.get('attribute_id'))

        return qs
