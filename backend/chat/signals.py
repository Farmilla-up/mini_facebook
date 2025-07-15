from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Chat, Message
from django.core.cache import cache


@receiver([post_save, post_delete], sender=Chat)
def invalidate_chats(sender, instance, **kwargs):
    cache.delete(f"user_chats_{instance.from_user_id}")
    cache.delete(f"user_chats_{instance.to_user_id}")

@receiver([post_save, post_delete], sender = Message)
def invalidate_presice_chat(sender, instance, **kwargs): 
    cache.delete(f'chat_{instance.to_chat_id}')