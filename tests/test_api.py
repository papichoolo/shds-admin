from __future__ import annotations

import os
import pathlib
import sys
import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient

os.environ["DEV_AUTH_BYPASS"] = "1"
os.environ["SUPER_ADMIN_EMAILS"] = "ops@example.com"

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import reset_settings_cache  # noqa: E402

reset_settings_cache()

from backend.main import app  # noqa: E402
from backend.deps.auth import get_user as auth_dependency  # noqa: E402


class FakeDocumentSnapshot:
    def __init__(self, doc_id: str, data: dict[str, Any] | None):
        self.id = doc_id
        self._data = data

    @property
    def exists(self) -> bool:
        return self._data is not None

    def to_dict(self) -> dict[str, Any] | None:
        if self._data is None:
            return None
        return dict(self._data)


class FakeDocumentReference:
    def __init__(self, client: "FakeFirestoreClient", collection: str, doc_id: str):
        self._client = client
        self._collection = collection
        self.id = doc_id

    def set(self, payload: dict[str, Any], merge: bool = False) -> None:
        bucket = self._client._store.setdefault(self._collection, {})
        if merge and self.id in bucket:
            bucket[self.id].update(payload)
        else:
            bucket[self.id] = dict(payload)

    def get(self) -> FakeDocumentSnapshot:
        bucket = self._client._store.setdefault(self._collection, {})
        data = bucket.get(self.id)
        return FakeDocumentSnapshot(self.id, dict(data) if data is not None else None)


class FakeCollectionReference:
    def __init__(
        self,
        client: "FakeFirestoreClient",
        name: str,
        filters: tuple[tuple[str, Any], ...] = (),
    ):
        self._client = client
        self._name = name
        self._filters = filters

    def document(self, doc_id: str | None = None) -> FakeDocumentReference:
        if not doc_id:
            doc_id = uuid.uuid4().hex
        return FakeDocumentReference(self._client, self._name, doc_id)

    def where(self, field: str, op: str, value: Any) -> "FakeCollectionReference":
        if op != "==":
            raise NotImplementedError("Only equality filters supported in tests")
        return FakeCollectionReference(
            self._client, self._name, self._filters + ((field, value),)
        )

    def _matches(self, data: dict[str, Any]) -> bool:
        for field, expected in self._filters:
            if data.get(field) != expected:
                return False
        return True

    def stream(self) -> list[FakeDocumentSnapshot]:
        bucket = self._client._store.setdefault(self._name, {})
        snapshots: list[FakeDocumentSnapshot] = []
        for doc_id, data in bucket.items():
            if self._matches(data):
                snapshots.append(FakeDocumentSnapshot(doc_id, dict(data)))
        return snapshots


class FakeFirestoreClient:
    def __init__(self) -> None:
        self._store: dict[str, dict[str, dict[str, Any]]] = {}

    def collection(self, name: str) -> FakeCollectionReference:
        return FakeCollectionReference(self, name)


@pytest.fixture(autouse=True)
def fake_firestore(monkeypatch: pytest.MonkeyPatch) -> FakeFirestoreClient:
    fake_client = FakeFirestoreClient()

    monkeypatch.setattr("backend.reps.firestore.fs", lambda: fake_client)
    monkeypatch.setattr("backend.services.collections.fs", lambda: fake_client)
    monkeypatch.setattr("backend.services.students.fs", lambda: fake_client)
    monkeypatch.setattr("backend.services.users.fs", lambda: fake_client)
    monkeypatch.setattr("backend.services.invites.fs", lambda: fake_client)

    def _fake_send(payload, token):
        return f"https://setup.local/invite?token={token}"

    monkeypatch.setattr("backend.services.email.send_invite_email", _fake_send)

    return fake_client


@pytest.fixture(autouse=True)
def override_auth_dependency() -> Any:
    def _set(user: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = user or {
            "uid": "dev",
            "roles": ["admin", "staff", "super_admin"],
            "branchId": "branch_demo_001",
            "email": "ops@example.com",
        }
        app.dependency_overrides[auth_dependency] = lambda: payload
        return payload

    _set()
    yield _set
    app.dependency_overrides.pop(auth_dependency, None)


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_setup_user_and_get_me(client: TestClient, override_auth_dependency) -> None:
    invite_payload = {
        "email": "teacher@example.com",
        "branchId": "branch_demo_001",
        "roles": ["staff"],
        "targetType": "staff",
    }
    response = client.post("/users/invites", json=invite_payload)
    assert response.status_code == 201, response.text
    invite = response.json()
    assert invite["token"]

    override_auth_dependency(
        {
            "uid": "teacher_uid",
            "roles": [],
            "branchId": None,
            "email": "teacher@example.com",
        }
    )

    setup_resp = client.post(
        "/users/setup", json={"inviteToken": invite["token"], "confirmedName": "Teacher"}
    )
    assert setup_resp.status_code == 200, setup_resp.text
    body = setup_resp.json()
    assert body["branchId"] == "branch_demo_001"
    assert "staff" in body["roles"]

    me_resp = client.get("/users/me")
    assert me_resp.status_code == 200
    me = me_resp.json()
    assert me["branchId"] == "branch_demo_001"
    assert "staff" in me["roles"]

    override_auth_dependency()


def _create_branch(client: TestClient) -> dict[str, Any]:
    payload = {
        "id": "branch_demo_001",
        "name": "Koramangala Center",
        "code": "KRM001",
        "timezone": "Asia/Kolkata",
        "isActive": True,
        "address": {
            "line1": "123 Residency Road",
            "city": "Bengaluru",
            "state": "KA",
            "postalCode": "560029",
        },
        "contact": {
            "phone": "+91-90000-22222",
            "email": "koramangala@school.example",
        },
    }
    response = client.post("/collections/branches", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def _create_staff(client: TestClient) -> dict[str, Any]:
    payload = {
        "id": "staff_demo_001",
        "firebaseUid": "demo_firebase_staff",
        "name": "Priya Menon",
        "email": "priya.menon@example.com",
        "phone": "+91-98765-43210",
        "branchRoles": [{"branchId": "branch_demo_001", "roles": ["admin"]}],
    }
    response = client.post("/collections/staff", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def _create_guardian(client: TestClient) -> dict[str, Any]:
    payload = {
        "id": "guardian_demo_001",
        "name": "Neel Sharma",
        "phone": "+91-90000-44444",
        "email": "neel.sharma@example.com",
        "relationship": "Father",
        "studentIds": [],
    }
    response = client.post("/collections/guardians", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_collection_create_and_list(client: TestClient) -> None:
    _create_branch(client)
    _create_staff(client)
    guardian = _create_guardian(client)

    student_payload = {
        "firstName": "Ishaan",
        "lastName": "Sharma",
        "branchId": "branch_demo_001",
        "status": "active",
        "guardianLinks": [
            {"guardianId": guardian["id"], "relationship": "Father", "primary": True}
        ],
    }
    response = client.post("/collections/students", json=student_payload)
    assert response.status_code == 200, response.text
    student = response.json()
    assert student["branchId"] == student_payload["branchId"]
    assert student["guardianLinks"][0]["guardianId"] == guardian["id"]

    list_response = client.get("/collections/students?branchId=branch_demo_001")
    assert list_response.status_code == 200
    students_list = list_response.json()
    assert any(item["id"] == student["id"] for item in students_list)


def test_student_route_uses_role_guard(client: TestClient) -> None:
    payload = {
        "name": "Aarav Patel",
        "guardianPhone": "+91-90000-11111",
        "branchId": "branch_demo_001",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["branchId"] == payload["branchId"]

    list_resp = client.get("/students")
    assert list_resp.status_code == 200
    students = list_resp.json()
    assert any(item["branchId"] == "branch_demo_001" for item in students)
