from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, DetailView
from messenger_users.models import Child
from posts.models import Interaction
from dateutil.parser import parse
from django.utils import timezone
from calendar import monthrange
from posts.models import Post


class ChildView(DetailView):
    model = Child
    pk_url_kwarg = 'child_id'
    template_name = 'messenger_users/child_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ChildView, self).get_context_data()
        context['parent'] = context['child'].parent_user
        try:
            if self.request.GET['date']:
                context['date'] = parse(self.request.GET['date'])
        except Exception as e:
            print(e)
            context['date'] = timezone.now()
        context['first_date'] = parse("%s-%s-%s" % (context['date'].year, context['date'].month, 1))
        context['last_date'] = parse("%s-%s-%s" % (context['date'].year, context['date'].month,
                                                   monthrange(context['date'].year, context['date'].month)[1]))
        context['dispatched'] = Interaction.objects.filter(user_id=context['parent'].pk, type='dispatched',
                                                           created_at__gte=context['first_date'],
                                                           created_at__lte=context['last_date'])

        context['opened'] = Interaction.objects.filter(user_id=context['parent'].pk, type='opened',
                                                       created_at__gte=context['first_date'],
                                                       created_at__lte=context['last_date'])

        context['done_activities'] = Post.objects.filter(id__in=set([interaction.post_id for interaction
                                                                     in context['opened']]))
        context['sent_activities'] = Post.objects.filter(id__in=set([interaction.post_id for interaction
                                                                     in context['dispatched']]))
        context['missed'] = context['sent_activities'].count() - context['done_activities'].count()
        return context
