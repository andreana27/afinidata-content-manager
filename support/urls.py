from django.contrib import admin
from django.urls import path
from support.views import index, chatfuel
app_name = 'support'

urlpatterns = [
    path('', index, name="index"),
    path('chatfuel', chatfuel, name="chatfuel")
]
