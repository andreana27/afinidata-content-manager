from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from entities.models import Entity
from areas.models import Area
from milestones.models import Milestone
from attributes.models import Attribute
from messenger_users import models as user_models
from posts.models import Post, Interaction
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
        return user_models.User.objects \
            .filter(id__in=set(assoc.user_id for assoc in self.instanceassociationuser_set.all()))

    def get_months(self):
        births = self.attributevalue_set.filter(attribute__name='birthday')
        if not births.exists():
            return None
        birth = births.last()
        try:
            birthday = parser.parse(birth.value) 
            rd = relativedelta.relativedelta(timezone.now(), birthday)
            if rd.months:
                months = rd.months
            else:
                months = 0
            if rd.years:
                months = months + (rd.years * 12)
            return months
        except:
            return None

    def get_time_feeds(self, first_limit, last_limit):
        feeds = self.instancefeedback_set.filter(created_at__gte=first_limit, created_at__lte=last_limit)
        return feeds

    def get_time_interactions(self, first_limit, last_limit):
        interactions = Interaction.objects.filter(created_at__gte=first_limit, created_at__lte=last_limit,
                                                  instance_id=self.pk)
        return interactions

    def get_assigned_milestones(self):
        milestones = self.get_completed_milestones().union(self.get_failed_milestones()).order_by('-code')
        for milestone in milestones:
            milestone.assign = self.response_set.filter(milestone=milestone).order_by('-created_at').first()
        return milestones

    def get_completed_milestones(self):
        milestones = Milestone.objects.filter(
            id__in=[m.milestone.pk for m in self.response_set.filter(response='done')])
        for milestone in milestones:
            milestone.assign = self.response_set.filter(milestone=milestone).filter(response='done') \
                .order_by('-created_at').first()
        return milestones

    def get_failed_milestones(self):
        milestones = Milestone.objects.filter(id__in=[m.milestone.pk for m in self.response_set.exclude(response='done')])
        for milestone in milestones:
            milestone.assign = self.response_set.filter(milestone=milestone).exclude(response='done')\
                .order_by('-created_at').first()
        return milestones

    def get_activities(self):
        posts = Post.objects.filter(id__in=set([x.post_id for x in Interaction.objects.filter(instance_id=self.pk)]))\
            .only('id', 'name')
        for post in posts:
            post.assign = Interaction.objects.filter(post_id=post.id, type='dispatched', instance_id=self.pk).last()
            sessions = Interaction.objects.filter(post_id=post.id, type='session', instance_id=self.pk)
            if sessions.count() > 0:
                post.completed = sessions.last()
            else:
                post.completed = None
        return posts

    def get_activities_area(self, area, first_limit, last_limit):
        if area > 0:
            posts = Post.objects.\
                filter(id__in=set([x.post_id for x in Interaction.objects.filter(instance_id=self.pk) \
                                  .filter(created_at__gte=first_limit, created_at__lte=last_limit, type='session')])) \
                .filter(area_id=area).only('id', 'name')
        else:
            posts = Post.objects. \
                filter(id__in=set([x.post_id for x in Interaction.objects.filter(instance_id=self.pk) \
                                  .filter(created_at__gte=first_limit, created_at__lte=last_limit, type='session')])) \
                .only('id', 'name')
        return posts

    def get_completed_activities(self, tipo='session'):
        posts = Post.objects\
            .filter(id__in=set([x.post_id for x in Interaction.objects.filter(instance_id=self.pk, type=tipo)]))\
            .only('id')
        return posts

    def get_attributes(self):
        attributes_ids = set(item.pk for item in self.attributes.all())
        attributes = Attribute.objects.filter(id__in=attributes_ids)
        for attribute in attributes:
            attribute.assign = self.attributevalue_set.filter(attribute=attribute).last()
        return attributes

    def get_attribute_values(self, name):
        attribute = self.attributevalue_set.filter(attribute__name=name)
        if not attribute.count() > 0:
            return None
        return attribute.last()


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

