"""User management service."""
from datetime import datetime, timezone
from typing import Any

from backend.reps.firestore import fs


def setup_user_profile(
    uid: str,
    branch_id: str,
    roles: list[str],
    *,
    display_name: str | None = None,
    student_id: str | None = None,
    guardian_id: str | None = None,
    invite_id: str | None = None,
    target_type: str | None = None,
    email: str | None = None,
) -> dict[str, Any]:
    """Create or update a user profile in Firestore."""

    user_ref = fs().collection("users").document(uid)
    snapshot = user_ref.get()
    existing = snapshot.to_dict() if snapshot and snapshot.exists else {}

    now = datetime.now(timezone.utc)
    history = list(existing.get("provisioningHistory") or [])
    history.append(
        {
            "at": now.isoformat(),
            "branchId": branch_id,
            "roles": roles,
            "inviteId": invite_id,
        }
    )

    user_data = {
        "uid": uid,
        "branchId": branch_id,
        "roles": roles,
        "displayName": display_name,
        "studentId": student_id,
        "guardianId": guardian_id,
        "targetType": target_type,
        "inviteId": invite_id,
        "email": email or existing.get("email"),
        "provisionedAt": now,
        "provisioningHistory": history,
    }

    filtered = {k: v for k, v in user_data.items() if v is not None}
    user_ref.set(filtered, merge=True)
    return filtered


def get_user_profile(uid: str) -> dict | None:
    """Get user profile from Firestore."""

    user_ref = fs().collection("users").document(uid)
    doc = user_ref.get()

    if doc.exists:
        return doc.to_dict()
    return None
