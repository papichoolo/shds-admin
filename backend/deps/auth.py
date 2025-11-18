"""Authentication dependencies for FastAPI routes."""
from __future__ import annotations

import firebase_admin
from fastapi import Header, HTTPException, status
from firebase_admin import auth as fb_auth, credentials

from backend.config import get_settings
from backend.logging_utils import get_logger
from backend.services.users import get_user_profile

logger = get_logger(__name__)


def _ensure_firebase_initialized() -> None:
    if firebase_admin._apps:
        return
    settings = get_settings()
    cred = None
    if settings.firebase_credentials_file:
        cred = credentials.Certificate(settings.firebase_credentials_file)
    options = {}
    if settings.firebase_project_id:
        options["projectId"] = settings.firebase_project_id
    firebase_admin.initialize_app(cred, options or None)
    logger.info(
        "firebase admin initialized",
        extra={"component": "auth", "project_id": settings.firebase_project_id},
    )


def _dev_user() -> dict[str, str | list[str]]:
    """Return a development user context."""

    return {"uid": "dev", "roles": ["admin", "super_admin"], "branchId": "1", "email": "dev@example.com"}


def get_user(x_firebase_token: str | None = Header(default=None)) -> dict[str, str | list[str] | None]:
    """Validate a Firebase ID token and return the caller context."""

    settings = get_settings()
    if settings.dev_auth_bypass:
        return _dev_user()

    if not x_firebase_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing firebase token",
        )

    _ensure_firebase_initialized()

    try:
        decoded = fb_auth.verify_id_token(x_firebase_token)
    except Exception as exc:  # pragma: no cover - firebase_admin specific
        logger.warning("invalid firebase token", extra={"component": "auth", "error": str(exc)})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        ) from exc

    profile = get_user_profile(decoded["uid"]) or {}

    roles = decoded.get("roles") or profile.get("roles") or ["student"]
    branch_id = decoded.get("branchId") or profile.get("branchId")
    email = decoded.get("email") or profile.get("email")

    return {
        "uid": decoded["uid"],
        "roles": roles,
        "branchId": branch_id,
        "email": email,
        "profile": profile or None,
    }
