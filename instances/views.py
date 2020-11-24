from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, RedirectView, TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from instances.models import Instance, AttributeValue, Response, ScoreTracking, Score
from django.shortcuts import get_object_or_404
from messenger_users.models import User, UserData
from user_sessions.models import Field, Interaction as SessionInteraction
from django.urls import reverse_lazy
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.utils import timezone
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from areas.models import Area
from languages.models import Language
from posts.models import Post, Interaction as PostInteraction
from instances import forms
from programs.models import Program, Level
from milestones.models import Milestone, Session, MilestoneAreaValue
from groups.models import Group, ProgramAssignation, MilestoneRisk
from django.shortcuts import redirect
import datetime
import calendar


class HomeView(PermissionRequiredMixin, ListView):
    permission_required = 'instances.view_all_instances'
    model = Instance
    paginate_by = 30
    login_url = reverse_lazy('static:login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(HomeView, self).get_context_data()
        return context


class InstanceView(PermissionRequiredMixin, DetailView):
    permission_required = 'instances.view_instance'
    model = Instance
    pk_url_kwarg = 'id'
    login_url = reverse_lazy('static:login')

    def get_context_data(self, **kwargs):
        c = super(InstanceView, self).get_context_data()
        c['today'] = timezone.now()
        c['first_month'] = parse("%s-%s-%s" % (c['today'].year, c['today'].month, 1))
        c['interactions'] = self.object.get_time_interactions(c['first_month'], c['today'])
        c['feeds'] = self.object.get_time_feeds(c['first_month'], c['today'])
        c['posts'] = Post.objects.filter(id__in=[x.post_id for x in c['interactions']]).only('id', 'name', 'area_id')
        c['completed_activities'] = 0
        c['assigned_activities'] = 0
        c['areas'] = Area.objects.all()
        for area in c['areas']:
            area.assigned_activities = 0
            area.completed_activities = 0
            area.feeds = c['feeds'].filter(area=area).order_by('created_at')
            print(area.feeds)
        for post in c['posts']:
            post.last_assignation = post.get_user_last_dispatched_interaction(self.object, c['first_month'], c['today'])
            post.last_session = post.get_user_last_session_interaction(self.object, c['first_month'], c['today'])
            if post.last_session:
                c['completed_activities'] = c['completed_activities'] + 1
            if post.last_assignation:
                c['assigned_activities'] = c['assigned_activities'] + 1
            for area in c['areas']:
                if post.last_assignation:
                    if area.pk == post.area_id:
                        area.assigned_activities = area.assigned_activities + 1
                if post.last_session:
                    if area.pk == post.area_id:
                        area.completed_activities = area.completed_activities + 1

        c['labels'] = [parse("%s-%s-%s" %
                             (c['today'].year, c['today'].month, day)) for day in range(1, c['today'].day + 1)]
        quick_replies = []
        replies = SessionInteraction.objects.filter(instance_id=54510)
        for reply in replies:
            rep = dict()
            position = Field.objects.filter(id=reply.field_id).first().position - 1

            rep['attribute'] = 'Atributo'
            rep['question'] = 0
            rep['answer'] = 'Pregunta'
            rep['value'] = reply.value
            rep['response'] = AttributeValue.objects.filter(instance_id=54510).last().value
            quick_replies.append(rep)
        c['quick_replies'] = quick_replies
        return c


class InstanceReportView(DetailView):
    model = Instance
    pk_url_kwarg = 'instance_id'
    template_name = 'instances/instance_report.html'

    def get_context_data(self, **kwargs):
        c = super(InstanceReportView, self).get_context_data(**kwargs)
        instance_interactions = PostInteraction.objects. \
            filter(instance_id=self.object.id, type='session', value__gte=0,
                   created_at__gte=timezone.now() + datetime.timedelta(days=-4))
        interactions = list(instance_interactions)
        c['trabajo_motor'] = Post.objects.\
            filter(id__in=[x.post_id for x in interactions]).filter(area_id=2).count()
        c['trabajo_cognitivo'] = Post.objects.\
            filter(id__in=[x.post_id for x in interactions]).filter(area_id=1).count()
        c['trabajo_socio'] = Post.objects.\
            filter(id__in=[x.post_id for x in interactions]).filter(area_id=3).count()
        c['activities'] = [
            len(set([interaction.post_id for interaction in interactions])),
            len(set([interaction.post_id for interaction in interactions
                     if timezone.now() + datetime.timedelta(days=-4) <=
                     interaction.created_at <= timezone.now() + datetime.timedelta(days=-3)])),
            len(set([interaction.post_id for interaction in interactions
                     if timezone.now() + datetime.timedelta(days=-3) <=
                     interaction.created_at <= timezone.now() + datetime.timedelta(days=-2)])),
            len(set([interaction.post_id for interaction in interactions
                     if timezone.now() + datetime.timedelta(days=-2) <=
                     interaction.created_at <= timezone.now() + datetime.timedelta(days=-1)])),
            len(set([interaction.post_id for interaction in interactions
                     if timezone.now() + datetime.timedelta(days=-1) <=
                     interaction.created_at <= timezone.now() + datetime.timedelta(days=0)])),
            len(set([interaction.post_id for interaction in interactions
                     if timezone.now() + datetime.timedelta(days=0) <=
                     interaction.created_at <= timezone.now() + datetime.timedelta(days=1)]))
        ]
        try:
            objective = UserData.objects.filter(user=self.object.instanceassociationuser_set.last().user_id).\
                                            filter(data_key='tiempo_intensidad').last().data_value
            if objective == '10 min':
                c['objective'] = 1
            elif objective == '30 min':
                c['objective'] = 3
            else:
                c['objective'] = 6
        except:
            c['objective'] = 6
        try:
            age = relativedelta(datetime.datetime.now(), parse(self.object.get_attribute_values('birthday').value))
            months = 0
            if age.months:
                months = age.months
            if age.years:
                months = months + (age.years * 12)
        except:
            months = 0
        c['months'] = months
        levels = Program.objects.get(id=1).levels.filter(assign_min__lte=months, assign_max__gte=months)
        level = levels.first()
        lang = Language.objects.get(id=self.object.get_users().first().language_id).name
        c['image_name'] = 'images/'+level.image
        c['etapa'] = level.name
        if level.levellanguage_set.filter(language__name=lang).exists():
            c['etapa'] = level.levellanguage_set.filter(language__name=lang).first().name
        c['lang'] = lang
        return c


class InstanceMilestonesView(DetailView):
    model = Instance
    pk_url_kwarg = 'instance_id'
    template_name = 'instances/instance_milestones.html'

    def get_context_data(self, **kwargs):
        c = super(InstanceMilestonesView, self).get_context_data(**kwargs)
        months = 0
        if self.object.get_months():
            months = self.object.get_months()
        c['months'] = months
        levels = Program.objects.get(id=1).levels.filter(assign_min__lte=months, assign_max__gte=months)
        level = levels.first()
        lang = Language.objects.get(id=self.object.get_users().first().language_id).name
        c['image_name'] = 'images/'+level.image
        c['etapa'] = level.name
        if level.levellanguage_set.filter(language__name=lang).exists():
            c['etapa'] = level.levellanguage_set.filter(language__name=lang).first().name
        responses = self.object.response_set.all()
        user = self.object.get_users().first()
        group = Group.objects.filter(assignationmessengeruser__user_id=user.pk).first()
        c['group'] = group
        program = group.programs.first()
        for area in program.areas.filter(topic_id=1):
            c['trabajo_' + str(area.id)] = 0
            c['trabajo_' + str(area.id)+'_total'] = 0
            milestones = Milestone.objects.filter(areas__in=[area], min__lte=months, max__gte=months,
                                                  id__in=[i.milestone_id for i in program.programmilestonevalue_set.all()]).order_by('value')
            for m in milestones:
                m_responses = responses.filter(milestone_id=m.pk).order_by('-id')
                if m_responses.exists():
                    if m_responses.first().response == 'done':
                        c['trabajo_'+str(area.id)] += 1
                c['trabajo_'+str(area.id)+'_total'] += 1
            if c['trabajo_' + str(area.id)+'_total'] == 0:
                c['trabajo_' + str(area.id) + '_total'] = 1
        c['activities'] = self.object.get_completed_activities('session').count()
        c['lang'] = lang
        print(c)
        return c


class NewInstanceView(PermissionRequiredMixin, CreateView):
    permission_required = 'instances.add_instance'
    model = Instance
    form_class = forms.InstanceModelForm
    login_url = reverse_lazy('static:login')

    def get_context_data(self, **kwargs):
        c = super(NewInstanceView, self).get_context_data()
        c['action'] = 'Create'
        return c

    def form_valid(self, form):
        users = User.objects.filter(id=form.cleaned_data['user_id'])
        if not users.count() > 0:
            form.add_error('user_id', 'User ID is not valid')
            messages.error(self.request, 'User ID is not valid')
            return super(NewInstanceView, self).form_invalid(form)

        return super(NewInstanceView, self).form_valid(form)

    def get_success_url(self):
        self.object.instanceassociationuser_set.create(user_id=self.request.POST['user_id'])
        messages.success(self.request, 'Instance with name: "%s" has been created.' % self.object.name)
        return reverse_lazy('instances:instance', kwargs={'id': self.object.pk})


class EditInstanceView(PermissionRequiredMixin, UpdateView):
    permission_required = 'instances.change_instance'
    model = Instance
    fields = ('name',)
    pk_url_kwarg = 'id'
    context_object_name = 'instance'
    login_url = reverse_lazy('static:login')

    def get_context_data(self, **kwargs):
        c = super(EditInstanceView, self).get_context_data()
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Instance with name "%s" has been updated.' % self.object.name)
        return reverse_lazy('instances:instance', kwargs={'id': self.object.pk})


class DeleteInstanceView(PermissionRequiredMixin, DeleteView):
    permission_required = 'instances.delete_instance'
    model = Instance
    template_name = 'instances/instance_form.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('instances:index')
    login_url = reverse_lazy('static:login')

    def get_context_data(self, **kwargs):
        c = super(DeleteInstanceView, self).get_context_data()
        c['action'] = 'Delete'
        c['delete_message'] = 'Are you sure to delete instance with name: "%s"?' % self.object.name
        return c

    def get_success_url(self):
        messages.success(self.request, 'Instance with name: "%s" has been deleted.' % self.object.name)
        return super(DeleteInstanceView, self).get_success_url()


class AddAttributeToInstanceView(PermissionRequiredMixin, CreateView):
    permission_required = 'instances.add_attributevalue'
    model = AttributeValue
    fields = ('attribute', 'value')

    def get_context_data(self, **kwargs):
        instance = Instance.objects.get(id=self.kwargs['instance_id'])
        c = super(AddAttributeToInstanceView, self).get_context_data()
        c['instance'] = instance
        c['action'] = 'Create'
        c['form'].fields['attribute'].queryset = instance.entity.attributes.all()
        return c

    def form_valid(self, form):
        form.instance.instance_id = self.kwargs['instance_id']
        return super(AddAttributeToInstanceView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'The value "%s" for attribute "%s" for instance: "%s" has been added' % (
            self.object.value, self.object.attribute.name, self.object.instance
        ))
        return reverse_lazy('instances:instance', kwargs={'id': self.object.instance.pk})


class AttributeValueEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'instances.change_attributevalue'
    template_name = 'instances/attributevalue_edit_form.html'
    model = AttributeValue
    fields = ('value',)
    pk_url_kwarg = 'attribute_id'
    login_url = reverse_lazy('static:login')

    def get_context_data(self, **kwargs):
        c = super(AttributeValueEditView, self).get_context_data()
        print(self.kwargs['instance_id'], self.object.instance.pk)
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, 'The value "%s" for attribute "%s" for instance: "%s" has been updated' % (
            self.object.value, self.object.attribute.name, self.object.instance
        ))
        return reverse_lazy('instances:instance', kwargs={'id': self.object.instance.pk})


class InstanceMilestonesListView(DetailView):
    model = Instance
    pk_url_kwarg = 'instance_id'
    template_name = 'instances/milestones_list.html'

    def get_context_data(self, **kwargs):
        c = super(InstanceMilestonesListView, self).get_context_data()
        user = None
        months = 0
        if self.object.get_months():
            months = self.object.get_months()
        levels = Program.objects.get(id=1).levels.filter(assign_min__lte=months, assign_max__gte=months)
        if 'key' in self.request.GET:
            fu = User.objects.filter(last_channel_id=self.request.GET['key'])
            if fu.exists():
                user = fu.first()

        responses = self.object.response_set.all()
        lang = Language.objects.get(id=self.object.get_users().first().language_id).name
        c['lang'] = lang
        if lang == 'en':
            c['hitos'] = 'Milestones of ' + self.object.name + ' (' + str(self.object.get_months()) + ')'
        elif lang == 'ar':
            c['hitos'] = ' (' + str(self.object.get_months()) + ')' + self.object.name + 'معالم '
        elif lang == 'pt':
            c['hitos'] = 'Marcos do ' + self.object.name + ' (' + str(self.object.get_months()) + ')'
        else:
            c['hitos'] = 'Hitos de ' + self.object.name + ' (' + str(self.object.get_months()) + ')'
        if levels.exists():
            level = levels.first()
            c['etapa'] = level.name
            if level.levellanguage_set.filter(language__name=lang).exists():
                c['etapa'] = level.levellanguage_set.filter(language__name=lang).first().name
            c['level'] = level
        print(months)
        c['milestones'] = Milestone.objects.filter(max__gte=months, min__lte=months, source__in=['CDC', '1', 'Credi'])\
            .order_by('secondary_value')
        for m in c['milestones']:
            m_responses = responses.filter(milestone_id=m.pk)
            m.label = m.milestonetranslation_set.get(language__name='es').name
            translations = m.milestonetranslation_set.filter(language__name=lang)
            if translations.exists():
                m.label = translations.last().name
            if m_responses.exists():
                m.status = m_responses.last().response
                print(m.status)
        return c


class CompleteMilestoneView(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        new_response = Response.objects.create(milestone_id=kwargs['milestone_id'], instance_id=kwargs['instance_id'],
                                               response='done', created_at=timezone.now())
        print(new_response)
        messages.success(self.request, 'Se han realizado los cambios.')
        if 'key' in self.request.GET:
            uri = "%s?key=%s" % (reverse_lazy('instances:milestones_list', kwargs=dict(instance_id=kwargs['instance_id'])),
                              self.request.GET['key'])
            return uri
        return reverse_lazy('instances:milestones_list', kwargs=dict(instance_id=kwargs['instance_id']))


class ReverseMilestoneView(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        new_response = Response.objects.create(milestone_id=kwargs['milestone_id'], instance_id=kwargs['instance_id'],
                                               response='failed', created_at=timezone.now())
        messages.success(self.request, 'Se han realizado los cambios.')
        if 'key' in self.request.GET:
            uri = "%s?key=%s" % (reverse_lazy('instances:milestones_list', kwargs=dict(instance_id=kwargs['instance_id'])),
                              self.request.GET['key'])
            return uri
        return reverse_lazy('instances:milestones_list', kwargs=dict(instance_id=kwargs['instance_id']))


class DontKnowMilestoneView(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        new_response = Response.objects.create(milestone_id=kwargs['milestone_id'], instance_id=kwargs['instance_id'],
                                               response='dont-know', created_at=timezone.now())
        messages.success(self.request, 'Se han realizado los cambios.')
        if 'key' in self.request.GET:
            uri = "%s?key=%s" % (reverse_lazy('instances:milestones_list', kwargs=dict(instance_id=kwargs['instance_id'])),
                              self.request.GET['key'])
            return uri
        return reverse_lazy('instances:milestones_list', kwargs=dict(instance_id=kwargs['instance_id']))


class QuestionMilestoneView(TemplateView):
    template_name = 'instances/single_response_milestone.html'

    def get_context_data(self, **kwargs):
        c = super(QuestionMilestoneView, self).get_context_data(**kwargs)
        c['instance'] = get_object_or_404(Instance, id=self.kwargs['instance_id'])
        sessions = c['instance'].sessions.filter(created_at__gte=timezone.now() - datetime.timedelta(days=7))
        if sessions.exists():
            c['session'] = sessions.last()
        else:
            c['session'] = c['instance'].sessions.create()
        responses = c['session'].response_set.all()

        if not responses.exists():
            c['milestone'] = Milestone.objects.get(init_value=c['instance'].get_months())
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
                milestone_responses = responses.filter(milestone_id=c['milestone'].pk)
                if milestone_responses.exists():
                    c['session'].active = False
                    c['session'].save()
            else:
                c['session'].active = False
                c['session'].save()

        c['responses'] = responses
        return c


class QuestionMilestoneCompleteView(RedirectView):
    permanent = False
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        session = Session.objects.get(uuid=self.kwargs['session_id'])
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

        new_response = Response.objects.create(instance_id=self.kwargs['instance_id'],
                                               session_id=self.kwargs['session_id'],
                                               milestone_id=self.kwargs['milestone_id'],
                                               created_at=timezone.now(),
                                               response='done')

        if 'source' in self.request.GET:
            if self.request.GET['source'] == 'program':
                return reverse_lazy('instances:instance_program_milestone',
                                    kwargs=dict(instance_id=self.kwargs['instance_id']))

        return reverse_lazy('instances:instance_question_milestone',
                            kwargs=dict(instance_id=self.kwargs['instance_id']))


class QuestionMilestoneFailedView(RedirectView):
    permanent = False
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        session = Session.objects.get(uuid=self.kwargs['session_id'])
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

        new_response = Response.objects.create(instance_id=self.kwargs['instance_id'],
                                               session_id=self.kwargs['session_id'],
                                               milestone_id=self.kwargs['milestone_id'],
                                               created_at=timezone.now(),
                                               response='failed')

        if 'source' in self.request.GET:
            if self.request.GET['source'] == 'program':
                return reverse_lazy('instances:instance_program_milestone',
                                    kwargs=dict(instance_id=self.kwargs['instance_id']))

        return reverse_lazy('instances:instance_question_milestone',
                            kwargs=dict(instance_id=self.kwargs['instance_id']))


class ProgramMilestoneView(TemplateView):
    template_name = 'instances/program_response_milestone.html'

    def save_score_tracking(self, responses, instance_id):

        done_response = responses.filter(response='done').order_by('id').last()

        if done_response:
            milestone_id = done_response.milestone_id

            if MilestoneAreaValue.objects.filter(milestone_id=milestone_id).exists():
                milestone_values = MilestoneAreaValue.objects.filter(milestone_id=milestone_id)
                for m in milestone_values:
                    scoretracking = ScoreTracking(value=m.value, area_id=m.area_id, instance_id=instance_id)
                    scoretracking.save()
                    Score.objects.update_or_create(
                        instance_id=instance_id,
                        area_id=m.area_id,
                        defaults={'value': m.value}
                    )

    def get_context_data(self, **kwargs):
        c = super(ProgramMilestoneView, self).get_context_data(**kwargs)
        c['instance'] = get_object_or_404(Instance, id=self.kwargs['instance_id'])
        months = c['instance'].get_months()
        c['user'] = c['instance'].get_users().first()
        group = Group.objects.filter(assignationmessengeruser__user_id=c['user'].pk).first()
        c['group'] = group
        program = group.programs.first()
        c['program'] = program
        sessions = c['instance'].sessions.filter(created_at__gte=timezone.now() - datetime.timedelta(days=7))
        c['level'] = Level.objects.filter(assign_min__lte=months,
                                          assign_max__gte=months).first()
        if sessions.exists():
            c['session'] = sessions.last()
        else:
            c['session'] = c['instance'].sessions.create()
        responses = c['session'].response_set.all()
        c['question_number'] = responses.count() + 1
        risks = MilestoneRisk.objects.filter(program=program)
        m_ids = set(x.milestone_id for x in risks)

        if c['session'].in_risks:
            risk_milestones = Milestone.objects.filter(id__in=m_ids)\
                .exclude(id__in=[im.milestone_id for im in
                                 program.programmilestonevalue_set.filter(init=months)])
            c['risk_milestones'] = []
            c['pending_risk_milestones'] = []
            for r in risk_milestones:
                rs = risks.filter(milestone_id=r.pk).order_by('value')
                if rs.first().value <= months <= rs.last().value:
                    c['risk_milestones'].append(r)
            for r in c['risk_milestones']:
                done_responses = c['instance'].response_set.filter(milestone_id=r.pk, response='done')
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
                                 program.programmilestonevalue_set.filter(init=months)])
            clear_responses = responses.exclude(milestone_id__in=[x.pk for x in risk_milestones])
            print(clear_responses)
            if not clear_responses.exists():
                mv = program.programmilestonevalue_set.filter(init__gte=0, init__lte=c['instance']
                                                              .get_months()).order_by('init')
                c['milestone'] = mv.last().milestone
                c['association'] = mv.last()
            else:
                print('here')
                c['session'].first_question = False
                c['session'].save()
                response_value = program.programmilestonevalue_set.get(milestone=responses.last().milestone)
                value = response_value.value + c['session'].step if \
                    responses.last().response == 'done' else \
                    responses.last().milestone.secondary_value - c['session'].step

                print(value, response_value.value)

                last_association = program.programmilestonevalue_set.get(milestone=responses.last().milestone)

                if responses.last().response == 'done':
                    associations = program.programmilestonevalue_set.filter(value__gte=last_association.value,
                                                                            value__lte=value,
                                                                            max__gte=c['instance'].get_months(),
                                                                            min__lte=c['instance'].get_months())\
                                                                            .order_by('-value')

                else:
                    associations = program.programmilestonevalue_set.filter(value__lte=last_association.value,
                                                                            value__gte=value,
                                                                            max__gte=c['instance'].get_months(),
                                                                            min__lte=c['instance'].get_months())\
                                                                            .order_by('value')

                for a in associations:
                    print(a.milestone, a.init, a.value, a.min, a.max, a.milestone.name)

                if associations.exists():
                    c['milestone'] = associations.first().milestone
                    c['association'] = associations.first()
                    milestone_responses = responses.filter(milestone_id=c['milestone'].pk)

                    if milestone_responses.exists():
                        self.save_score_tracking(responses, self.kwargs['instance_id'])
                        c['session'].active = False
                        c['session'].save()
                else:
                    self.save_score_tracking(responses, self.kwargs['instance_id'])
                    c['session'].active = False
                    c['session'].save()

        print(c['session'].in_risks, c['session'].first_question, c['session'].step)

        c['responses'] = responses
        return c


class ProgramMilestonesListView(DetailView):
    model = Instance
    pk_url_kwarg = 'instance_id'
    template_name = 'instances/milestones_list.html'

    def get_context_data(self, **kwargs):
        c = super(ProgramMilestonesListView, self).get_context_data(**kwargs)
        user = User.objects.filter(id__in=set(x.user_id for x in self.object.instanceassociationuser_set.all())).first()
        months = 0
        if self.object.get_months():
            months = self.object.get_months()
        levels = Program.objects.get(id=1).levels.filter(assign_min__lte=months, assign_max__gte=months)
        responses = self.object.response_set.all()
        lang = Language.objects.get(id=user.language_id).name
        groups = Group.objects.filter(assignationmessengeruser__user_id=user.pk)
        if not groups.exists():
            return redirect('instances:milestones_list', kwargs=dict(instance_id=self.kwargs['instance_id']))
        group = groups.first()
        c['group'] = group
        programs = group.programs.all()
        if not programs.exists():
            return redirect('instances:milestones_list', kwargs=dict(instance_id=self.kwargs['instance_id']))
        program = programs.first()
        c['program'] = program
        c['lang'] = lang
        if lang == 'en':
            c['hitos'] = 'Milestones of ' + self.object.name + ' (' + str(self.object.get_months()) + ')'
        elif lang == 'ar':
            c['hitos'] = ' (' + str(self.object.get_months()) + ')' + self.object.name + 'معالم '
        elif lang == 'pt':
            c['hitos'] = 'Marcos do ' + self.object.name + ' (' + str(self.object.get_months()) + ')'
        else:
            c['hitos'] = 'Hitos de ' + self.object.name + ' (' + str(self.object.get_months()) + ')'
        if levels.exists():
            level = levels.first()
            c['etapa'] = level.name
            if level.levellanguage_set.filter(language__name=lang).exists():
                c['etapa'] = level.levellanguage_set.filter(language__name=lang).first().name
            c['level'] = level
        c['milestones'] = set()
        for assign in program.programmilestonevalue_set.filter(min__lte=months, max__gte=months).order_by('min', 'max'):
            c['milestones'].add(assign.milestone)
        for m in c['milestones']:
            m_responses = responses.filter(milestone_id=m.pk)
            m.label = m.milestonetranslation_set.get(language__name='es').name
            translations = m.milestonetranslation_set.filter(language__name=lang)
            if translations.exists():
                m.label = translations.last().name
            if m_responses.exists():
                m.status = m_responses.last().response
                print(m.status)
        return c


class ProgramInstanceMilestonesView(DetailView):
    model = Instance
    pk_url_kwarg = 'instance_id'
    template_name = 'instances/instance_milestones.html'

    def get_context_data(self, **kwargs):
        c = super(ProgramInstanceMilestonesView, self).get_context_data(**kwargs)
        months = 0
        if self.object.get_months():
            months = self.object.get_months()
        user = self.object.get_users().first()
        c['months'] = months
        group = Group.objects.filter(assignationmessengeruser__user_id=user.pk).first()
        c['group'] = group
        program = group.programs.first()
        c['program'] = program
        print(group, program)
        print(program.areas.all())
        levels = Program.objects.get(id=1).levels.filter(assign_min__lte=months, assign_max__gte=months)
        level = levels.first()
        lang = Language.objects.get(id=self.object.get_users().first().language_id).name
        c['image_name'] = 'images/'+level.image
        c['etapa'] = level.name
        if level.levellanguage_set.filter(language__name=lang).exists():
            c['etapa'] = level.levellanguage_set.filter(language__name=lang).first().name
        responses = self.object.response_set.all()
        m_ids = set(p.milestone_id for p in program.programmilestonevalue_set.filter(min__lte=months, max__gte=months))
        print(m_ids)
        for area in Area.objects.filter(topic_id=1):
            c['trabajo_' + str(area.id)] = 0
            c['trabajo_' + str(area.id)+'_total'] = 0
            milestones = Milestone.objects.filter(areas__in=[area], min__lte=months, max__gte=months, id__in=m_ids)\
                .order_by('value')
            for m in milestones:
                m_responses = responses.filter(milestone_id=m.pk).order_by('-id')
                if m_responses.exists():
                    if m_responses.first().response == 'done':
                        c['trabajo_'+str(area.id)] += 1
                c['trabajo_'+str(area.id)+'_total'] += 1
            if c['trabajo_' + str(area.id)+'_total'] == 0:
                c['trabajo_' + str(area.id) + '_total'] = 1
        c['activities'] = self.object.get_completed_activities('session').count()
        c['lang'] = lang
        return c


class ProgramInstanceReportView(DetailView):
    model = Instance
    pk_url_kwarg = 'instance_id'
    template_name = 'instances/new_program_report.html'

    def get_context_data(self, **kwargs):
        c = super(ProgramInstanceReportView, self).get_context_data(**kwargs)
        # c['response'] = self.object.response_set.last()
        # c['milestone'] = c['response'].milestone
        # c['values'] = c['milestone'].milestoneareavalue_set.all()
        # print(c)
        return c
