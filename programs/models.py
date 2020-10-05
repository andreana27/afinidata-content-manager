from milestones.models import Milestone
from attributes.models import Attribute
from languages.models import Language
from entities.models import Entity
from django.db import models


class Program(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    languages = models.ManyToManyField(Language)
    levels = models.ManyToManyField('Level')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        permissions = (
            ('view_all_programs', 'User can view all programs'),
            ('view_user_programs', 'User can view programs in your groups')
        )


class AttributeType(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
    weight = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Attributes(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    attribute_type = models.ForeignKey(AttributeType, on_delete=models.CASCADE)
    weight = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Level(models.Model):
    name = models.CharField(max_length=50)
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
