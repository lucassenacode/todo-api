# tests/test_admin_dashboard.py
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


def create_admin_and_get_token(
    client: TestClient, db_session: Session, email: str
) -> str:
    # Regista como user normal
    reg = client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123"},
    )
    assert reg.status_code == 201
    user_id = reg.json()["id"]

    # Promove para admin direto na DB de teste
    user = db_session.query(User).filter(User.id == user_id).first()
    user.role = "admin"
    db_session.commit()

    # Login
    login = client.post(
        "/api/auth/login",
        data={"username": email, "password": "password123"},
    )
    assert login.status_code == 200
    return login.json()["access_token"]


def create_user_and_tasks(
    client: TestClient, email: str, num_pending: int, num_completed: int
):
    reg = client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123"},
    )
    assert reg.status_code == 201

    login = client.post(
        "/api/auth/login",
        data={"username": email, "password": "password123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # cria pendentes
    for i in range(num_pending):
        r = client.post(
            "/api/tasks/",
            headers=headers,
            json={"title": f"Pending {i}"},
        )
        assert r.status_code == 201

    # cria completas
    for i in range(num_completed):
        r = client.post(
            "/api/tasks/",
            headers=headers,
            json={"title": f"Done {i}"},
        )
        assert r.status_code == 201
        task_id = r.json()["id"]
        u = client.put(
            f"/api/tasks/{task_id}",
            headers=headers,
            json={"status": "completed"},
        )
        assert u.status_code == 200


def test_admin_dashboard_stats(client: TestClient, db_session: Session):
    # usa email exclusivo pro admin
    admin_token = create_admin_and_get_token(
        client, db_session, "admin_dashboard@example.com"
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # usa email exclusivo pro user desse teste
    create_user_and_tasks(
        client,
        "dashboard_user1@example.com",
        num_pending=2,
        num_completed=1,
    )

    resp = client.get("/api/admin/dashboard", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()

    # total_users: admin + user dashboard = 2
    assert data["total_users"] == 2
    assert data["total_tasks"] == 3
    assert data["total_tasks_pending"] == 2
    assert data["total_tasks_completed"] == 1


def test_admin_dashboard_requires_admin(client: TestClient):
    reg = client.post(
        "/api/auth/register",
        json={"email": "not_admin_dash@example.com", "password": "password123"},
    )
    assert reg.status_code == 201

    login = client.post(
        "/api/auth/login",
        data={"username": "not_admin_dash@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/admin/dashboard", headers=headers)
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Admin access required"}


def test_admin_dashboard_requires_auth(client: TestClient):
    resp = client.get("/api/admin/dashboard")
    assert resp.status_code == 401
