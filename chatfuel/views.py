from instances.models import InstanceAssociationUser, Instance, AttributeValue, PostInteraction, Response
from articles.models import Article, Interaction as ArticleInteraction, ArticleFeedback
from django.views.generic import View, CreateView, TemplateView, UpdateView
from user_sessions.models import Session, Interaction as SessionInteraction, Reply
from languages.models import Language, MilestoneTranslation
from groups.models import Code, AssignationMessengerUser, Group
from messenger_users.models import User as MessengerUser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from messenger_users.models import User, UserData
from django.http import JsonResponse, Http404
from dateutil import relativedelta, parser
from datetime import datetime, timedelta
from attributes.models import Attribute
from milestones.models import Milestone
from groups import forms as group_forms
from programs.models import Program, Attributes as ProgramAttributes
from entities.models import Entity
from licences.models import License
from django.utils import timezone
from django.db.models import Max
from django.utils.http import is_safe_url
import requests
from chatfuel import forms
import random
import boto3
import os
import re
from django.db.models import Q


''' MESSENGER USERS VIEWS '''


@method_decorator(csrf_exempt, name='dispatch')
class CreateMessengerUserView(CreateView):
    model = User
    form_class = forms.CreateUserForm

    def form_valid(self, form):
        group = None
        code = None
        if 'ref' in form.cleaned_data:
            code_filter = Code.objects.filter(code=form.cleaned_data['ref'])
            if code_filter.exists():
                code = code_filter.first()
                group = code_filter.first().group
                print(group)

        form.instance.last_channel_id = form.data['channel_id']
        form.instance.username = form.data['channel_id']
        form.instance.backup_key = form.data['channel_id']
        user = form.save()
        user.entity = Entity.objects.get(id=4)
        user.license = License.objects.get(id=1)
        user.language = Language.objects.get(id=1)
        user.save()
        user.userdata_set.create(data_key='user_reg', data_value='unregistered', attribute_id='210')
        if group:
            exchange = AssignationMessengerUser.objects.create(messenger_user_id=user.pk, group=group,
                                                               user_id=user.pk, code=code)
            print(exchange)
            if code.group.country:
                user.userdata_set.create(data_key='Pais', data_value=group.country)
            if code.group.region:
                user.userdata_set.create(data_key='Región', data_value=group.region)
            return JsonResponse(dict(set_attributes=dict(user_id=user.pk, request_status='done',
                                                         service_name='Create User', user_reg='unregistered',
                                                         request_code=code.code, request_code_group=group.name)))
        return JsonResponse(dict(set_attributes=dict(user_id=user.pk, request_status='done',
                                                     service_name='Create User', user_reg='unregistered')))

    def form_invalid(self, form):
        user_set = User.objects.filter(channel_id=form.data['channel_id'])
        if user_set.count() > 0:
            return JsonResponse(dict(set_attributes=dict(user_id=user_set.last().pk,
                                                         request_status='error', request_error='User exists',
                                                         service_name='Create User')))

        return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid params',
                                                     service_name='Create User')))


@method_decorator(csrf_exempt, name='dispatch')
class VerifyMessengerUserView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request):
        form = forms.MessengerUserForm(self.request.POST)

        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='done', user_exist='false',
                                                         service_name='Verify User')))

        user = form.cleaned_data['user']

        return JsonResponse(dict(set_attributes=dict(request_status='done', user_exist='true', user_id=user.pk,
                                                     service_name='Verify User')))


@method_decorator(csrf_exempt, name='dispatch')
class ReplaceUserInfoView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request):
        form = forms.ReplaceUserForm(self.request.POST)
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Incomplete params.',
                                                         service_name='Replace Info User')))

        users = User.objects.filter(id=form.data['id'])
        if not users.count() > 0:
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='User with ID %s not exist.' % form.data['id'],
                                                         service_name='Replace Info User')))
        user = users.first()
        user.first_name = form.data['first_name']
        user.last_name = form.data['last_name']
        user.channel_id = form.data['channel_id']
        user.last_channel_id = form.data['channel_id']
        user.username = form.data['channel_id']
        user.save()
        return JsonResponse(dict(set_attributes=dict(request_status='done', service_name='Replace Info User')))


@method_decorator(csrf_exempt, name='dispatch')
class CreateMessengerUserDataView(CreateView):
    model = UserData
    fields = ('user', 'data_key', 'data_value')

    def form_valid(self, form):
        form.save()
        if form.data['data_key'] == 'tipo_de_licencia':
            user = User.objects.get(id=form.data['user'])
            user.license = License.objects.get(name=form.data['data_value'])
            user.save()
            return JsonResponse(dict(set_attributes=dict(request_status='done', service_name='Update user license')))
        if form.data['data_key'] == 'language':
            user = User.objects.get(id=form.data['user'])
            user.language = Language.objects.get(name=form.data['data_value'])
            user.save()
            return JsonResponse(dict(set_attributes=dict(request_status='done', service_name='Update user language')))
        if form.data['data_key'] == 'user_type':
            user = User.objects.get(id=form.data['user'])
            user.entity = Entity.objects.get(name=form.data['data_value'])
            user.save()
            return JsonResponse(dict(set_attributes=dict(request_status='done', service_name='Update user entity')))
        return JsonResponse(dict(set_attributes=dict(request_status='done', service_name=form.data['data_key'])))

    def form_invalid(self, form):
        return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid params',
                                                     service_name='Create User Data')))


@method_decorator(csrf_exempt, name='dispatch')
class GetInitialUserData(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid Method',
                                                     service_name='Get Initial User Data')))

    def post(self, request):
        form = forms.UserForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid data.',
                                                         service_name='Get Initial User Data')))

        attributes = dict()

        for item in form.cleaned_data['user_id'].userdata_set.all():
            attributes[item.data_key] = item.data_value

        return JsonResponse(dict(set_attributes=attributes))


''' INSTANCES VIEWS '''


@method_decorator(csrf_exempt, name='dispatch')
class GetInstancesByUserView(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid Method',
                                                     service_name='Get Instances')))

    def post(self, request):
        form = forms.GetInstancesForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid data.',
                                                         service_name='Get Instances')))

        label = "Choice your instance: "
        try:
            if form.data['label']:
                label = form.data['label']
        except:
            pass
        user = MessengerUser.objects.get(id=int(form.data['user']))
        replies = [dict(title=item.name, set_attributes=dict(instance=item.pk, instance_name=item.name)) for item in
                   user.get_instances()]

        return JsonResponse(dict(
            set_attributes=dict(request_status='done', service_name='Get Instances'),
            messages=[
                dict(
                    text=label,
                    quick_replies=replies
                )
            ]
        ))


@csrf_exempt
def create_instance(request):

    if request.method == 'GET':
        return JsonResponse(dict(
            set_attributes=dict(request_status='error', request_error='Invalid Method',
                                service_name='Create Instance')))

    form = forms.InstanceModelForm(request.POST)

    if not form.is_valid():
        return JsonResponse(dict(
            set_attributes=dict(request_status='error', request_error='Invalid Params',
                                service_name='Create Instance')))

    new_instance = form.save()
    assignation = InstanceAssociationUser.objects.create(user_id=form.data['user_id'], instance=new_instance)

    return JsonResponse(dict(
        set_attributes=dict(
            request_status='done',
            instance=new_instance.pk,
            instance_name=new_instance.name,
            instance_assignation_id=assignation.pk,
            service_name='Create Instance'
        )))


@method_decorator(csrf_exempt, name='dispatch')
class GetInstanceAttributeView(TemplateView):
    template_name = 'chatfuel/form.html'

    def get_context_data(self, **kwargs):
        c = super(GetInstanceAttributeView, self).get_context_data()
        c['form'] = forms.GetInstanceAttributeValue(None)
        return c

    def post(self, request, *args, **kwargs):
        form = forms.GetInstanceAttributeValue(self.request.POST)

        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid params',
                                                         service_name='Get Instance Attribute')))

        instance = Instance.objects.get(id=form.data['instance'])
        attributes = instance.entity.attributes.filter(name=form.data['attribute'])

        if not attributes.count() > 0:
            return JsonResponse(dict(set_attributes=dict(
                request_status='error',
                request_error='Entity of instance has not attribute with name %s.' % form.data['attribute'],
                service_name='Get Instance Attribute')))

        attribute = Attribute.objects.get(name=form.data['attribute'])
        instance_attributes = AttributeValue.objects.filter(attribute=attribute, instance=instance)

        if not instance_attributes.count() > 0:
            return JsonResponse(dict(set_attributes=dict(
                request_status='error',
                request_error='Instance has not values with attribute: %s.' % form.data['attribute'],
                service_name='Get Instance Attribute')))

        return JsonResponse(
            dict(set_attributes={
                'request_status': 'done',
                form.data['attribute']: instance_attributes.last().value,
                'service_name': 'Get Instance Attribute'
            })
        )


@method_decorator(csrf_exempt, name='dispatch')
class ChangeInstanceNameView(TemplateView):
    template_name = 'chatfuel/form.html'

    def get_context_data(self, **kwargs):
        c = super(ChangeInstanceNameView, self).get_context_data()
        c['form'] = forms.ChangeNameForm(None)
        print(c['form'])
        return c

    def post(self, request, *args, **kwargs):

        form = forms.ChangeNameForm(self.request.POST)

        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(
                request_status='error',
                request_error='Invalid Params.',
                service_name='Change Instance Name'
            )))

        instance = Instance.objects.get(id=form.data['instance'])
        instance.name = form.data['name']
        response = instance.save()

        return JsonResponse(dict(set_attributes=dict(
            request_status='done',
            request_message="name for instance has been changed.",
            instance_name=instance.name,
            service_name='Change Instance Name'
        ), messages=[]))


''' CODE VIEWS '''


@method_decorator(csrf_exempt, name='dispatch')
class VerifyCodeView(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse(dict(request_status='error', request_error='Invalid Method',
                                 service_name='Verify Code'))

    def post(self, request):
        form = forms.VerifyCodeForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid params',
                                                         service_name='Verify Code')))

        code = Code.objects.get(code=form.data['code'])

        return JsonResponse(dict(set_attributes=dict(request_status='done', request_code=code.code,
                                                     request_code_group=code.group.name, service_name='Verify Code')))


@method_decorator(csrf_exempt, name='dispatch')
class ExchangeCodeView(TemplateView):
    template_name = 'groups/code_form.html'

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        form = group_forms.ExchangeCodeForm(request.POST)

        if form.is_valid():
            user = form.cleaned_data['messenger_user_id']
            code = form.cleaned_data['code']
            changes = AssignationMessengerUser.objects.filter(messenger_user_id=user.pk, group_id=code.group_id)
            print(changes)
            if not changes.count() > 0:
                exchange = AssignationMessengerUser.objects.create(messenger_user_id=user.pk, group=code.group,
                                                                   user_id=user.pk, code=code)
                code.exchange()
                if code.group.country:
                    user.userdata_set.create(data_key='Pais', data_value=code.group.country)
                if code.group.region:
                    user.userdata_set.create(data_key='Región', data_value=code.group.region)
                return JsonResponse(dict(set_attributes=dict(request_status='done', service_name='Exchange Code')))
            else:
                return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                             request_error='User be in group',
                                                             service_name='Exchange Code')))
        else:
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='User ID or code wrong',
                                                         service_name='Exchange Code')))


@method_decorator(csrf_exempt, name='dispatch')
class CreateInstanceAttributeView(CreateView):
    model = AttributeValue
    template_name = 'chatfuel/form.html'
    fields = ('instance', 'value', 'attribute')

    def get(self, request, *args, **kwargs):
        raise Http404

    def get_form(self, form_class=None):
        form = super(CreateInstanceAttributeView, self).get_form(form_class=None)
        form.fields['attribute'].to_field_name = 'name'
        return form

    def form_valid(self, form):

        if not form.instance.instance.entity.attributes.filter(id=form.instance.attribute.pk):
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Attribute not in instance',
                                                         service_name='Create Instance Attribute')))

        attribute_value = form.save()

        return JsonResponse(dict(set_attributes=dict(request_status='done', request_attribute_value_id=attribute_value.pk,
                                                     service_name='Create Instance Attribute')))

    def form_invalid(self, form):
        return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                     request_error='Invalid params'), messages=[]))

    def get(self, request, *args):
        raise Http404


''' INTERACTION VIEWS '''


@method_decorator(csrf_exempt, name='dispatch')
class CreateInstanceInteractionView(CreateView):
    template_name = 'chatfuel/form.html'
    form_class = forms.InstanceInteractionForm

    def form_valid(self, form):
        form.instance.post_id = form.data['post_id']
        form.instance.created_at = datetime.now()
        interaction = form.save()

        if not interaction:
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Invalid params'), messages=[]))

        return JsonResponse(dict(set_attributes=dict(request_status='done',
                                                     request_interaction_id=interaction.pk),
                                 messages=[]))

    def form_invalid(self, form):
        return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                     request_error='Invalid params'), messages=[]))


''' CHILDREN '''

# FIX LATER, maybe not necessary in a future


@method_decorator(csrf_exempt, name='dispatch')
class GetFavoriteChildView(View):

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):

        form = forms.UserForm(request.POST)
        day_first = True

        if 'en' in form.data:
            if form.data['en'] == 'true':
                day_first = False

        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Invalid params',
                                                         favorite_request_error='invalid params'), messages=[]))

        user = form.cleaned_data['user_id']
        instances = user.get_instances()
        children = instances.filter(entity_id=1)

        if not children.count() > 0:
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='User has not children',
                                                         favorite_request_error='User has not children'), messages=[]))

        if children.count() == 1:
            birthdays = children.first().attributevalue_set.filter(attribute__name='birthday')
            birth = None

            if not birthdays.count() > 0:
                return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                             request_error='Unique child has not birthday',
                                                             favorite_request_error='Unique child has not birthday'),
                                         messages=[]))

            birth = birthdays.last().value

            return JsonResponse(dict(set_attributes=dict(request_status='done',
                                                         favorite_instance=children.first().pk,
                                                         favorite_instance_name=children.first().name,
                                                         favorite_birthday=birth), messages=[]))
        dates = set()
        for child in children:
            child_birthdays = child.attributevalue_set.filter(attribute__name='birthday')
            if child_birthdays.count() > 0:
                dates.add(child_birthdays.last().pk)

        print(dates)

        if not len(dates) > 0:
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Neither child has birthday property',
                                                         favorite_request_error='Neither child has birthday property'),
                                     messages=[]))

        registers = AttributeValue.objects.filter(id__in=dates)

        favorite = dict(id=registers.first().instance_id, value=parser.parse(registers.first().value,
                                                                             dayfirst=day_first))

        for register in registers:
            print(register.value)
            register.value = parser.parse(register.value, dayfirst=day_first)
            print(register.value)
            if register.value > favorite['value']:
                favorite = dict(id=register.instance_id, value=register.value)

        attributes= dict(
                request_status='done',
                favorite_instace=favorite['id'],
                favorite_instance_name=Instance.objects.get(id=favorite['id']).name,
                favorite_birthday=favorite['value'].strftime('%d/%m/%Y')\
                    if day_first else favorite['value'].strftime('%m/%d/%Y')
            )

        return JsonResponse(dict(
            set_attributes=attributes,
            messages=[]
        ))


@method_decorator(csrf_exempt, name='dispatch')
class GetLastChildView(View):

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        form = forms.UserForm(self.request.POST)
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(
                request_status='error',
                request_error='Invalid params.'
            ), messages=[]))

        instances = form.cleaned_data['user_id'].get_instances()
        children = instances.filter(entity_id=1).order_by('id')

        if not children.count() > 0:
            return JsonResponse(dict(set_attributes=dict(
                request_status='error',
                request_error='User has not children.'
            ), messages=[]))

        attributes = dict(
            instance=children.last().pk,
            instance_name=children.last().name,
            favorite_instance=children.last().pk,
            favorite_instance_name=children.last().name,
            request_status='done'
        )

        if children.last().attributevalue_set.filter(attribute__name='birthday'):
            attributes['birthday'] = children.last().attributevalue_set.filter(attribute__name='birthday').\
                last().value
            attributes['favorite_birthday'] = children.last().attributevalue_set.filter(attribute__name='birthday'). \
                last().value

        return JsonResponse(dict(set_attributes=attributes, messages=[]))


''' ARTICLES '''


@method_decorator(csrf_exempt, name='dispatch')
class GetArticleView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request, *args, **kwargs):
        form = forms.UserArticleForm(request.POST)
        user = User.objects.get(id=form.data['user_id'])
        if 'article' in form.data:
            articles = Article.objects.filter(id=form.data['article'])\
                .only('id', 'name', 'min', 'max', 'preview', 'thumbnail')
            article = articles.first()
            new_interaction = ArticleInteraction.objects \
                .create(user_id=form.data['user_id'], article=article, type='dispatched')

            return JsonResponse(dict(set_attributes=dict(
                request_status='done',
                article_id=article.pk,
                article_name=article.name,
                article_content=("%s/articles/%s/?key=%s" % (os.getenv('CM_DOMAIN_URL'), article.pk,
                                                             user.last_channel_id)),
                article_preview=article.preview,
                article_thumbail=article.thumbnail,
                article_instance="false",
                article_instance_name="false"
            )))

        articles = Article.objects.filter(campaign=False).only('id', 'name', 'min', 'max', 'preview', 'thumbnail')
        article = articles[random.randrange(0, articles.count())]
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(
                request_status='error',
                request_error='Invalid params.'
            )))
        instances = form.cleaned_data['user_id'].get_instances().filter(entity_id=1)
        if not instances.count() > 0:
            new_interaction = ArticleInteraction.objects\
                .create(user_id=form.data['user_id'], article=article, type='dispatched')

            return JsonResponse(dict(set_attributes=dict(
                request_status='done',
                article_id=article.pk,
                article_name=article.name,
                article_content=("%s/articles/%s/?key=%s" % (os.getenv('CM_DOMAIN_URL'), article.pk,
                                                             user.last_channel_id)),
                article_preview=article.preview,
                article_thumbail=article.thumbnail,
                article_instance="false",
                article_instance_name="false"
            )))
        birthdays = []
        for instance in instances:
            birthday_list = instance.attributevalue_set.filter(attribute__name='birthday')
            if birthday_list.count() > 0:
                try:
                    valid = parser.parse(birthday_list.last().value)
                    if valid:
                        birthdays.append(birthday_list.last())
                except:
                    pass
        if len(birthdays) < 1:
            new_interaction = ArticleInteraction.objects \
                .create(user_id=form.data['user_id'], article=article, type='dispatched')
            return JsonResponse(dict(set_attributes=dict(
                request_status='done',
                article_id=article.pk,
                article_name=article.name,
                article_content=("%s/articles/%s/?key=%s" % (os.getenv('CM_DOMAIN_URL'), article.pk,
                                                             user.last_channel_id)),
                article_preview=article.preview,
                article_thumbail=article.thumbnail,
                article_instance="false",
                article_instance_name="false"
            )))
        random_number = random.randrange(0, len(birthdays))
        date = birthdays[random_number]
        print(date.instance)
        rel = relativedelta.relativedelta(timezone.now(), parser.parse(date.value))
        months = (rel.years * 12) + rel.months
        print(months)
        filter_articles = articles.filter(min__lte=months, max__gte=months)
        if not filter_articles.count() > 0:
            if not articles.count() > 0:
                return JsonResponse(dict(set_attributes=dict(
                    request_status='error',
                    request_error='Articles not exist.'
                )))
        else:
            article = filter_articles[random.randrange(0, filter_articles.count())]
            new_interaction = ArticleInteraction.objects \
                .create(user_id=form.data['user_id'], article=article, type='dispatched', instance_id=date.instance_id)
            print(new_interaction)
        return JsonResponse(dict(
            set_attributes=dict(
                request_status='done',
                article_id=article.pk,
                article_name=article.name,
                article_content=("%s/articles/%s/?key=%s&instance=%s" % (os.getenv('CM_DOMAIN_URL'), article.pk,
                                 user.last_channel_id, date.instance_id)),
                article_preview=article.preview,
                article_thumbail=article.thumbnail,
                article_instance=date.instance.pk,
                article_instance_name=date.instance.name
            )))


@method_decorator(csrf_exempt, name='dispatch')
class GetArticleTextView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request, *args, **kwargs):
        form = forms.ArticleForm(self.request.POST)
        if not form.is_valid():
            return JsonResponse(dict(request_status='error', request_error='Article not exist.'))
        split_content = form.cleaned_data['article'].text_content.split('| ')
        messages = [dict(text=content) for content in split_content]
        return JsonResponse(dict(messages=messages))


@method_decorator(csrf_exempt, name='dispatch')
class GetArticleImageView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request, *args, **kwargs):
        form = forms.ArticleForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(request_status='error', request_error='Article not exist.'))

        if not form.cleaned_data['article'].thumbnail:
            return JsonResponse(dict(request_status='error', request_error='Article has not image.'))

        return JsonResponse(dict(messages=[
            dict(
                attachment=dict(
                    type='image',
                    payload=dict(url=form.cleaned_data['article'].thumbnail)
                )
            )
        ]))


@method_decorator(csrf_exempt, name='dispatch')
class AddFeedbackToArticleView(CreateView):
    model = ArticleFeedback
    fields = ('user', 'value', 'article')

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def form_valid(self, form):
        new_feedback = form.save()
        return JsonResponse(dict(set_attributes=dict(request_status='done', request_feedback_id=new_feedback.pk)))

    def form_invalid(self, form):
        return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid params',
                                                     service_name='Add feedback to article')))


''' MILESTONES UTILITIES '''


@method_decorator(csrf_exempt, name='dispatch')
class GetMilestoneView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request, *args, **kwargs):
        form = forms.InstanceForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid params.')))

        instance = form.cleaned_data['instance']
        months = 0
        if instance.get_months():
            months = instance.get_months()
        print(months)
        day_range = (datetime.now() - timedelta(days=1))
        responses = instance.response_set.filter(created_at__gte=day_range)
        milestones = Milestone.objects.filter(max__gte=months, min__lte=months, source__in=['CDC', '1', 'Credi'])\
            .exclude(id__in=[i.milestone_id for i in responses])

        if not milestones.exists():
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Instance has not milestones to do.',
                                                         all_range_milestones_dispatched='true',
                                                         all_level_milestones_dispatched='true')))

        filtered_milestones = []
        for m in milestones:
            responses = instance.response_set.filter(milestone_id=m.pk)
            if not responses.exists():
                filtered_milestones.append(m.pk)
            else:
                if responses.last().response != 'done':
                    filtered_milestones.append(m.pk)
        print(filtered_milestones)

        filtered_milestones = milestones.filter(id__in=filtered_milestones)
        act_range = 'false'

        if filtered_milestones.exists():
            milestone = filtered_milestones.order_by('secondary_value').first()
            if filtered_milestones.count() < 2:
                act_range = 'true'
        else:
            milestone = milestones.exclude(id__in=[m.pk for m in filtered_milestones]).order_by('secondary_value')\
                .first()

        lang = 'es'
        if 'user_id' in form.data:
            lang = form.cleaned_data['user_id'].get_language()

        language = Language.objects.get(name=lang)

        translations = MilestoneTranslation.objects.filter(milestone=milestone, language=language)
        if translations.exists():
            milestone_text = translations.first().name
        else:
            region = os.getenv('region')
            translate = boto3.client(service_name='translate', region_name=region, use_ssl=True)
            result = translate.translate_text(Text=milestone.milestonetranslation_set.first().name,
                                              SourceLanguageCode="auto", TargetLanguageCode=language.name)
            new_translation = MilestoneTranslation.objects.create(
                milestone=milestone, language=language, name=result['TranslatedText'],
                description=result['TranslatedText'])
            milestone_text = new_translation.name

        return JsonResponse(dict(set_attributes=dict(request_status='done',
                                                     milestone=milestone.pk,
                                                     milestone_text=milestone_text,
                                                     all_level_milestones_dispatched='false',
                                                     all_range_milestones_dispatched=act_range)))


@method_decorator(csrf_exempt, name='dispatch')
class GetProgramMilestoneView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request, *args, **kwargs):
        form = forms.InstanceForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid params.')))

        instance = form.cleaned_data['instance']
        months = 0
        if instance.get_months():
            months = instance.get_months()
        user = instance.get_users().first()
        group = Group.objects.filter(assignationmessengeruser__user_id=user.pk).first()
        program = group.programs.first()
        m_ids = set(m.milestone_id for m in program.programmilestonevalue_set.filter(min__lte=months, max__gte=months))
        day_range = (datetime.now() - timedelta(days=1))
        milestones = Milestone.objects.filter(id__in=m_ids)\
            .exclude(id__in=[i.milestone_id for i in instance.response_set.filter(created_at__gte=day_range)])

        if not milestones.exists():
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Instance has not milestones to do.',
                                                         all_range_milestones_dispatched='true',
                                                         all_level_milestones_dispatched='true')))

        filtered_milestones = []
        for m in milestones:
            responses = instance.response_set.filter(milestone_id=m.pk)
            if not responses.exists():
                filtered_milestones.append(m.pk)
            else:
                if responses.last().response != 'done':
                    filtered_milestones.append(m.pk)
        print(filtered_milestones)

        filtered_milestones = milestones.filter(id__in=filtered_milestones)
        act_range = 'false'

        if filtered_milestones.exists():
            milestone = filtered_milestones.order_by('secondary_value').first()
            if filtered_milestones.count() < 2:
                act_range = 'true'
        else:
            milestone = milestones.exclude(id__in=[m.pk for m in filtered_milestones]).order_by('secondary_value')\
                .first()

        lang = 'es'
        if 'user_id' in form.data:
            lang = form.cleaned_data['user_id'].get_language()

        language = Language.objects.get(name=lang)

        translations = MilestoneTranslation.objects.filter(milestone=milestone, language=language)
        if translations.exists():
            milestone_text = translations.first().name
        else:
            region = os.getenv('region')
            translate = boto3.client(service_name='translate', region_name=region, use_ssl=True)
            result = translate.translate_text(Text=milestone.milestonetranslation_set.first().name,
                                              SourceLanguageCode="auto", TargetLanguageCode=language.name)
            new_translation = MilestoneTranslation.objects.create(
                milestone=milestone, language=language, name=result['TranslatedText'],
                description=result['TranslatedText'])
            milestone_text = new_translation.name

        return JsonResponse(dict(set_attributes=dict(request_status='done',
                                                     milestone=milestone.pk,
                                                     milestone_text=milestone_text,
                                                     all_level_milestones_dispatched='false',
                                                     all_range_milestones_dispatched=act_range)))


@method_decorator(csrf_exempt, name='dispatch')
class GetInstanceMilestoneView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request, *args, **kwargs):
        form = forms.InstanceForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid params.')))

        instance = form.cleaned_data['instance']

        birth = instance.get_attribute_values('birthday')
        if not birth:
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Instance has not birthday.')))
        try:
            date = parser.parse(birth.value)
            print(date)
        except:
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Instance has not a valid date in birthday.')))

        months = instance.get_months()
        user = instance.get_users().first()
        group = Group.objects.filter(assignationmessengeruser__user_id=user.pk).first()
        program = group.programs.first()

        associations = set(i.milestone_id for i in
                           program.programmilestonevalue_set.filter(min__lte=months, max__gte=months))
        print(associations)

        milestones = Milestone.objects.filter(id__in=[i.milestone_id for i
                                                      in program.programmilestonevalue_set.filter(min__lte=months,
                                                                                                  max__gte=months)])
        available = 0
        completed = 0
        print(milestones.count())
        for m in milestones:
            print(m.name)
            responses = instance.response_set.filter(milestone_id=m.pk)
            if responses.exists():
                if responses.last().response == 'done':
                    completed = completed + 1
                else:
                    available = available + 1
            else:
                available = available + 1

        return JsonResponse(dict(
            set_attributes=dict(
                all_level_milestones=milestones.count(),
                all_range_milestones=milestones.count(),
                level_milestones_available=available,
                range_milestones_available=completed,
                level_milestones_completed=available,
                range_milestones_completed=completed
            )
        ))


@method_decorator(csrf_exempt, name='dispatch')
class CreateResponseView(CreateView):
    model = Response
    fields = ('instance', 'milestone', 'response')

    def form_valid(self, form):
        form.instance.created_at = datetime.now()
        r = form.save()
        if r.response == 'si':
            r.response = 'done'
        elif r.response == 'no sé':
            r.response = 'dont-know'
        else:
            r.response = 'failed'
        r.save()
        return JsonResponse(dict(set_attributes=dict(request_status='done', request_transaction_id=r.pk)))

    def form_invalid(self, form):
        return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid params.')))


''' SESSIONS UTILITIES '''


@method_decorator(csrf_exempt, name='dispatch')
class GetSessionView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request, *args, **kwargs):
        form = forms.SessionForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid params.')))

        if form.cleaned_data['Type'].exists() and form.cleaned_data['Type'].first().name == 'Register':
            session = Session.objects.filter(session_type__in=form.cleaned_data['Type']).first()
            if form.cleaned_data['session']:
                session = form.cleaned_data['session']
            return JsonResponse(dict(set_attributes=dict(session=session.pk, position=0,
                                                         request_status='done', session_finish='false')))
        user = form.cleaned_data['user_id']

        if form.cleaned_data['instance']:
            instance = form.cleaned_data['instance']
            instance_id = instance.id
            if instance.entity_id == 2:#Pregnant
                weeks = instance.get_attribute_values('pregnant_weeks')
                if weeks:
                    age = weeks.value
                else:
                    age = -1
            else:
                birth = instance.get_attribute_values('birthday')
                if not birth:
                    return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                                 request_error='Instance has not birthday.')))
                try:
                    date = parser.parse(birth.value)
                except:
                    return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                                 request_error='Instance has not a valid date in birthday.')))
                rd = relativedelta.relativedelta(datetime.now(), date)
                age = rd.months
                if rd.years:
                    age = age + (rd.years * 12)
        else:
            age = 0
            instance_id = None

        if form.cleaned_data['session']:
            session = form.cleaned_data['session']
        else:
            # Filter by age, language and license
            sessions = Session.objects.filter(min__lte=age, max__gte=age,
                                              lang__language_id=user.language.id,
                                              licences=user.license)

            if form.cleaned_data['instance']:  # Filter by entity o user and/or instance
                sessions = sessions.filter(entities__in=[user.entity, instance.entity]).distinct()
            else:
                sessions = sessions.filter(entities=user.entity)

            if user.assignationmessengeruser_set.exists():  # If user has a group, hence a program, filter by program
                sessions = sessions.filter(programs__group__assignationmessengeruser__messenger_user_id=user.id
                                           ).distinct()

            if form.cleaned_data['Type'].exists():  # Filter by type of session
                sessions = sessions.filter(session_type__in=form.cleaned_data['Type'])

            interactions = SessionInteraction.objects.filter(user_id=form.data['user_id'],
                                                             instance_id=instance_id,
                                                             type='session_init',
                                                             session__in=sessions)

            sessions_new = sessions.exclude(id__in=[interaction.session_id for interaction in interactions])
            if not sessions_new.exists():
                if not sessions.exists():
                    return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                                 request_error='Instance has not sessions.')))
                else:
                    session = sessions.last()
            else:
                session = sessions_new.first()
        # Guardar interaccion
        SessionInteraction.objects.create(user_id=user.id,
                                          instance_id=instance_id,
                                          type='broadcast_init',
                                          session=session)

        return JsonResponse(dict(set_attributes=dict(session=session.pk, position=0, request_status='done',
                                                     session_finish='false')))


@method_decorator(csrf_exempt, name='dispatch')
class GetSessionFieldView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request, *args, **kwargs):
        form = forms.SessionFieldForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid params.')))
        user = form.cleaned_data['user_id']
        instance = form.cleaned_data['instance']
        instance_id = None
        if form.cleaned_data['instance']:
            instance_id = instance.id
        session = form.cleaned_data['session']
        field = session.field_set.filter(position=int(form.cleaned_data['position']))
        response = dict()
        attributes = dict()

        if not field.exists():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Field not exists.')))

        field = field.first()
        fields = session.field_set.all().order_by('position')
        finish = 'false'
        response_field = field.position + 1
        if field.position == 0:
            # Guardar interaccion
            SessionInteraction.objects.create(user_id=user.id,
                                              instance_id=instance_id,
                                              type='session_init',
                                              field=field,
                                              session=session)
            # Guardar atributos de riesgo en chatfuel
            interactions = SessionInteraction.objects.filter(instance_id=instance_id)
            for program_attribute in ProgramAttributes.objects.filter(attribute__entity__in=[1, 2]):# child or pregnant
                a = AttributeValue.objects.filter(instance_id=instance_id,
                                                  attribute=program_attribute.attribute).order_by('id')
                if a.exists():
                    reply = Reply.objects.filter(attribute=program_attribute.attribute.name,
                                                 value=a.last().value,
                                                 field_id__in=[x.field_id for x in interactions])
                    if reply.exists():
                        attributes[program_attribute.attribute.name] = reply.last().label
                    else:
                        reply = Reply.objects.filter(attribute=program_attribute.attribute.name,
                                                     value=a.last().value)
                        if reply.exists():
                            attributes[program_attribute.attribute.name] = reply.last().label
                        else:
                            attributes[program_attribute.attribute.name] = a.last().value
            for program_attribute in ProgramAttributes.objects.filter(attribute__entity__in=[4, 5]):# caregiver/professional
                a = UserData.objects.filter(user=user, attribute=program_attribute.attribute).order_by('id')
                if a.exists():
                    reply = Reply.objects.filter(attribute=program_attribute.attribute.name,
                                                 value=a.last().data_value,
                                                 field_id__in=[x.field_id for x in interactions])
                    if reply.exists():
                        attributes[program_attribute.attribute.name] = reply.last().label
                    else:
                        reply = Reply.objects.filter(attribute=program_attribute.attribute.name,
                                                     value=a.last().data_value)
                        if reply.exists():
                            attributes[program_attribute.attribute.name] = reply.last().label
                        else:
                            attributes[program_attribute.attribute.name] = a.last().data_value
        if field.field_type == 'redirect_session':
            session = field.redirectsession.session
            attributes['session'] = session.id
            field = session.field_set.filter(position=int(field.redirectsession.position)).first()
            fields = session.field_set.all().order_by('position')
            response_field = field.position + 1

        attributes['save_text_reply'] = False
        attributes['save_user_input'] = False
        messages = []

        if field.field_type == 'consume_service':
            service_url = field.service.url
            if is_safe_url(service_url, allowed_hosts={'core.afinidata.com',
                                                       'contentmanager.afinidata.com',
                                                       'program.afinidata.com'}, require_https=True):
                service_params = {}
                for param in field.service.serviceparam_set.all():
                    if re.search("{{.*}}", param.value):
                        attribute_name = param.value[2:-2]
                        if Attribute.objects.filter(name=attribute_name, entity__in=[1, 2]).exists():
                            attribute_value = AttributeValue.objects.filter(instance=instance,
                                                                            attribute__name=attribute_name). \
                                order_by('id')
                            if attribute_value.exists():
                                attribute_value = attribute_value.last().value
                            else:
                                attribute_value = ''
                        if Attribute.objects.filter(name=attribute_name, entity__in=[4, 5]).exists():
                            attribute_value = UserData.objects.filter(user_id=user,
                                                                      attribute__name=attribute_name).order_by('id')
                            if attribute_value.exists():
                                attribute_value = attribute_value.last().data_value
                            else:
                                attribute_value = ''
                        service_params[param.parameter] = attribute_value
                    else:
                        service_params[param.parameter] = param.value
                if field.service.request_type == 'get':
                    service_response = requests.get(service_url, params=service_params)
                else:
                    service_response = requests.post(service_url, data=service_params)
                return JsonResponse(service_response.json())
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='URL not safe')))

        elif field.field_type == 'set_attributes':
            for a in field.setattribute_set.all():
                attributes[a.attribute.name] = a.value
                # Guardar atributo instancia o embarazo
                if Entity.objects.get(id=1).attributes.filter(name=a.attribute.name).exists() \
                        or Entity.objects.get(id=2).attributes.filter(name=a.attribute.name).exists():
                    attribute = Attribute.objects.filter(name=a.attribute.name)
                    AttributeValue.objects.create(instance=instance, attribute=attribute.first(),
                                                  value=a.value)
                # Guardar atributo usuario
                if Entity.objects.get(id=4).attributes.filter(name=a.attribute.name).exists() \
                        or Entity.objects.get(id=5).attributes.filter(name=a.attribute.name).exists():
                    UserData.objects.create(user=user, data_key=a.attribute.name, attribute=a.attribute,
                                            data_value=a.value)
                if a.attribute.name == 'tipo_de_licencia':
                    user.license = License.objects.get(name=a.value)
                    user.save()
                if a.attribute.name == 'language':
                    user.language = Language.objects.get(name=a.value)
                    user.save()
                if a.attribute.name == 'user_type':
                    user.entity = Entity.objects.get(name=a.value)
                    user.save()

        elif field.field_type == 'text':
            for m in field.message_set.all():
                cut_message = m.text.split(' ')
                new_text = ""
                for c in cut_message:
                    first_search = re.search(".*{{.*}}*", c)
                    last_search = re.search(".*{.*}*", c)
                    if first_search:
                        idx = c.index('}')
                        exc = c[(idx + 2):]
                        attribute = c[c.find('{')+2:idx]
                        if attribute == 'name':
                            attribute = instance.name
                        else:
                            qs = instance.attributevalue_set.filter(attribute__name=attribute)
                            if qs.exists():
                                attribute = qs.last().value
                            else:
                                attribute = '-' + attribute + '-'
                        text = c[:c.find('{')] + attribute + exc
                        new_text = new_text + ' ' + text
                    elif last_search:
                        idx = c.index('}')
                        exc = c[(idx + 1):]
                        attribute = c[1:idx]
                        if attribute == 'first_name':
                            attribute = user.first_name
                        elif attribute == 'last_name':
                            attribute = user.last_name
                        else:
                            qs = user.userdata_set.filter(data_key=attribute)
                            if qs.exists():
                                attribute = qs.last().data_value
                            else:
                                attribute = '-' + attribute + '-'
                        text = attribute + exc
                        new_text = new_text + ' ' + text
                    else:
                        new_text = new_text + ' ' + c
                if session.field_set.filter(field_type='buttons', position=field.position + 1).exists():
                    buttons = []
                    for b in session.field_set.\
                            filter(field_type='buttons', position=field.position + 1).first().button_set.all():
                        if b.button_type == 'show_block':
                            buttons.append(dict(type=b.button_type,
                                                block_names=[b.block_names],
                                                title=b.title))
                        else:
                            buttons.append(dict(type=b.button_type,
                                                url=b.url,
                                                title=b.title))
                    messages.append(dict(attachment=dict(type="template",
                                                         payload=dict(template_type="button",
                                                                      text=new_text,
                                                                      buttons=buttons))))
                    response_field = response_field + 1
                else:
                    messages.append(dict(text=new_text))

        elif field.field_type == 'image':
            m = field.message_set.first()
            messages.append(dict(attachment=dict(type='image', payload=dict(url=m.text))))

        elif field.field_type == 'quick_replies':
            message = dict(text='Responde: ', quick_replies=[])
            save_attribute = False
            for r in field.reply_set.all():
                rep = dict(title=r.label)
                message['quick_replies'].append(rep)
                if r.attribute or r.redirect_block or r.session:
                    save_attribute = True
                    if r.value:
                        rep['set_attributes'] = {'last_reply': r.value, 'reply_id': r.id}
                    else:
                        rep['set_attributes'] = {'last_reply': '', 'reply_id': r.id}
            message['quick_reply_options'] = dict(process_text_by_ai=False, text_attribute_name='last_reply')
            attributes['save_text_reply'] = save_attribute
            messages.append(message)
            attributes['field_id'] = field.id

        elif field.field_type == 'save_values_block':
            response['redirect_to_blocks'] = [field.redirectblock.block]

        elif field.field_type == 'user_input':
            attributes['save_user_input'] = True
            # The first decimal of 'position' represents the number of times the user failed the validation
            # For example: position = 1.2 means that the field position is 1, but the user has failed the validation
            #               2 times, so the following text is the third text
            # Here I just extract the decimal part to get the correct text
            user_input_try = round((float(form.cleaned_data['position'])*10 - int(form.cleaned_data['position'])*10))
            attributes['user_input_text'] = field.userinput_set.all().order_by('id')[user_input_try].text
            attributes['field_id'] = field.id

        elif field.field_type == 'condition':
            satisfies_conditions = True
            for condition in field.condition_set.all():
                is_attribute_set = False
                if condition.attribute.entity_set.filter(id__in=[1, 2]).exists():
                    attribute = AttributeValue.objects.filter(attribute=condition.attribute,
                                                              instance=instance).order_by('id')
                    if attribute.exists():
                        is_attribute_set = True
                        attribute = attribute.last()
                    else:
                        satisfies_conditions = False
                        condition.condition == 'None'
                elif condition.attribute.entity_set.filter(id__in=[4, 5]).exists():
                    attribute = UserData.objects.filter(attribute=condition.attribute,
                                                        user=user).order_by('id')
                    if attribute.exists():
                        is_attribute_set = True
                        attribute = attribute.last()
                        attribute.value = attribute.data_value
                    else:
                        satisfies_conditions = False
                        condition.condition == 'None'
                else:
                    satisfies_conditions = False
                    condition.condition == 'None'
                if condition.condition == 'is_set':
                    satisfies_conditions = is_attribute_set
                elif condition.condition == 'is_not_set':
                    satisfies_conditions = not is_attribute_set
                elif condition.condition == 'equal':
                    satisfies_conditions = satisfies_conditions and (attribute.value == condition.value)
                elif condition.condition == 'not_equal':
                    satisfies_conditions = satisfies_conditions and (attribute.value != condition.value)
                elif condition.condition == 'in':
                    satisfies_conditions = satisfies_conditions and (attribute.value in condition.value.split(","))
                elif condition.condition == 'lt':
                    try:
                        satisfies_conditions = satisfies_conditions \
                                               and (float(attribute.value) < float(condition.value))
                    except:
                        satisfies_conditions = False
                elif condition.condition == 'gt':
                    try:
                        satisfies_conditions = satisfies_conditions \
                                               and (float(attribute.value) > float(condition.value))
                    except:
                        satisfies_conditions = False
                elif condition.condition == 'lte':
                    try:
                        satisfies_conditions = satisfies_conditions \
                                               and (float(attribute.value) <= float(condition.value))
                    except:
                        satisfies_conditions = False
                elif condition.condition == 'gte':
                    try:
                        satisfies_conditions = satisfies_conditions \
                                               and (float(attribute.value) >= float(condition.value))
                    except:
                        satisfies_conditions = False
            if not satisfies_conditions:
                response_field = response_field + 1

        if fields.last().position < response_field:
            finish = 'true'
            response_field = 0
            # Guardar interaccion
            SessionInteraction.objects.create(user_id=user.id,
                                              instance_id=instance_id,
                                              type='session_finish',
                                              field=field,
                                              session=session)
        attributes['session_finish'] = finish
        attributes['position'] = response_field
        response['set_attributes'] = attributes
        response['messages'] = messages

        return JsonResponse(response)


@method_decorator(csrf_exempt, name='dispatch')
class SaveLastReplyView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request, *args, **kwargs):
        form = forms.SessionFieldReplyForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid params.')))
        user = form.cleaned_data['user_id']
        instance = form.cleaned_data['instance']
        instance_id = None
        is_input_valid = True
        attributes = dict()
        response = dict()
        if form.cleaned_data['instance']:
            instance_id = instance.id
        field = form.cleaned_data['field_id']
        if field.field_type == 'user_input':
            user_input_try = round((float(form.cleaned_data['position'])*10 - int(form.cleaned_data['position'])*10))
            user_input = field.userinput_set.all().order_by('id')[user_input_try]
            attribute_name = user_input.attribute.name
            reply_type = 'user_input'
            reply_value = None
            reply_text = form.data['last_reply']
            chatfuel_value = form.data['last_reply']
            if user_input.validation:
                is_input_valid = False
            else:
                is_input_valid = True
            if user_input.validation == 'date':
                validation_response = is_valid_date(reply_text, user.language.name)
                if validation_response['set_attributes']['request_status'] == 'done':
                    is_input_valid = True
                    reply_text = validation_response['set_attributes']['childDOB']
                    chatfuel_value = validation_response['set_attributes']['locale_date']
            if user_input.validation == 'number':
                is_input_valid = is_valid_number(str(reply_text))
            if user_input.validation == 'phone':
                is_input_valid = is_valid_phone(str(reply_text))
            if user_input.validation == 'email':
                is_input_valid = is_valid_email(str(reply_text))
            if user_input.validation and not is_input_valid:
                # If it is the first failure of validation
                if float(form.cleaned_data['position']) == 0 or int(form.cleaned_data['position']) == field.position+1:
                    attributes['position'] = float(field.position) + 0.1
                elif field.userinput_set.all().count() > user_input_try + 1:  # If it has more validations to make
                    attributes['position'] = float(form.cleaned_data['position']) + 0.1
                elif field.userinput_set.all().order_by('id').last().session:
                    attributes['session_finish'] = 'false'
                    attributes['session'] = field.userinput_set.all().order_by('id').last().session.id
                    attributes['position'] = field.userinput_set.all().order_by('id').last().position
        elif field.field_type == 'quick_replies':
            reply_type = 'quick_reply'
            reply = field.reply_set.all().filter(
                Q(value=form.data['last_reply']) | Q(label__iexact=form.data['last_reply']))
            if reply.exists():
                reply_value = reply.first().value
                reply_text = None
                attribute_name = reply.first().attribute
                chatfuel_value = reply.first().label
            else:
                reply_value = None
                reply_text = form.data['last_reply']
                attribute_name = field.reply_set.first().attribute
                chatfuel_value = form.data['last_reply']
            if form.cleaned_data['reply_id']:
                r = form.cleaned_data['reply_id']
                if r.redirect_block:
                    response['redirect_to_blocks'] = [r.redirect_block]
                elif r.session:
                    attributes['session_finish'] = 'false'
                    attributes['session'] = r.session.id
                    attributes['position'] = r.position
        if form.data['bot_id']:
            bot_id = form.data['bot_id']
        else:
            bot_id = 0
        # Guardar interaccion
        SessionInteraction.objects.create(user_id=user.id,
                                          instance_id=instance_id,
                                          bot_id=int(bot_id),
                                          type=reply_type,
                                          value=reply_value,
                                          text=reply_text,
                                          field=field,
                                          session=Session.objects.filter(id=field.session_id).first())
        if is_input_valid:
            # Guardar atributo instancia o embarazo
            if Entity.objects.get(id=1).attributes.filter(name=attribute_name).exists() \
                    or Entity.objects.get(id=2).attributes.filter(name=attribute_name).exists():
                attribute = Attribute.objects.filter(name=attribute_name)
                AttributeValue.objects.create(instance=instance, attribute=attribute.first(), value=form.data['last_reply'])
            # Guardar atributo usuario
            if Entity.objects.get(id=4).attributes.filter(name=attribute_name).exists() \
                    or Entity.objects.get(id=5).attributes.filter(name=attribute_name).exists():
                attribute = Attribute.objects.filter(name=attribute_name)
                UserData.objects.create(user=user, data_key=attribute_name, attribute=attribute.first(),
                                        data_value=form.data['last_reply'])
            if attribute_name == 'tipo_de_licencia':
                user.license = License.objects.get(name=form.data['last_reply'])
                user.save()
            if attribute_name == 'language':
                user.language = Language.objects.get(name=form.data['last_reply'])
                user.save()
            if attribute_name == 'user_type':
                user.entity = Entity.objects.get(name=form.data['last_reply'])
                user.save()
        attributes[attribute_name] = chatfuel_value
        attributes['save_text_reply'] = False
        response['set_attributes'] = attributes
        response['messages'] = []
        return JsonResponse(response)


''' CHATFUEL UTILITIES '''


@method_decorator(csrf_exempt, name='dispatch')
class BlockRedirectView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request, *args, **kwargs):
        form = forms.BlockRedirectForm(self.request.POST or None)
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='Error',
                                                         request_error='Next field not found.'),
                                     messages=[]))

        return JsonResponse(dict(
            redirect_to_blocks=[form.cleaned_data['next']]
        ))


@method_decorator(csrf_exempt, name='dispatch')
class ValidatesDateView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request):
        form = forms.ValidatesDateForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_message='Invalid params')))

        return JsonResponse(is_valid_date(form.data['date'], form.data['locale'][0:2], form.data['variant']))


@method_decorator(csrf_exempt, name='dispatch')
class CalculateWeeksView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request):
        form = forms.SingleDateForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Invalid params')))

        return JsonResponse(dict(set_attributes=dict(Semanas_Embarazo="-%s" % (int(form.data['months']) * 4))))


@method_decorator(csrf_exempt, name='dispatch')
class DefaultDateValuesView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request):
        ps = Program.objects.filter(id=1)
        if not ps.exists():
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Program not exists.')))
        levels = ps.first().levels.all()
        replies = []
        for l in levels:
            replies.append(dict(title="%s - %s" % (l.assign_min, l.assign_max), set_attributes=dict(level_number=l.pk)))
        print(replies)
        return JsonResponse(dict(messages=[dict(text='?', quick_replies=replies)]))


@method_decorator(csrf_exempt, name='dispatch')
class SetDefaultDateValueView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request):
        form = forms.SetDefaultDateValueForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Invalid params.')))
        level = form.cleaned_data['level_number']
        instance = form.cleaned_data['instance']
        today = datetime.now()
        limit = (level.assign_min + 1.5) * 30
        assign = today - timedelta(days=limit)
        attr = instance.attributevalue_set.create(attribute=Attribute.objects.get(name='birthday'), value=assign)
        gattr = instance.attributevalue_set.create(attribute=Attribute.objects.get(name='generic_birthday'),
                                                   value='true')
        print(gattr)
        return JsonResponse(dict(set_attributes=dict(
            request_status='done',
            birthday=attr.value,
            generic_birthday='true'
        )))


def is_valid_number(s):
    return s.replace(',', '', 1).isdigit() or s.replace('.', '', 1).isdigit()


def is_valid_phone(s):
    return s.isdigit()


def is_valid_email(s):
    return True


def is_valid_date(date, lang='es', variant='true'):
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
              'november', 'december']

    region = os.getenv('region')
    translate = boto3.client(service_name='translate', region_name=region, use_ssl=True)
    result = translate.translate_text(Text=date,
                                      SourceLanguageCode="auto", TargetLanguageCode="en")
    try:
        if variant == 'true':
            date = parser.parse(result.get('TranslatedText'))
        else:
            date = parser.parse(result.get('TranslatedText'), dayfirst=True)
    except Exception as e:
        print(e)
        return dict(set_attributes=dict(request_status='error', request_message='Not a valid string date'))

    rel = relativedelta.relativedelta(datetime.now(), date)
    child_months = (rel.years * 12) + rel.months

    month = months[date.month - 1]
    date_result = translate.translate_text(Text="%s %s, %s" % (month, date.day, date.year), SourceLanguageCode="en",
                                           TargetLanguageCode=lang)
    locale_date = date_result.get('TranslatedText')
    return dict(set_attributes=dict(
        childDOB=date,
        locale_date=locale_date,
        childMonths=child_months,
        request_status='done',
        childYears=rel.years,
        childExceedMonths=rel.months if rel.years > 0 else 0
    ))
