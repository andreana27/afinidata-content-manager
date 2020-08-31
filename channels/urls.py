from django.urls import path
from channels import views

app_name = 'channels'

urlpatterns = [
    path('', views.HomeView.as_view(), name='channel_list'),
    path('new/', views.CreateChannelView.as_view(), name='create_channel'),
    path('<int:channel_id>', views.ChannelView.as_view(), name='channel_detail'),
    path('<int:channel_id>/edit/', views.UpdateChannelView.as_view(), name='edit_channel'),
    path('<int:channel_id>/delete/', views.DeleteChannelView.as_view(), name='delete_channel')
]