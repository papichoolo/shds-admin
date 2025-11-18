from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.deps.auth import get_user
from backend.models.invite import InviteAcceptPayload, InviteCreatePayload, InviteRecord
from backend.services.invites import (
    InviteError,
    InvitePermissionError,
    InviteStateError,
    InviteTokenError,
    accept_invite,
    create_invite,
)
from backend.services.users import get_user_profile

r = APIRouter(prefix="/users", tags=["users"])


class ProvisioningResponse(BaseModel):
    uid: str
    branchId: str
    roles: list[str]
    message: str


@r.post("/invites", response_model=InviteRecord, status_code=status.HTTP_201_CREATED)
def issue_invite(payload: InviteCreatePayload, user=Depends(get_user)):
    """Allow a super-admin to invite staff/students."""

    try:
        return create_invite(payload, user)
    except InvitePermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except InviteError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@r.post("/setup", response_model=ProvisioningResponse)
def setup_user(payload: InviteAcceptPayload, user=Depends(get_user)):
    """Complete profile provisioning using a secure invite token."""

    try:
        profile = accept_invite(payload, user)
        return {
            "uid": profile["uid"],
            "branchId": profile["branchId"],
            "roles": profile["roles"],
            "message": "User setup complete",
        }
    except InviteTokenError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvitePermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except InviteStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except InviteError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@r.get("/me")
def get_current_user(user=Depends(get_user)):
    """Get current user info with persisted profile blend."""

    profile = get_user_profile(user["uid"]) or {}
    merged_roles = user.get("roles") or profile.get("roles") or []
    merged_branch = user.get("branchId") or profile.get("branchId")
    merged_profile = profile or user.get("profile")
    return {**user, "roles": merged_roles, "branchId": merged_branch, "profile": merged_profile}
