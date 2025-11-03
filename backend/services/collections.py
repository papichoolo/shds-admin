"""Generic collection service for Firestore-backed resources."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

from google.cloud import firestore

from backend.reps.firestore import fs


class CollectionError(Exception):
    """Base error for collection operations."""

    status_code = 400


class UnknownCollectionError(CollectionError):
    """Raised when a collection is not described by the metadata."""

    status_code = 404

    def __init__(self, collection: str) -> None:
        super().__init__(f"unknown collection '{collection}'")


class AuthorizationError(CollectionError):
    """Raised when the caller is not allowed to perform the action."""

    status_code = 403


class ValidationError(CollectionError):
    """Raised when payload validation fails."""

    status_code = 422


@dataclass(frozen=True)
class RelationshipRule:
    """Describe a relationship constraint."""

    field_path: str
    target_collections: tuple[str, ...]
    optional: bool = False


@dataclass(frozen=True)
class CollectionDefinition:
    """Describe how to validate and scope a Firestore collection."""

    name: str
    required_fields: tuple[str, ...]
    relationship_rules: tuple[RelationshipRule, ...] = ()
    branch_scope_field: str | None = None
    create_roles: tuple[str, ...] = ("admin",)
    read_roles: tuple[str, ...] = ("admin", "staff")


def _split_multi(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split("|") if part.strip())


COLLECTION_DEFINITIONS: dict[str, CollectionDefinition] = {
    "branches": CollectionDefinition(
        name="branches",
        required_fields=("name", "code", "timezone", "isActive", "address", "contact"),
        relationship_rules=(
            RelationshipRule("managerStaffId", ("staff",), optional=True),
        ),
        create_roles=("admin",),
        read_roles=("admin", "staff"),
    ),
    "staff": CollectionDefinition(
        name="staff",
        required_fields=("firebaseUid", "name", "email", "phone", "branchRoles"),
        relationship_rules=(
            RelationshipRule("branchRoles[].branchId", ("branches",), optional=True),
        ),
        create_roles=("admin",),
        read_roles=("admin",),
    ),
    "guardians": CollectionDefinition(
        name="guardians",
        required_fields=("name", "phone", "email", "relationship", "studentIds"),
        relationship_rules=(
            RelationshipRule("studentIds[]", ("students",), optional=True),
        ),
        create_roles=("admin", "staff"),
        read_roles=("admin", "staff"),
    ),
    "students": CollectionDefinition(
        name="students",
        required_fields=("firstName", "lastName", "branchId", "status"),
        relationship_rules=(
            RelationshipRule("branchId", ("branches",)),
            RelationshipRule("guardianLinks[].guardianId", ("guardians",), optional=True),
        ),
        branch_scope_field="branchId",
        create_roles=("admin", "staff"),
        read_roles=("admin", "staff"),
    ),
    "batches": CollectionDefinition(
        name="batches",
        required_fields=(
            "name",
            "branchId",
            "startDate",
            "endDate",
            "schedule",
            "isActive",
            "leadInstructorId",
        ),
        relationship_rules=(
            RelationshipRule("branchId", ("branches",)),
            RelationshipRule("leadInstructorId", ("staff",), optional=True),
        ),
        branch_scope_field="branchId",
        create_roles=("admin", "staff"),
        read_roles=("admin", "staff"),
    ),
    "enrollments": CollectionDefinition(
        name="enrollments",
        required_fields=(
            "studentId",
            "batchId",
            "branchId",
            "status",
            "joinedAt",
            "tuitionPlan",
        ),
        relationship_rules=(
            RelationshipRule("studentId", ("students",)),
            RelationshipRule("batchId", ("batches",)),
            RelationshipRule("branchId", ("branches",)),
        ),
        branch_scope_field="branchId",
        create_roles=("admin", "staff"),
        read_roles=("admin", "staff"),
    ),
    "attendanceRecords": CollectionDefinition(
        name="attendanceRecords",
        required_fields=(
            "studentId",
            "batchId",
            "sessionDate",
            "status",
            "recordedBy",
            "recordedAt",
        ),
        relationship_rules=(
            RelationshipRule("studentId", ("students",)),
            RelationshipRule("batchId", ("batches",)),
            RelationshipRule("recordedBy", ("staff",)),
        ),
        branch_scope_field=None,
        create_roles=("admin", "staff"),
        read_roles=("admin", "staff"),
    ),
    "attendanceSummaries": CollectionDefinition(
        name="attendanceSummaries",
        required_fields=(
            "studentId",
            "batchId",
            "month",
            "year",
            "presentCount",
            "absentCount",
            "lateCount",
        ),
        relationship_rules=(
            RelationshipRule("studentId", ("students",)),
            RelationshipRule("batchId", ("batches",)),
        ),
        create_roles=("admin", "staff"),
        read_roles=("admin", "staff"),
    ),
    "invoices": CollectionDefinition(
        name="invoices",
        required_fields=(
            "enrollmentId",
            "billingPeriod",
            "issueDate",
            "dueDate",
            "status",
            "totalAmount",
        ),
        relationship_rules=(
            RelationshipRule("enrollmentId", ("enrollments",)),
        ),
        branch_scope_field=None,
        create_roles=("admin",),
        read_roles=("admin", "staff"),
    ),
    "payments": CollectionDefinition(
        name="payments",
        required_fields=("invoiceId", "amount", "method", "receivedAt", "reference"),
        relationship_rules=(
            RelationshipRule("invoiceId", ("invoices",)),
        ),
        create_roles=("admin",),
        read_roles=("admin", "staff"),
    ),
    "roleAssignments": CollectionDefinition(
        name="roleAssignments",
        required_fields=("staffId", "permissions", "branchScope"),
        relationship_rules=(
            RelationshipRule("staffId", ("staff",)),
            RelationshipRule("branchScope[]", ("branches",), optional=True),
        ),
        create_roles=("admin",),
        read_roles=("admin",),
    ),
    "auditLogs": CollectionDefinition(
        name="auditLogs",
        required_fields=(
            "actorId",
            "action",
            "entityType",
            "entityId",
            "timestamp",
            "metadata",
        ),
        relationship_rules=(
            RelationshipRule("actorId", ("staff",), optional=True),
        ),
        create_roles=("admin",),
        read_roles=("admin",),
    ),
    "notifications": CollectionDefinition(
        name="notifications",
        required_fields=(
            "recipient",
            "channel",
            "message",
            "status",
            "scheduledAt",
        ),
        relationship_rules=(
            RelationshipRule("recipient.id", _split_multi("guardians|staff"), optional=True),
        ),
        create_roles=("admin", "staff"),
        read_roles=("admin", "staff"),
    ),
    "config": CollectionDefinition(
        name="config",
        required_fields=("key", "value", "environment", "updatedAt"),
        create_roles=("admin",),
        read_roles=("admin", "staff"),
    ),
}


def _get_definition(collection: str) -> CollectionDefinition:
    definition = COLLECTION_DEFINITIONS.get(collection)
    if not definition:
        raise UnknownCollectionError(collection)
    return definition


def _ensure_role(user_roles: Iterable[str], allowed_roles: Iterable[str]) -> None:
    if not set(user_roles or ()).intersection(allowed_roles):
        raise AuthorizationError("forbidden")


def _extract_values(payload: Any, field_path: str) -> list[Any]:
    parts = field_path.split(".")

    def _walk(current: Any, idx: int) -> list[Any]:
        if current is None:
            return []
        part = parts[idx]
        is_list = part.endswith("[]")
        key = part[:-2] if is_list else part

        if isinstance(current, dict):
            if key not in current:
                return []
            value = current[key]
        else:
            return []

        if is_list:
            if not isinstance(value, list):
                return []
            values: list[Any] = []
            if idx == len(parts) - 1:
                values.extend(value)
            else:
                for item in value:
                    values.extend(_walk(item, idx + 1))
            return values

        if idx == len(parts) - 1:
            return [value]

        return _walk(value, idx + 1)

    return _walk(payload, 0)


def _validate_required_fields(definition: CollectionDefinition, payload: dict[str, Any]) -> None:
    missing = [field for field in definition.required_fields if field not in payload]
    if missing:
        raise ValidationError(f"missing required fields: {', '.join(missing)}")


def _document_exists(client: firestore.Client, collection: str, doc_id: str) -> bool:
    if not doc_id:
        return False
    return client.collection(collection).document(doc_id).get().exists


def _validate_relationships(definition: CollectionDefinition, payload: dict[str, Any], client: firestore.Client) -> None:
    for rule in definition.relationship_rules:
        if "varies" in rule.target_collections:
            continue

        values = _extract_values(payload, rule.field_path)

        if not values:
            if rule.optional:
                continue
            raise ValidationError(f"missing relationship field '{rule.field_path}'")

        for value in values:
            if value is None or value == "":
                if rule.optional:
                    continue
                raise ValidationError(f"relationship '{rule.field_path}' cannot be empty")

            if not isinstance(value, str):
                raise ValidationError(
                    f"relationship '{rule.field_path}' values must be strings (document ids)"
                )

            targets = rule.target_collections
            if len(targets) == 1:
                if not _document_exists(client, targets[0], value):
                    raise ValidationError(
                        f"related document '{value}' not found in '{targets[0]}'"
                    )
            else:
                if not any(_document_exists(client, target, value) for target in targets):
                    targets_str = ", ".join(targets)
                    raise ValidationError(
                        f"related document '{value}' not found in any of: {targets_str}"
                    )


def _enforce_branch_scope(
    definition: CollectionDefinition, payload: dict[str, Any], user: dict[str, Any]
) -> None:
    if not definition.branch_scope_field:
        return

    branch_value = payload.get(definition.branch_scope_field)
    if not branch_value:
        raise ValidationError(
            f"field '{definition.branch_scope_field}' is required for branch scoping"
        )

    user_branch = user.get("branchId")
    if user_branch and branch_value != user_branch:
        raise AuthorizationError("branch scope violation")


def create_document(collection: str, payload: dict[str, Any], user: dict[str, Any]) -> dict[str, Any]:
    """Create a new document in the given collection with validation."""

    definition = _get_definition(collection)
    _ensure_role(user.get("roles"), definition.create_roles)

    _validate_required_fields(definition, payload)
    _enforce_branch_scope(definition, payload, user)

    client = fs()
    _validate_relationships(definition, payload, client)

    now = datetime.now(timezone.utc)
    doc_meta = {
        "createdAt": now,
        "createdBy": user.get("uid"),
        "updatedAt": now,
        "updatedBy": user.get("uid"),
    }

    data = {**payload, **doc_meta}
    doc_id = payload.get("id")

    collection_ref = client.collection(collection)
    doc_ref = collection_ref.document(doc_id) if doc_id else collection_ref.document()
    doc_ref.set(data)

    return {"id": doc_ref.id, **data}


def list_documents(
    collection: str,
    user: dict[str, Any],
    filters: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """List documents from a collection respecting branch scoping."""

    definition = _get_definition(collection)
    _ensure_role(user.get("roles"), definition.read_roles)

    client = fs()
    collection_ref = client.collection(collection)
    query_filters = filters.copy() if filters else {}

    if definition.branch_scope_field:
        scope_value = query_filters.pop(definition.branch_scope_field, None)
        if scope_value:
            user_branch = user.get("branchId")
            if user_branch and scope_value != user_branch:
                raise AuthorizationError("branch scope violation")
        else:
            scope_value = user.get("branchId")
            if not scope_value:
                raise ValidationError(
                    f"missing '{definition.branch_scope_field}' filter for branch-scoped collection"
                )
        collection_ref = collection_ref.where(definition.branch_scope_field, "==", scope_value)

    doc_id = query_filters.pop("id", None)
    if doc_id:
        snapshot = collection_ref.document(doc_id).get()
        if not snapshot.exists:
            return []
        doc = snapshot.to_dict() or {}
        return [{"id": snapshot.id, **doc}]

    if query_filters:
        # Apply additional filters if provided. Firestore requires indexes for compound queries,
        # so keep expectations minimal.
        for field, value in query_filters.items():
            collection_ref = collection_ref.where(field, "==", value)

    snapshots = collection_ref.stream()
    results: list[dict[str, Any]] = []
    for snap in snapshots:
        data = snap.to_dict() or {}
        results.append({"id": snap.id, **data})

    return results
