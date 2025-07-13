from rest_framework import serializers

class ChatsSerializer(serializers.ModelSerializer):
    chat_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = ["id", "chat_name"]

    def get_chat_name(self, obj):
        user = self.context.get("user")
        if obj.from_user == user:
            return str(obj.to_user)
        return str(obj.from_user)
