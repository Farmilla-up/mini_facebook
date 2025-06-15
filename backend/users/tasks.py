from celery import shared_task
from django.core.files.base import ContentFile
from PIL import Image
from .models import PreRegistration, User
from django.utils import timezone
from datetime import timedelta
from .utils import SendMail
from decouple import config
from io import BytesIO

@shared_task
def delete_expired_preregistrations():
    """
    Перманетно удаляет временные не потвержденные аккаунты
    :return:
    """
    threshold = timezone.now() - timedelta(minutes= 15)
    PreRegistration.objects.filter(created_at__lt=threshold).delete()

    return

@shared_task
def send_welcome_email(email_to, name ):
    text = f'{name}, благодарим за регистрацию, надеюсь вы еще зацените .. '
    password = config("APP_PASSWORD")
    email_from = config("EMAIL_FROM")
    email_to = email_to

    send = SendMail(
        password= password ,
        email_from= email_from,
        email_to = email_to ,
        text = text,
        subject = "Спасибо за регистрацию "
    )
    send.connect()
    send.send()
    send.close()


@shared_task
def send_confirmation_code(email_to, code):
    password = config("APP_PASSWORD")
    email_from = config("EMAIL_FROM")
    text = f"Your confirmation code : {code}, if you did not registrate , please ignore it"

    send = SendMail(
        password=password,
        email_from=email_from,
        email_to=email_to,
        text= text,
        subject= "Код подтверждения"
    )
    send.connect()
    send.send()
    send.close()


@shared_task
def compress_image(user_id):
    try:
        user = User.objects.get(id=user_id)
        image_field = user.avatar

        if not image_field:
            return

        img = Image.open(image_field)
        img = img.convert("RGB")


        max_size = (500, 500)
        img.thumbnail(max_size)

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=70)
        buffer.seek(0)

        file_name = image_field.name.split("/")[-1]
        user.avatar.save(file_name, ContentFile(buffer.read()), save=True)

    except Exception as e:
        print(f"Ошибка при сжатии изображения: {e}")