"""Utility script to display recommended Firestore collections and roadmap.

Run this script to print a prioritized outline for building out the student
information system data model, including attendance tracking and supporting
collections. The guidance mirrors the architectural notes in the README, so it
can serve as a quick reference without opening documentation.
"""

from textwrap import indent


COLLECTIONS = {
    "Structural": [
        {
            "name": "branches",
            "purpose": "Store branch metadata (name, address, contact, status).",
            "key_fields": ["name", "address", "contact", "capacity", "isActive"],
            "notes": "Reference this from students, staff, enrollments, and sessions.",
        },
        {
            "name": "staff",
            "purpose": "Profiles for admins/teachers with branch and role assignments.",
            "key_fields": ["firebaseUid", "name", "email", "branchIds", "roles"],
            "notes": "Keep in sync with Firebase custom claims for authorization.",
        },
        {
            "name": "guardians",
            "purpose": "Contact information for parents/guardians shared by students.",
            "key_fields": ["name", "phone", "email", "relationship"],
            "notes": "Link guardian IDs from student documents to avoid duplication.",
        },
        {
            "name": "courses",
            "purpose": "Catalog of programs/classes offered across branches.",
            "key_fields": ["title", "gradeLevel", "description", "feeScheduleId"],
            "notes": "Attendance, enrollment, and finance collections reference this.",
        },
        {
            "name": "enrollments",
            "purpose": "Junction mapping student to course, branch, and schedule.",
            "key_fields": [
                "studentId",
                "courseId",
                "branchId",
                "status",
                "startDate",
                "endDate",
            ],
            "notes": "Anchor document for attendance, billing, and performance data.",
        },
    ],
    "Attendance": [
        {
            "name": "classSessions",
            "purpose": "Each scheduled meeting with instructor, date, and timing.",
            "key_fields": ["courseId", "branchId", "date", "startTime", "endTime", "instructorId"],
            "notes": "Generate from timetable rules or manual scheduling tools.",
        },
        {
            "name": "attendanceRecords",
            "purpose": "Student attendance status per session with optional notes.",
            "key_fields": ["sessionId", "studentId", "status", "recordedAt", "recordedBy"],
            "notes": "Index by session and student for dashboard queries.",
        },
        {
            "name": "attendanceSummaries",
            "purpose": "Denormalized rollups for reporting and analytics.",
            "key_fields": ["studentId", "courseId", "term", "presentCount", "absentCount"],
            "notes": "Update via backend jobs or Cloud Functions after records change.",
        },
    ],
    "Academic": [
        {
            "name": "assignments",
            "purpose": "Homework/tests linked to courses with due dates.",
            "key_fields": ["courseId", "title", "dueDate", "maxScore"],
            "notes": "Optional, enables grade tracking features.",
        },
        {
            "name": "grades",
            "purpose": "Scores per student per assignment with normalization details.",
            "key_fields": ["assignmentId", "studentId", "score", "gradedAt", "gradedBy"],
            "notes": "Supports progress reports and parent dashboards.",
        },
        {
            "name": "interventions",
            "purpose": "Document counseling or support actions tied to students.",
            "key_fields": ["studentId", "type", "notes", "createdAt", "createdBy"],
            "notes": "Helps maintain student support history.",
        },
    ],
    "Finance": [
        {
            "name": "feeSchedules",
            "purpose": "Baseline tuition/discount rules per course or program.",
            "key_fields": ["courseId", "baseAmount", "discounts", "dueDates"],
            "notes": "Link to enrollments to calculate invoices.",
        },
        {
            "name": "invoices",
            "purpose": "Billing documents per student/guardian per cycle.",
            "key_fields": ["enrollmentId", "issueDate", "lineItems", "total", "status"],
            "notes": "Supports payment tracking and reconciliation.",
        },
        {
            "name": "payments",
            "purpose": "Records of received payments with method and confirmation.",
            "key_fields": ["invoiceId", "amount", "method", "receivedAt", "reference"],
            "notes": "Enable receipts and outstanding balance calculations.",
        },
    ],
    "Operations": [
        {
            "name": "roleAssignments",
            "purpose": "Fine-grained permissions beyond Firebase custom claims.",
            "key_fields": ["staffId", "permissions", "branchScope"],
            "notes": "Cache aggressively (e.g., Redis) for authorization checks.",
        },
        {
            "name": "auditLogs",
            "purpose": "Append-only log of sensitive operations for compliance.",
            "key_fields": ["actorId", "action", "entity", "payload", "timestamp"],
            "notes": "Consider export to BigQuery or cold storage for retention.",
        },
        {
            "name": "notifications",
            "purpose": "Outbound communication queue to guardians/staff.",
            "key_fields": ["recipient", "channel", "message", "status", "scheduledAt"],
            "notes": "Integrate with SMS/email providers, track delivery state.",
        },
        {
            "name": "config",
            "purpose": "Feature flags and runtime settings consumed by services.",
            "key_fields": ["key", "value", "environment"],
            "notes": "Store branch calendars, integrations, or toggles.",
        },
    ],
}

ROADMAP = [
    "Start with structural collections (branches, staff, guardians, courses, enrollments).",
    "Layer in attendance by generating classSessions and attendanceRecords; update summaries via jobs.",
    "Introduce financial and administrative collections when tuition and permissions workflows are defined.",
    "Leverage Redis for caching hot reads (e.g., today\\'s sessions) and background job coordination once Firestore schema is live.",
]


def format_collection(entry: dict) -> str:
    """Format a collection entry for display."""

    fields = ", ".join(entry["key_fields"])
    block = [
        f"Name: {entry['name']}",
        f"Purpose: {entry['purpose']}",
        f"Key fields: {fields}",
        f"Notes: {entry['notes']}",
    ]
    return "\n".join(block)


def print_collections() -> None:
    """Print the categorized collection suggestions."""

    for category, items in COLLECTIONS.items():
        print(f"\n=== {category} Collections ===")
        for entry in items:
            print()
            print(indent(format_collection(entry), "  "))


def print_roadmap() -> None:
    """Print the prioritized roadmap steps."""

    print("\n=== Roadmap Priorities ===")
    for idx, step in enumerate(ROADMAP, start=1):
        print(f"  {idx}. {step}")


if __name__ == "__main__":
    print("Recommended Firestore Schema Extensions")
    print("=" * 40)
    print_collections()
    print_roadmap()
