# Simple Guide: Sign-In and Registration with Firebase

This guide explains in plain language how to create a sign-in and registration experience for the admin dashboard that works with the existing FastAPI backend.

## 1. Create your Firebase project
1. Go to [console.firebase.google.com](https://console.firebase.google.com) and create a project.
2. Enable **Authentication** and turn on an email/password provider (or another provider you prefer).
3. In **Project settings → General**, scroll to "Your apps" and copy the Web SDK configuration. You will paste this into the frontend in step 3.

## 2. Set up the backend credentials
1. Download a Firebase Admin service account key.
2. On the machine that runs FastAPI, set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` to point at that JSON file. The backend loads this file automatically when it starts up.
3. If you want to skip Firebase checks on your own computer, run the API with `DEV_AUTH_BYPASS=1`. Do **not** use this setting in staging or production. With the bypass off, every request must include a Firebase ID token. 【F:backend/deps/auth.py†L1-L43】

## 3. Build the frontend login & registration screens
1. Install the Firebase Web SDK (`npm install firebase`).
2. Paste the config from step 1 into your frontend and call `initializeApp` once.
3. For **registration**, call `createUserWithEmailAndPassword(email, password)` when the user submits the sign-up form.
4. For **login**, call `signInWithEmailAndPassword(email, password)`.
5. After each successful login, call `currentUser.getIdToken()`; this returns the Firebase **ID token** that the backend trusts.

## 4. Send the token to FastAPI
1. On every API request, attach the ID token in the `x-firebase-token` header:
   ```http
   x-firebase-token: <paste the string from getIdToken()>
   ```
2. The backend checks that header with `firebase_admin.auth.verify_id_token` and pulls out the user ID, roles, and branch information. 【F:backend/deps/auth.py†L19-L43】
3. If the token is missing or invalid, FastAPI returns `401 Unauthorized`. This usually means the user must log in again or the frontend is pointing at the wrong Firebase project.

## 5. Give each admin the right permissions
1. After registering an admin, assign them a role and branch.
2. The simplest option is to run a short Python script with the Firebase Admin SDK:
   ```python
   auth.set_custom_user_claims(uid, {"roles": ["admin"], "branchId": "1"})
   ```
3. Ask the admin to log out and back in (or call `getIdToken(true)`) so the new claims appear in their token.
4. The FastAPI routes read these fields to decide whether the user may create students for a branch. 【F:backend/deps/auth.py†L34-L42】

## 6. Seed any starting data
1. Use the Firebase console or a Python script to create Firestore documents such as branches or sample students.
2. Match the same field names the API expects (`name`, `guardianPhone`, `branchId`, etc.) so the dashboard shows consistent data.

Follow these steps in order and you will have a working email/password sign-in and registration flow that produces Firebase ID tokens the backend already understands.
