from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from posts.models import Post, Notification
from django.core.cache import cache


@receiver([post_save, post_delete], sender=Post)
def invalidate_user_posts_cache(sender, instance, **kwargs):
    cache.delete(f"posts_from_user_{instance.owner.id}")
    cache.delete(f"post_{instance.id}")


@receiver([post_save, post_delete], sender=Notification)
def invalidate_notification_cache(sender, instance, **kwargs):
    user_id = instance.recipient.id
    cache.delete(f"notifications_about_post_{user_id}")
