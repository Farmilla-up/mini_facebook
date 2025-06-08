from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from posts.models import Post
from users.models import Friendship
from django.core.cache import cache
from likes.models import Like


@receiver([post_save, post_delete], sender=Like)
def invalidate_like(sender, instance, **kwargs):
    """Удаление кеша при снятия лайка"""
    user_id = instance.from_who.id
    cache.delete(f"like_cache_{user_id}")
