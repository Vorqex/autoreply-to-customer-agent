from __future__ import annotations

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


async def _send_smtp(to: str, subject: str, body: str) -> None:
    try:
        import smtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"noreply@{settings.PROJECT_NAME.lower().replace(' ', '')}.com"
        msg["To"] = to
        msg.attach(MIMEText(body, "plain"))
        msg.attach(MIMEText(body.replace("\n", "<br>\n"), "html"))

        with smtplib.SMTP("localhost", 25, timeout=5) as s:
            s.sendmail(msg["From"], [to], msg.as_string())
    except Exception as exc:
        logger.warning("SMTP unavailable, falling back to console: %s", exc)
        logger.info("Email to=%s subject=%s body=%s", to, subject, body[:200])


async def send_email(to: str, subject: str, body: str) -> None:
    await _send_smtp(to, subject, body)


async def send_verification_email(email: str, token: str) -> None:
    verify_url = f"http://localhost:3000/verify-email?token={token}"
    subject = "Verify your email address"
    body = (
        f"Welcome to {settings.PROJECT_NAME}!\n\n"
        f"Please verify your email by clicking the link below:\n\n"
        f"{verify_url}\n\n"
        f"This link expires in 24 hours.\n\n"
        f"If you did not sign up, please ignore this email."
    )
    await send_email(email, subject, body)


async def send_password_reset(email: str, token: str) -> None:
    reset_url = f"http://localhost:3000/reset-password?token={token}"
    subject = "Reset your password"
    body = (
        f"You requested a password reset for {settings.PROJECT_NAME}.\n\n"
        f"Click the link below to reset your password:\n\n"
        f"{reset_url}\n\n"
        f"This link expires in 1 hour.\n\n"
        f"If you did not request this, please ignore this email."
    )
    await send_email(email, subject, body)
