from django.contrib import admin
from django.urls import path
from reply_repo.views import index

app_name = 'dash'

urlpatterns = [
    path('', index, name="index")
]
