from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Chat

@receiver([post_save, post_delete], sender = Chat)
def invalidate_chats(ender, instance, **kwargs): 
    cache.delete(f"user_chats_{instance.from_user_id}")
    cache.delete(f"user_chats_{instance.to_user_id}")