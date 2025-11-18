"""Central application configuration helpers."""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_emails(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value)]


class Settings(BaseSettings):
    """Configuration envelope loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    firestore_project_id: str = Field(
        default="primeval-gizmo-474808-m7",
        alias="FIRESTORE_PROJECT_ID",
        description="Default Firestore project identifier.",
    )
    firestore_database_id: str | None = Field(
        default="shdsdb",
        alias="FIRESTORE_DATABASE_ID",
        description="Named Firestore database (or default).",
    )
    firebase_project_id: str | None = Field(
        default=None,
        alias="FIREBASE_PROJECT_ID",
        description="Firebase project id for token validation.",
    )
    firebase_credentials_file: str | None = Field(
        default=None,
        alias="FIREBASE_CREDENTIALS_FILE",
        description="Path to a Firebase service account JSON file.",
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    invite_sender_email: str | None = Field(default=None, alias="INVITE_SENDER_EMAIL")
    invite_reply_to_email: str | None = Field(
        default=None, alias="INVITE_REPLY_TO_EMAIL"
    )
    invite_callback_base_url: str | None = Field(
        default=None, alias="INVITE_CALLBACK_BASE_URL"
    )
    smtp_host: str | None = Field(default=None, alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: str | None = Field(default=None, alias="SMTP_USERNAME")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")
    super_admin_emails_raw: str | list[str] | None = Field(
        default=None,
        alias="SUPER_ADMIN_EMAILS",
        description="Comma-separated list of email addresses allowed to invite users.",
    )
    dev_auth_bypass: bool = Field(default=False, alias="DEV_AUTH_BYPASS")

    @property
    def super_admin_emails(self) -> list[str]:
        return _split_emails(self.super_admin_emails_raw)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()


def reset_settings_cache() -> None:
    """Clear cached settings (handy in tests)."""

    get_settings.cache_clear()  # type: ignore[attr-defined]
