
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
=======
# SHDS Admin

A school/branch administration system with Firebase authentication and a Next.js + shadcn/ui frontend backed by FastAPI + Firestore.

---

## Application Flow

```
┌─────────────┐
│ Login Screen│
└──────┬──────┘
       │
       ▼
   ┌─────────┐
   │ Sign In │
   │ (Email/ │
   │ Google) │
   └────┬────┘
        │
        ▼
  Is new user?
  (no branchId)
        │
        ├─ Yes ──▶ ┌──────────────────┐
        │          │ Batch/Role Setup │
        │          │ (set branchId +  │
        │          │  roles: admin/   │
        │          │  staff)          │
        │          └────────┬─────────┘
        │                   │
        └─ No ──────────────┤
                            ▼
                   ┌────────────────┐
                   │   Dashboard    │
                   ├────────────────┤
                   │ Student Info   │
                   │ Attendance Info│
                   │ Fees Info      │
                   └────────────────┘
```

### Flow Details

1. **Login Screen** (`/login`)
   - Email/password or Google sign-in via Firebase Auth
   - After successful login, frontend calls `GET /users/me`
   - If user has `branchId` → redirect to **Dashboard**
   - If user missing `branchId` → redirect to **Setup**

2. **Batch/Role Setup** (`/setup`)
   - New users select:
     - **Branch ID** (e.g., `1`, `branch_001`)
     - **Roles**: Admin (full access) and/or Staff (branch-level access)
   - Frontend posts to `POST /users/setup` with Firebase token
   - After setup → redirect to **Dashboard**

3. **Dashboard** (`/dashboard`)
   - Header shows user info + logout button
   - Tabs:
     - **Student Info**: Displays students from `GET /students` (filtered by user's `branchId`)
     - **Attendance Info**: Coming soon
     - **Fees Info**: Coming soon

---

## Architecture

### Backend: FastAPI + Firestore

- **Framework**: FastAPI (Python)
- **Database**: Google Firestore (collections: `users`, `students`)
- **Auth**: Firebase Admin SDK validates ID tokens via `x-firebase-token` header
- **Endpoints**:
  - `POST /users/setup` – Assign branch + roles to user
  - `GET /users/me` – Get current user profile
  - `POST /students` – Create student (admin/staff only, branch-scoped)
  - `GET /students` – List students for user's branch
- **Dev bypass**: Set `DEV_AUTH_BYPASS=1` to skip token validation (local dev only)

### Frontend: Next.js 16 + shadcn/ui + Tailwind v4

- **Framework**: Next.js (App Router, TypeScript)
- **UI**: shadcn/ui components (button, card, input, tabs, table, etc.)
- **Auth**: Firebase Web SDK (email/password + Google provider)
- **State**: React Context (`AuthProvider`) manages user + token
- **API calls**: All requests to backend send `x-firebase-token` header

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Firebase project (Auth + Firestore enabled)
- Google Cloud credentials for Firestore (service account JSON)

### 1. Backend Setup

```powershell
cd backend
pip install -r ../requirements.txt

# Set Google Cloud credentials (if not using ADC)
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account.json"

# Optional: bypass Firebase token validation for quick local tests
# $env:DEV_AUTH_BYPASS="1"

# Start server
uvicorn main:app --reload --port 8000
```

Backend runs at http://localhost:8000

### 2. Frontend Setup

```powershell
cd web

# Create .env.local from the example
Copy-Item .env.local.example .env.local

# Edit .env.local and fill:
# - NEXT_PUBLIC_API_BASE=http://localhost:8000
# - NEXT_PUBLIC_FIREBASE_API_KEY=...
# - NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
# - NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
# - NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
# - NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
# - NEXT_PUBLIC_FIREBASE_APP_ID=...

npm install
npm run dev
```

Frontend runs at http://localhost:3000

---

## Known Gaps & Future Work

### Not Implemented (Yet)

- **Signup Service**: Self-service signup is not configured. Users are created manually in Firebase Console or via admin scripts.
- **Email Service**: No automated email flow for sending credentials to new users. Credentials are shared manually.
- **Forgot Password Flow**: Password reset is not implemented in the UI. Users must use Firebase's default password reset email or be reset manually.

### Planned Features

- **Attendance Module**: Track student attendance by date/session
- **Fees Management**: Record fee payments, generate receipts
- **Student CRUD**: Add forms to create/edit/delete students in the UI
- **Role-based UI**: Hide/show features based on user roles (admin vs. staff)
- **Reports**: Export student lists, attendance summaries, fee reports
- **Multi-tenancy**: Better branch isolation and admin controls

---

## Project Structure

```
shds-admin/
├── backend/
│   ├── main.py              # FastAPI app + CORS
│   ├── deps/
│   │   └── auth.py          # Firebase token validation
│   ├── models/
│   │   └── students.py      # Pydantic models
│   ├── reps/
│   │   └── firestore.py     # Firestore client
│   ├── routes/
│   │   ├── students.py      # Student endpoints
│   │   └── users.py         # User setup endpoints
│   └── services/
│       ├── students.py      # Student business logic
│       └── users.py         # User profile logic
├── web/                     # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── login/       # Login page
│   │   │   ├── setup/       # Profile setup page
│   │   │   └── dashboard/   # Dashboard with tabs
│   │   ├── components/ui/   # shadcn/ui components
│   │   ├── lib/
│   │   │   ├── api.ts       # API helper (adds x-firebase-token)
│   │   │   ├── firebase.ts  # Firebase client init
│   │   │   └── utils.ts     # Tailwind merge util
│   │   └── providers/
│   │       └── auth-provider.tsx  # Auth context
│   ├── .env.local.example   # Environment template
│   └── package.json
├── frontend/
│   └── _legacy/             # Old vanilla HTML prototype (archived)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## Security Notes

### What NOT to Commit

- `.env`, `.env.local`, `web/.env.*` (contains Firebase config + API keys)
- Service account JSON files (`*service-account*.json`, `*firebase-adminsdk*.json`)
- Any `*.key.json`, `*.pem`, `*.p12` private keys

A `.gitignore` is provided at the root to prevent these files from being committed.

### Firebase Web API Key

The `NEXT_PUBLIC_FIREBASE_API_KEY` in `.env.local` is **not a secret**. It's safe to expose in client-side code. Firebase security is enforced by:
- Auth rules (who can sign in)
- Firestore security rules (who can read/write data)

**Never** commit server-side credentials (service account JSON) to version control.

---

## Development Tips

- **Hot reload**: Both FastAPI (`--reload`) and Next.js (`npm run dev`) auto-reload on file changes.
- **Firestore emulator** (optional): Run `firebase emulators:start` for local Firestore; update `reps/firestore.py` to point to emulator.
- **Bypass auth for backend testing**: Set `DEV_AUTH_BYPASS=1` in backend; the frontend will still require real Firebase login.
- **Check build**: Run `npm run build` in `web/` to catch TypeScript errors before deployment.

---

## Deployment

### Backend

- Deploy to Google Cloud Run, Heroku, or any Python hosting
- Set environment variable `GOOGLE_APPLICATION_CREDENTIALS` or use ADC
- Remove `DEV_AUTH_BYPASS` in production

### Frontend

- Deploy to Vercel (recommended for Next.js):
  ```bash
  cd web
  vercel --prod
  ```
- Set environment variables in Vercel dashboard:
  - `NEXT_PUBLIC_API_BASE`
  - `NEXT_PUBLIC_FIREBASE_*`

---

## Support & Contributing

- **Issues**: Open an issue in the GitHub repo
- **PRs**: Contributions welcome! Please follow existing code style
- **Questions**: Contact the maintainer or check Firebase/Next.js docs

---

## License

MIT (or specify your license here)

