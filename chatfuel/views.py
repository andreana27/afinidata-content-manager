from instances.models import InstanceAssociationUser, Instance, AttributeValue, PostInteraction, Response
from django.views.generic import View, CreateView, TemplateView, UpdateView
from articles.models import Article, Interaction as ArticleInteraction
from languages.models import Language, MilestoneTranslation
from groups.models import Code, AssignationMessengerUser
from messenger_users.models import User as MessengerUser
from entities.models import Entity
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from messenger_users.models import User, UserData
from django.http import JsonResponse, Http404
from dateutil import relativedelta, parser
from datetime import datetime, timedelta
from user_sessions.models import Session, Interaction as SessionInteraction
from attributes.models import Attribute
from milestones.models import Milestone
from groups import forms as group_forms
from posts.models import Interaction
from programs.models import Program
from django.utils import timezone
from chatfuel import forms
import random
import boto3
import os
import re


''' MESSENGER USERS VIEWS '''


@method_decorator(csrf_exempt, name='dispatch')
class CreateMessengerUserView(CreateView):
    model = User
    fields = ('channel_id', 'bot_id', 'first_name', 'last_name')

    def form_valid(self, form):
        form.instance.last_channel_id = form.data['channel_id']
        form.instance.username = form.data['channel_id']
        form.instance.backup_key = form.data['channel_id']
        user = form.save()
        return JsonResponse(dict(set_attributes=dict(user_id=user.pk, request_status='done',
                                                     service_name='Create User')))

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
        return JsonResponse(dict(set_attributes=dict(request_status='done', service_name='Create User Data')))

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
            changes = AssignationMessengerUser.objects.filter(messenger_user_id=user.pk)
            print(changes)
            if not changes.count() > 0:
                exchange = AssignationMessengerUser.objects.create(messenger_user_id=user.pk, group=code.group,
                                                                   code=code)
                code.exchange()
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
        rel = relativedelta.relativedelta(datetime.now(), parser.parse(date.value))
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
        rd = relativedelta.relativedelta(datetime.now(), date)
        print(rd)
        months = rd.months 
        if rd.years:
            months = months + (rd.years * 12)
        print(months)
        level = None
        if form.cleaned_data['program']:
            level = form.cleaned_data['program'].level_set\
                .filter(assign_min__lte=months, assign_max__gte=months).first()
        else:
            level = Program.objects.get(id=1).level_set\
                .filter(assign_min__lte=months, assign_max__gte=months).first()
        print(level)
        if not level:
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Instance has not level.')))
        day_range = (datetime.now() - timedelta(7))
        responses = instance.response_set.filter(response='done')
        milestones = level.milestones.filter(value__gte=months, value__lte=months)\
            .exclude(id__in=[i.milestone_id for i in responses])\
            .exclude(id__in=[i.milestone_id for i in instance.response_set.filter(created_at__gte=day_range)])

        if not milestones.exists():
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Instance has not milestones to do.',
                                                         all_range_milestones_dispatched='true',
                                                         all_level_milestones_dispatched='true')))

        filtered_milestones = milestones.filter(value__gte=months, value__lte=months)
        act_range = 'false'

        if filtered_milestones.exists():
            milestone = filtered_milestones.order_by('?').first()
            if filtered_milestones.count() < 2:
                act_range = 'true'
        else:
            milestone = milestones.exclude(id__in=[m.pk for m in filtered_milestones]).order_by('?').first()

        milestone_text = milestone.name

        if 'locale' in form.data:
            locale = form.data['locale']
            print(locale)
            languages = Language.objects.filter(name=locale[0:2])
            if languages.exists():
                check_translation = False
                language = languages.first()
                if language.available:
                    codes = language.languagecode_set.filter(code=locale)
                    lang_translations = MilestoneTranslation.objects.filter(milestone=milestone, language=language)
                    if codes.exists():
                        code = codes.first()
                        translations = MilestoneTranslation.objects.filter(milestone=milestone, language_code=code)
                        if translations.exists():
                            milestone_text = translations.first().name
                        else:
                            check_translation = True
                    else:
                        check_translation = True

                    if check_translation:
                        if lang_translations.exists():
                            milestone_text = lang_translations.first().name
                        else:
                            if language.auto_translate:
                                region = os.getenv('region')
                                translate = boto3.client(service_name='translate', region_name=region, use_ssl=True)
                                result = translate.translate_text(Text=milestone.name, SourceLanguageCode="auto",
                                                                  TargetLanguageCode=language.name)
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

        if not form.cleaned_data['program']:
            program = Program.objects.get(id=1)
        else:
            program = form.cleaned_data['program']

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
        rd = relativedelta.relativedelta(datetime.now(), date)
        months = rd.months

        if rd.years:
            months = months + (rd.years * 12)

        levels = program.level_set.filter(assign_min__lte=months, assign_max__gte=months)

        if not levels.exists():
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Instance has not level.')))

        level = levels.first()

        milestones = level.milestones.all()
        filtered_milestones = milestones.filter(value__gte=months, value__lte=months)
        responses = instance.response_set.filter(response='done', milestone_id__in=[m.pk for m in milestones])
        f_responses = instance.response_set\
            .filter(response='done', milestone_id__in=[m.pk for m in filtered_milestones])

        return JsonResponse(dict(
            set_attributes=dict(
                all_level_milestones=milestones.count(),
                all_range_milestones=filtered_milestones.count(),
                level_milestones_available=milestones.exclude(id__in=(f.milestone_id for f in responses)).count(),
                range_milestones_available=filtered_milestones
                                           .exclude(id__in=(f.milestone_id for f in responses)).count(),
                level_milestones_completed=len(set(f.milestone_id for f in responses)),
                range_milestones_completed=len(set(f.milestone_id for f in f_responses))
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
            print('done')
            r.response = 'done'
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

        instance = form.cleaned_data['instance']
        user = form.cleaned_data['user_id']

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
        months = rd.months

        if rd.years:
            months = months + (rd.years * 12)

        print(months)

        if form.cleaned_data['Type'].exists():
            sessions = Session.objects.filter(min__lte=months, max__gte=months,
                                              session_type__in=form.cleaned_data['Type'])
        else:
            sessions = Session.objects.filter(min__lte=months, max__gte=months)
        print(sessions)

        interactions = SessionInteraction.objects.filter(user_id=form.data['user_id'],
                                                         instance_id=instance.id,
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
                                          instance_id=instance.id,
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
        session = form.cleaned_data['session']
        field = session.field_set.filter(position=form.cleaned_data['position'])
        response = dict()

        if not field.exists():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Field not exists.')))

        field = field.first()
        fields = session.field_set.all().order_by('position')
        finish = 'false'
        response_field = field.position + 1
        if field.position == 0:
            # Guardar interaccion
            SessionInteraction.objects.create(user_id=user.id,
                                              instance_id=instance.id,
                                              type='session_init',
                                              field=field,
                                              session=session)
        if fields.last().position == field.position:
            finish = 'true'
            response_field = 0
            # Guardar interaccion
            SessionInteraction.objects.create(user_id=user.id,
                                              instance_id=instance.id,
                                              type='session_finish',
                                              field=field,
                                              session=session)
        attributes = dict(
            session_finish=finish,
            save_text_reply=False,
            position=response_field
        )
        messages = []
        if field.field_type == 'text':
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
                        text = attribute + exc
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
                messages.append(dict(text=new_text))

        elif field.field_type == 'quick_replies':
            message = dict(text='Responde: ', quick_replies=[])
            save_attribute = False
            for r in field.reply_set.all():
                rep = dict(title=r.label)
                message['quick_replies'].append(rep)
                if r.attribute:
                    save_attribute = True
                if r.attribute and r.value:
                    rep['set_attributes'] = {'last_reply': r.value}
                if r.redirect_block:
                    rep['block_names'] = [r.redirect_block]
            message['quick_reply_options'] = dict(process_text_by_ai=False, text_attribute_name='last_reply')
            attributes['save_text_reply'] = save_attribute
            messages.append(message)
            attributes['field_id'] = field.id

        elif field.field_type == 'save_values_block':
            response['redirect_to_blocks'] = [field.redirectblock.block]

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
        field = form.cleaned_data['field_id']
        reply = field.reply_set.all().filter(value=form.data['last_reply'])
        if reply.exists():
            reply_value = reply.first().value
            reply_text = None
            attribute_name = reply.first().attribute
            chatfuel_value = reply.first().label
        else:
            reply_value = 0
            reply_text = form.data['last_reply']
            attribute_name = field.reply_set.first().attribute
            chatfuel_value = form.data['last_reply']
        if form.data['bot_id']:
            bot_id = form.data['bot_id']
        else:
            bot_id = 0
        # Guardar interaccion
        SessionInteraction.objects.create(user_id=user.id,
                                          instance_id=instance.id,
                                          bot_id=int(bot_id),
                                          type='quick_reply',
                                          value=int(reply_value),
                                          text=reply_text,
                                          field=field,
                                          session=Session.objects.filter(id=field.session_id).first())
        attributes = dict()
        # Guardar atributo instancia o embarazo
        if Entity.objects.get(id=1).attributes.filter(name=attribute_name).exists() or \
                Entity.objects.get(id=2).attributes.filter(name=attribute_name).exists():
            attribute = Attribute.objects.filter(name=attribute_name)
            AttributeValue.objects.create(instance=instance, attribute=attribute.first(), value=form.data['last_reply'])
            attributes[attribute_name] = chatfuel_value
        # Guardar atributo usuario
        if Entity.objects.get(id=4).attributes.filter(name=attribute_name).exists():
            UserData.objects.create(user=user, data_key=attribute_name, data_value=form.data['last_reply'])
            attributes[attribute_name] = chatfuel_value
        response = dict()
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

        months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
                  'november', 'december']

        region = os.getenv('region')
        translate = boto3.client(service_name='translate', region_name=region, use_ssl=True)
        result = translate.translate_text(Text=form.data['date'],
                                          SourceLanguageCode="auto", TargetLanguageCode="en")
        try:
            if form.data['variant'] == 'true':
                date = parser.parse(result.get('TranslatedText'))
            else:
                date = parser.parse(result.get('TranslatedText'), dayfirst=True)
        except Exception as e:
            print(e)
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_message='Not a valid string date')))

        rel = relativedelta.relativedelta(datetime.now(), date)
        child_months = (rel.years * 12) + rel.months

        lang = form.data['locale'][0:2]
        month = months[date.month - 1]
        date_result = translate.translate_text(Text="%s %s, %s" % (month, date.day, date.year), SourceLanguageCode="en",
                                               TargetLanguageCode=lang)
        locale_date = date_result.get('TranslatedText')
        return JsonResponse(dict(set_attributes=dict(
            childDOB=date,
            locale_date=locale_date,
            childMonths=child_months,
            request_status='done',
            childYears=rel.years,
            childExceedMonths=rel.months if rel.years > 0 else 0
        )))


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
