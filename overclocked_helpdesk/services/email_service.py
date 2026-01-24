import smtplib
import ssl
from email.message import EmailMessage

from overclocked_helpdesk.config import settings


def send_email_alert(
    to_email: str,
    subject: str,
    body: str,
    html: str | None = None
) -> bool:
    """
    Sends an email with optional HTML content.
    Plain text is always included as fallback.
    """

    msg = EmailMessage()
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    # Plain text fallback (ALWAYS)
    msg.set_content(body)

    # Optional HTML version
    if html:
        msg.add_alternative(html, subtype="html")

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(
            settings.SMTP_SERVER,
            settings.SMTP_PORT,
            context=context
        ) as server:
            server.login(
                settings.SMTP_USER,
                settings.SMTP_PASSWORD
            )
            server.send_message(msg)

        return True

    except Exception as e:
        print("Email error:", e)
        return False
