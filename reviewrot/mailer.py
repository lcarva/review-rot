"""This script is used to send emails."""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


class Mailer:
    """A mailer component used to send emails."""

    def __init__(self, sender, server):
        """Returns mailer object."""
        self._cfg = {
            "sender": sender,
            "server": server,
        }

    def send(self, recipients, subject, text):
        """Sends email to recipients.

        :param list recipients : recipients of email
        :param string subject : subject of the email
        :pram string text: text of the email
        """
        sender = self._cfg["sender"]
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["from"] = sender
        msg["To"] = ", ".join(recipients)
        server = smtplib.SMTP(self._cfg["server"])
        part = MIMEText(text, "html", "utf-8")
        msg.attach(part)

        try:
            server.sendmail(sender, recipients, msg.as_string())
        finally:
            server.quit()
