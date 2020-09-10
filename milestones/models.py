from django.db import models
from areas.models import Area


class Milestone(models.Model):
    areas = models.ManyToManyField(Area)
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True, null=True)
    second_code = models.CharField(max_length=20, unique=True, null=True)
    description = models.TextField(null=True)
    value = models.FloatField(default=0)
    secondary_value = models.FloatField(default=0)
    source = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Step(models.Model):
    step = models.IntegerField()
    value = models.FloatField(default=0.0)
    secondary_value = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.step)