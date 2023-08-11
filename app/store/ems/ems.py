from email.message import EmailMessage
from typing import Dict, Tuple

from aiosmtplib import SMTP, SMTPResponse
from base.base_accessor import BaseAccessor
from core.settings import EmailMessageServiceSettings
from icecream import ic
from pydantic import EmailStr
from store.ems.templates_letters import EMAIL_VERIFIER_TEXT, TEMPLATE_HTML_TEXT


class EmailMessageService(BaseAccessor):
    """Email Message Service.

    Create and send email message.
    """

    _settings: EmailMessageServiceSettings()
    _smtp: SMTP

    def _init(self):
        """initialization of additional service settings."""
        self._settings = EmailMessageServiceSettings()

    async def connect(self):
        """Connect to SMTP server."""
        self._smtp = SMTP(
            hostname=self._settings.ems_host,
            port=self._settings.ems_port,
            use_tls=self._settings.ems_is_tls,
        )
        if self._settings.ems_is_tls:
            await self._smtp.starttls()
        response = await self._smtp.connect()
        assert response.code in range(
            200, 300
        ), "EmailMessageService, Connection error host={host}, message={message}".format(
            host=self._settings.ems_host, message=response.message
        )
        response = await self._smtp.login(
            self._settings.ems_user, self._settings.ems_password.get_secret_value()
        )
        assert response.code in range(
            200, 300
        ), "EmailMessageService, Authorization  error host={host}, message={message}".format(
            host=self._settings.ems_host, message=response.message
        )
        self.logger.info("Connected to SMTP server: {smtp}".format(smtp=self._settings.ems_host))
        self.logger.info("SMTP server response message: {msg}".format(msg=response.message))

    async def disconnect(self):
        if self._smtp.is_connected:
            self._smtp.close()
        self.logger.info("Disconnect SMTP server: {smtp}".format(smtp=self._settings.ems_host))

    async def send(self, msg: EmailMessage):
        """Send an outgoing email with the user's credentials.

        Args:
            msg: email message to send
        """
        if not self._smtp.is_connected:
            await self._smtp.connect()
            await self._smtp.login(
                self._settings.ems_user, self._settings.ems_password.get_secret_value()
            )
        errors, message = await self._smtp.send_message(msg)
        self._smtp.close()
        assert not errors, message

    def create_email_message(
        self,
        email: EmailStr,
        subject: str,
        text: str,
        html_text: str = None,
    ) -> EmailMessage:
        """Create a new email.

        Args:
            email: Email
            subject: Email subject
            text: Email text
            html_text: html Email text
        """
        msg = EmailMessage()
        msg.preamble = subject
        msg["Subject"] = subject
        msg["From"] = self._settings.ems_sender
        msg["To"] = email
        msg.set_content(text)
        if html_text is not None:
            msg.add_alternative(html_text, subtype="html")
        return msg

    async def send_message_to_confirm_email(
        self, email: EmailStr, name: str, token: str, link: str
    ):
        """Send message to confirm email."""
        subject = "Service My blog - Verifier of the email address"
        text = EMAIL_VERIFIER_TEXT.format(name=name, token=token)
        htm_text = TEMPLATE_HTML_TEXT.format(
            **{
                "name": name,
                "title": "Подтверждение адреса электронной почты",
                "text": "Для завершения регистрации требуется подтвердить"
                " адрес электронной почты:",
                "link": link,
                "token": token,
                "label": "подтвердить",
            },
        )
        msg = self.create_email_message(email, subject, text, htm_text)
        await self.send(msg)

    async def send_message_to_reset_password(
        self, email: EmailStr, name: str, token: str, link: str
    ):
        """Send message to confirm email."""
        subject = "Service My blog - Verifier of the email address"
        text = EMAIL_VERIFIER_TEXT.format(name=name, token=token)
        htm_text = TEMPLATE_HTML_TEXT.format(
            **{
                "name": name,
                "title": "Сброс пароля",
                "text": "Для сброса пароля необходимо перейти по ссылке. "
                "Обратите внимание старый пароль будет изменен"
                " только в момент внесения нового",
                "link": link,
                "token": token,
                "label": "Сбросить",
            },
        )
        msg = self.create_email_message(email, subject, text, htm_text)
        await self.send(msg)
