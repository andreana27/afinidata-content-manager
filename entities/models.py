from django.db import models
from attributes.models import Attribute


class Entity(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    attributes = models.ManyToManyField(Attribute)

    def __str__(self):
        return self.name

    class Meta:
        permissions = (
            ('view_all_entities', 'View all entities types for instances.'),
        )
