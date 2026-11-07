import hashlib
from urllib.parse import urlparse, parse_qs

from app.core.config import settings
from app.main import app
from app.core.database import get_db
from app.routers import auth as auth_router
from app.routers import diagnosis as diagnosis_router


def register(client, email="test@example.com", password="StrongPass!234"):
    return client.post("/api/auth/register", json={
        "full_name": "Test User", "email": email, "password": password,
        "age_group": "30-45", "privacy_consent": True,
    })


def auth_headers(client, email="test@example.com"):
    response = register(client, email=email)
    assert response.status_code == 200
    cookie = response.cookies.get("mv_session")
    assert cookie
    return {"Cookie": f"mv_session={cookie}", "Origin": "http://testserver"}


def test_health_checks_database_and_security_configuration(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"
    assert response.json()["security"]["malware_scanning"] == "disabled_fail_closed"


def test_registration_uses_httponly_cookie_and_duplicate_email(client):
    first = register(client)
    second = register(client)
    assert first.status_code == 200
    assert first.json()["token_type"] == "cookie"
    assert first.cookies.get("mv_session")
    assert "httponly" in first.headers.get("set-cookie", "").lower()
    assert second.status_code == 409


def test_account_data_is_user_scoped(client):
    user_a = auth_headers(client, "a@example.com")
    user_b = auth_headers(client, "b@example.com")
    created = client.post("/api/wellness", headers=user_a, json={
        "mood": "Normal", "sleep_hours": 7, "note": "synthetic test",
    })
    assert created.status_code == 200
    assert client.get("/api/wellness", headers=user_a).json()
    assert client.get("/api/wellness", headers=user_b).json() == []


def test_womens_health_requires_opt_in(client):
    headers = auth_headers(client)
    response = client.get("/api/womens-health/cycles", headers=headers)
    assert response.status_code == 403


def test_private_attachment_requires_owner_after_clean_scan(client, monkeypatch):
    monkeypatch.setattr(diagnosis_router, "scan_uploaded_file", lambda content: None)
    owner = auth_headers(client, "owner@example.com")
    other = auth_headers(client, "other@example.com")
    png = bytes([137, 80, 78, 71, 13, 10, 26, 10]) + b"synthetic-png-payload"
    upload = client.post("/api/diagnosis", headers=owner, data={"symptoms": "test note"}, files={
        "file": ("sample.png", png, "image/png"),
    })
    assert upload.status_code == 200
    record_id = upload.json()["id"]
    assert client.get(f"/api/diagnosis/{record_id}/attachment", headers=owner).status_code == 200
    assert client.get(f"/api/diagnosis/{record_id}/attachment", headers=other).status_code == 404


def test_upload_content_signature_is_checked_before_scanning(client):
    headers = auth_headers(client)
    response = client.post("/api/diagnosis", headers=headers, data={"symptoms": "test note"}, files={
        "file": ("fake.png", b"not a png", "image/png"),
    })
    assert response.status_code == 415


def test_upload_is_rejected_when_scanner_is_not_configured(client, monkeypatch):
    monkeypatch.setattr(settings, "malware_scanner_url", "")
    monkeypatch.setattr(settings, "malware_scanner_token", "")
    headers = auth_headers(client)
    png = bytes([137, 80, 78, 71, 13, 10, 26, 10]) + b"synthetic-png-payload"
    response = client.post("/api/diagnosis", headers=headers, data={"symptoms": "test note"}, files={
        "file": ("sample.png", png, "image/png"),
    })
    assert response.status_code == 503
    assert "scanning is not configured" in response.json()["detail"].lower()


def test_upload_is_rejected_if_scanner_finds_malware(client, monkeypatch):
    def infected(_content):
        from fastapi import HTTPException
        raise HTTPException(422, "This attachment was blocked by the malware scanner.")
    monkeypatch.setattr(diagnosis_router, "scan_uploaded_file", infected)
    headers = auth_headers(client)
    png = bytes([137, 80, 78, 71, 13, 10, 26, 10]) + b"synthetic-png-payload"
    response = client.post("/api/diagnosis", headers=headers, data={"symptoms": "test note"}, files={
        "file": ("sample.png", png, "image/png"),
    })
    assert response.status_code == 422


def test_password_reset_is_generic_single_use_and_revokes_old_sessions(client, monkeypatch):
    monkeypatch.setattr(settings, "resend_api_key", "test-resend-key")
    monkeypatch.setattr(settings, "email_from", "MediVision Test <no-reply@example.test>")
    monkeypatch.setattr(settings, "app_base_url", "https://medivision.example.test")
    sent = {}
    def fake_send(recipient, reset_url):
        sent["recipient"] = recipient
        sent["url"] = reset_url
    monkeypatch.setattr(auth_router, "send_password_reset_email", fake_send)

    original = register(client, "reset@example.com", "OriginalPass!234")
    assert original.status_code == 200
    old_cookie = original.cookies.get("mv_session")
    reset_request = client.post("/api/auth/forgot-password", headers={"Origin": "http://testserver"},
                                json={"email": "reset@example.com"})
    assert reset_request.status_code == 202
    assert reset_request.json()["message"] == auth_router.RESET_GENERIC
    assert sent["recipient"] == "reset@example.com"
    token = parse_qs(urlparse(sent["url"]).fragment)["reset_token"][0]

    assert client.get("/api/auth/me", headers={"Cookie": f"mv_session={old_cookie}"}).status_code == 200
    reset = client.post("/api/auth/reset-password", headers={"Origin": "http://testserver"}, json={
        "token": token, "password": "A-New-Strong-Pass!456",
    })
    assert reset.status_code == 200
    assert client.get("/api/auth/me", headers={"Cookie": f"mv_session={old_cookie}"}).status_code == 401

    repeated = client.post("/api/auth/reset-password", headers={"Origin": "http://testserver"}, json={
        "token": token, "password": "Another-Strong-Pass!789",
    })
    assert repeated.status_code == 400

    login = client.post("/api/auth/login", json={
        "email": "reset@example.com", "password": "A-New-Strong-Pass!456",
    })
    assert login.status_code == 200


def test_password_reset_unknown_account_has_same_generic_response(client, monkeypatch):
    monkeypatch.setattr(settings, "resend_api_key", "test-resend-key")
    monkeypatch.setattr(settings, "email_from", "MediVision Test <no-reply@example.test>")
    monkeypatch.setattr(settings, "app_base_url", "https://medivision.example.test")
    sent = []
    monkeypatch.setattr(auth_router, "send_password_reset_email", lambda *args: sent.append(args))
    response = client.post("/api/auth/forgot-password", headers={"Origin": "http://testserver"},
                           json={"email": "not-registered@example.com"})
    assert response.status_code == 202
    assert response.json()["message"] == auth_router.RESET_GENERIC
    assert sent == []


def test_password_reset_does_not_persist_token_when_email_delivery_fails(client, monkeypatch):
    monkeypatch.setattr(settings, "resend_api_key", "test-resend-key")
    monkeypatch.setattr(settings, "email_from", "MediVision Test <no-reply@example.test>")
    monkeypatch.setattr(settings, "app_base_url", "https://medivision.example.test")
    register(client, "delivery@example.com")
    def fail_send(*_args):
        raise RuntimeError("mail provider test failure")
    monkeypatch.setattr(auth_router, "send_password_reset_email", fail_send)
    response = client.post("/api/auth/forgot-password", headers={"Origin": "http://testserver"},
                           json={"email": "delivery@example.com"})
    assert response.status_code == 202
    from app.models.user import PasswordResetToken
    override = app.dependency_overrides[get_db]
    generator = override()
    db = next(generator)
    try:
        assert db.query(PasswordResetToken).filter(PasswordResetToken.used_at.is_(None)).count() == 0
    finally:
        db.close()
        generator.close()


def test_untrusted_origin_is_blocked_for_cookie_requests(client):
    headers = auth_headers(client)
    headers["Origin"] = "https://attacker.example"
    response = client.post("/api/wellness", headers=headers, json={
        "mood": "Normal", "sleep_hours": 7,
    })
    assert response.status_code == 403


def test_delete_account_removes_account_and_data(client):
    headers = auth_headers(client)
    response = client.delete("/api/auth/me", headers=headers)
    assert response.status_code == 204
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_untrusted_origin_is_blocked_for_registration(client):
    response = client.post("/api/auth/register", headers={"Origin": "https://preview.example"}, json={
        "full_name": "Preview User", "email": "preview@example.com",
        "password": "StrongPass!234", "privacy_consent": True,
    })
    assert response.status_code == 403
