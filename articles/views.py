from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from messenger_users.models import User
from django.urls import reverse_lazy
from django.contrib import messages
from articles import models


class ArticleDetailView(DetailView):
    model = models.Article
    pk_url_kwarg = 'article_id'

    def get_context_data(self, **kwargs):
        c = super(ArticleDetailView, self).get_context_data()
        print(self.request.GET)
        if 'key' in self.request.GET:
            default_license = 'free'
            user = User.objects.get(last_channel_id=self.request.GET['key'])
            licenses = user.userdata_set.filter(data_key='tipo_de_licencia')
            if licenses.count() > 0:
                default_license = licenses.last().data_value
            c['object'].content = c['object'].content + "?&?license=%s" % default_license
        return c


class ArticleListView(PermissionRequiredMixin, ListView):
    permission_required = 'articles.view_article'
    model = models.Article
    paginate_by = 20


class ArticleCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'articles.add_article'
    model = models.Article
    fields = ('name', 'content', 'text_content', 'min', 'max', 'preview', 'thumbnail', 'campaign')

    def get_context_data(self, **kwargs):
        c = super(ArticleCreateView, self).get_context_data()
        c['action'] = 'Create'
        return c
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ArticleCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Article with ID %s has been created. " % self.object.pk)
        return reverse_lazy('articles:article_edit', kwargs={'article_id': self.object.pk})


class ArticleUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'articles.change_article'
    model = models.Article
    fields = ('name', 'content', 'text_content', 'min', 'max', 'preview', 'thumbnail', 'campaign')
    pk_url_kwarg = 'article_id'

    def get_context_data(self, **kwargs):
        c = super(ArticleUpdateView, self).get_context_data()
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, "Article with ID %s has been updated. " % self.object.pk)
        return reverse_lazy('articles:article_edit', kwargs={'article_id': self.object.pk})


class TopicDetailView(DetailView):
    model = models.Topic
    pk_url_kwarg = 'topic_id'

    def get_context_data(self, **kwargs):
        c = super(TopicDetailView, self).get_context_data()
        print(self.request.GET)
        return c


class TopicListView(PermissionRequiredMixin, ListView):
    permission_required = 'articles.view_topic'
    model = models.Topic
    paginate_by = 20


class TopicCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'articles.add_topic'
    model = models.Topic
    fields = ('name')

    def get_context_data(self, **kwargs):
        c = super(TopicCreateView, self).get_context_data()
        c['action'] = 'Create'
        return c

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TopicCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Topic with ID %s has been created. " % self.object.pk)
        return reverse_lazy('articles:topic_edit', kwargs={'topic_id': self.object.pk})


class TopicUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'articles.change_topic'
    model = models.Topic
    fields = ('name')
    pk_url_kwarg = 'topic_id'

    def get_context_data(self, **kwargs):
        c = super(TopicUpdateView, self).get_context_data()
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, "Topic with ID %s has been updated. " % self.object.pk)
        return reverse_lazy('articles:topic_edit', kwargs={'topic_id': self.object.pk})
