## SHDS Admin – Next.js Frontend

This is a new Next.js + shadcn/ui frontend that replaces the legacy static HTML pages.

### Features

- Firebase authentication (email/password and Google)
- Setup flow to assign user roles and branch
- Dashboard with tabs and a Students table fetching from the FastAPI backend
- Tailwind CSS v4 + shadcn/ui components

### Prerequisites

- Node.js 18+ and npm
- A running backend at `http://localhost:8000` (FastAPI in `../backend`)

### Configuration

Copy the example environment file and fill your Firebase config:

```powershell
Copy-Item .env.local.example .env.local
```

Then edit `.env.local` and set:

- `NEXT_PUBLIC_API_BASE` – backend URL (default is `http://localhost:8000`)
- `NEXT_PUBLIC_FIREBASE_*` – your Firebase web app config values

### Run locally

```powershell
npm install
npm run dev
```

Open http://localhost:3000

Routes:
- `/login` – sign-in page
- `/setup` – complete profile (branch + roles)
- `/dashboard` – dashboard with tabs and Students list

### Legacy prototype

The previous vanilla HTML is saved in `../frontend/_legacy` for reference.
