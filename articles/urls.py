from django.urls import path
from articles import views

app_name = 'articles'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='articles_list'),
    path('create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('<int:article_id>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('<int:article_id>/edit/', views.ArticleUpdateView.as_view(), name='article_edit')
]
