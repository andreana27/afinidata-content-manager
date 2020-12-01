from django.db import models
from areas.models import Area
import uuid


class Milestone(models.Model):
    areas = models.ManyToManyField(Area)
    name = models.CharField(max_length=255, null=True)
    code = models.CharField(max_length=255, unique=True, null=True)
    second_code = models.CharField(max_length=20, unique=True, null=True)
    description = models.TextField(null=True)
    value = models.FloatField(default=0)
    min = models.FloatField(default=0, null=True)
    max = models.FloatField(default=0, null=True)
    secondary_value = models.FloatField(default=0)
    init_value = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class Session(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    active = models.BooleanField(default=True)
    in_risks = models.BooleanField(default=True)
    first_question = models.BooleanField(default=True)
    step = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)


class Step(models.Model):
    step = models.IntegerField()
    value = models.FloatField(default=0.0)
    secondary_value = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.step)


class MilestoneAreaValue(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    value = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
