from sessions import views
from django.urls import path

app_name = 'user_sessions'

urlpatterns = [
    path('', views.SessionListView.as_view(), name='session_list'),
    path('create/', views.SessionCreateView.as_view(), name='session_create'),
    path('<int:session_id>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('<int:session_id>/edit/', views.SessionUpdateView.as_view(), name='session_update'),
    path('<int:session_id>/delete/', views.SessionDeleteView.as_view(), name='session_delete'),
    path('<int:session_id>/add_field/', views.FieldCreateView.as_view(), name='field_create'),
    path('<int:session_id>/fields/<int:field_id>/delete/', views.FieldDeleteView.as_view(), name='field_delete'),
    path('<int:session_id>/fields/<int:field_id>/up/', views.FieldUpView.as_view(),
         name='field_up'),
    path('<int:session_id>/fields/<int:field_id>/down/', views.FieldDownView.as_view(),
         name='field_down'),
    path('<int:session_id>/fields/<int:field_id>/add_message/', views.MessageCreateView.as_view(),
         name='message_create'),
    path('<int:session_id>/fields/<int:field_id>/messages/<int:message_id>/edit/', views.MessageEditView.as_view(),
         name='message_edit'),
    path('<int:session_id>/fields/<int:field_id>/messages/<int:message_id>/delete/', views.MessageDeleteView.as_view(),
         name='message_delete'),
    path('<int:session_id>/fields/<int:field_id>/add_reply/', views.ReplyCreateView.as_view(),
         name='reply_create'),
    path('<int:session_id>/fields/<int:field_id>/replies/<int:reply_id>/edit/', views.ReplyEditView.as_view(),
         name='reply_edit'),
    path('<int:session_id>/fields/<int:field_id>/replies/<int:reply_id>/delete/', views.ReplyDeleteView.as_view(),
         name='reply_delete'),
    path('<int:session_id>/fields/<int:field_id>/add_block/', views.RedirectBlockCreateView.as_view(),
         name='block_create'),
    path('<int:session_id>/fields/<int:field_id>/blocks/<int:block_id>/edit/', views.RedirectBlockEditView.as_view(),
         name='block_edit'),
    path('<int:session_id>/fields/<int:field_id>/blocks/<int:block_id>/delete/', views.RedirectBlockDeleteView.as_view(),
         name='block_delete')
]
