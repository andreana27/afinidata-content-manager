from .models import  UserChannel, UserData, User, Child, ChildData
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        # exclude = ['created_at']


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        exclude = ['created']


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        exclude = ['created']


class ChildDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChildData
        exclude = ['timestamp']


class UserChannelSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserChannel
        fields = '__all__'


class DetailedUserChannelSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=False)
    
    class Meta:
        model = UserChannel
        fields = '__all__'
