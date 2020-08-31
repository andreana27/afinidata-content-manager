from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from messenger_users.models import User
from django.urls import reverse_lazy
from django.contrib import messages
from channels.models import Channel


class HomeView(PermissionRequiredMixin, ListView):
    model = Channel
    context_object_name = 'channels'
    login_url = reverse_lazy('pages:login')


class ChannelView(LoginRequiredMixin, DetailView):
    model = Channel
    pk_url_kwarg = 'channel_id'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(ChannelView, self).get_context_data()

        return c


class CreateChannelView(LoginRequiredMixin, CreateView):
    model = Channel
    fields = ('name', 'description')
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(CreateChannelView, self).get_context_data()
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Channel with name: %s has been created.' % self.object.name)
        return reverse_lazy('channels:channel_detail', kwargs={'channel_id': self.object.pk})


class UpdateChannelView(LoginRequiredMixin, UpdateView):
    model = Channel
    fields = ('name', 'description')
    pk_url_kwarg = 'channel_id'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(UpdateChannelView, self).get_context_data()
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Channel with name: %s has been updated.' % self.object.name)
        return reverse_lazy('channels:channel', kwargs={'id': self.object.pk})


class DeleteChannelView(LoginRequiredMixin, DeleteView):
    model = Channel
    template_name = 'channels/channel_form.html'
    pk_url_kwarg = 'channel_id'
    login_url = reverse_lazy('pages:login')

    def get_context_data(self, **kwargs):
        c = super(DeleteChannelView, self).get_context_data()
        c['action'] = 'Delete'
        c['delete_message'] = 'Are you sure to delete channel with name: "%s"' % self.object.name
        return c

    def get_success_url(self):
        messages.success(self.request, 'Channel with name "%s" has been deleted.' % self.object.name)
        return reverse_lazy('channels:channel_list')
