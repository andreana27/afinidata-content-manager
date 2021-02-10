from django.core.validators import MinValueValidator, MaxValueValidator
from messenger_users import models as user_models
from milestones.models import Milestone, Session, MilestoneAreaValue
from posts.models import Post, Interaction
from dateutil import parser, relativedelta
from attributes.models import Attribute
from programs.models import Program
from entities.models import Entity
from django.utils import timezone
from areas.models import Area
import datetime
from django.db import models
from django.db.models.aggregates import Max


class Instance(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    name = models.TextField()
    attributes = models.ManyToManyField(Attribute, through='AttributeValue')
    milestones = models.ManyToManyField(Milestone, through='Response')
    program = models.ForeignKey(
        Program, on_delete=models.DO_NOTHING, null=True)
    sessions = models.ManyToManyField(Session)
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
        if self.entity_id == 1:
            births = self.attributevalue_set.filter(attribute__name='birthday')
            if not births.exists():
                return None
            birth = births.last()
            print(self)
            print(birth)
            try:
                birthday = parser.parse(birth.value)
                if timezone.is_aware(birthday):
                    now = timezone.now()
                else:
                    now = datetime.datetime.now()
                rd = relativedelta.relativedelta(now, birthday)
                if rd.months:
                    months = rd.months
                else:
                    months = 0
                if rd.years:
                    months = months + (rd.years * 12)
                return months
            except:
                return None
        elif self.entity_id == 2:
            pregnant_weeks = self.attributevalue_set.filter(
                attribute__name='pregnant_weeks')
            if not pregnant_weeks.exists():
                return None
            pw = pregnant_weeks.last()
            months = round(int(pw.value) / 4)
            if months == 0:
                months = -1
            return months
        else:
            return None

    def get_weeks(self):
        if self.entity_id == 2:
            pregnant_weeks = self.attributevalue_set.filter(
                attribute__name='pregnant_weeks')
            if not pregnant_weeks.exists():
                return None
            pw = pregnant_weeks.last()
            weeks = int(pw.value)
            if weeks == 0:
                weeks = -1
            return weeks
        else:
            return None

    def get_time_feeds(self, first_limit, last_limit):
        feeds = self.instancefeedback_set.filter(
            created_at__gte=first_limit, created_at__lte=last_limit)
        return feeds

    def get_time_interactions(self, first_limit, last_limit):
        interactions = Interaction.objects.filter(created_at__gte=first_limit, created_at__lte=last_limit,
                                                  instance_id=self.pk)
        return interactions

    def get_assigned_milestones(self):
        milestones = self.get_completed_milestones().union(
            self.get_failed_milestones()).order_by('-code')
        for milestone in milestones:
            milestone.assign = self.response_set.filter(
                milestone=milestone).order_by('-created_at').first()
        return milestones

    def get_completed_milestones(self):
        milestones = Milestone.objects.filter(
            id__in=[m.milestone.pk for m in self.response_set.filter(response='done')])
        for milestone in milestones:
            milestone.assign = self.response_set.filter(milestone=milestone).filter(response='done') \
                .order_by('-created_at').first()
        return milestones

    def get_failed_milestones(self):
        milestones = Milestone.objects.filter(
            id__in=[m.milestone.pk for m in self.response_set.exclude(response='done')])
        for milestone in milestones:
            milestone.assign = self.response_set.filter(milestone=milestone).exclude(response='done')\
                .order_by('-created_at').first()
        return milestones

    def get_activities(self):
        posts = Post.objects.filter(id__in=set([x.post_id for x in Interaction.objects.filter(instance_id=self.pk)]))\
            .only('id', 'name')
        for post in posts:
            post.assign = Interaction.objects.filter(
                post_id=post.id, type='dispatched', instance_id=self.pk).last()
            sessions = Interaction.objects.filter(
                post_id=post.id, type='session', instance_id=self.pk)
            if sessions.count() > 0:
                post.completed = sessions.last()
            else:
                post.completed = None
        return posts

    def get_activities_area(self, area, first_limit, last_limit):
        if area > 0:
            posts = Post.objects.\
                filter(id__in=set([x.post_id for x in Interaction.objects.filter(instance_id=self.pk)
                                   .filter(created_at__gte=first_limit, created_at__lte=last_limit, type='session')])) \
                .filter(area_id=area).only('id', 'name')
        else:
            posts = Post.objects. \
                filter(id__in=set([x.post_id for x in Interaction.objects.filter(instance_id=self.pk)
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
            attribute.assign = self.attributevalue_set.filter(
                attribute=attribute).last()
        return attributes

    def get_attribute_values(self, name):
        attribute = self.attributevalue_set.filter(attribute__name=name)
        if not attribute.count() > 0:
            return None
        return attribute.last()

    def is_session_active(self):
        sessions = self.sessions.filter(
            created_at__gte=timezone.now() - datetime.timedelta(days=7))
        return sessions.exists()

    def get_session(self):
        sessions = self.sessions.filter(
            created_at__gte=timezone.now() - datetime.timedelta(days=7))
        if sessions.exists():
            session = sessions.last()
        else:
            session = self.sessions.create()
            milestone_interaction = MilestoneInteraction.objects.create(
                instance=self, milestone_id=0)
        return session

    def question_milestone_complete(self, milestone_id, session_id=None):
        # Get active session, if there is none, then return
        if session_id:
            session = Session.objects.get(uuid=session_id)
        else:
            if self.is_session_active():
                session = self.get_session()
            else:
                return False
        last_response = session.response_set.last()

        if not session.in_risks and not session.first_question:
            if session.step == 5:
                session.step = 1
                session.save()
            elif session.step == 10:
                if last_response:
                    if last_response.response != 'done':
                        session.step = 5
                        session.save()
            else:
                if last_response:
                    if last_response.response != 'done':
                        session.active = False
                        session.save()

        new_response = Response.objects.create(instance_id=self.pk,
                                               session_id=session.uuid,
                                               milestone_id=milestone_id,
                                               created_at=timezone.now(),
                                               response='done')
        return new_response

    def question_milestone_fail(self, milestone_id, session_id=None):
        # Get active session, if there is none, then return
        if session_id:
            session = Session.objects.get(uuid=session_id)
        else:
            if self.is_session_active():
                session = self.get_session()
            else:
                return False
        last_response = session.response_set.last()
        if not session.in_risks and not session.first_question:
            if session.step == 5:
                session.step = 1
                session.save()
            elif session.step == 10:
                if last_response:
                    if last_response.response != 'failed':
                        session.step = 5
                        session.save()
                else:
                    session.step = 5
                    session.save()
            else:
                if last_response:
                    if last_response.response != 'failed':
                        session.active = False
                        session.save()

        new_response = Response.objects.create(instance_id=self.pk,
                                               session_id=session.uuid,
                                               milestone_id=milestone_id,
                                               created_at=timezone.now(),
                                               response='failed')
        return new_response

    def get_question_milestone(self):
        c = dict()
        c['instance'] = self
        c['session'] = c['instance'].get_session()
        responses = c['session'].response_set.all()

        if not responses.exists():
            c['milestone'] = Milestone.objects.get(
                init_value=c['instance'].get_months())
        else:
            value = responses.last().milestone.secondary_value + c['session'].step if \
                responses.last().response == 'done' else \
                responses.last().milestone.secondary_value - c['session'].step
            print(value, responses.last().milestone.secondary_value)
            milestones = Milestone.objects.filter(secondary_value__gte=responses.last().milestone.secondary_value,
                                                  secondary_value__lte=value).order_by('-secondary_value') if \
                responses.last().response == 'done' else \
                Milestone.objects.filter(secondary_value__lte=responses.last().milestone.secondary_value,
                                         secondary_value__gte=value).order_by('secondary_value')
            for m in milestones:
                print(m.code, m.secondary_value)
            if milestones.exists():
                c['milestone'] = milestones.first()
                milestone_responses = responses.filter(
                    milestone_id=c['milestone'].pk)
                if milestone_responses.exists():
                    c['session'].active = False
                    c['session'].save()
            else:
                c['session'].active = False
                c['session'].save()

        c['responses'] = responses
        return c

    def save_score_tracking(self, responses):
        done_response = responses.filter(response='done').order_by('id').last()
        if done_response:
            milestone_id = done_response.milestone_id
            if MilestoneAreaValue.objects.filter(milestone_id=milestone_id).exists():
                milestone_values = MilestoneAreaValue.objects.filter(
                    milestone_id=milestone_id)
                for m in milestone_values:
                    scoretracking = ScoreTracking(
                        value=m.value, area_id=m.area_id, instance_id=self.id)
                    scoretracking.save()
                    Score.objects.update_or_create(
                        instance_id=self.id,
                        area_id=m.area_id,
                        defaults={'value': m.value}
                    )
        return True

    def get_program_milestone(self, program, risks):
        c = dict()
        c['session'] = self.get_session()
        c['instance'] = self
        months = c['instance'].get_months()
        responses = c['session'].response_set.all()
        c['question_number'] = responses.count() + 1
        m_ids = set(x.milestone_id for x in risks)

        if c['session'].in_risks:
            risk_milestones = Milestone.objects.filter(id__in=m_ids)\
                .exclude(id__in=[im.milestone_id for im in
                                 program.programmilestonevalue_set.filter(init=months)]).order_by('second_code')
            c['risk_milestones'] = []
            c['pending_risk_milestones'] = []
            for r in risk_milestones:
                rs = risks.filter(milestone_id=r.pk).order_by('value')
                if rs.first().value <= months <= rs.last().value:
                    c['risk_milestones'].append(r)
            for r in c['risk_milestones']:
                done_responses = c['instance'].response_set.filter(
                    milestone_id=r.pk, response='done')
                if not done_responses.exists():
                    session_responses = responses.filter(milestone_id=r.pk)
                    if not session_responses.exists():
                        c['pending_risk_milestones'].append(r)
            if len(c['pending_risk_milestones']) > 0:
                print(c['pending_risk_milestones'])
                c['milestone'] = c['pending_risk_milestones'][0]
            else:
                c['session'].in_risks = False
                c['session'].save()

        if not c['session'].in_risks:
            risk_milestones = Milestone.objects.filter(id__in=m_ids)\
                .exclude(id__in=[im.milestone_id for im in
                                 program.programmilestonevalue_set.filter(init=months)]).order_by('second_code')
            clear_responses = responses.exclude(
                milestone_id__in=[x.pk for x in risk_milestones])
            if not clear_responses.exists():
                mv = program.programmilestonevalue_set.filter(init__gte=0, init__lte=c['instance']
                                                              .get_months()).order_by('init')
                c['milestone'] = mv.last().milestone
                c['association'] = mv.last()
            else:
                c['session'].first_question = False
                c['session'].save()
                response_value = program.programmilestonevalue_set.get(
                    milestone=responses.last().milestone)
                value = response_value.value + c['session'].step if \
                    responses.last().response == 'done' else \
                    responses.last().milestone.secondary_value - \
                    c['session'].step

                last_association = program.programmilestonevalue_set.get(
                    milestone=responses.last().milestone)

                if responses.last().response == 'done':
                    associations = program.programmilestonevalue_set.filter(value__gte=last_association.value,
                                                                            value__lte=value,
                                                                            max__gte=c['instance'].get_months(
                                                                            ),
                                                                            min__lte=c['instance'].get_months())\
                        .order_by('-value')

                else:
                    associations = program.programmilestonevalue_set.filter(value__lte=last_association.value,
                                                                            value__gte=value,
                                                                            max__gte=c['instance'].get_months(
                                                                            ),
                                                                            min__lte=c['instance'].get_months())\
                        .order_by('value')

                if associations.exists():
                    c['milestone'] = associations.first().milestone
                    c['association'] = associations.first()
                    milestone_responses = responses.filter(
                        milestone_id=c['milestone'].pk)

                    if milestone_responses.exists():
                        self.save_score_tracking(responses)
                        c['session'].active = False
                        c['session'].save()
                else:
                    self.save_score_tracking(responses)
                    c['session'].active = False
                    c['session'].save()
        c['responses'] = responses
        return c

    # Returns a dict with keys the porcentage of the risk, e.g. percent_50
    # and value an array of the texts of the failed milestones
    def get_risk_milestones_text(self, program):
        instance = self
        months = 0
        if instance.get_months():
            months = instance.get_months()
        response = dict()
        # Get all the possible percentages for risk, usually are 0, 50, 100
        percentages = program.milestonerisk_set.filter(value__lte=months).\
            values('percent_value').distinct().order_by('-percent_value')
        # Avoid repeting milestones in two different risk percentages
        repeated_milestones = []
        for percent in percentages:
            # Get the milestones that represent risks, by program
            milestones_risks = [int(m['milestone_id']) for m in program.milestonerisk_set.
                                filter(percent_value=percent['percent_value'],
                                       value__lte=months).values('milestone_id').
                                exclude(milestone_id__in=repeated_milestones).distinct()]
            # Get the ids of the las responses for milestones. It can happen that an instance previously failed
            #       a milestone but then completed it
            last_responses = [int(r['id']) for r in instance.response_set.values(
                'milestone_id').annotate(id=Max('id'))]
            # Get the description/name of the failed milestones risks
            milestones = instance.response_set.filter(response__in=['failed', 'dont-know'],
                                                      milestone__id__in=milestones_risks,
                                                      id__in=last_responses).values('milestone__name').distinct()
            if len(milestones) > 0:
                response['percent_%s' % percent['percent_value']] = [
                    m['milestone__name'] for m in milestones]
            repeated_milestones += milestones_risks
        return response


class InstanceAssociationUser(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    user = models.ForeignKey('messenger_users.User',
                             on_delete=models.CASCADE, null=True)
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
    session = models.ForeignKey(
        Session, on_delete=models.SET_NULL, null=True, blank=True)
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
    value = models.IntegerField(default=1, validators=[
                                MinValueValidator(0), MaxValueValidator(5)])
    reference_text = models.CharField(max_length=50)
    register_id = models.IntegerField(null=True)
    register_type = models.CharField(max_length=20, default=0)
    migration_field_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField()

    def __str__(self):
        return "%s %s %s %s" % (self.pk, self.instance_id, self.area, self.value)


class MilestoneInteraction(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    milestone_id = models.IntegerField()
    type = models.CharField(max_length=255, default='hitos_monitoreo')
    value = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s %s %s %s" % (self.pk, self.instance, self.milestone_id, self.type)
