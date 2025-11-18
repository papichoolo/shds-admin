from __future__ import annotations

from google.cloud import firestore

from backend.config import get_settings

_client: firestore.Client | None = None

def _build_client() -> firestore.Client:
    settings = get_settings()
    kwargs: dict[str, str] = {}
    if settings.firestore_project_id:
        kwargs["project"] = settings.firestore_project_id
    if settings.firestore_database_id:
        kwargs["database"] = settings.firestore_database_id
    return firestore.Client(**kwargs)

def fs() -> firestore.Client:
    global _client
    if _client is None:
        _client = _build_client()
    return _client
