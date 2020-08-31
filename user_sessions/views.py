from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView, RedirectView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from user_sessions import models


class SessionListView(PermissionRequiredMixin, ListView):
    permission_required = 'user_sessions.view_session'
    model = models.Session
    paginate_by = 30


class SessionDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'user_sessions.view_session'
    model = models.Session
    pk_url_kwarg = 'session_id'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(SessionDetailView, self).get_context_data()
        c['fields'] = self.object.field_set.order_by('position')
        c['last_field'] = c['fields'].last()
        return c


class SessionCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_session'
    model = models.Session
    fields = ('name', 'lang', 'min', 'max')

    def get_context_data(self, **kwargs):
        c = super(SessionCreateView, self).get_context_data()
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, "the session with ID: %s has created." % self.object.pk)
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.object.pk))


class SessionUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_session'
    model = models.Session
    fields = ('name', 'lang', 'min', 'max')
    pk_url_kwarg = 'session_id'

    def get_context_data(self, **kwargs):
        c = super(SessionUpdateView, self).get_context_data()
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, "the session with ID: %s has updated." % self.object.pk)
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.object.pk))


class SessionDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_session'
    model = models.Session
    pk_url_kwarg = 'session_id'

    def get_success_url(self):
        messages.success(self.request, "the session with ID: %s has deleted." % self.object.pk)
        return reverse_lazy('sessions:session_list')


class FieldCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_field'
    model = models.Field
    fields = ('field_type', )

    def get_context_data(self, **kwargs):
        c = super(FieldCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        return c

    def form_valid(self, form):
        session = models.Session.objects.get(id=self.kwargs['session_id'])
        form.instance.session_id = self.kwargs['session_id']
        form.instance.position = session.field_set.count()
        return super(FieldCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Field added to session.')
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class FieldDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.add_field'
    model = models.Field
    pk_url_kwarg = 'field_id'

    def get_success_url(self):
        fields = self.object.session.field_set.filter(position__gt=self.object.position)
        for field in fields:
            field.position = field.position - 1
            field.save()
        messages.success(self.request, "Field has been deleted.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class FieldUpView(PermissionRequiredMixin, RedirectView):
    permission_required = 'user_sessions.change_field'
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        field = models.Field.objects.get(id=self.kwargs['field_id'])
        top_field = models.Field.objects.get(position=(field.position - 1))
        field.position = field.position - 1
        top_field.position = top_field.position + 1
        field.save()
        top_field.save()
        messages.success(self.request, "Changed position for fields.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class FieldDownView(PermissionRequiredMixin, RedirectView):
    permission_required = 'user_sessions.change_field'
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        field = models.Field.objects.get(id=self.kwargs['field_id'])
        bottom_field = models.Field.objects.get(position=(field.position + 1))
        field.position = field.position + 1
        bottom_field.position = bottom_field.position - 1
        field.save()
        bottom_field.save()
        messages.success(self.request, "Changed position for fields.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class MessageCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_message'
    model = models.Message
    fields = ('text', )

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        return super(MessageCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        c = super(MessageCreateView, self).get_context_data()
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, "Message added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class MessageEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_message'
    model = models.Message
    fields = ('text', )
    pk_url_kwarg = 'message_id'

    def get_context_data(self, **kwargs):
        c = super(MessageEditView, self).get_context_data()
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        c['action'] = 'Update'
        return c

    def get_success_url(self):
        messages.success(self.request, "Message changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class MessageDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_message'
    model = models.Message
    pk_url_kwarg = 'message_id'

    def get_success_url(self):
        messages.success(self.request, "Message deleted in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ReplyCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_reply'
    model = models.Reply
    fields = ('label', 'attribute', 'value', 'redirect_block')

    def get_context_data(self, **kwargs):
        c = super(ReplyCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        form.instance.session_id = self.kwargs['session_id']
        return super(ReplyCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Reply added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ReplyEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_reply'
    model = models.Reply
    fields = ('label', 'attribute', 'value', 'redirect_block')
    pk_url_kwarg = 'reply_id'

    def get_context_data(self, **kwargs):
        c = super(ReplyEditView, self).get_context_data()
        c['action'] = 'Edit'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "Reply changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class ReplyDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_reply'
    model = models.Reply
    pk_url_kwarg = 'reply_id'

    def get_context_data(self, **kwargs):
        c = super(ReplyDeleteView, self).get_context_data()
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "Reply deleted in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class RedirectBlockCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_redirectblock'
    model = models.RedirectBlock
    fields = ('block', )

    def get_context_data(self, **kwargs):
        c = super(RedirectBlockCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        return super(RedirectBlockCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Redirect Block added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class RedirectBlockEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_redirectblock'
    model = models.RedirectBlock
    fields = ('block', )
    pk_url_kwarg = 'block_id'

    def get_context_data(self, **kwargs):
        c = super(RedirectBlockEditView, self).get_context_data()
        c['action'] = 'Edit'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, "Redirect Block changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class RedirectBlockDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_redirectblock'
    model = models.RedirectBlock
    pk_url_kwarg = 'block_id'

    def get_success_url(self):
        messages.success(self.request, "Redirect Block has deleted.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))
