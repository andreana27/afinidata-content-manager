from django import forms
from groups import models
from messenger_users.models import User


class ExchangeCodeForm(forms.Form):
    code = forms.ModelChoiceField(queryset=models.Code.objects.filter(available=True), to_field_name='code')
    messenger_user_id = forms.ModelChoiceField(User.objects.all())

