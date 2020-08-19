from django.db import models
from django.contrib.auth.models import User


class Topic(models.Model):
    name = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Demographic(models.Model):
    name = models.CharField(max_length=140)
    topics = models.ManyToManyField(Topic)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    text_content = models.TextField()
    topics = models.ManyToManyField(Topic)
    min = models.IntegerField(null=True, default=0)
    max = models.IntegerField(null=True, default=72)
    preview = models.TextField()
    thumbnail = models.TextField()
    campaign = models.BooleanField(default=False)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Interaction(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)
    user_id = models.IntegerField(default=0)
    type = models.CharField(max_length=255, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s %s %s" % (self.article.name, self.user_id, self.type)


class ArticleTranslate(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    language = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    content = models.TextField()
    text_content = models.TextField()
    min = models.IntegerField(null=True, default=0)
    max = models.IntegerField(null=True, default=72)
    preview = models.TextField()
    thumbnail = models.TextField()
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
