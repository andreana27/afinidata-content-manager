from django.views.generic import TemplateView, ListView, DetailView, View
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.http import JsonResponse, Http404
from django.contrib import messages
from random_codes import models
from random_codes import forms
from rest_framework.generics import CreateAPIView


class CodeListView(PermissionRequiredMixin, ListView):
    model = models.Code
    permission_required = 'random_codes.view_code'
    ordering = ['-pk']
    paginate_by = 10


class CodeView(PermissionRequiredMixin, DetailView):
    model = models.Code
    pk_url_kwarg = 'code_id'
    permission_required = 'random_codes.view_code'


class GenerateCodesView(PermissionRequiredMixin, TemplateView):
    template_name = 'random_codes/generate_code.html'
    permission_required = 'random_codes.add_code'

    def get_context_data(self, **kwargs):
        context = super(GenerateCodesView, self).get_context_data()
        context['form'] = forms.CodesForm()
        return context

    def post(self, request):
        form = forms.CodesForm(request.POST)

        if form.is_valid():
            for i in range(int(form.data['qty'])):
                models.Code.objects.create()
            messages.success(request, "%s codes has been added." % form.data['qty'])
            return redirect('codes:codes')

        else:
            messages.error(request, "Check your data and try again.")
            return super(GenerateCodesView, self).get(request)


@method_decorator(csrf_exempt, name='dispatch')
class UseCodeView(TemplateView):
    template_name = 'random_codes/use_code.html'

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        form = forms.UseCodeForm(request.POST)

        if form.is_valid():
            user = form.cleaned_data['user_id']
            code = form.cleaned_data['code']
            code.available = False
            code.user_id = user.pk
            code.save()
            user.userdata_set.create(data_key='premium', data_value='true')
            response = dict(set_attributes=dict(activo_premium1='true', code_error='false'), messages=[])
            return JsonResponse(response)

        response = dict(set_attributes=dict(code_error='true'), messages=[])
        return JsonResponse(response)
