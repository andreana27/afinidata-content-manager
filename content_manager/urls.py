"""content_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include("static.urls", namespace="static")),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('posts/', include("posts.urls", namespace="posts")),
    path('upload/', include('upload.urls', namespace='upload')),
    path('messenger_users/', include("messenger_users.urls", namespace="users")),
    path('utilities/', include("utilities.urls", namespace="utilities")),
    path('dashboard/', include("dash.urls", namespace="dash")),
    path('codes/', include("random_codes.urls", namespace="codes")),
    path('reply/', include("reply_repo.urls", namespace="replies")),
    path('support/', include("support.urls", namespace="support")),
    path('articles/', include('articles.urls', namespace='articles')),
    path('user_sessions/', include('user_sessions.urls', namespace='user_sessions')),
    path('areas/', include('areas.urls', namespace='areas')),
    path('milestones/', include('milestones.urls', namespace='milestones'))
]
