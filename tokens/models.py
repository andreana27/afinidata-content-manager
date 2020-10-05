from messenger_users.models import User
from datetime import timedelta
from django.db import models
import uuid


class Token(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True)

    def __str__(self):
        return "%s" % self.token

    def generate_finish(self, days):
        self.expired_at = self.created_at + timedelta(days=days)
        self.save()
