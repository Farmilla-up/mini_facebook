from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta :
        exclude = ['friends']
        model = User


class AddUserSerializer(serializers.ModelSerializer):
    class Meta :
        model = User
        exclude = ['created_at','id', 'friends']


class ChangeUserSerializer(serializers.Serializer):
    name = serializers.CharField(max_length= 50, required= False)
    user_name = serializers.CharField(max_length= 50, required= False)
    avatar = serializers.FileField(required= False)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data


class EmptySerializer(serializers.Serializer):
    pass

