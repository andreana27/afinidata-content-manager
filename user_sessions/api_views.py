from rest_framework import viewsets, permissions
from user_sessions import models, serializers
from django.utils.decorators import method_decorator


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Session.objects.all()
    serializer_class = serializers.SessionSerializer
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))
        return qs

    def list(self, request, *args, **kwargs):
        return super(SessionViewSet, self).list(request, *args, **kwargs)


class BotSessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.BotSessions.objects.all()
    serializer_class = serializers.BotSessionsSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        if self.request.query_params.get('bot_id'):
            qs = qs.filter(bot_id=self.request.query_params.get('bot_id'))

        if self.request.query_params.get('session_type'):
            qs = qs.filter(session_type=self.request.query_params.get('session_type'))

        return qs

