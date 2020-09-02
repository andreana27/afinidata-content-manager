from django.db import models


class Level(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    range_min = models.IntegerField(null=True, blank=True, default=0)
    range_max = models.IntegerField(null=True, blank=True, default=1)

    def __str__(self):
        return self.name
