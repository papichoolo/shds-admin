from __future__ import annotations

import smtplib
from email.message import EmailMessage

from backend.config import get_settings
from backend.logging_utils import get_logger
from backend.models.invite import InviteCreatePayload

logger = get_logger(__name__)


def _invite_link(token: str) -> str:
    settings = get_settings()
    base = (settings.invite_callback_base_url or "").rstrip("/")
    if not base:
        return f"/setup?token={token}"
    return f"{base}/setup?token={token}"


def send_invite_email(payload: InviteCreatePayload, token: str) -> str:
    """Send an invite email via SMTP (logs when SMTP is not configured)."""

    settings = get_settings()
    invite_url = _invite_link(token)
    subject = f"You're invited to SHDS - {payload.branchId}"
    lines = [
        f"Hello,",
        "",
        f"You've been invited to access the SHDS dashboard for branch {payload.branchId}.",
    ]
    if payload.studentName:
        lines.append(f"Student: {payload.studentName}")
    if payload.batchName:
        lines.append(f"Batch: {payload.batchName}")
    lines.extend(
        [
            "",
            f"Roles: {', '.join(payload.roles)}",
            "",
            f"Finish setup here: {invite_url}",
            "",
            "If you were not expecting this email you can ignore it.",
        ]
    )
    if payload.message:
        lines.insert(3, payload.message)

    message = EmailMessage()
    message["To"] = payload.email
    if settings.invite_sender_email:
        message["From"] = settings.invite_sender_email
    if settings.invite_reply_to_email:
        message["Reply-To"] = settings.invite_reply_to_email
    message["Subject"] = subject
    message.set_content("\n".join(lines))

    if not settings.smtp_host or not settings.invite_sender_email:
        logger.warning(
            "Invite email not sent (SMTP incomplete)",
            extra={"to": payload.email, "branch": payload.branchId, "invite_url": invite_url},
        )
        return invite_url

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as client:
        if settings.smtp_username and settings.smtp_password:
            client.starttls()
            client.login(settings.smtp_username, settings.smtp_password)
        client.send_message(message)

    logger.info(
        "Invite email dispatched",
        extra={"to": payload.email, "branch": payload.branchId},
    )
    return invite_url
