# tests/test_tasks.py
from typing import Tuple

from fastapi.testclient import TestClient


def create_user_and_get_token(client: TestClient, email: str) -> Tuple[str, int]:
    """
    Helper: Regista um utilizador, faz login e retorna o token E o ID do utilizador.
    """
    # 1. Registar
    reg_response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123"},
    )
    assert reg_response.status_code == 201
    user_id = reg_response.json()["id"]

    # 2. Fazer Login
    login_response = client.post(
        "/api/auth/login",
        data={"username": email, "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    return token, user_id


def get_auth_headers(token: str) -> dict:
    """Cria o cabeçalho de autorização."""
    return {"Authorization": f"Bearer {token}"}


# --- Testes do CRUD de Tarefas ---


def test_create_task_success(client: TestClient):
    """Teste 1: Criação de tarefa bem-sucedida (autenticado)."""
    # 5. CAPTURAR OS DOIS VALORES
    token, user_id = create_user_and_get_token(client, "user1@example.com")
    headers = get_auth_headers(token)

    response = client.post(
        "/api/tasks/",
        headers=headers,
        json={"title": "Minha Tarefa de Teste", "description": "Descrição"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minha Tarefa de Teste"
    assert data["status"] == "pending"
    assert data["owner_id"] == user_id


def test_create_task_unauthenticated(client: TestClient):
    """Teste 2: Tenta criar tarefa sem token."""
    response = client.post(
        "/api/tasks/",
        json={"title": "Tarefa Falhada", "description": "Sem token"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_list_tasks_ownership(client: TestClient):
    """Teste 3: Lista tarefas e verifica o ownership (RN-04)."""
    # 7. ATUALIZAR A CHAMADA (usar '_' para ignorar o ID)
    token_A, _ = create_user_and_get_token(client, "userA@example.com")
    headers_A = get_auth_headers(token_A)

    token_B, _ = create_user_and_get_token(client, "userB@example.com")
    headers_B = get_auth_headers(token_B)

    # 2. Utilizador A cria 2 tarefas
    client.post("/api/tasks/", headers=headers_A, json={"title": "Tarefa A1"})
    client.post("/api/tasks/", headers=headers_A, json={"title": "Tarefa A2"})

    # 3. Utilizador B cria 1 tarefa
    client.post("/api/tasks/", headers=headers_B, json={"title": "Tarefa B1"})

    # 4. Testar a listagem do Utilizador A
    response_A = client.get("/api/tasks/", headers=headers_A)
    assert response_A.status_code == 200
    data_A = response_A.json()
    assert data_A["total"] == 2
    assert data_A["items"][0]["title"] == "Tarefa A2"

    # 5. Testar a listagem do Utilizador B
    response_B = client.get("/api/tasks/", headers=headers_B)
    data_B = response_B.json()
    assert data_B["total"] == 1
    assert data_B["items"][0]["title"] == "Tarefa B1"


def test_get_task_not_found_or_not_owner(client: TestClient):
    """Teste 4: Tenta obter uma tarefa que não existe ou pertence a outro (RN-05)."""
    # 8. ATUALIZAR A CHAMADA (usar '_' para ignorar o ID)
    token_C, _ = create_user_and_get_token(client, "userC@example.com")
    headers_C = get_auth_headers(token_C)

    token_D, _ = create_user_and_get_token(client, "userD@example.com")
    headers_D = get_auth_headers(token_D)

    # 1. Utilizador C cria a tarefa
    response_create = client.post(
        "/api/tasks/", headers=headers_C, json={"title": "Tarefa C"}
    )
    task_id = response_create.json()["id"]

    # 2. Utilizador D tenta obter a tarefa do Utilizador C
    response_get = client.get(f"/api/tasks/{task_id}", headers=headers_D)

    assert response_get.status_code == 404
    assert response_get.json() == {"detail": "Task not found"}

    # 3. Utilizador C tenta obter uma tarefa que não existe
    # (Corrigi o seu caminho original de "/api//tasks/9999" para "/api/tasks/9999")
    response_get_nonexistent = client.get("/api/tasks/9999", headers=headers_C)
    assert response_get_nonexistent.status_code == 404
