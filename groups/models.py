from django.core.validators import MinValueValidator, MaxValueValidator
from messenger_users.models import User as MessengerUser
from django.contrib.auth.models import User
from milestones.models import Milestone
from programs.models import Program
from django.db import models
from bots.models import Bot


ROLE_CHOICES = (('administrator', 'Administrator'), ('collaborator', 'Collaborator'))


class Group(models.Model):
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    available = models.BooleanField(default=True)
    bots = models.ManyToManyField(Bot, through='BotAssignation')
    programs = models.ManyToManyField(Program, through='ProgramAssignation')
    users = models.ManyToManyField(User, through='RoleGroupUser')

    def __str__(self):
        return self.name

    class Meta:
        permissions = (
            ('view_all_groups', 'User can view all groups'),
            ('view_user_groups', 'User can view only property groups')
        )


class RoleGroupUser(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


class Code(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, unique=True)
    available = models.BooleanField(default=True)
    exchanges = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def exchange(self):
        self.exchanges = self.exchanges + 1
        self.save()


class AssignationMessengerUser(models.Model):
    messenger_user_id = models.IntegerField()
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.ForeignKey(Code, null=True, on_delete=models.SET_NULL)

    def get_messenger_user(self):
        return MessengerUser.objects.get(id=self.messenger_user_id)


class BotAssignation(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ProgramAssignation(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class RiskGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    groups = models.ManyToManyField(Group)
    programs = models.ManyToManyField(Program)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MilestoneRisk(models.Model):
    risk_group = models.ForeignKey(RiskGroup, on_delete=models.CASCADE, null=True, blank=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True, blank=True)
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    value = models.IntegerField()
    percent_value = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
