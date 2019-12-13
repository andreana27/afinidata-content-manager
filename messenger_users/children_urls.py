from django.urls import path
from messenger_users import children_views

app_name = 'children'

urlpatterns = [
    path('<int:child_id>/', children_views.ChildView.as_view(), name='child')
]
