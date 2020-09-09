from django.urls import path
from utilities import views

app_name = 'utilities'

urlpatterns = [
    path('validates_date', views.validates_date, name="validates_date"),
    path('validates_kids_date', views.validates_kids_date, name="validates_kids_date"),
    path('fix_date', views.fix_date, name='fix_date'),
    path('check_valid_date', views.check_valid_date, name='check_valid_date'),
    path('change_kids_date', views.change_kids_date, name='change_kids_date'),
    path('set_new_broadcast/<int:broadcast_id>/<variable>', views.set_new_broadcast, name='set_new_broadcast'),
    path('get_bot_user_id/', views.get_user_id_by_username, name='get_bot_user_id'),
    path('set_chatfuel_variable/', views.set_chatfuel_variable, name="set_chatfuel_variable"),
    path('child_months/', views.GetMonthsView.as_view(), name="get_months"),
    path('en_child_months/', views.EnGetMonthsView.as_view(), name="get_months_en"),
    path('article_interaction_update_count/<int:interaction_id>/', views.AddMinuteForArticleInteraction.as_view(),
         name='article_interaction_update_count')
]
