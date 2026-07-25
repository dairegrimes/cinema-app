"""Pluggable email sender.

Selects a backend based on environment variables, in priority order:

1. Resend  – if RESEND_API_KEY is set (uses the Resend HTTP API).
2. SMTP    – if SMTP_HOST is set (uses smtplib).
3. Console – fallback that just logs the email (useful for local dev/tests).

Common config:
    EMAIL_FROM        – the From address (default: "Cinema Alerts <onboarding@resend.dev>")

Resend config:
    RESEND_API_KEY

SMTP config:
    SMTP_HOST, SMTP_PORT (default 587), SMTP_USERNAME, SMTP_PASSWORD,
    SMTP_USE_TLS (default "true")
"""
import logging
import os
import smtplib
from email.message import EmailMessage

import requests

logger = logging.getLogger(__name__)

DEFAULT_FROM = "Cinema Alerts <onboarding@resend.dev>"


def _email_from() -> str:
    return os.environ.get("EMAIL_FROM", DEFAULT_FROM)


def _send_resend(to: str, subject: str, html_body: str, text_body: str) -> None:
    api_key = os.environ["RESEND_API_KEY"]
    response = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "from": _email_from(),
            "to": [to],
            "subject": subject,
            "html": html_body,
            "text": text_body,
        },
        timeout=30,
    )
    response.raise_for_status()
    logger.info("Sent email to %s via Resend", to)


def _send_smtp(to: str, subject: str, html_body: str, text_body: str) -> None:
    msg = EmailMessage()
    msg["From"] = _email_from()
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    username = os.environ.get("SMTP_USERNAME")
    password = os.environ.get("SMTP_PASSWORD")
    use_tls = os.environ.get("SMTP_USE_TLS", "true").lower() == "true"

    with smtplib.SMTP(host, port, timeout=30) as server:
        if use_tls:
            server.starttls()
        if username and password:
            server.login(username, password)
        server.send_message(msg)
    logger.info("Sent email to %s via SMTP", to)


def _send_console(to: str, subject: str, html_body: str, text_body: str) -> None:
    logger.warning(
        "No email backend configured; logging email instead.\n"
        "  To: %s\n  Subject: %s\n  Body:\n%s",
        to,
        subject,
        text_body,
    )


def send_email(to: str, subject: str, html_body: str, text_body: str) -> None:
    """Send an email using the configured backend.

    Raises on hard failures (e.g. Resend/SMTP errors) so callers can decide
    whether to retry. The console fallback never raises.
    """
    if os.environ.get("RESEND_API_KEY"):
        _send_resend(to, subject, html_body, text_body)
    elif os.environ.get("SMTP_HOST"):
        _send_smtp(to, subject, html_body, text_body)
    else:
        _send_console(to, subject, html_body, text_body)
