from django.urls import path
from areas import views

app_name = 'areas'

urlpatterns = [
    path('', views.AreasListView.as_view(), name='area_list')
]