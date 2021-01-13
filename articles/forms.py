from articles import models
from django import forms


class AdminArticleForm(forms.ModelForm):

    class Meta:
        model = models.Article
        fields = ('name', 'status', 'type', 'content', 'text_content', 'topics', 'min', 'max', 'preview', 'thumbnail',
                  'campaign', 'programs')
