from django.urls import path
from articles import views

app_name = 'articles'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='articles_list'),
    path('create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('<int:article_id>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('<int:article_id>/info/', views.ArticleInfoDetailView.as_view(), name='article_info'),
    path('<int:article_id>/edit/', views.ArticleUpdateView.as_view(), name='article_edit'),
    path('topic/', views.TopicListView.as_view(), name='topics_list'),
    path('topic/create/', views.TopicCreateView.as_view(), name='topic_create'),
    path('topic/<int:topic_id>/', views.TopicDetailView.as_view(), name='topic_detail'),
    path('topic/<int:topic_id>/edit/', views.TopicUpdateView.as_view(), name='topic_edit'),
    path('<int:article_id>/create_translate/', views.ArticleTranslateCreateView.as_view(), name='translate_create'),
    path('<int:article_id>/translates/<int:translate_id>/', views.ArticleTranslateDetailView.as_view(),
         name='translate_detail'),
    path('<int:article_id>/translates/<int:translate_id>/edit/', views.ArticleTranslateEditView.as_view(),
         name='translate_edit'),
    path('<int:article_id>/translates/<int:translate_id>/delete/', views.ArticleTranslateDeleteView.as_view(),
         name='translate_delete'),
]
