from fastapi.testclient import TestClient


def register_and_login(
    client: TestClient,
    email: str,
    password: str = "password123",
):
    reg = client.post(
        "/api/auth/register",
        json={"email": email, "password": password},
    )
    assert reg.status_code == 201
    user_data = reg.json()

    login = client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200
    token_data = login.json()
    assert token_data["token_type"] == "bearer"

    return token_data["access_token"], user_data


def get_auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_get_me_returns_current_user(client: TestClient):
    token, user = register_and_login(client, "me@example.com")
    headers = get_auth_headers(token)

    resp = client.get("/api/users/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["id"] == user["id"]
    assert data["email"] == user["email"]
    assert data["name"] is None
    assert data["role"] == "user"


def test_update_me_name_only(client: TestClient):
    token, user = register_and_login(client, "profile@example.com")
    headers = get_auth_headers(token)

    resp = client.put(
        "/api/users/me",
        headers=headers,
        json={"name": "Lucas Dev"},
    )
    assert resp.status_code == 200

    data = resp.json()
    assert data["id"] == user["id"]
    assert data["email"] == user["email"]
    assert data["name"] == "Lucas Dev"
    assert data["role"] == "user"

    check = client.get("/api/users/me", headers=headers)
    assert check.status_code == 200
    assert check.json()["name"] == "Lucas Dev"


def test_update_me_password_and_login_with_new_password(client: TestClient):
    old_password = "oldpassword123"
    new_password = "newpassword456"

    token, _ = register_and_login(
        client,
        "pwchange@example.com",
        old_password,
    )
    headers = get_auth_headers(token)

    resp = client.put(
        "/api/users/me",
        headers=headers,
        json={"new_password": new_password},
    )
    assert resp.status_code == 200

    bad_login = client.post(
        "/api/auth/login",
        data={
            "username": "pwchange@example.com",
            "password": old_password,
        },
    )
    assert bad_login.status_code == 401

    good_login = client.post(
        "/api/auth/login",
        data={
            "username": "pwchange@example.com",
            "password": new_password,
        },
    )
    assert good_login.status_code == 200
    assert "access_token" in good_login.json()


def test_delete_me_soft_delete(client: TestClient):
    token, _ = register_and_login(client, "delete.me@example.com")
    headers = get_auth_headers(token)

    resp_delete = client.delete("/api/users/me", headers=headers)
    assert resp_delete.status_code == 204

    resp_me = client.get("/api/users/me", headers=headers)
    assert resp_me.status_code in (401, 404)
