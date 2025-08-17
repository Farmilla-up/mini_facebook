from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Chat, Message, ChatLastSeen
from django.core.cache import cache


@receiver([post_save, post_delete], sender=Chat)
def invalidate_chats(sender, instance, **kwargs):
    """Удаляет кэш списка чатов для участников при изменении чата."""
    cache.delete(f"user_chats_{instance.from_user_id}")
    cache.delete(f"user_chats_{instance.to_user_id}")


@receiver([post_save, post_delete], sender=Message)
def invalidate_precise_chat(sender, instance, **kwargs):
    """Удаляет кэш конкретного чата при изменении сообщений."""
    cache.delete(f"chat_{instance.to_chat_id}")


@receiver([post_save, post_delete], sender=ChatLastSeen)
def invalidate_last_seen(sender, instance, **kwargs):
    """Удаляет кеш при изменении Последнего захода в сеть"""
    cache.delete(f"last_seen_{instance.chat_id}_{instance.user_id}")
