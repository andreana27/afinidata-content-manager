from django.urls import path
from milestones import views

app_name = 'milestones'

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('new/', views.NewMilestoneView.as_view(), name='new'),
    path('<int:milestone_id>/', views.MilestoneView.as_view(), name='milestone'),
    path('<int:milestone_id>/edit/', views.EditMilestoneView.as_view(), name='edit'),
    path('<int:milestone_id>/delete/', views.DeleteMilestoneView.as_view(), name='delete'),
    path('<int:milestone_id>/create_translation/', views.MilestoneTranslationCreateView.as_view(),
         name='create_translation')
]
