from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from articles import models


class ArticleDetailView(DetailView):
    model = models.Article
    pk_url_kwarg = 'article_id'

    def get_context_data(self, **kwargs):
        c = super(ArticleDetailView, self).get_context_data()
        print(self.request.GET)
        if 'licence' in self.request.GET:
            c['object'].content = c['object'].content + "?licence=%s" % self.request.GET['licence']
        return c


class ArticleListView(PermissionRequiredMixin, ListView):
    permission_required = 'articles.view_article'
    model = models.Article
    paginate_by = 10


class TopicListView(PermissionRequiredMixin, ListView):
    permission_required = 'articles.view_topic'
    model = models.Topic
    paginate_by = 20


class ArticleCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'articles.add_article'
    model = models.Article
    fields = ('name', 'content', 'text_content', 'min', 'max', 'preview', 'thumbnail')

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
    fields = ('name', 'content', 'text_content', 'min', 'max', 'preview', 'thumbnail')
    pk_url_kwarg = 'article_id'

    def get_context_data(self, **kwargs):
        c = super(ArticleUpdateView, self).get_context_data()
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, "Article with ID %s has been updated. " % self.object.pk)
        return reverse_lazy('articles:article_edit', kwargs={'article_id': self.object.pk})


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


class TopicDetailView(DetailView):
    model = models.Topic
    pk_url_kwarg = 'topic_id'

    def get_context_data(self, **kwargs):
        c = super(TopicDetailView, self).get_context_data()
        return c


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
