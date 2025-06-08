from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import User, Friendship


@receiver([post_save, post_delete], sender=User)
def invalidate_user_info_cache(sender, instance, **kwargs):
    cache.delete(f"cache_user_{instance.id}")


@receiver([post_save, post_delete], sender=Friendship)
def invalidate_users_friends_cache(sender, instance, **kwargs):
    cache.delete(f"all_friends_{instance.from_user.id}")
    cache.delete(f"all_friends_{instance.to_user.id}")
    cache.delete(f"subscribed_to_{instance.from_user.id}")
    cache.delete(f"subscribers_of_{instance.to_user.id}")
    cache.delete(f"friend_requests_{instance.to_user.id}")
