from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from entities.models import Entity
from areas.models import Area
from milestones.models import Milestone
from attributes.models import Attribute
from messenger_users import models as user_models
from posts.models import Post
from dateutil import parser, relativedelta
from django.utils import timezone
from datetime import datetime


class Instance(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    name = models.TextField()
    attributes = models.ManyToManyField(Attribute, through='AttributeValue')
    milestones = models.ManyToManyField(Milestone, through='Response')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ('view_all_instances', 'User can view all instances'),
        )

    def __str__(self):
        return self.name

    def get_users(self):
        return user_models.User.objects\
            .filter(id__in=set(assoc.user_id for assoc in self.instanceassociationuser_set.all()))

    def get_months(self):
        births = self.attributevalue_set.filter(attribute__name='birthday')
        print(births)
        if not births.exists():
            return None
        birth = births.last()
        try:
            birthday = parser.parse(birth.value) 
            rd = relativedelta.relativedelta(datetime.now(), birthday)
            if rd.months:
                months = rd.months
            else:
                months = 0
            if rd.years:
                months = months + (rd.years * 12)
            return months
        except:
            return None



class InstanceAssociationUser(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Score(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    value = models.FloatField(default=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.instance.name + '__' + self.area.name + '__' + str(round(self.value, 2))


class ScoreTracking(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    value = models.FloatField(default=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.instance.name + '__' + self.area.name + '__' + str(round(self.value, 2))


class Response(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    response = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s__%s__%s%s__%s" % (self.pk, self.instance.name, self.milestone.pk, self.milestone.name, self.response)


class AttributeValue(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s__%s__%s__%s" % (self.pk, self.instance.name, self.attribute.name, self.value)


class PostInteraction(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    post_id = models.IntegerField()
    type = models.CharField(max_length=255, default='open')
    value = models.IntegerField(default=0)
    created_at = models.DateTimeField()

    def __str__(self):
        return "%s %s %s %s" % (self.pk, self.instance, self.post_id, self.type)


REGISTER_TYPE_CHOICES = (
    (0, "Script with number"),
    (1, "Script with text")
)


class InstanceFeedback(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    post_id = models.IntegerField()
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    value = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(5)])
    reference_text = models.CharField(max_length=50)
    register_id = models.IntegerField(null=True)
    register_type = models.CharField(max_length=20, default=0)
    migration_field_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField()

    def __str__(self):
        return "%s %s %s %s" % (self.pk, self.instance_id, self.area, self.value)

