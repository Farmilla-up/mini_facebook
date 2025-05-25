import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SendConfirmationCode:
    """
    Класс для отправки письма с кодом подтверждения на email с использованием SMTP через Gmail.
    """

    def __init__(self, email_from, email_to, text_with_code, password):
        """
        Инициализирует параметры письма и подключения к SMTP-серверу.

        :param email_from: Email-адрес отправителя.
        :param email_to: Email-адрес получателя.
        :param text_with_code: Текст письма с кодом подтверждения.
        :param password: Пароль от email-аккаунта отправителя.
        """
        self.email_from = email_from
        self.email_to = email_to
        self.subject = "Code confirmation"
        self.text_with_code = text_with_code
        self.password = password
        self.smtp_server = "smtp.gmail.com"
        self.port = 465
        self.server = None

    def connect(self):
        """
        Устанавливает защищённое соединение с SMTP-сервером и выполняет вход в аккаунт отправителя.

        :return: Словарь с результатом подключения (успешно или с ошибкой).
        """
        try:
            self.server = smtplib.SMTP_SSL(self.smtp_server, self.port)
            self.server.login(self.email_from, self.password)
        except Exception as e:
            return {"success": False, "error": f"Connection failed: {str(e)}"}

    def send(self):
        """
        Формирует и отправляет письмо с кодом подтверждения на указанный email.

        :return: Словарь с результатом отправки (успешно или с ошибкой).
        """
        msg = MIMEMultipart()
        msg["From"] = self.email_from
        msg["To"] = self.email_to
        msg["Subject"] = self.subject

        msg.attach(MIMEText(self.text_with_code, "plain"))

        try:
            self.server.sendmail(self.email_from, self.email_to, msg.as_string())
            return {"success": True, "text": f"Письмо отправлено на {self.email_to}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def close(self):
        """
        Закрывает соединение с SMTP-сервером, если оно было установлено.
        """
        if self.server:
            self.server.quit()
            self.server = None