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

def test_health_checks_database_connection(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"

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

def test_private_attachment_requires_ownership(client):
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

def test_upload_content_signature_is_checked(client):
    headers = auth_headers(client)
    response = client.post("/api/diagnosis", headers=headers, data={"symptoms": "test note"}, files={
        "file": ("fake.png", b"not a png", "image/png"),
    })
    assert response.status_code == 415

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
