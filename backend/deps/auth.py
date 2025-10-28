"""Authentication dependencies for FastAPI routes."""
from __future__ import annotations

import os

import firebase_admin
from fastapi import Header, HTTPException, status
from firebase_admin import auth as fb_auth
from reps.firestore import fs


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

    uid = decoded["uid"]
    
    # Try to get user profile from Firestore
    user_ref = fs().collection("users").document(uid)
    user_doc = user_ref.get()
    
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return {
            "uid": uid,
            "roles": user_data.get("roles", []),
            "branchId": user_data.get("branchId"),
        }
    
    # Fallback to token claims if no Firestore profile exists
    return {
        "uid": uid,
        "roles": decoded.get("roles", []),
        "branchId": decoded.get("branchId"),
    }
