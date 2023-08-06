from email.message import EmailMessage

from aiosmtplib import SMTP
from pydantic import EmailStr

from base.base_accessor import BaseAccessor
from core.settings import EmailMessageServiceSettings


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
        assert response.code in range(200, 300), (
            "EmailMessageService, Connection error host={host}, message={message}".format(
                host=self._settings.ems_host, message=response.message))

        self.logger.info("Connected to SMTP server: {smtp}".format(smtp=self._settings.ems_host))
        self.logger.info("SMTP server response message: {msg}".format(msg=response.message))

    async def disconnect(self):
        response = await self._smtp.quit()
        self.logger.info("Disconnect SMTP server: {smtp}".format(smtp=self._settings.ems_host))
        self.logger.info("SMTP server response message: {msg}".format(msg=response.message))

    async def send(self, msg: EmailMessage) -> None:
        """Send an outgoing email with the user's credentials.

        Args:
            msg: email message to send
        """
        await self._smtp.login(self._settings.ems_user, self._settings.ems_password.get_secret_value())
        await self._smtp.send_message(msg)

    def create_email_message(self,
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
        msg['Subject'] = subject
        msg['From'] = self._settings.ems_sender
        msg['To'] = email
        msg.set_content(text)
        if html_text is not None:
            msg.add_alternative(html_text, subtype='html')
        return msg

    async def create_and_sent(self,
                              email: EmailStr,
                              subject: str,
                              text: str,
                              html_text: str = None,
                              ) -> EmailMessage:
        """Create and send a message to a specific email address.

        Args:
            email: Email
            subject: Email subject
            text: Email text
            html_text: html Email text
        """
        msg = self.create_email_message(email, subject, text, html_text)
        await self.send(msg)
        return msg
