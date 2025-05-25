from celery import shared_task
from .models import PreRegistration
from django.utils import timezone
from datetime import timedelta


@shared_task
def delete_expired_preregistrations():
    """
    Перманетно удаляет временные не потвержденные аккаунты
    :return:
    """
    threshold = timezone.now() - timedelta(minutes=15)
    PreRegistration.objects.filter(created_at__lt=threshold).delete()

    return
