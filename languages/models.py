from django.db import models
from milestones.models import Milestone

CODE_ORIGIN = (('generated', 'Generated'), ('created', 'Created'))


class Language(models.Model):
    name = models.CharField(max_length=2, unique=True)
    label = models.CharField(max_length=20, unique=True, null=True)
    description = models.TextField()
    available = models.BooleanField(default=True, blank=True)
    auto_translate = models.BooleanField(default=False, blank=True)
    redirect = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.label


class LanguageCode(models.Model):
    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING)
    code = models.CharField(max_length=5, unique=True)
    origin = models.CharField(max_length=15, choices=CODE_ORIGIN, default='generated')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class MilestoneTranslation(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    language_code = models.ForeignKey(LanguageCode, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)