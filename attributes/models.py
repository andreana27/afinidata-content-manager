from django.db import models


attribute_types = (
    ('numeric', 'Numeric'),
    ('string', 'String'),
    ('date', 'Date'),
    ('boolean', 'Boolean')
)


class Attribute(models.Model):
    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=20, choices=attribute_types, default='string')
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        permissions = (
            ('view_all_attributes', 'User can view all attributes for entities'),
        )
