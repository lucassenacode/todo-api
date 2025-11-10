from fastapi.testclient import TestClient


def register_and_login(client: TestClient, email: str, password: str = "password123"):
    """
    Helper: cria um utilizador e faz login, retornando (token, user_data).
    """
    # Registar
    reg_response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password},
    )
    assert reg_response.status_code == 201
    user_data = reg_response.json()

    # Login
    login_response = client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    token = token_data["access_token"]
    assert token_data["token_type"] == "bearer"

    return token, user_data


def get_auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_get_me_returns_current_user(client: TestClient):
    """
    GET /api/users/me deve devolver o utilizador autenticado.
    """
    token, user = register_and_login(client, "me@example.com")
    headers = get_auth_headers(token)

    response = client.get("/api/users/me", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user["id"]
    assert data["email"] == user["email"]
    assert data["name"] is None  # começa sem nome
    assert data["role"] == "user"


def test_update_me_name_only(client: TestClient):
    """
    PUT /api/users/me com 'name' deve atualizar o nome,
    manter o email e não quebrar o login.
    """
    token, user = register_and_login(client, "profile@example.com")
    headers = get_auth_headers(token)

    # Atualizar apenas o nome
    response = client.put(
        "/api/users/me",
        headers=headers,
        json={"name": "Lucas Dev"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user["id"]
    assert data["email"] == user["email"]  # não muda
    assert data["name"] == "Lucas Dev"
    assert data["role"] == "user"

    # Conferir com GET /me
    get_resp = client.get("/api/users/me", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Lucas Dev"


def test_update_me_password_and_login_with_new_password(client: TestClient):
    """
    PUT /api/users/me com 'new_password' deve:
    - atualizar a password
    - permitir login com a nova
    - recusar login com a antiga
    """
    old_password = "oldpassword123"
    new_password = "newpassword456"

    token, _ = register_and_login(client, "pwchange@example.com", old_password)
    headers = get_auth_headers(token)

    # Trocar a password
    response = client.put(
        "/api/users/me",
        headers=headers,
        json={"new_password": new_password},
    )
    assert response.status_code == 200

    # Login com a antiga deve falhar
    bad_login = client.post(
        "/api/auth/login",
        data={"username": "pwchange@example.com", "password": old_password},
    )
    assert bad_login.status_code == 401

    # Login com a nova deve funcionar
    good_login = client.post(
        "/api/auth/login",
        data={"username": "pwchange@example.com", "password": new_password},
    )
    assert good_login.status_code == 200
    assert "access_token" in good_login.json()


def test_delete_me_soft_delete(client: TestClient):
    """
    DELETE /api/users/me deve fazer soft delete:
    - request retorna 204
    - o mesmo token deixa de funcionar (get_current_user falha)
    """
    token, _ = register_and_login(client, "delete.me@example.com")
    headers = get_auth_headers(token)

    # Apagar conta
    resp_delete = client.delete("/api/users/me", headers=headers)
    assert resp_delete.status_code == 204

    # Tentar usar o mesmo token depois deve falhar (user soft-deletado)
    resp_me = client.get("/api/users/me", headers=headers)
    # Dependendo da tua implementação de get_current_user, pode ser 401 ou 404.
    # Na maioria dos casos (user None) = 401 "Could not validate credentials"
    assert resp_me.status_code in (401, 404)
