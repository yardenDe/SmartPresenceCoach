import smtplib
from email.message import EmailMessage
from core.exceptions import EmailUnavailableError
from core.config import get_settings
from core.logger import get_logger

logger = get_logger("app.email")

class EmailEngine:
    def __init__(self):
        self.settings = get_settings()

    def _get_connection(self):
        server = smtplib.SMTP(
            self.settings.MAIL_HOST,
            self.settings.MAIL_PORT, 
            self.settings.MAIL_TIMEOUT
        )
        if self.settings.MAIL_USE_TLS:
            server.starttls()
        if self.settings.MAIL_USERNAME:
            server.login(self.settings.MAIL_USERNAME, self.settings.MAIL_PASSWORD)
        return server

    def _close_connection(self, server):
        if server:
            try:
                server.quit()
            except Exception:
                server.close()

    def send_email(self, to: str, subject: str, body: str, html: str | None = None):
        
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.settings.MAIL_USERNAME
        msg["To"] = to
        msg.set_content(body)

        try:
            server = self._get_connection()
            server.send_message(msg)
            logger.info(f"Email sent to {to}")
        except Exception as e:
            logger.error(f"Error sending email to {to}: {str(e)}")
            raise EmailUnavailableError
        finally:
            self._close_connection(server)