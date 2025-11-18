from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone
from typing import Any

from backend.config import get_settings
from backend.logging_utils import get_logger
from backend.models.invite import InviteAcceptPayload, InviteCreatePayload
from backend.reps.firestore import fs
from backend.services.email import send_invite_email
from backend.services.users import setup_user_profile

logger = get_logger(__name__)


class InviteError(Exception):
    """Base invite exception."""


class InvitePermissionError(InviteError):
    pass


class InviteTokenError(InviteError):
    pass


class InviteStateError(InviteError):
    pass


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _ensure_super_admin(user: dict[str, Any]) -> None:
    roles = set(user.get("roles") or [])
    email = (user.get("email") or "").lower()
    allowed = {addr.lower() for addr in get_settings().super_admin_emails}
    if "super_admin" in roles or (email and email in allowed):
        return
    raise InvitePermissionError("only super admins can manage invites")


def create_invite(payload: InviteCreatePayload, actor: dict[str, Any]) -> dict[str, Any]:
    _ensure_super_admin(actor)

    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    record = {
        "tokenHash": _token_hash(token),
        "email": payload.email.lower(),
        "branchId": payload.branchId,
        "roles": payload.roles,
        "targetType": payload.targetType,
        "targetId": payload.targetId,
        "studentName": payload.studentName,
        "batchName": payload.batchName,
        "status": "pending",
        "createdAt": now,
        "createdBy": actor.get("uid"),
        "history": [
            {"status": "pending", "at": now.isoformat(), "by": actor.get("uid")}
        ],
    }
    client = fs()
    ref = client.collection("userInvites").document()
    ref.set(record)

    invite_link = send_invite_email(payload, token)
    logger.info(
        "invite created",
        extra={"invite_id": ref.id, "email": payload.email},
    )

    safe_record = {k: v for k, v in record.items() if k != "tokenHash"}
    safe_record["id"] = ref.id
    safe_record["inviteLink"] = invite_link
    safe_record["token"] = token
    return safe_record


def accept_invite(payload: InviteAcceptPayload, actor: dict[str, Any]) -> dict[str, Any]:
    # Manual fall-back: allow setup without an invite token (e.g., self-onboarding)
    if payload.inviteToken == "-1":
        branch_id = payload.branchId or actor.get("branchId")
        if not branch_id:
            raise InviteError("branchId is required for manual setup")
        roles = payload.roles or ["student"]
        profile = setup_user_profile(
            uid=actor["uid"],
            branch_id=branch_id,
            roles=roles,
            display_name=payload.confirmedName,
            invite_id=None,
            target_type=payload.targetType,
            email=actor.get("email"),
        )
        logger.info(
            "manual setup completed",
            extra={"uid": actor.get("uid"), "branchId": branch_id, "roles": roles},
        )
        return profile

    token_hash = _token_hash(payload.inviteToken)
    client = fs()
    collection = client.collection("userInvites").where("tokenHash", "==", token_hash)
    snapshot = None
    for snap in collection.stream():
        if getattr(snap, "exists", False):
            snapshot = snap
            break
    if not snapshot:
        raise InviteTokenError("invalid or expired invite token")

    data = snapshot.to_dict() or {}
    if data.get("status") != "pending":
        raise InviteStateError("invite already used")

    invite_email = (data.get("email") or "").lower()
    actor_email = (actor.get("email") or "").lower()
    if not actor_email or actor_email != invite_email:
        raise InvitePermissionError("invite email mismatch")

    profile = setup_user_profile(
        uid=actor["uid"],
        branch_id=data["branchId"],
        roles=list(data.get("roles") or []),
        display_name=payload.confirmedName,
        student_id=data.get("targetId") if data.get("targetType") == "student" else None,
        invite_id=snapshot.id,
        target_type=data.get("targetType"),
        email=actor.get("email"),
    )

    now = datetime.now(timezone.utc)
    history = list(data.get("history") or [])
    history.append({"status": "accepted", "at": now.isoformat(), "by": actor.get("uid")})
    client.collection("userInvites").document(snapshot.id).set(
        {
            "status": "accepted",
            "acceptedAt": now,
            "acceptedBy": actor.get("uid"),
            "history": history,
        },
        merge=True,
    )
    logger.info(
        "invite accepted",
        extra={"invite_id": snapshot.id, "uid": actor.get("uid")},
    )
    return profile
