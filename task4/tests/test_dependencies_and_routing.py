import pytest
from fastapi.testclient import TestClient
from app.main import app, clear_storage
from app.storage import get_storage


@pytest.fixture
def client():
    clear_storage()
    return TestClient(app)


@pytest.fixture
def user_headers():
    return {"X-User-Id": "10", "X-User-Role": "user"}


@pytest.fixture
def admin_headers():
    return {"X-User-Id": "1", "X-User-Role": "admin"}


def test_users_me_returns_current_user(client, user_headers):
    response = client.get("/users/me", headers=user_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 10
    assert data["role"] == "user"


def test_users_me_without_auth_returns_401(client):
    response = client.get("/users/me")

    assert response.status_code == 401
    assert "X-User-Id header is required" in response.json()["detail"]


def test_admin_stats_returns_403_for_regular_user(client, user_headers):
    response = client.get("/admin/stats", headers=user_headers)

    assert response.status_code == 403
    assert "Admin access required" in response.json()["detail"]


def test_admin_stats_returns_stats_for_admin(client, admin_headers):
    client.post("/tasks/", json={
        "title": "Task 1",
        "description": "test",
        "status": "todo",
        "priority": 3
    }, headers={"X-User-Id": "10", "X-User-Role": "user"})

    client.post("/tasks/", json={
        "title": "Task 2",
        "description": "test",
        "status": "in_progress",
        "priority": 4
    }, headers={"X-User-Id": "10", "X-User-Role": "user"})

    client.post("/tasks/", json={
        "title": "Task 3",
        "description": "test",
        "status": "done",
        "priority": 5
    }, headers={"X-User-Id": "20", "X-User-Role": "user"})

    response = client.get("/admin/stats", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 3
    assert data["by_status"]["todo"] == 1
    assert data["by_status"]["in_progress"] == 1
    assert data["by_status"]["done"] == 1


def test_regular_user_cannot_delete_others_task(client, user_headers):
    create_response = client.post("/tasks/", json={
        "title": "User 10 task",
        "description": "test",
        "status": "todo",
        "priority": 3
    }, headers={"X-User-Id": "10", "X-User-Role": "user"})
    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "20", "X-User-Role": "user"})

    assert response.status_code == 404


def test_admin_can_delete_others_task(client, admin_headers):
    create_response = client.post("/tasks/", json={
        "title": "User task",
        "description": "test",
        "status": "todo",
        "priority": 3
    }, headers={"X-User-Id": "10", "X-User-Role": "user"})
    task_id = create_response.json()["id"]

    response = client.delete(f"/admin/tasks/{task_id}", headers=admin_headers)

    assert response.status_code == 204

    get_response = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "10", "X-User-Role": "user"})
    assert get_response.status_code == 404


def test_regular_user_can_delete_own_task(client, user_headers):
    create_response = client.post("/tasks/", json={
        "title": "My task",
        "description": "test",
        "status": "todo",
        "priority": 3
    }, headers=user_headers)
    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=user_headers)

    assert response.status_code == 204


def test_admin_cannot_delete_nonexistent_task(client, admin_headers):
    response = client.delete("/admin/tasks/999", headers=admin_headers)

    assert response.status_code == 404


def test_get_user_by_id(client, user_headers):
    response = client.get("/users/5", headers=user_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 5
    assert data["role"] == "user"


def test_create_task_with_valid_data(client, user_headers):
    response = client.post("/tasks/", json={
        "title": "New task",
        "description": "Description",
        "status": "todo",
        "priority": 4
    }, headers=user_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New task"
    assert data["owner_id"] == 10


def test_create_task_with_invalid_priority(client, user_headers):
    response = client.post("/tasks/", json={
        "title": "Invalid priority",
        "description": "test",
        "status": "todo",
        "priority": 6
    }, headers=user_headers)

    assert response.status_code == 422


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_admin_stats_empty(client, admin_headers):
    response = client.get("/admin/stats", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 0
    assert data["by_status"]["todo"] == 0
    assert data["by_status"]["in_progress"] == 0
    assert data["by_status"]["done"] == 0