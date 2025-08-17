from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from users.models import User
from .models import Chat, ChatLastSeen
import pytest


@pytest.mark.django_db
def test_last_seen_view_online():
    client = APIClient()

    user1 = User.objects.create(
        name="User1", email="example1@gmail.com", username="user1"
    )
    user2 = User.objects.create(
        name="User2", email="example2@gmail.com", username="user2"
    )

    chat = Chat.objects.create(from_user=user1, to_user=user2)

    ChatLastSeen.objects.create(chat=chat, user=user2, last_seen=timezone.now())

    url = f"/api/v1/chat/{user1.id}/last_seen/{chat.id}/"
    response = client.get(url)

    assert response.status_code == 200
    assert response.json()["status"] == "online"
