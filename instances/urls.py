from django.urls import path
from instances import views

app_name = 'instances'

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('new/', views.NewInstanceView.as_view(), name='new'),
    path('<int:id>/', views.InstanceView.as_view(), name='instance'),
    path('<int:id>/edit/', views.EditInstanceView.as_view(), name='edit'),
    path('<int:id>/delete/', views.DeleteInstanceView.as_view(), name='delete'),
    path('<int:instance_id>/milestones_list/', views.InstanceMilestonesListView.as_view(), name='milestones_list'),
    path('<int:instance_id>/program_milestones_list/', views.ProgramMilestonesListView.as_view(),
         name='program_milestones_list'),
    path('<int:instance_id>/complete_milestone/<int:milestone_id>/', views.CompleteMilestoneView.as_view(),
         name='complete_milestone'),
    path('<int:instance_id>/reverse_milestone/<int:milestone_id>/', views.ReverseMilestoneView.as_view(),
         name='reverse_milestone'),
    path('<int:instance_id>/dont_know_milestone/<int:milestone_id>/', views.DontKnowMilestoneView.as_view(),
         name='dont_know_milestone'),
    path('<int:instance_id>/add_attribute/', views.AddAttributeToInstanceView.as_view(), name='add_instance_attribute'),
    path('<int:instance_id>/edit_attribute/<int:attribute_id>/', views.AttributeValueEditView.as_view(),
         name='edit_instance_attribute'),
    path('<int:instance_id>/report/', views.InstanceReportView.as_view(), name='instance_report'),
    path('<int:instance_id>/milestones/', views.InstanceMilestonesView.as_view(), name='instance_milestones'),
    path('<int:instance_id>/question_milestone/', views.QuestionMilestoneView.as_view(),
         name='instance_question_milestone'),
    path('<int:instance_id>/complete_question_milestone/<int:milestone_id>/session/<uuid:session_id>/',
         views.QuestionMilestoneCompleteView.as_view(), name='complete_question_milestone'),
    path('<int:instance_id>/failed_question_milestone/<int:milestone_id>/session/<uuid:session_id>/',
         views.QuestionMilestoneFailedView.as_view(), name='failed_question_milestone'),
    path('<int:instance_id>/program_milestone/', views.ProgramMilestoneView.as_view(),
         name='instance_program_milestone'),
]