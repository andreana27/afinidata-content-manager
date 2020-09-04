from django.urls import path
from chatfuel import views

app_name = 'chatfuel'

urlpatterns = [
    path('create_messenger_user_data/', views.CreateMessengerUserDataView.as_view(), name='create_messenger_user_data'),
    path('create_instance_attribute/', views.CreateInstanceAttributeView.as_view(), name='create_instance_attribute'),
    path('get_initial_user_data/', views.GetInitialUserData.as_view(), name='get_initial_user_data'),
    path('get_instance_attribute/', views.GetInstanceAttributeView.as_view(), name='get_instance_attribute'),
    path('change_instance_name/', views.ChangeInstanceNameView.as_view(), name='change_instance_name'),
    path('create_instance_interaction_view/', views.CreateInstanceInteractionView.as_view(),
         name='create_instance_interaction_view'),
    path('create_messenger_user/', views.CreateMessengerUserView.as_view(), name='create_messenger_user'),
    path('create_instance/', views.create_instance, name='new_instance'),
    path('get_instances/', views.GetInstancesByUserView.as_view(), name='get_instances'),
    path('exchange_code/', views.ExchangeCodeView.as_view(), name='exchange_code'),
    path('verify_code/', views.VerifyCodeView.as_view(), name='verify_code'),
    path('get_favorite_child/', views.GetFavoriteChildView.as_view(), name='get_favorite_child'),
    path('get_last_child/', views.GetLastChildView.as_view(), name='get_last_child'),
    path('redirect_to_block/', views.BlockRedirectView.as_view(), name='redirect_to_block'),
    path('get_article/', views.GetArticleView.as_view(), name='get_article'),
    path('get_article_image/', views.GetArticleImageView.as_view(), name='get_article_image'),
    path('get_article_text/', views.GetArticleTextView.as_view(), name='get_article_text'),
    path('validates_date/', views.ValidatesDateView.as_view(), name='validates_date'),
    path('verify_user/', views.VerifyMessengerUserView.as_view(), name='verify_user'),
    path('replace_user_info/', views.ReplaceUserInfoView.as_view(), name='replace_user_info'),
    path('get_milestone/', views.GetMilestoneView.as_view(), name='get_milestone'),
    path('response_milestone/', views.CreateResponseView.as_view(), name='response_milestone'),
    path('get_instance_milestones/', views.GetInstanceMilestoneView.as_view(), name='get_instance_milestones'),
    path('get_session_field/', views.GetSessionFieldView.as_view(), name='get_session_field'),
    path('get_session/', views.GetSessionView.as_view(), name='get_session')
]