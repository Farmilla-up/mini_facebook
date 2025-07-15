import pytest
from datetime import timedelta
from django.utils import timezone
from posts.models import Notification, Post
from posts.tasks import notify_friends, delete_expired_notifications
from users.models import User, Friendship


@pytest.mark.django_db
def test_notifications_and_delete_expired_notifications():
    """Проверяет создание оповещений и их последующее удаление"""

    user1 = User.objects.create(
        name="User1",
        email="example1@gmail.com",
        username="example1",
    )
    user2 = User.objects.create(
        name="User2",
        email="example2@gmail.com",
        username="example2",
    )

    Friendship.objects.create(from_user=user2, to_user=user1, accepted=True)

    post = Post.objects.create(owner=user2, text="some_text")

    notify_friends(user2.id, post.id)

    assert Notification.objects.filter(post=post, recipient=user1).exists()

    old_notification = Notification.objects.create(
        recipient=user1,
        post=post,
        message="Old notification",
    )

    old_notification.created_at = timezone.now() - timedelta(days=32)
    old_notification.save(update_fields=["created_at"])

    delete_expired_notifications()

    assert not Notification.objects.filter(id=old_notification.id).exists()
