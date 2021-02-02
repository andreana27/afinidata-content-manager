from rest_framework import viewsets, permissions
from user_sessions import models, serializers
from django.utils.decorators import method_decorator


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Session.objects.all()
    serializer_class = serializers.SessionSerializer

    def list(self, request, *args, **kwargs):
        return super(SessionViewSet, self).list(request, *args, **kwargs)
