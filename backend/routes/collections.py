from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request

from backend.deps.auth import get_user
from backend.services.collections import (
    AuthorizationError,
    CollectionError,
    UnknownCollectionError,
    ValidationError,
    create_document,
    list_documents,
)

r = APIRouter(prefix="/collections", tags=["collections"])


@r.post("/{collection_name}")
def create_collection_document(
    collection_name: str,
    payload: dict[str, Any] = Body(..., description="Document payload to persist."),
    user=Depends(get_user),
):
    """Create a document with metadata and relationship validation."""

    try:
        return create_document(collection_name, payload, user)
    except (UnknownCollectionError, AuthorizationError, ValidationError) as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except CollectionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@r.get("/{collection_name}")
def list_collection_documents(
    collection_name: str,
    request: Request,
    user=Depends(get_user),
):
    """List documents for the provided collection."""

    filters = {key: value for key, value in request.query_params.items()}

    try:
        return list_documents(collection_name, user, filters)
    except (UnknownCollectionError, AuthorizationError, ValidationError) as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except CollectionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
