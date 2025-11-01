"""Plan or seed Firestore collections for the SHDS admin backend.

This script can either print the recommended collection design or create
placeholder documents in Firestore so the collections visibly exist in your
project. Use it while shaping the data model around batches, attendance, and
finance.
"""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from textwrap import indent
from typing import Iterable

import importlib.util

if importlib.util.find_spec("dotenv"):
    from dotenv import load_dotenv

    load_dotenv()


@dataclass(frozen=True)
class CollectionSpec:
    """Describe a Firestore collection and a seed document example."""

    name: str
    purpose: str
    key_fields: tuple[str, ...]
    notes: str
    sample_document: dict[str, object]


COLLECTION_CATEGORIES: dict[str, tuple[CollectionSpec, ...]] = {
    "Structural": (
        CollectionSpec(
            name="batches",
            purpose="Group students by academic batch or cohort per branch.",
            key_fields=(
                "name",
                "branchId",
                "startDate",
                "endDate",
                "schedule",
                "isActive",
            ),
            notes="Reference from enrollments so attendance and invoicing know which batch a student belongs to.",
            sample_document={
                "name": "Batch A - Grade 10",
                "branchId": "branch_001",
                "startDate": "2025-04-01",
                "endDate": "2026-03-31",
                "schedule": {
                    "days": ["Mon", "Wed", "Fri"],
                    "startTime": "09:00",
                    "endTime": "11:00",
                },
                "isActive": True,
            },
        ),
        CollectionSpec(
            name="staff",
            purpose="Store admin/teacher profiles tied to Firebase UIDs.",
            key_fields=("firebaseUid", "name", "email", "phone", "branchRoles"),
            notes="Synchronise roles with Firebase custom claims for quick authorization checks.",
            sample_document={
                "firebaseUid": "firebase_uid_123",
                "name": "Aparna Rao",
                "email": "aparna@example.com",
                "phone": "+91-90000-11111",
                "branchRoles": [
                    {"branchId": "branch_001", "roles": ["admin"]},
                    {"branchId": "branch_002", "roles": ["teacher"]},
                ],
                "active": True,
            },
        ),
        CollectionSpec(
            name="guardians",
            purpose="Capture parent/guardian contact information shared by students.",
            key_fields=("name", "phone", "email", "relationship", "studentIds"),
            notes="Attach guardian IDs to student documents so multiple siblings can share one guardian record.",
            sample_document={
                "name": "Rahul Singh",
                "phone": "+91-98888-22222",
                "email": "rahul.singh@example.com",
                "relationship": "Father",
                "studentIds": ["student_abc123", "student_xyz987"],
                "preferredChannel": "sms",
            },
        ),
        CollectionSpec(
            name="enrollments",
            purpose="Link a student to a batch with status and tuition context.",
            key_fields=(
                "studentId",
                "batchId",
                "branchId",
                "status",
                "joinedAt",
                "tuitionPlan",
            ),
            notes="Enrollments become the anchor for attendance and invoices.",
            sample_document={
                "studentId": "student_abc123",
                "batchId": "batch_a_2025",
                "branchId": "branch_001",
                "status": "active",
                "joinedAt": "2025-04-05",
                "tuitionPlan": {
                    "feeAmount": 15000,
                    "currency": "INR",
                    "billingCycle": "monthly",
                },
            },
        ),
    ),
    "Attendance": (
        CollectionSpec(
            name="attendanceRecords",
            purpose="Track each student's attendance for a given date or session.",
            key_fields=(
                "studentId",
                "batchId",
                "sessionDate",
                "status",
                "recordedBy",
                "recordedAt",
            ),
            notes="Use one document per student per session to keep history auditable.",
            sample_document={
                "studentId": "student_abc123",
                "batchId": "batch_a_2025",
                "sessionDate": "2025-04-08",
                "status": "present",
                "recordedBy": "staff_uid_987",
                "recordedAt": "2025-04-08T09:05:00+05:30",
                "notes": "Arrived on time.",
            },
        ),
        CollectionSpec(
            name="attendanceSummaries",
            purpose="Maintain monthly rollups for analytics and dashboard charts.",
            key_fields=(
                "studentId",
                "batchId",
                "month",
                "year",
                "presentCount",
                "absentCount",
                "lateCount",
            ),
            notes="Regenerate after attendanceRecords change, either via Cloud Functions or backend jobs.",
            sample_document={
                "studentId": "student_abc123",
                "batchId": "batch_a_2025",
                "month": 4,
                "year": 2025,
                "presentCount": 20,
                "absentCount": 1,
                "lateCount": 2,
                "generatedAt": "2025-05-01T00:00:00Z",
            },
        ),
    ),
    "Finance": (
        CollectionSpec(
            name="invoices",
            purpose="Represent billing cycles per enrollment with totals and due dates.",
            key_fields=(
                "enrollmentId",
                "billingPeriod",
                "issueDate",
                "dueDate",
                "status",
                "totalAmount",
            ),
            notes="Line items can reference tuition, materials, or adjustments for the period.",
            sample_document={
                "enrollmentId": "enrollment_001",
                "billingPeriod": "2025-04",
                "issueDate": "2025-04-01",
                "dueDate": "2025-04-10",
                "status": "pending",
                "totalAmount": 15000,
                "currency": "INR",
                "lineItems": [
                    {"description": "April tuition", "amount": 15000},
                ],
            },
        ),
        CollectionSpec(
            name="payments",
            purpose="Log incoming payments against invoices with reconciliation data.",
            key_fields=("invoiceId", "amount", "method", "receivedAt", "reference"),
            notes="Use status fields to manage failed or reversed payments if required.",
            sample_document={
                "invoiceId": "invoice_2025_04_student_abc123",
                "amount": 15000,
                "currency": "INR",
                "method": "upi",
                "receivedAt": "2025-04-05T14:30:00+05:30",
                "reference": "TXN123456789",
                "status": "completed",
            },
        ),
    ),
    "Operations": (
        CollectionSpec(
            name="roleAssignments",
            purpose="Fine-grained permissions stored separately from Firebase custom claims.",
            key_fields=("staffId", "permissions", "branchScope", "expiresAt"),
            notes="Cache in Redis for rapid lookup if you introduce heavier authorization rules.",
            sample_document={
                "staffId": "firebase_uid_123",
                "permissions": ["students:create", "attendance:edit"],
                "branchScope": ["branch_001"],
                "expiresAt": None,
            },
        ),
        CollectionSpec(
            name="auditLogs",
            purpose="Append-only record of sensitive actions for compliance and debugging.",
            key_fields=(
                "actorId",
                "action",
                "entityType",
                "entityId",
                "timestamp",
                "metadata",
            ),
            notes="Consider exporting to cold storage or BigQuery for long-term retention.",
            sample_document={
                "actorId": "firebase_uid_123",
                "action": "student.created",
                "entityType": "student",
                "entityId": "student_abc123",
                "timestamp": "2025-04-08T09:00:00Z",
                "metadata": {"branchId": "branch_001"},
            },
        ),
        CollectionSpec(
            name="notifications",
            purpose="Queue outbound SMS/email/app notifications to guardians and staff.",
            key_fields=(
                "recipient",
                "channel",
                "message",
                "status",
                "scheduledAt",
                "sentAt",
            ),
            notes="Supports batching and retry logic when coupled with a worker or Cloud Function.",
            sample_document={
                "recipient": {
                    "type": "guardian",
                    "id": "guardian_xyz123",
                },
                "channel": "sms",
                "message": "Reminder: Tuition due on 10 Apr.",
                "status": "queued",
                "scheduledAt": "2025-04-05T10:00:00+05:30",
                "sentAt": None,
            },
        ),
        CollectionSpec(
            name="config",
            purpose="Centralise feature flags and runtime configuration values.",
            key_fields=("key", "value", "environment", "updatedAt"),
            notes="Store calendars, integration tokens, or toggles that the dashboard consumes.",
            sample_document={
                "key": "attendance.gracePeriodMinutes",
                "value": 10,
                "environment": "production",
                "updatedAt": "2025-04-01T12:00:00Z",
            },
        ),
    ),
}

ROADMAP = (
    "Start with structural collections (batches, staff, guardians, enrollments) so every student has context.",
    "Layer in attendance by recording daily attendanceRecords and generating monthly attendanceSummaries.",
    "Introduce invoices and payments once tuition rules are defined to keep finance data consistent.",
    "Add Redis-backed caching or queues to accelerate operations such as attendance rollups and notifications.",
)


def iter_specs() -> Iterable[CollectionSpec]:
    """Yield every collection spec in category order."""

    for category in COLLECTION_CATEGORIES.values():
        yield from category


def format_spec(spec: CollectionSpec) -> str:
    """Render a collection spec for CLI output."""

    lines = [
        f"Name: {spec.name}",
        f"Purpose: {spec.purpose}",
        f"Key fields: {', '.join(spec.key_fields)}",
        f"Notes: {spec.notes}",
    ]
    return "\n".join(lines)


def print_plan() -> None:
    """Print the collection plan and roadmap."""

    print("Recommended Firestore Collections")
    print("=" * 40)
    for category_name, specs in COLLECTION_CATEGORIES.items():
        print(f"\n=== {category_name} ===")
        for spec in specs:
            print()
            print(indent(format_spec(spec), "  "))

    print("\n=== Roadmap Priorities ===")
    for idx, step in enumerate(ROADMAP, start=1):
        print(f"  {idx}. {step}")


def ensure_firebase_app(credential_path: str | None, project_id: str | None) -> None:
    """Initialise the Firebase app if needed."""

    import firebase_admin
    from firebase_admin import credentials

    if firebase_admin._apps:
        return

    options: dict[str, str] = {}
    if project_id:
        options["projectId"] = project_id

    if credential_path:
        cred = credentials.Certificate(credential_path)
        firebase_admin.initialize_app(cred, options or None)
        return

    env_credential = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if env_credential:
        cred = credentials.Certificate(env_credential)
        firebase_admin.initialize_app(cred, options or None)
        return

    firebase_admin.initialize_app(options=options or None)


def seed_firestore(
    credential_path: str | None,
    project_id: str | None,
    doc_prefix: str,
    dry_run: bool,
) -> None:
    """Create placeholder documents so the collections exist in Firestore."""

    timestamp = datetime.now(timezone.utc).isoformat()
    if dry_run:
        for spec in iter_specs():
            doc_id = f"{doc_prefix}_{spec.name}"
            payload = {
                "purpose": spec.purpose,
                "keyFields": list(spec.key_fields),
                "notes": spec.notes,
                "sampleDocument": spec.sample_document,
                "generatedAt": timestamp,
            }
            path = f"{spec.name}/{doc_id}"
            print(f"[DRY-RUN] Would upsert {path} -> {payload}")

        print("\nDry run complete. No documents were written.")
        return

    from firebase_admin import firestore

    ensure_firebase_app(credential_path, project_id)
    client = firestore.client()

    for spec in iter_specs():
        doc_id = f"{doc_prefix}_{spec.name}"
        payload = {
            "purpose": spec.purpose,
            "keyFields": list(spec.key_fields),
            "notes": spec.notes,
            "sampleDocument": spec.sample_document,
            "generatedAt": timestamp,
        }
        path = f"{spec.name}/{doc_id}"
        client.collection(spec.name).document(doc_id).set(payload)
        print(f"Upserted {path}")

    print("\nAll placeholder documents created or updated successfully.")


def build_parser() -> argparse.ArgumentParser:
    """Configure the CLI parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Print the Firestore schema plan or seed placeholder documents in your "
            "Firebase project."
        )
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Write placeholder documents to Firestore instead of just printing the plan.",
    )
    parser.add_argument(
        "--credentials",
        help="Path to a Firebase service account JSON file. Defaults to GOOGLE_APPLICATION_CREDENTIALS if set.",
    )
    parser.add_argument(
        "--project",
        help="Optional Firebase project ID override if you want to seed a non-default project.",
    )
    parser.add_argument(
        "--doc-prefix",
        default="_schema",
        help="Prefix for the placeholder document IDs (default: _schema).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the writes that would occur when seeding without touching Firestore.",
    )
    return parser


def main() -> None:
    """Entry point for the CLI."""

    parser = build_parser()
    args = parser.parse_args()

    if args.seed:
        seed_firestore(
            credential_path=args.credentials,
            project_id=args.project,
            doc_prefix=args.doc_prefix,
            dry_run=args.dry_run,
        )
    else:
        print_plan()


if __name__ == "__main__":
    main()
