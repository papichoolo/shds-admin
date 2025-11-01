# SHDS Admin Backend Overview

This repository holds a very small FastAPI service that currently exposes a single `/students` endpoint. The codebase already assumes Firebase Authentication for user identity and Google Firestore as the primary data store.

## What exists today

| Area | Status | Source |
| --- | --- | --- |
| FastAPI app | Single router registered in `backend/main.py`. | `backend/main.py` |
| Student endpoint | `POST /students` creates a Firestore document after role/branch checks. | `backend/routes/students.py`, `backend/services/students.py` |
| Data models | Pydantic schemas for student creation/response payloads. | `backend/models/students.py` |
| Firestore integration | Hard-coded helper returning the `primeval-gizmo-474808-m7/shdsdb` client. | `backend/reps/firestore.py` |
| Auth dependency | Firebase Admin SDK verifies an `x-firebase-token` header, with a `DEV_AUTH_BYPASS` escape hatch. | `backend/deps/auth.py` |
| Docs | Plain-language Firebase sign-in walkthrough. | `docs/simple_auth_flow.md` |

## Immediate gaps

1. **No project-level environment story** – there is no `.env.example`, container spec, or README instructions for installing dependencies, running FastAPI, or providing Firebase/Firestore credentials.
2. **Authentication stops at verification** – the backend trusts custom claims (`roles`, `branchId`) but there is no provisioning workflow, user management UI, or audit logging beyond a `createdBy` stamp.
3. **Data modeling is minimal** – only a `students` collection exists. There is no schema for branches, guardians, classes, payments, or any relational consistency checks.
4. **Infrastructure placeholders** – Redis, queues, background jobs, monitoring, and CI are absent. There are no tests or linting scripts.
5. **Frontend/dashboard is missing** – the repository does not include the admin UI that would invoke these endpoints.

## Suggested next steps

### 1. Establish local & deployment environments
- Write setup instructions (Python version, `pip install -r requirements.txt`, `.env` variables such as `GOOGLE_APPLICATION_CREDENTIALS`, `DEV_AUTH_BYPASS`).
- Provide a default `uvicorn` command and optional Dockerfile/Compose for API + any future dependencies (Redis, Firestore emulator).
- Add a `.env.example` with placeholders for Firebase web API key, Firestore project, Redis URL, etc.

### 2. Decide on core data stores
- **Firestore vs. relational**: confirm whether Firestore remains the system of record. If a relational database is required (e.g., PostgreSQL), define an ORM layer and migration workflow (Alembic).
- **Redis usage**: clarify whether Redis will serve as a cache (e.g., storing session/branch metadata) or a queue (e.g., background onboarding tasks). Document connection settings and resilience requirements.
- Draft an initial data model (ER diagram or collection schema) covering students, branches, staff, guardians, attendance, and any financial records.

### 3. Flesh out authentication & authorization flows
- Design the admin provisioning process: who can create admins, how roles/branch assignments are set, and where that state lives (custom claims vs database lookup).
- Implement token refresh handling and role caching if Redis is introduced (e.g., store decoded claims keyed by UID with TTL to reduce Firebase Admin calls).
- Add audit logging and rate limiting around sensitive endpoints.

### 4. Expand the API surface
- Add read/list endpoints for students, branches, and supporting entities.
- Introduce validation rules (e.g., phone number normalization) and idempotency safeguards.
- Plan for background jobs (notifications, async integrations) using Celery or RQ if Redis is selected.

### 5. Testing & quality gates
- Set up pytest with fixtures for the Firestore emulator or a mock layer so service functions are testable.
- Add linting/formatting (ruff/black) and a CI workflow that runs tests plus type checks.

### 6. Observability & operations
- Decide on logging format/level, request tracing, and how secrets are stored in deployment environments.
- If Redis or other managed services are used, define monitoring (Cloud Monitoring, Prometheus) and alert thresholds.

Documenting answers to the questions above (data store choice, Redis role, schema design) will unlock the next implementation tasks and align the backend, frontend, and infrastructure workstreams.
