from django.db import models


class User(models.Model):
    last_channel_id = models.CharField(max_length=50, unique=True)
    channel_id = models.CharField(max_length=50, unique=True, null=True)
    backup_key = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bot_id = models.IntegerField(default=1)

    def __str__(self):
        return self.backup_key

    class Meta:
        app_label = 'messenger_users'


class UserData(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    data_key = models.CharField(max_length=30)
    data_value = models.TextField()

    def __str__(self):
        return self.data_value

    class Meta:
        app_label = 'messenger_users'
