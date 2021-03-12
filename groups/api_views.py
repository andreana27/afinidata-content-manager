from .models import Group
from .serializers import GroupSerializer
from rest_framework import viewsets

class GroupViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all().order_by("-id")
    serializer_class = GroupSerializer
    pagination_class = None
