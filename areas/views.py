from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import DetailView, ListView
from django.urls import reverse_lazy
from areas import models


class AreasListView(PermissionRequiredMixin, ListView):
    model = models.Area
    paginate_by = 10
    permission_required = 'areas.view_area'
    login_url = reverse_lazy('static:login')

