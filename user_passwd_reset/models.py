from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class PasswdReset(models.Model):
    token = models.CharField(max_length=60)
    status = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta():
        db_table = "password_resets"
