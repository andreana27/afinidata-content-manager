from rest_framework import serializers
from posts.models import Area, Materiales, PostComplexity, Post, Situacional


class PostComplexitySerializer(serializers.ModelSerializer):

    class Meta:
        model = PostComplexity
        fields = ('post', 'user_id', 'months', 'complexity')


class AreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Area
        fields = ('id', 'name')


class MaterialesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Materiales
        fields = ('id', 'name')


class SituacionalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Situacional
        fields = ('id', 'name')


class PostSerializer(serializers.ModelSerializer):
    area = AreaSerializer()
    materiales = MaterialesSerializer(read_only=True, many=True)
    situacional = SituacionalSerializer(read_only=True, many=True)

    class Meta:
        model = Post
        fields = ('id', 'name', 'status', 'type', 'content', 'content_activity', 'preview', 'new',
        'thumbnail', 'area', 'materiales', 'situacional', 'preparacion', 'cantidad_materiales', 
        'ar_id', 'integrantes', 'min_range', 'max_range', 'tiempo_duracion')


