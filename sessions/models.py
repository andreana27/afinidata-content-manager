from articles.models import Topic, Demographic
from django.db import models

LANGS = [
        ('en', 'English'),
        ('es', 'Spanish; Castilian'),
        ('ar', 'Arabic')
]


class Session(models.Model):
    name = models.CharField(max_length=100)
    lang = models.CharField(max_length=10, choices=LANGS, default=LANGS[0][0], verbose_name='idioma')
    min = models.IntegerField(null=True, default=0, verbose_name='Min meses')
    max = models.IntegerField(null=True, default=72, verbose_name='Max meses')
    topics = models.ManyToManyField(Topic)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Field(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    position = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    field_type = models.CharField(max_length=50, choices=(('text', 'Text'), ('quick_replies', 'Quick Replies'),
                                           ('save_values_block', 'Save Values Block')))

    def __str__(self):
        return "%s" % self.pk


class Message(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


class Reply(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    label = models.CharField(max_length=30)
    attribute = models.CharField(max_length=30, null=True, blank=True)
    value = models.CharField(max_length=100, null=True, blank=True)
    redirect_block = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.label


class RedirectBlock(models.Model):
    field = models.OneToOneField(Field, on_delete=models.CASCADE)
    block = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.block


class DemographicQuestion(models.Model):
    demographic = models.ForeignKey(Demographic, on_delete=models.CASCADE)
    lang = models.CharField(max_length=10, choices=LANGS, default=LANGS[0][0], verbose_name='idioma')
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question


class DemographicReply(models.Model):
    demographic = models.ForeignKey(Demographic, on_delete=models.CASCADE)
    lang = models.CharField(max_length=10, choices=LANGS, default=LANGS[0][0], verbose_name='idioma')
    reply = models.TextField()
    value = models.IntegerField(null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.reply
