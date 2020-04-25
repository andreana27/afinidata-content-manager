from django.contrib import admin
from django.urls import path
from reply_repo.views import index, download_messages, upload_messages, fix_messages_view, translate, do_translate, done
app_name = 'reply_repo'

urlpatterns = [
    path('', index, name="index"),
    path('translate/do', do_translate, name='do_translate'),
    path('translate/', translate, name='translate'),
    path('done/', done, name='done'),
    path('fix_messages/', fix_messages_view, name='fixer'),
    path('fix_messages/download', download_messages, name="down"),
    path('fix_messages/upload', upload_messages, name="up")
]
