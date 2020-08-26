from django.views.generic import DetailView, UpdateView, ListView, CreateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from languages.models import MilestoneTranslation
from milestones.models import Milestone
from django.urls import reverse_lazy
from django.contrib import messages


class HomeView(PermissionRequiredMixin, ListView):
    login_url = reverse_lazy('static:login')
    permission_required = 'milestones.view_milestone'
    model = Milestone
    context_object_name = 'milestones'
    paginate_by = 20

    def get_context_data(self, *, object_list=None, **kwargs):
        c = super(HomeView, self).get_context_data()
        c['get_params'] = self.request.GET.copy()
        if 'page' in c['get_params']:
            del c['get_params']['page']
        c['get_params'] = c['get_params'].urlencode()
        return c


class MilestoneView(PermissionRequiredMixin, DetailView):
    permission_required = 'milestones.view_milestone'
    login_url = reverse_lazy('static:login')
    model = Milestone
    pk_url_kwarg = 'milestone_id'


class EditMilestoneView(PermissionRequiredMixin, UpdateView):
    login_url = reverse_lazy('static:login')
    permission_required = 'milestones.add_milestone'
    model = Milestone
    fields = ('name', 'code', 'second_code', 'area', 'value', 'secondary_value', 'source', 'description')
    pk_url_kwarg = 'milestone_id'
    context_object_name = 'milestone'

    def get_success_url(self):
        messages.success(self.request, 'Milestone with Code: "%s" has been updated.' % self.object.code)
        return reverse_lazy('milestones:milestone', kwargs={'milestone_id': self.object.pk})

    def get_context_data(self, **kwargs):
        c = super(EditMilestoneView, self).get_context_data()
        c['action'] = 'Edit'
        return c


class NewMilestoneView(PermissionRequiredMixin, CreateView):
    login_url = reverse_lazy('static:login')
    permission_required = 'milestones.change_milestone'
    model = Milestone
    fields = ('name', 'code', 'second_code', 'area', 'value', 'secondary_value', 'source', 'description')

    def get_success_url(self):
        messages.success(self.request, 'Milestone with Code: "%s" has been created.' % self.object.code)
        return reverse_lazy('milestones:milestone', kwargs={'milestone_id': self.object.pk})

    def get_context_data(self, **kwargs):
        c = super(NewMilestoneView, self).get_context_data()
        c['action'] = 'Create'
        return c


class DeleteMilestoneView(PermissionRequiredMixin, DeleteView):
    login_url = reverse_lazy('static:login')
    template_name = 'milestones/milestone_form.html'
    permission_required = 'milestones.delete_milestone'
    model = Milestone
    pk_url_kwarg = 'milestone_id'

    def get_context_data(self, **kwargs):
        c = super(DeleteMilestoneView, self).get_context_data()
        c['action'] = 'Delete'
        c['delete_message'] = 'Are you sure to delete milestone with name: "%s"' % self.object.name
        return c

    def get_success_url(self):
        messages.success(self.request, 'Milestone with Code: "%s" has been deleted.' % self.object.code)
        return reverse_lazy('milestones:index')


class MilestoneTranslationCreateView(PermissionRequiredMixin, CreateView):
    login_url = reverse_lazy('static:login')
    permission_required = 'languages.add_milestonetranslation'
    model = MilestoneTranslation
    fields = ('name', 'description', 'language', 'language_code')

    def get_context_data(self, **kwargs):
        c = super(MilestoneTranslationCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['milestone'] = Milestone.objects.get(id=self.kwargs['milestone_id'])
        return c
    
    def form_valid(self, form):
        form.instance.milestone_id = self.kwargs['milestone_id']
        return super(MilestoneTranslationCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "the translation has been added.")
        return reverse_lazy('milestones:milestone', kwargs=dict(milestone_id=self.kwargs['milestone_id']))


class MilestoneTranslationEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'languages.add_milestonetranslation'
    login_url = reverse_lazy('static:login')
    model = MilestoneTranslation
    pk_url_kwarg = 'translation_id'
    fields = ('name', 'description', 'language', 'language_code')

    def get_context_data(self, **kwargs):
        c = super(MilestoneTranslationEditView, self).get_context_data()
        c['action'] = 'Edit'
        c['milestone'] = Milestone.objects.get(id=self.kwargs['milestone_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "the translation has been updated.")
        return reverse_lazy('milestones:milestone', kwargs=dict(milestone_id=self.kwargs['milestone_id']))


class MilestoneTranslationDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'languages.delete_milestonetranslation'
    login_url = reverse_lazy('static:login')
    model = MilestoneTranslation
    pk_url_kwarg = 'translation_id'
    template_name = 'languages/milestonetranslation_form.html'

    def get_context_data(self, **kwargs):
        c = super(MilestoneTranslationDeleteView, self).get_context_data()
        c['action'] = 'Delete'
        c['delete_message'] = 'Are you sure to delete this translation?'
        c['milestone'] = Milestone.objects.get(id=self.kwargs['milestone_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "the translation has been deleted.")
        return reverse_lazy('milestones:milestone', kwargs=dict(milestone_id=self.kwargs['milestone_id']))
