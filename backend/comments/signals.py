from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Comment


@receiver([post_save, post_delete], sender=Comment)
def clear_comment_cache(sender, instance, **kwargs):
    post_id = instance.to_post_id
    cache_key = f"comments_for_post_{post_id}"
    cache.delete(cache_key)
