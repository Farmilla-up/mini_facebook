from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ["friends"]
        model = User


class AddUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "username", "name", "password"]


class ChangeUserSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50, required=False)
    user_name = serializers.CharField(max_length=50, required=False)
    avatar = serializers.FileField(required=False)

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


class ConfirmationEmailSerializer(serializers.Serializer):
    code = serializers.IntegerField(max_value=99999, min_value=10000)
    email = serializers.EmailField(max_length=4000)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=4000, required=False)
    username = serializers.CharField(max_length=4000, required=False)
    password = serializers.CharField(max_length=4000)
