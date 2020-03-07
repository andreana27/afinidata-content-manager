from django.views.generic import TemplateView, UpdateView, CreateView, DeleteView, DetailView, ListView, View
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView
from posts.models import Post, Interaction, Feedback, Label, Question, Response, Review, UserReviewRole, Approbation, \
    Rejection, ReviewComment, QuestionResponse, MessengerUserCommentPost, Tip, TipSerializer, Taxonomy
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from posts import forms
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from messenger_users.models import User, UserActivity
from django.contrib.auth.models import User as DjangoUser
from django.contrib import messages
from datetime import datetime, timedelta
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
import math
import random
import pytz
import requests
from posts.models import STATUS_CHOICES
from posts import serializers
import logging
## FIXME : lots of issues; simplfy, create validator decorator, auth, duplication, unused vars.

import celery
from json import loads as json_loads

logger = logging.getLogger(__name__)


class HomeView(LoginRequiredMixin, ListView):
    template_name = 'posts/index.html'
    model = Post
    context_object_name = 'posts'
    paginate_by = 30
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        try:
            params = dict()
            if self.request.GET.get('name'):
                params['name__contains'] = self.request.GET['name']
            if self.request.GET.get('user_id'):
                params['user_id'] = self.request.GET['user_id']
            if self.request.GET.get('status'):
                params['status'] = self.request.GET['status']

            try:
                if self.request.GET['tags']:
                    tagsList = self.request.GET.getlist('tags')
                    tag_posts = Post.objects.filter(label__name__in=tagsList)
                    posts = tag_posts.filter(**params)
                    print(posts)
            except Exception as e:
                posts = Post.objects.filter(**params)
            return posts
        except Exception as e:
            logger.warning("error when filtering")
            logger.warning(e)
            return Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        get_copy = self.request.GET.copy()
        parameters = get_copy.pop('page', True) and get_copy.urlencode()
        context['parameters'] = parameters
        context['status_list'] = [item[0] for item in STATUS_CHOICES]
        context['tags'] = Label.objects.all()
        try:
            context['request_tags'] = self.request.GET.getlist('tags')
        except:
            context['request_tags'] = []
        print(context['request_tags'])

        try:
            params = dict()
            if self.request.GET.get('name'):
                params['name__contains'] = self.request.GET['name']
                context['name'] = self.request.GET['name']
            if self.request.GET.get('user_id'):
                params['user_id'] = self.request.GET['user_id']
                context['user_id'] = int(self.request.GET['user_id'])
            if self.request.GET.get('status'):
                params['status'] = self.request.GET['status']
                context['status'] = self.request.GET['status']
            posts = Post.objects.filter(**params)
            logger.info(params)
            logger.info(posts)
            try:
                if self.request.GET['tags']:
                    tagsList = self.request.GET.getlist('tags')
                    tag_posts = Post.objects.filter(label__name__in=tagsList)
                    posts = tag_posts.filter(**params)
            except:
                pass
            context['total'] = posts.count()
        except Exception as e:
            context['total'] = Post.objects.all().count()
            pass
        try:
            group = Group.objects.get(name='author')
            users = group.user_set.all()
            context['users'] = users
        except Exception as e:
            logger.error(e)

        for post in context['posts']:
            post.clicks = post.interaction_set.filter(type='opened').count()
            session_total = 0
            users = set()
            sessions = post.interaction_set.filter(type='session')
            for session in sessions:
                users.add(session.user_id)
                session_total = session_total + int(session.value)
            post.session_total = session_total
            if sessions.count() > 0:
                post.session_average = round(session_total / sessions.count(), 2)
            else:
                post.session_average = 0
            feedback_total = 0
            feedback_list = post.feedback_set.all()
            for feedback in feedback_list:
                feedback_total = feedback_total + int(feedback.value)
            post.feedback_total = feedback_total
            if feedback_list.count() > 0:
                post.feedback_average = round(feedback_total / feedback_list.count(), 2)
                post.feedback_total_users = feedback_list.count()
            else:
                post.feedback_average = 0
                post.feedback_total_users = 0
            posts_sended = post.interaction_set.filter(type='sended')
            if posts_sended.count() > 0:
                users_to_sended = set()
                for interaction in posts_sended:
                    users_to_sended.add(interaction.user_id)
                post.total_sended_users = len(users_to_sended)
            else:
                post.total_sended_users = 0
            post.users = len(users)
            posts_used = post.interaction_set.filter(type='used')
            if posts_used.count() > 0:
                users_to_used = set()
                for interaction in posts_used:
                    users_to_used.add(interaction.user_id)
                post.total_used_users = len(users_to_used)
            else:
                post.total_used_users = 0
        return context


def fetch_post(request, id):

    if request.method == 'GET':
        post = Post.objects.get(id=id)
        user = None
        try:
            username = request.GET['username']
            user = User.objects.get(username=username)
            logger.info('fetching post for user : ', user)
        except:
            logger.warning('not user with username')
            pass

        if not user:
            try:
                channel_id = request.GET['channel_id']
                user = User.objects.get(last_channel_id=channel_id)
            except:
                logger.warning('not user with last channel id')
                pass

        if not user:
            try:
                channel_id = request.GET['channel_id']
                user = User.objects.get(channel_id=channel_id)
            except:
                logger.warning('not user with channel id')
                pass

        if user:
            try:

                bot_id = request.GET['bot_id']
                o = Interaction\
                    .objects\
                    .create(
                        post=post,
                        channel_id=user.last_channel_id,
                        username=user.username,
                        bot_id=bot_id,
                        type='opened',
                        user_id=user.pk
                )
                o.save()
                post_session = Interaction(post=post,
                                           channel_id=user.last_channel_id,
                                           bot_id=bot_id,
                                           username=user.username,
                                           type='session',
                                           user_id=user.pk,
                                           value=-1)
                post_session.save()

                try:
                    ua = UserActivity.objects.get(user_id=user.id)
                    ua.open_post()
                    ua.save()
                except Exception:
                    logger.exception("fail on setting opened User Activity")

                return render(request, 'posts/post.html',
                              {'post': post, 'session_id': post_session.pk})
            except:
                return render(request, 'posts/post.html', {'post': post, 'session_id': 'null'})

        return render(request, 'posts/post.html', {'post': post, 'session_id': 'null'})


class StatisticsView(TemplateView):
    template_name = 'posts/statistics.html'

    def get_context_data(self, **kwargs):
        #context = super().get_context_data(**kwargs)
        context = dict()
        view_post = Post.objects.get(id=kwargs['id'])
        clicks = view_post.interaction_set.filter(type='opened')
        sessions = view_post.interaction_set.filter(type='session')
        feedbacks = view_post.feedback_set.all()
        users = set()
        context['post'] = view_post
        context['clicks'] = clicks
        context['sessions'] = sessions
        context['domain'] = settings.DOMAIN_URL

        sessions_minutes = 0
        for session in sessions:
            users.add(session.user_id)
            if session.value != 0:
                sessions_minutes = sessions_minutes + int(session.value)
            else:
                sessions_minutes = sessions_minutes + .3

        context['channel_users'] = len(users)

        sessions_minutes = math.floor(sessions_minutes)
        context['session_minutes'] = sessions_minutes
        if sessions.count() > 0:
            context['session_average'] = round(sessions_minutes / int(sessions.count()), 2)
        else:
            context['session_average'] = 0

        feedback_total = 0

        for feedback in feedbacks:
            feedback_total = feedback_total + int(feedback.value)

        context['feedback_total'] = feedback_total
        if feedbacks.count() > 0:
            context['feedback_average'] = round(feedback_total / feedbacks.count(), 2)
        else:
            context['feedback_average'] = 0
        context['feedback_ideal'] = feedbacks.count() * 5

        return context


class NewPostView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ('name', 'thumbnail', 'new', 'min_range', 'max_range', 'content',
              'content_activity', 'preview')
    template_name = 'posts/new.html'
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def form_valid(self, form):
        print(form)
        user = self.request.user
        post = form.save(commit=False)
        post.user = user
        post.save()
        messages.success(self.request, 'The post with id %s has been created' % post.pk)
        return redirect('posts:edit-post', id=post.pk)

@csrf_exempt
def set_taxonomy(request):
    post = get_object_or_404(Post, id=request.POST.get("post"))
    t = forms.UpdateTaxonomy(instance = post.taxonomy, data=request.POST)
    if t.is_valid():
        taxonomy = t.save(commit=False)
        post.taxonomy = taxonomy
        taxonomy.save()
        post.save()
    return redirect('posts:edit-post', id=post.pk)


class EditPostView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = Post
    pk_url_kwarg = 'id'
    context_object_name = 'post'
    fields = ('name', 'thumbnail', 'new', 'min_range', 'max_range', 'content',
              'content_activity', 'preview')
    template_name = 'posts/edit.html'

    def form_valid(self, form):
        post = form.save()
        return redirect('posts:edit-post', id=post.pk)

    def get_context_data(self, **kwargs):
        id_post_context = self.kwargs['id']
        context = super().get_context_data()
        user = self.request.user
        post = get_object_or_404(Post, id=id_post_context)
        if user.is_superuser:
            context['role'] = 'superuser'
        elif post.user == user:
            context['role'] = 'owner'
        else:
            last_reviews = Review.objects.filter(post=post, status='pending').order_by('-id')[:1]
            if not last_reviews.count() > 0:
                post = get_object_or_404(Post, id=id_post_context)

            last_review = last_reviews.first()
            try:
                review = get_object_or_404(UserReviewRole, review=last_review, user=user)
                context['role'] = 'reviser'
                context['review'] = review.id
            except Http404:
                context['role'] = 'reviser'
                context['review'] = None
        try:
            tax = post.taxonomy
            ftax = forms.UpdateTaxonomy(instance=tax)
            context['tax'] = ftax
        except Post.taxonomy.RelatedObjectDoesNotExist:
            logger.exception("no taxonomy object on post, lets set")
            try:
                post.taxonomy = forms.UpdateTaxonomy(instance=tax)
                context['tax'] = post.taxonomy
            except:
                logger.exception("no taxonomy available")
        return context


@csrf_exempt
def edit_interaction(request, id):

    if request.method == 'POST':

        print(request.POST)

        try:
            interaction = Interaction.objects.filter(pk=id).update(value=request.POST['minutes'])
            return JsonResponse(dict(
                status='updated',
                interaction=interaction
            ))
        except:
            raise Http404('Error')

    else:
        return JsonResponse(dict(hello="world"))


@csrf_exempt
def feedback(request):
    if request.method == 'POST':
        user = None
        print(request.POST)
        try:
            username = request.POST['username']
            user = User.objects.get(username=username)
            print('user: ', user)
        except:
            print('not user with username')
            pass

        if not user:
            try:
                channel_id = request.POST['channel_id']
                user = User.objects.get(last_channel_id=channel_id)
                print(user)
            except:
                print('not user with last channel id')
                pass

        if not user:
            try:
                channel_id = request.POST['channel_id']
                user = User.objects.get(channel_id=channel_id)
                print(user)
            except:
                print('not user with channel id')
                pass

        try:
            if request.POST \
               and len(request.POST) >= 4 \
               and request.POST['bot_id'] \
               and user \
               and request.POST['post_id'] \
               and request.POST['value']:
                print(request.POST)
                active_feedback = Feedback.objects.filter(bot_id=request.POST['bot_id'],
                                                          user_id=user.pk,
                                                          post_id=request.POST['post_id'])
                if not active_feedback:
                    if 1 <= int(request.POST['value']) <= 5:
                        new_feedback = Feedback.objects.create(bot_id=request.POST['bot_id'],
                                                               channel_id=user.last_channel_id,
                                                               post_id=request.POST['post_id'],
                                                               user_id=user.pk,
                                                               value=request.POST['value'],
                                                               username=user.username)

                        return JsonResponse(dict(status='created',
                                                 data=dict(
                                                     id=new_feedback.pk,
                                                     post_id=new_feedback.post_id,
                                                     user_id=new_feedback.user_id,
                                                     bot_id=new_feedback.bot_id,
                                                     value=new_feedback.value,
                                                     username=user.username
                                                 )))
                    else:
                        return JsonResponse(dict(status='error',
                                                 error='value is not valid'))
                else:
                    change_feedback = Feedback.objects.get(bot_id=request.POST['bot_id'],
                                                           user_id=user.pk,
                                                           post_id=request.POST['post_id'])

                    if change_feedback.value != int(request.POST['value']) \
                       and 1 <= int(request.POST['value']) <= 5:

                        change_feedback.value = request.POST['value']
                        change_feedback.save(update_fields=['value'])
                        return JsonResponse(dict(status='updated',
                                                 data=dict(
                                                     id=change_feedback.pk,
                                                     post_id=change_feedback.post_id,
                                                     user_id=change_feedback.user_id,
                                                     bot_id=change_feedback.bot_id,
                                                     value=change_feedback.value,
                                                     username=user.username
                                                 )))
                    else:
                        return JsonResponse(dict(status='not-updated',
                                                 data=dict(
                                                     id=change_feedback.pk,
                                                     post_id=change_feedback.post_id,
                                                     user_id=change_feedback.user_id,
                                                     bot_id=change_feedback.bot_id,
                                                     value=change_feedback.value,
                                                     username=user.username
                                                 )))

            else:
                return JsonResponse(dict(status='error',
                                         error='invalid params'))
        except Exception as e:
            return JsonResponse(dict(status='error',
                                     error='invalid params'))

    else:
        raise Http404('Not found')


class DeletePostView(LoginRequiredMixin, DeleteView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = Post
    template_name = 'posts/delete.html'
    pk_url_kwarg = 'id'
    context_object_name = 'post'

    success_url = '/posts/'


@csrf_exempt
def create_tag(request):

    if request.method == 'POST':
        print(request)
        try:
            name = request.POST['name']
        except:
            name = None
        if not name:
            return JsonResponse(dict(status='error', error='Param name not defined'))

        possible_tag = Label.objects.filter(name=name)

        if len(possible_tag) > 0:
            return JsonResponse(dict(status='error', error='Label exists'))

        new_label = Label.objects.create(name=name)

        if new_label:
            return JsonResponse(dict(status='created', data=dict(id=new_label.pk, name=new_label.name)))

        else:
            return JsonResponse(dict(status='error', error='not identified error'))

    else:
        raise Http404('Not found')


@csrf_exempt
def tags(request):
    tags = Label.objects.all()
    show_tags = []

    for tag in tags:
        new_tag = dict(id=tag.pk, name=tag.name)
        show_tags.append(new_tag)

    return JsonResponse(dict(status='founded', data=show_tags))

@csrf_exempt
def set_tag_to_post(request, id):
    if request.method == 'POST':

        try:
            post = Post.objects.get(id=id)
        except:
            post = None

        if not post:
            return JsonResponse(dict(status='error', error='Post with id not exists'))

        try:
            tag = request.POST['name']
        except:
            tag = None

        if not tag:
            return JsonResponse(dict(status='error', error='param tag not present'))

        try:
            tag = Label.objects.get(name=tag)
        except:
            tag = None

        if not tag:
            return JsonResponse(dict(status='error',
                                     error='tag with name {name} not exist'.format(name=request.POST['name'])))

        tags = post.label_set.filter(id=tag.pk)

        if len(tags) > 0:
            return JsonResponse(dict(status='error', error='posts has tag now'))

        tag.posts.add(post)
        return JsonResponse(dict(status='added', data=dict(id=tag.pk, name=tag.name)))
    else:
        raise Http404('Not found')

@csrf_exempt
def get_tags_for_post(request, id):

    if request.method == 'GET':
        try:
            post = Post.objects.get(id=id)
        except:
            post = None

        if not post:
            return JsonResponse(dict(status='error', error='Post with id not exists'))

        tags = post.label_set.all()
        show_tags = []

        for tag in tags:
            show_tags.append(dict(id=tag.pk, name=tag.name))

        return JsonResponse(dict(status='founded', data=show_tags))

    else:
        raise Http404('Not found')

@csrf_exempt
def remove_tag_for_post(request, id):

    if request.method != 'POST':
        raise Http404('Not found')

    try:
        post = Post.objects.get(id=id)
        print(post)
    except:
        post = None

    if not post:
        return JsonResponse(dict(status='error', error='Post with id not founded'))

    try:
        tag = request.POST['name']
    except:
        tag = None

    if not tag:
        return JsonResponse(dict(status='error', error='Param name not set'))

    try:
        tag = Label.objects.get(name=tag)
    except:
        tag = None

    if not tag:
        return JsonResponse(dict(status='error', error='Tag with name not exist'))

    try:
        search_tag = post.label_set.get(id=tag.pk)
        logger.info('found tag to remove')
        logger.info(search_tag)
    except:
        search_tag = None

    if not search_tag:
        return JsonResponse(dict(status='error', error='Post has not tag with name'))

    result = post.label_set.remove(tag)
    logger.info(result)
    return JsonResponse(dict(status='removed', data=dict(id=tag.pk, name=tag.name)))


class PostsListView(LoginRequiredMixin, TemplateView):

    template_name = 'posts/list.html'
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, *args, **kwargs):
        context = dict()
        context['domain'] = settings.DOMAIN_URL
        posts = Post.objects.all()
        for post in posts:
            post.clicks = post.interaction_set.filter(type='opened').count()
            session_total = 0
            users = set()
            sessions = post.interaction_set.filter(type='session')
            for session in sessions:
                users.add(session.user_id)
                session_total = session_total + int(session.value)
            post.session_total = session_total
            if sessions.count() > 0:
                post.session_average = round(session_total / sessions.count(), 2)
            else:
                post.session_average = 0
            feedback_total = 0
            feedback_list = post.feedback_set.all()
            for feedback in feedback_list:
                feedback_total = feedback_total + int(feedback.value)
            post.feedback_total = feedback_total
            if feedback_list.count() > 0:
                post.feedback_average = round(feedback_total / feedback_list.count(), 2)
                post.feedback_total_users = feedback_list.count()
            else:
                post.feedback_average = 0
                post.feedback_total_users = 0
            posts_sended = post.interaction_set.filter(type='sended')
            if posts_sended.count() > 0:
                users_to_sended = set()
                for interaction in posts_sended:
                    users_to_sended.add(interaction.user_id)
                post.total_sended_users = len(users_to_sended)
            else:
                post.total_sended_users = 0
            post.users = len(users)
            posts_used = post.interaction_set.filter(type='used')
            if posts_used.count() > 0:
                users_to_used = set()
                for interaction in posts_used:
                    users_to_used.add(interaction.user_id)
                post.total_used_users = len(users_to_used)
                print(len(users_to_used))
            else:
                post.total_used_users = 0
        context['posts'] = posts

        return context


def getting_posts_reco(request):
    from django.conf import settings

    BROKER = getattr(settings, "CELERY_BROKER")

    logger.info("recommend posts for user")
    months_old_value = 0
    uid = 0
    try:
        months_old_value = int(request.GET['value'])
        uid = int(request.GET['user_id'])
    except:
        logger.exception("Invalid params on recommend get post")
        return JsonResponse(dict(status='error', error='Invalid params.'))

    logger.info("Fetching recommended posts for user {} at {} months".format(uid, months_old_value))

    broker = BROKER
    app = celery.Celery('tasks', backend='rpc://', broker=broker, broker_pool_limit=None)

    recoo = {}

    try:
        reco_sign = celery.signature('afinidata_recommender.tasks.tasks.recommend', (uid, months_old_value))
        reco_obj = reco_sign.delay()
        reco_res = app.AsyncResult(reco_obj)
        reco_data = reco_res.get()
        recoo = json_loads(reco_data)
    except:
        logger.exception("Invalid params on recommend get post")
        return JsonResponse(dict(status='error', error='Invalid params.'))

    logger.warning(f"fetched for user id {uid} recommends {recoo}")
    recommend_id = list(recoo["post_id"].values())[0]

    posto = Post.objects.filter(pk=recommend_id).first()

    post_dispatch = Interaction(post=posto, user_id=uid, type='dispatched', value=1)
    post_dispatch.save()

    resp = dict(
            post_id=posto.pk,
            post_uri=settings.DOMAIN_URL + '/posts/' + str(posto.pk),
            post_preview=posto.preview,
            post_title=posto.name,
            warn=None
        )

    logging.warning("sent activity: {}".format(resp))

    return JsonResponse(dict(
        set_attributes=resp,
        messages=[],
    ))


def get_posts_for_user(request):
    if request.method == 'POST':
        return JsonResponse(dict(status='error', error='Invalid method.'))

    logger.info("getting posts for user")

    months_old_value = 0
    user = None
    warning_message = None
    is_premium = False
    locale = None
    try:
        locale = request.GET.get('locale')
        months_old_value = int(request.GET['value'])
        username = request.GET['username']
        user = User.objects.get(username=username)
        is_premium = request.GET['premium']
    except Exception as e:
        logger.error("Invalid Parameters on getting posts for user")
        logger.error(e)
        logger.error(request.POST)
        return JsonResponse(dict(status='error', error='Invalid params.'))
    #TODO: DO LOCALE!!!

    logger.info("Fetching posts for user {} at {} months".format(user, months_old_value))

    today = datetime.now()
    days = timedelta(days=35)
    date_limit = today - days
    ## Fetch sent activities to exclude
    interactions = Interaction.objects.filter(user_id=user.pk, type='sended', created_at__gt=date_limit)

    excluded = set()
    for interaction in interactions:
        if interaction.post_id:
            excluded.add(interaction.post_id)
    logger.info("excluding activities seen: {} ".format(excluded))

    if is_premium:
        if locale:
            posts = Post.objects \
                .exclude(id__in=excluded) \
                .filter(min_range__lte=months_old_value,
                        max_range__gte=months_old_value,
                        id__gte=473,
                        status='need_changes')
        else:
            posts = Post.objects \
                .exclude(id__in=excluded) \
                .filter(min_range__lte=months_old_value,
                        max_range__gte=months_old_value,
                        id__gte=208,
                        status='published')
    else:
        if locale:
            posts = Post.objects \
                .exclude(id__in=excluded) \
                .filter(min_range__lte=months_old_value,
                        max_range__gte=months_old_value,
                        id__gte=473,
                        status='need_changes')
        else:
            posts = Post.objects \
                .exclude(id__in=excluded) \
                .filter(min_range__lte=months_old_value,
                        max_range__gte=months_old_value,
                        status='published')

    if posts.count() <= 0:
        # Repeat; report error that has been seen.
        warning_message = 'no values without sended available'
        logger.warning(warning_message+ ": username {}".format(username))
        if locale:
            posts = Post.objects \
                .filter(min_range__lte=months_old_value,
                        max_range__gte=months_old_value,
                        id__gte=473,
                        status='need_changes')
        else:
            posts = Post.objects \
                .filter(min_range__lte=months_old_value,
                        max_range__gte=months_old_value,
                        status='published')

    rand_limit = random.randrange(0, posts.count())
    service_post = posts[rand_limit]
    if service_post.content_activity:
        activity = " -- ".join(service_post.content_activity.split('|'))
        logging.info("activity selected: {}".format(activity))

    post_dispatch = Interaction(post=service_post, user_id=user.id, type='dispatched', value=1)
    post_dispatch.save()

    try:
        ua = UserActivity.objects.get(user_id=user.id)
        ua.get_post()
        ua.save()
    except Exception:
        logger.exception("fail on setting User Activity")

    resp = dict(
            post_id=service_post.pk,
            post_uri=settings.DOMAIN_URL + '/posts/' + str(service_post.pk),
            post_preview=service_post.preview,
            post_title=service_post.name,
            warn=warning_message
        )

    logging.warning("sent activity: {}".format(resp))

    return JsonResponse(dict(
        set_attributes=resp,
        messages=[],
    ))


def post_activity(request, id):
    if request.method == 'POST':
        return JsonResponse(dict(status='error', error='Invalid params.'))

    try:
        search_post = Post.objects.get(id=id)
        post_count = int(request.GET['post_count'])
    except Exception as e:
        return JsonResponse(dict(status='error', error=str(e)))

    if not search_post.content_activity:
        return JsonResponse(dict(status='error', error='Post has not activity'))

    activity_array = search_post.content_activity.split('|')
    print(len(activity_array))
    if post_count > len(activity_array) - 1:
        return JsonResponse(dict(status='error', error='Invalid params.'))
    if post_count < len(activity_array) - 1:
        post_has_finished = False
    else:
        post_has_finished = True
    return JsonResponse(dict(
        set_attributes=dict(
            activity_content=activity_array[post_count].strip(),
            post_count=post_count + 1,
            post_has_finished=post_has_finished
        ),
        messages=[]
    ))


class QuestionsView(LoginRequiredMixin, TemplateView):
    template_name = 'posts/questions.html'
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        questions = Question.objects.all()
        return dict(questions=questions)


class CreateQuestion(LoginRequiredMixin, CreateView):
    model = Question
    template_name = 'posts/new-question.html'
    fields = ('name', 'post', 'replies')
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def form_valid(self, form):
        new_question = form.save()
        print(new_question)
        return redirect('posts:edit-post', id=new_question.post.pk)


class EditQuestion(LoginRequiredMixin, UpdateView):
    model = Question
    template_name = 'posts/question-edit.html'
    fields = ('name', 'post', 'replies')
    pk_url_kwarg = 'id'
    context_object_name = 'question'
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def form_valid(self, form):
        question = form.save()
        return redirect('posts:edit-post', id=question.post.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['response_form'] = forms.QuestionResponseForm()
        return context


class QuestionView(LoginRequiredMixin, DetailView):
    template_name = 'posts/question.html'
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = Question
    context_object_name = 'question'
    pk_url_kwarg = 'id'


class DeleteQuestionView(LoginRequiredMixin, DeleteView):
    template_name = 'posts/question-delete.html'
    model = Question
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    pk_url_kwarg = 'id'
    context_object_name = 'question'

    def get_success_url(self):
        q = self.get_object()
        post_pk = q.post.pk
        return redirect('posts:edit-post', id=post_pk).url


@csrf_exempt
def question_by_post(request, id):
    if request.method == 'POST':
        return JsonResponse(dict(status='error', error='Invalid method.'))

    questions = Question.objects.filter(post_id=id)

    if questions.count() <= 0:
        return JsonResponse(dict(status='error', error='No questions for this post'))

    random_limit = random.randrange(0, questions.count())
    question = questions[random_limit]
    print(question)
    return JsonResponse(dict(
        set_attributes=dict(
            question_id=question.pk,
            question_name=question.name
        ),
        messages=[]
    ))


@csrf_exempt
def set_interaction(request):
    if request.method == 'GET':
        return JsonResponse(dict(status='error', error='Invalid method.'))
    value = 0

    logger.info('setting interaction')

    try:
        username = request.POST['username']
        user = User.objects.get(username=username)
    except Exception as e:
        logger.error(e)
        return JsonResponse(dict(status='error', error='Invalid params.'))

    ## if post id set get post, if not; then cannot be post interaction
    try:
        post_id = request.POST['post_id']
        post=Post.objects.get(id=post_id)
    except Exception as e:
        logger.info("setting interaction w no post_id")
        post = None

    try:
        value = request.POST['value']
    except Exception as e:
        logger.warning("no value set")
        logger.warning("POST {}".format(request.POST))
        logger.warning(e)
        value = 0

    interaction = Interaction.objects.create(
        type=request.POST['interaction_type'],
        channel_id=user.last_channel_id,
        username=user.username,
        user_id=user.pk,
        bot_id=request.POST['bot_id'],
        post=post,
        value=value
    )
    return JsonResponse(dict(status='done', data=dict(
        interaction=dict(
            id=interaction.pk
        )
    )))


@csrf_exempt
def get_thumbnail_by_post(request, id):
    if request.method == 'POST':
        return JsonResponse(dict(status='error', error='Invalid params'))

    try:
        post = Post.objects.get(pk=id)
        logger.info("getting thumbnail for post")
        thumbnail = post.thumbnail
    except Exception as e:
        return JsonResponse(dict(status='error', error='Invalid params'))

    return JsonResponse(dict(
        set_attributes=dict(),
        messages=[
            dict(
                attachment=dict(
                    type='image',
                    payload=dict(
                        url=thumbnail
                    )
                )
            )
        ]
    ))


@csrf_exempt
def create_response_for_question(request, id):
    if request.method == 'GET':
        return JsonResponse(dict(status='error', error='Invalid method.'))

    try:
        username = request.POST['username']
        user = User.objects.get(username=username)
        question = Question.objects.get(id=id)
        user_response = request.POST['response']
        response_text = request.POST['response_text']
        response_value = request.POST['response_value']
    except Exception as e:
        return JsonResponse(dict(status='error', error='Invalid params.'))

    print(question)
    print(user)
    print(user_response)
    response = Response.objects.create(
        question=question,
        user_id=user.pk,
        username=username,
        response=user_response,
        response_text=response_text,
        response_value=response_value
    )

    return JsonResponse(dict(
        status='done',
        data=dict(
            response=dict(
                id=response.pk,
                user_id=response.user_id,
                username=response.username,
                response=response.response,
                question=response.question.name
            )
        )
    ))


@csrf_exempt
def get_replies_to_question(request, id):

    if request.method == 'POST':
        return JsonResponse(dict(status='error', error='Invalid method.'))

    try:
        question = Question.objects.get(pk=id)
    except:
        return JsonResponse(dict(status='error', error='Invalid params'))

    value_replies = question.questionresponse_set.all()
    print(value_replies)
    quick_replies = []
    if not value_replies.count() > 0:
        split_replies = question.replies.split(', ')
        for reply in split_replies:
            new_reply = dict(title=reply, set_attributes=dict(response=reply, response_text=reply, response_value=None),
                             block_names=['Validador Feedback Ciclo 1-2'])
            quick_replies.append(new_reply)
    else:
        for reply in value_replies:
            new_reply = dict(title=reply.response, set_attributes=dict(response=reply.value,
                                                                       response_text=reply.response,
                                                                       response_value=reply.value),
                             block_names=['Validador Feedback Ciclo 1-2'])
            quick_replies.append(new_reply)

    return JsonResponse(dict(
        messages=[
            {
                "text": question.name,
                "quick_replies": quick_replies
            }
        ]
    ))


class ReviewPostView(LoginRequiredMixin, DetailView):
    template_name = 'posts/review.html'
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = Post
    pk_url_kwarg = 'pid'
    context_object_name = 'review'


class ChangePostStatusToReviewView(LoginRequiredMixin, CreateView):

    model = Review
    fields = ('comment', )
    context_object_name = 'review'
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'posts/new-review.html'

    def get_context_data(self, **kwargs):
        context = super(ChangePostStatusToReviewView, self).get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, id=self.kwargs['id'])
        return context

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['id'])
        last_post_review = None
        try:
            last_post_review = Review.objects.filter(post=post).order_by('-id')[:1]
            last_post_review = last_post_review.first()
        except Exception as e:
            logger.error(e)

        if last_post_review and last_post_review.status == 'pending':
            messages.error(self.request, 'Post is actually in review, wait for approbation')
            return redirect('posts:edit-post', id=post.pk)

        if post.status == 'published':
            messages.error(self.request, 'Post is actually published')
            return redirect('posts:edit-post', id=post.pk)

        last_reviews = Review.objects.all().exclude(post=post).order_by('-id')[:1]
        reviser_list = DjangoUser.objects.filter(groups__name='reviser')
        post_reviser = reviser_list.first()
        print('first: ', post_reviser)

        if not post_reviser:
            messages.error(self.request, 'User with role reviser not exist')
            return redirect('posts:send_to_review', id=self.kwargs['id'])

        if reviser_list.count() > 1:
            print('more revisers')
            if last_reviews.count() > 0:
                last_review = last_reviews.first()
                print(last_review)
                reviser_index = 0
                user = UserReviewRole.objects.filter(review=last_review, role='reviser').first().user
                for counter, reviser_user in enumerate(reviser_list):
                    if user == reviser_user:
                        print('equals', counter)
                        reviser_index = counter
                        print(reviser_user)
                        print(user)
                        print(reviser_index)

                print('count', reviser_list.count())
                if reviser_index < (reviser_list.count() - 1):
                    print(reviser_index, reviser_list.count() - 1)
                    post_reviser = reviser_list[reviser_index + 1]

        print(post_reviser)

        post_user = post.user

        if post_user and post and post_reviser:
            new_review = form.save(commit=False)
            new_review.post = post
            new_review.save()
            author_role = UserReviewRole.objects.create(user=post_user, review=new_review)
            reviser_role = UserReviewRole.objects.create(user=post_reviser, review=new_review, role='reviser')
            author_role.save()
            reviser_role.save()
            post.status = 'review'
            post.save()
            try:
                messages.success(self.request, 'Your request for approbation has been created')
            except messages.api.MessageFailure:
                logger.error("Request approved yet no messages app installed")
            return redirect('posts:edit-post', id=post.pk)


class Reviews(LoginRequiredMixin, ListView):
    template_name = 'posts/reviser-reviews.html'
    model = Review
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        superuser = user.is_superuser
        status = ['pending', 'completed']
        try:
            status = [self.request.GET['status']]
        except Exception as e:
            logger.error(e)
        print(status)
        if superuser:
            queryset = Review.objects.filter(status__in=status).order_by('-pk')
        else:
            queryset = Review.objects.filter(status__in=status, users__in=[user.pk]).order_by('-pk')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['role'] = 'author'
        get_copy = self.request.GET.copy()
        parameters = get_copy.pop('page', True) and get_copy.urlencode()
        context['parameters'] = parameters
        if self.request.user.is_superuser:
            context['role'] = 'superuser'
        else:
            is_reviser = True if self.request.user.groups.filter(name='reviser').count() > 0 else False

            if is_reviser:
                context['role'] = 'reviser'
        return context


class ReviewView(LoginRequiredMixin, DetailView):
    template_name = 'posts/review-detail.html'
    model = Review
    pk_url_kwarg = 'review_id'
    context_object_name = 'review'
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, id=self.kwargs['id'])
        object = get_object_or_404(Review.objects.filter(post=post), id=self.kwargs['review_id'])
        if not self.request.user.is_superuser:
            if not self.request.user == post.user:
                user = get_object_or_404(object.users.all(), id=self.request.user.pk)
                ## TODO: is this supposed to be a way to ensure user exists...?
        return object

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['post'] = get_object_or_404(Post, id=self.kwargs['id'])
        print('here')
        if not self.request.user.is_superuser:
            if not self.request.user == context['post'].user:
                role = get_object_or_404(UserReviewRole, user=self.request.user, review=context['object'])
                context['role'] = role
        context['form'] = forms.ReviewCommentForm()
        return context


class AcceptReviewView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        review = get_object_or_404(Review, id=kwargs['review_id'])
        user = self.request.user
        post_user = False

        if review.post.status == 'published':
            messages.error(self.request, 'Post is actually published, no need to review')
            return redirect('posts:edit-post', id=review.post.pk)

        if not user.is_superuser:
            post_user = True if review.userreviewrole_set.filter(user=user, role='reviser').count() > 0 else False

        if not (post_user or user.is_superuser):
            messages.error(self.request, 'User not authorize to approve the post')
            return redirect('posts:edit-post', id=review.post.pk)

        review.post.status = 'published'
        published = review.post.save()
        print(published)

        review.status = 'completed'
        completed = review.save()
        print(completed)

        approbation = Approbation.objects.create(user=user, review=review)
        print(approbation)

        messages.success(self.request, "Post with id: %s has been approved for %s." % (review.post.pk, user.username))
        return redirect('posts:edit-post', id=review.post.pk)


class RejectionView(LoginRequiredMixin, CreateView):

    model = Rejection
    template_name = 'posts/new-rejection.html'
    fields = ('comment',)
    context_object_name = 'rejection'
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        context['post'] = review.post
        if not self.request.user.is_superuser:
            role = get_object_or_404(UserReviewRole, user=self.request.user, review=review)
            context['role'] = role
        return context

    def form_valid(self, form):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        post = review.post
        review.status = 'completed'
        review.save()
        post.status = 'rejected'
        post.save()
        rejection = form.save(commit=False)
        rejection.user = self.request.user
        rejection.review = review
        rejection.save()
        print(rejection)
        messages.success(self.request, 'Post with id: %s has been rejected.' % post.pk)
        return redirect('posts:home')


class ChangePostToNeedChangesView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        review = get_object_or_404(Review, id=kwargs['review_id'])
        if not self.request.user.is_superuser:
            authorized_user = get_object_or_404(UserReviewRole, review=review, user=self.request.user,
                                                role='reviser')
            logger.info("User: {} is editing review {} ".format(authorized_user, review))
        post = review.post
        post.status = 'need_changes'
        post.save()
        review.status = 'completed'
        review.save()
        messages.success(request, 'Request to changes created')
        return redirect('posts:post-review', id=post.pk, review_id=review.pk)


class AddReviewCommentView(LoginRequiredMixin, CreateView):
    model = ReviewComment
    fields = ('comment', )
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def form_valid(self, form):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        comment = form.save(commit=False)
        comment.user = self.request.user
        comment.review = review
        comment.save()
        messages.success(self.request, 'Comment has been added to review')
        return redirect('posts:post-review', id=review.post.pk, review_id=review.pk)


class CreateQuestionResponseView(LoginRequiredMixin, CreateView):
    model = QuestionResponse
    fields = ('response', 'value')
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        form = forms.QuestionResponseForm(self.request.POST)

        if form.is_valid():
            return self.form_valid(form)
        else:
            messages.error(self.request, 'Error in form')
            return redirect('posts:edit-question', id=self.kwargs['id'])

    def form_valid(self, form):
        response = form.save(commit=False)
        response.question_id = self.kwargs['id']
        response.save()
        messages.success(self.request, 'Reply with value has been added to question')
        return redirect('posts:edit-question', id=self.kwargs['id'])


class EditQuestionResponseView(LoginRequiredMixin, UpdateView):
    model = QuestionResponse
    fields = ('response', 'value')
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    pk_url_kwarg = 'response_id'
    template_name = 'posts/edit-question-response.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['question_id'] = self.kwargs['question_id']
        return context

    def get(self, *args, **kwargs):
        question = get_object_or_404(Question, id=self.kwargs['question_id'])
        response = get_object_or_404(question.questionresponse_set.all(), id=self.kwargs['response_id'])
        if not(self.request.user.is_superuser or question.post.user == self.request.user):
            last_reviews = Review.objects.filter(post=question.post, status='pending').order_by('-id')
            if not last_reviews.count() > 0:
                raise Http404('Not found')
            review = last_reviews.first()
            permit = get_object_or_404(UserReviewRole, review=review, user=self.request.user)
        return super().get(self.request)

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Question reply has been updated.')
        return redirect('posts:edit-question', id=self.kwargs['question_id'])


class DeleteQuestionResponseView(LoginRequiredMixin, DeleteView):
    model = QuestionResponse
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'posts/delete-question-response.html'
    pk_url_kwarg = 'response_id'
    context_object_name = 'response'

    success_url = '/posts/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['question_id'] = self.kwargs['question_id']
        return context

    def get_success_url(self):
        messages.success(self.request, 'Response for question has been deleted.')
        return reverse_lazy('posts:edit-question', kwargs=dict(id=self.kwargs['question_id']))


class AddCommentToPostByUserView(CreateView):
    model = MessengerUserCommentPost
    fields = ('post', 'user_id', 'comment')

    # for view data in form only
    # template_name = 'posts/onlytest_form.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(AddCommentToPostByUserView, self).dispatch(request, *args, **kwargs)

    # not visible for all people, ignore for view form
    def get(self, *args, **kwargs):
        raise Http404('Not found')

    def form_valid(self, form):
        form.save()
        return JsonResponse(dict(status='done', data=dict(message='Gracias por contestar')))

    def form_invalid(self, form):
        return JsonResponse(dict(status='error', error='invalid form'))


class TipsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tips to be viewed or edited.
    """
    queryset = Tip.objects.all()
    serializer_class = TipSerializer


class PostComplexityCreateApiView(CreateAPIView):
    serializer_class = serializers.PostComplexitySerializer


class PostByArea(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PostByArea, self).dispatch(request, *args, **kwargs)

    def get(self):
        raise Http404('Not found')

    def post(self, request):
        form = forms.PostByAreaForm(request.POST)

        if form.is_valid():
            limit = datetime.now() - timedelta(days=35)
            user = form.cleaned_data['user']
            print(form.cleaned_data['area'])
            posts = Post.objects\
                .filter(min_range__lte=form.cleaned_data['months'], max_range__gte=form.cleaned_data['months'],
                        taxonomy__area__id=form.cleaned_data['area'])

            filter_posts = posts\
                .exclude(interaction__user_id=user.pk,
                         interaction__type__in=['dispatched', 'sended', 'opened'],
                         interaction__created_at__gte=limit)

            if filter_posts.count() < 1:
                post = posts[random.randrange(0, posts.count())]
            else:
                post = filter_posts[random.randrange(0, filter_posts.count())]

            for item in ['sended', 'dispatched']:
                Interaction.objects.create(user_id=user.pk, post=post, type=item, value=0)

            attributes = dict(
                post_id=post.pk,
                post_uri=settings.DOMAIN_URL + '/posts/' + str(post.pk),
                post_preview=post.preview,
                post_title=post.name,
                post_error='false'
            )

            response = {
                'set_attributes': attributes,
                'messages': []
            }

        else:
            response = {
                'set_attributes': {
                    'post_error': 'Invalid params'
                },
                'messages': []
            }
        return JsonResponse(response)


class AddTaxonomyView(PermissionRequiredMixin, CreateView):
    permission_required = 'posts.add_taxonomy'
    model = Taxonomy
    fields = ('area', 'subarea', 'component')
    template_name = 'posts/add_taxonomy.html'

    def get_context_data(self, **kwargs):
        context = super(AddTaxonomyView, self).get_context_data()
        context['post'] = Post.objects.get(id=self.kwargs['id'])
        context['action'] = 'Add'
        return context

    def form_valid(self, form):
        form.instance.post = Post.objects.get(id=self.kwargs['id'])
        return super(AddTaxonomyView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'The taxonomy has been added.')
        return reverse_lazy('posts:edit-post', kwargs={'id': self.kwargs['id']})
