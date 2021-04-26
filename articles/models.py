from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from messenger_users.models import User as MessengerUser
from user_sessions.models import SessionType
from languages.models import Language
from programs.models import Program
from topics.models import Topic



STATUS_CHOICES = (
    ('draft', 'draft'),
    ('review', 'review'),
    ('rejected', 'rejected'),
    ('need_changes', 'need changes'),
    ('published', 'published')
)


class Demographic(models.Model):
    name = models.CharField(max_length=140)
    topics = models.ManyToManyField(Topic)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(choices=STATUS_CHOICES, max_length=255, default='draft')
    type = models.ForeignKey(SessionType, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    text_content = models.TextField()
    topics = models.ManyToManyField(Topic)
    min = models.IntegerField(null=True, default=0)
    max = models.IntegerField(null=True, default=72)
    preview = models.TextField()
    thumbnail = models.TextField()
    campaign = models.BooleanField(default=False)
    programs = models.ManyToManyField(Program)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Intent(models.Model):
    intent_id = models.IntegerField(default=0)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    def __str__(self):
        return "intent: {0}, article: {1}".format(self.intent_id, self.article.name)


class Interaction(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)
    user_id = models.IntegerField(default=0)
    instance_id = models.IntegerField(null=True)
    type = models.CharField(max_length=255, default='open')
    value = models.IntegerField(default=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s %s %s" % (self.article.name, self.user_id, self.type)


class ArticleTranslate(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    content = models.TextField()
    text_content = models.TextField()
    preview = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ArticleFeedback(models.Model):
    user = models.ForeignKey(MessengerUser, on_delete=models.SET_NULL, null=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)


class Missing(models.Model):
    filter_params = models.TextField()
    seen = models.TextField()
    seen_count = models.IntegerField(default=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    