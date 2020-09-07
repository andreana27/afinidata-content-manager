from instances.models import ScoreTracking, Instance
from attributes.models import Attribute
from areas.models import Area
from django import forms


class ScoreTrackingModelForm(forms.ModelForm):

    class Meta:
        model = ScoreTracking
        fields = ('value', 'area', 'instance')


class InstanceModelForm(forms.ModelForm):
    user_id = forms.IntegerField()

    class Meta:
        model = Instance
        fields = ('entity', 'name')


class InstanceAttributeValueForm(forms.Form):
    attribute = forms.ModelChoiceField(queryset=Attribute.objects.all())
    value = forms.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')
        super(InstanceAttributeValueForm, self).__init__(*args, **kwargs)
        self.fields['attribute'].queryset = self.queryset


class InstanceSectionForm(forms.Form):
    area = forms.ModelChoiceField(queryset=Area.objects.all())
    value_to_init = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')
        super(InstanceSectionForm, self).__init__(*args, **kwargs)
        self.fields['area'].queryset = self.queryset
