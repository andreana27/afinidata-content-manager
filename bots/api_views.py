from rest_framework import viewsets, permissions
from rest_framework.response import Response

from bots import models, serializers



class InteractionViewSet(viewsets.ModelViewSet):
    queryset = models.Interaction.objects.all().order_by('-id')
    serializer_class = serializers.InteractionSerializer
    http_method_names = ['get', 'post', 'options', 'head']

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        return qs

    def create(self, request, *args, **kwargs):
        interaction, created = models.Interaction.objects.get_or_create(name=request.data['name'])
        interaction = self.get_serializer(interaction)
        return Response({'status': 201 if created else 200, 'data': interaction.data})
        

class UserInteractionViewSet(viewsets.ModelViewSet):
    queryset = models.UserInteraction.objects.all().order_by('-id')
    serializer_class = serializers.UserInteractionSerializer
    http_method_names = ['get', 'post', 'options', 'head']

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.query_params.get('id'):
            return qs.filter(id=self.request.query_params.get('id'))

        return qs

