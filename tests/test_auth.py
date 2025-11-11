from fastapi.testclient import TestClient


def test_register_user_success(client: TestClient):
    resp = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_user_duplicate_email(client: TestClient):
    client.post(
        "/api/auth/register",
        json={"email": "test2@example.com", "password": "password123"},
    )

    resp = client.post(
        "/api/auth/register",
        json={"email": "test2@example.com", "password": "password123"},
    )

    assert resp.status_code == 409
    assert resp.json() == {"detail": "Email already registered"}


def test_login_success(client: TestClient):
    reg = client.post(
        "/api/auth/register",
        json={"email": "test3@example.com", "password": "password123"},
    )
    assert reg.status_code == 201

    resp = client.post(
        "/api/auth/login",
        data={"username": "test3@example.com", "password": "password123"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient):
    client.post(
        "/api/auth/register",
        json={"email": "test4@example.com", "password": "password123"},
    )

    resp = client.post(
        "/api/auth/login",
        data={"username": "test4@example.com", "password": "wrongpassword"},
    )

    assert resp.status_code == 401
    assert resp.json() == {"detail": "Incorrect email or password"}
