"""Authentication dependencies for FastAPI routes."""
from __future__ import annotations

import os

import firebase_admin
from fastapi import Header, HTTPException, status
from firebase_admin import auth as fb_auth


if not firebase_admin._apps:
    firebase_admin.initialize_app()


def _dev_user() -> dict[str, str | list[str]]:
    """Return a development user context."""
    return {"uid": "dev", "roles": ["admin"], "branchId": "1"}


def get_user(x_firebase_token: str | None = Header(default=None)) -> dict[str, str | list[str] | None]:
    """Validate a Firebase ID token and return the caller context.

    When ``DEV_AUTH_BYPASS`` is truthy, the dependency returns a static user to
    keep local development and tests unblocked.
    """

    if os.getenv("DEV_AUTH_BYPASS"):
        return _dev_user()

    if not x_firebase_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing firebase token",
        )

    try:
        decoded = fb_auth.verify_id_token(x_firebase_token)
    except Exception as exc:  # pragma: no cover - firebase_admin specific
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        ) from exc

    return {
        "uid": decoded["uid"],
        "roles": decoded.get("roles", []),
        "branchId": decoded.get("branchId"),
    }
