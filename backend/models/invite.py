from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

InviteAudience = Literal["admin", "staff", "student", "guardian"]


class InviteCreatePayload(BaseModel):
    email: str
    branchId: str = Field(min_length=1)
    roles: list[str] = Field(min_length=1)
    targetType: InviteAudience = Field(default="staff")
    targetId: str | None = Field(default=None, description="Optional related document id")
    studentName: str | None = None
    batchName: str | None = None
    message: str | None = Field(default=None, max_length=500)

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("invalid email address")
        return value


class InviteAcceptPayload(BaseModel):
    inviteToken: str = Field(min_length=2, max_length=255, description="Provide '-1' to allow manual setup without an invite token")
    confirmedName: str | None = Field(default=None, max_length=120)
    branchId: str | None = Field(default=None, description="Required when no invite token is provided")
    roles: list[str] | None = Field(default=None, description="Fallback roles when no invite token is provided")
    targetType: InviteAudience | None = Field(default=None, description="Role type when no invite token is provided")


class InviteRecord(BaseModel):
    id: str
    email: str
    branchId: str
    roles: list[str]
    status: str
    targetType: InviteAudience
    studentName: str | None = None
    batchName: str | None = None
    inviteLink: str | None = None
    createdAt: datetime | None = None
    token: str | None = None
