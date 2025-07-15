from rest_framework import serializers
from .models import Chat, Message

class ChatsSerializer(serializers.ModelSerializer):
    chat_name = serializers.SerializerMethodField()
    
    class Meta : # Запрещена на территории Российской Федерации
        model = Chat
        fields = ["id", "chat_name"]

    def get_chat_name(self, obj):
        user = self.context.get("user")
        if obj.from_user == user:
            return str(obj.to_user)
        return str(obj.from_user) 


class MessageSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Message 
        fields = "__all__"


class WriteMessageSerializer(serializers.ModelSerializer): 
    class Meta : 
        fields = ["text"]
        model = Message

        def create(self, validated_data):
            return Message.objects.create(**validated_data)