from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from posts.models import Post
from users.models import Friendship
from django.core.cache import cache


@receiver([post_save, post_delete], sender=Post)
def invalidate_feed_in_case_changing_post(sender, instance, **kwargs):
    """Удаление кеша у всех юзеров у которых этот пост был в ленте при изменении/удалении поста"""
    author = instance.owner
    friends = Friendship.objects.filter(from_user=author, accepted=True).values_list(
        "to_user_id", flat=True
    )
    subscribers = Friendship.objects.filter(to_user=author).values_list(
        "from_user_id", flat=True
    )

    users_id = list(friends) + list(subscribers)
    for user_id in users_id:
        cache.delete(f"cached_feed_{user_id}")


@receiver([post_save, post_delete], sender=Friendship)
def invalidate_feed_in_case_changing_friend(sender, instance, **kwargs):
    """Удаление кеша при изменении/удалении друзей"""
    cache.delete(f"cached_feed_{instance.from_user}")
    cache.delete(f"cached_feed_{instance.to_user}")
