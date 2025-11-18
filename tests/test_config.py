from backend.config import get_settings, reset_settings_cache


def test_settings_reads_environment(monkeypatch):
    monkeypatch.setenv("FIRESTORE_PROJECT_ID", "demo-project")
    monkeypatch.setenv("FIRESTORE_DATABASE_ID", "unit-test-db")
    monkeypatch.setenv("SUPER_ADMIN_EMAILS", "ops@example.com, security@example.com")
    reset_settings_cache()

    settings = get_settings()

    assert settings.firestore_project_id == "demo-project"
    assert settings.firestore_database_id == "unit-test-db"
    assert settings.super_admin_emails == ["ops@example.com", "security@example.com"]


def test_reset_settings_cache(monkeypatch):
    monkeypatch.setenv("FIRESTORE_PROJECT_ID", "first")
    reset_settings_cache()
    assert get_settings().firestore_project_id == "first"

    monkeypatch.setenv("FIRESTORE_PROJECT_ID", "second")
    reset_settings_cache()
    assert get_settings().firestore_project_id == "second"
