from typing import Tuple

from fastapi.testclient import TestClient


def create_user_and_get_token(
    client: TestClient,
    email: str,
) -> Tuple[str, int]:
    reg = client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123"},
    )
    assert reg.status_code == 201
    user_id = reg.json()["id"]

    login = client.post(
        "/api/auth/login",
        data={"username": email, "password": "password123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    return token, user_id


def get_auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_create_task_success(client: TestClient):
    token, user_id = create_user_and_get_token(client, "user1@example.com")
    headers = get_auth_headers(token)

    resp = client.post(
        "/api/tasks/",
        headers=headers,
        json={"title": "Minha Tarefa de Teste", "description": "Descrição"},
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Minha Tarefa de Teste"
    assert data["status"] == "pending"
    assert data["owner_id"] == user_id


def test_create_task_unauthenticated(client: TestClient):
    resp = client.post(
        "/api/tasks/",
        json={"title": "Tarefa Falhada", "description": "Sem token"},
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Not authenticated"}


def test_list_tasks_ownership(client: TestClient):
    token_A, _ = create_user_and_get_token(client, "userA@example.com")
    headers_A = get_auth_headers(token_A)

    token_B, _ = create_user_and_get_token(client, "userB@example.com")
    headers_B = get_auth_headers(token_B)

    client.post("/api/tasks/", headers=headers_A, json={"title": "Tarefa A1"})
    client.post("/api/tasks/", headers=headers_A, json={"title": "Tarefa A2"})
    client.post("/api/tasks/", headers=headers_B, json={"title": "Tarefa B1"})

    resp_A = client.get("/api/tasks/", headers=headers_A)
    assert resp_A.status_code == 200
    data_A = resp_A.json()
    assert data_A["total"] == 2
    assert data_A["items"][0]["title"] == "Tarefa A2"

    resp_B = client.get("/api/tasks/", headers=headers_B)
    assert resp_B.status_code == 200
    data_B = resp_B.json()
    assert data_B["total"] == 1
    assert data_B["items"][0]["title"] == "Tarefa B1"


def test_get_task_not_found_or_not_owner(client: TestClient):
    token_C, _ = create_user_and_get_token(client, "userC@example.com")
    headers_C = get_auth_headers(token_C)

    token_D, _ = create_user_and_get_token(client, "userD@example.com")
    headers_D = get_auth_headers(token_D)

    create_resp = client.post(
        "/api/tasks/",
        headers=headers_C,
        json={"title": "Tarefa C"},
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    resp_other = client.get(f"/api/tasks/{task_id}", headers=headers_D)
    assert resp_other.status_code == 404
    assert resp_other.json() == {"detail": "Task not found"}

    resp_missing = client.get("/api/tasks/9999", headers=headers_C)
    assert resp_missing.status_code == 404
