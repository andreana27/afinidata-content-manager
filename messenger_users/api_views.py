from django.db.models import Q
from rest_framework import filters
from rest_framework import viewsets, permissions
from messenger_users import models, serializers
from django.utils.decorators import method_decorator

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.User.objects.all().order_by('id')
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))
       
        if self.request.query_params.get('search'):
            search = self.request.query_params.get('search')
            qs = qs.filter(
                Q(id__icontains=search) | 
                Q(username__icontains=search) | 
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search) | 
                Q(assignationmessengeruser__group__name__icontains=search)
            )

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

        if self.request.query_params.get('search'):
            search = self.request.query_params.get('search')
            qs = qs.filter(data_value__icontains=search)

        return qs
