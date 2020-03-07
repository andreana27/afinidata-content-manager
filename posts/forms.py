from django import forms
from posts import models
from messenger_users.models import User


class CreatePostForm(forms.Form):

    TYPE_CHOICES = (('embeded', 'Embeded'), ('youtube', 'Youtube'))

    name = forms.CharField(label='Name')
    thumbnail = forms.CharField(label='Thumbnail')
    new = forms.BooleanField(label='New?', required=False)
    type = forms.ChoiceField(widget=forms.Select, choices=TYPE_CHOICES)
    min_range = forms.IntegerField()
    max_range = forms.IntegerField()
    area_id = forms.IntegerField()
    content = forms.CharField(label='Content')
    content_activity = forms.CharField(label='Activity for FB. (Divide sections with | )', widget=forms.Textarea)
    preview = forms.CharField(widget=forms.Textarea)


class UpdatePostFormModel(forms.ModelForm):

    class Meta:
        model = models.Post
        fields = ['name', 'content', 'type', 'min_range', 'max_range', 'area_id', 'preview']


class UpdateTaxonomy(forms.ModelForm):
    class Meta:
        model = models.Taxonomy
        fields = ['post', 'area', 'subarea', 'component']


class QuestionForm(forms.ModelForm):

    class Meta:
        model = models.Question
        fields = ('name', 'post', 'replies')


class ReviewCommentForm(forms.ModelForm):

    class Meta:
        model = models.ReviewComment
        fields = ('comment',)


class QuestionResponseForm(forms.ModelForm):

    class Meta:
        model = models.QuestionResponse
        fields = ('response', 'value')


class PostByAreaForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    area = forms.ChoiceField(choices=models.AREA)
    months = forms.IntegerField()
    is_premium = forms.ChoiceField(choices=(('true', 'true'),))
