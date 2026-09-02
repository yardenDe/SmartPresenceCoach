import smtplib
from email.message import EmailMessage

from core.config import get_settings
from core.exceptions import EmailUnavailableError
from core.logger import get_logger


logger = get_logger("app.email")

EmailAttachment = tuple[str, bytes, str]


class EmailEngine:
    def __init__(self):
        self.settings = get_settings()

    def _get_connection(self) -> smtplib.SMTP:
        server = smtplib.SMTP(
            self.settings.MAIL_HOST,
            self.settings.MAIL_PORT,
            self.settings.MAIL_TIMEOUT,
        )
        if self.settings.MAIL_USE_TLS:
            server.starttls()
        if self.settings.MAIL_USERNAME:
            server.login(self.settings.MAIL_USERNAME, self.settings.MAIL_PASSWORD)
        return server

    def _close_connection(self, server: smtplib.SMTP | None) -> None:
        if server is None:
            return

        try:
            server.quit()
        except Exception:
            try:
                server.close()
            except Exception:
                logger.exception("event=email.connection_close.failed")

    def send(
        self,
        to: str,
        subject: str,
        body: str,
        html: str | None = None,
        attachments: list[EmailAttachment] | None = None,
    ) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.settings.MAIL_FROM or self.settings.MAIL_USERNAME
        message["To"] = to
        message.set_content(body)

        if html:
            message.add_alternative(html, subtype="html")

        for filename, content, mime_type in attachments or []:
            maintype, subtype = mime_type.split("/", 1)
            message.add_attachment(
                content,
                maintype=maintype,
                subtype=subtype,
                filename=filename,
            )

        server = None
        try:
            server = self._get_connection()
            server.send_message(message)
            logger.info("event=email.send.done")
        except Exception as error:
            logger.exception("event=email.send.failed")
            raise EmailUnavailableError() from error
        finally:
            self._close_connection(server)
