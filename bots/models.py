from messenger_users.models import User
from django.db import models


class Bot(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    url = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        permissions = (
            ("view_all_bots", "Can view all bots in platform"),
            ("view_user_bots", "Can view property user bots in platform")
        )


class Interaction(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserInteraction(models.Model):
    interaction = models.ForeignKey(Interaction, on_delete=models.DO_NOTHING)
    bot = models.ForeignKey(Bot, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    value = models.TextField(blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

