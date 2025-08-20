from datetime import timezone, timedelta

from celery import shared_task
from users.models import User, Friendship
from .models import Post, Notification
from django.utils import timezone


@shared_task
def notify_friends(user_id, post_id):
    """Оповестить всех друзей в случае публикации поста"""
    try:

        user = User.objects.get(id=user_id)
        post = Post.objects.get(id=post_id)
        friends_from = Friendship.objects.filter(
            from_user=user, accepted=True
        ).values_list("to_user", flat=True)
        friends_to = Friendship.objects.filter(to_user=user, accepted=True).values_list(
            "from_user", flat=True
        )
        friends_lst = list(friends_from) + list(friends_to)
        friends = User.objects.filter(id__in=friends_lst)

        for friend in friends:
            Notification.objects.create(
                recipient=friend,
                post=post,
                message=f"Your friend, {user.name} just added a new post, click to watch it ",
            )

    except Exception as e:
        print("Error in notification celery function ")


@shared_task
def delete_expired_notifications():
    threshold = timezone.now() - timedelta(days=30)
    old_notifications = Notification.objects.filter(
        created_at__lte=threshold).delete()
    return
