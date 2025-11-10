# tests/test_auth.py
from fastapi.testclient import TestClient


# O 'client' vem da nossa fixture em 'conftest.py'
def test_register_user_success(client: TestClient):
    """
    Teste 1: Registo de utilizador bem-sucedido.
    Espera um 201 Created.
    """
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data  # Garante que a password não é retornada


def test_register_user_duplicate_email(client: TestClient):
    """
    Teste 2: Tenta registar um email duplicado.
    Espera um 409 Conflict.
    """
    # 1. Cria o utilizador primeiro
    client.post(
        "/api/auth/register",
        json={"email": "test2@example.com", "password": "password123"},
    )

    # 2. Tenta criar de novo
    response = client.post(
        "/api/auth/register",
        json={"email": "test2@example.com", "password": "password123"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Email already registered"}


# tests/test_auth.py


def test_login_success(client: TestClient):
    """
    Teste 3: Login bem-sucedido.
    Espera um 200 OK e os tokens JWT.
    """
    # 1. Cria o utilizador
    reg_response = client.post(
        "/api/auth/register",
        json={"email": "test3@example.com", "password": "password123"},
    )
    assert reg_response.status_code == 201  # Garante que o registo funcionou

    # 2. Tenta fazer login
    response = client.post(
        "/api/auth/login",
        data={"username": "test3@example.com", "password": "password123"},
    )

    # 3. Agora as asserções devem passar
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    # MANTENHA ESTA LINHA:
    assert data["token_type"] == "bearer"  # Verifica o tipo de token


def test_login_wrong_password(client: TestClient):
    """
    Teste 4: Tenta fazer login com a password errada.
    Espera um 401 Unauthorized.
    """
    # 1. Cria o utilizador
    client.post(
        "/api/auth/register",
        json={"email": "test4@example.com", "password": "password123"},
    )

    # 2. Tenta fazer login com a password errada
    response = client.post(
        "/api/auth/login",
        data={"username": "test4@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}
