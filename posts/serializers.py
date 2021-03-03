from rest_framework import serializers
from posts.models import PostComplexity


class PostComplexitySerializer(serializers.ModelSerializer):

    class Meta:
        model = PostComplexity
        fields = ('post', 'user_id', 'months', 'complexity')
