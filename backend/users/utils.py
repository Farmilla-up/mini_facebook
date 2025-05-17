import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SendConfirmationCode:

    def __init__(self, email_from, email_to, text_with_code, password):
        self.email_from = email_from
        self.email_to = email_to
        self.subject = "Code confirmation"
        self.text_with_code = text_with_code
        self.password = password
        self.smtp_server = "smtp.gmail.com"
        self.port = 465
        self.server = None

    def connect(self):
        try:
            self.server = smtplib.SMTP_SSL(self.smtp_server, self.port)
            self.server.login(self.email_from, self.password)
        except Exception as e:
            return {"success": False, "error": f"Connection failed: {str(e)}"}

    def send(self):
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
        if self.server:
            self.server.quit()
            self.server = None
