from django.db import models


class License(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        permissions = (
            ('view_all_licences', 'View all licences types for users.'),
        )
