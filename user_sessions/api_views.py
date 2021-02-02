from rest_framework import viewsets, permissions
from user_sessions import models, serializers
from django.utils.decorators import method_decorator


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Session.objects.all()
    serializer_class = serializers.SessionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))
        return qs

    def list(self, request, *args, **kwargs):
        return super(SessionViewSet, self).list(request, *args, **kwargs)
