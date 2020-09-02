from milestones.models import Milestone
from django.db import models


class Program(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        permissions = (
            ('view_all_programs', 'User can view all programs'),
            ('view_user_programs', 'User can view programs in your groups')
        )


class Level(models.Model):
    name = models.CharField(max_length=50)
    program = models.ForeignKey(Program, on_delete=models.DO_NOTHING)
    description = models.TextField()
    assign_min = models.IntegerField(null=True, blank=True, default=0)
    assign_max = models.IntegerField(null=True, blank=True, default=1)
    milestones = models.ManyToManyField(Milestone, through='LevelMilestoneAssociation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class LevelMilestoneAssociation(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
