import pytest
from fastapi.testclient import TestClient
from app.main import app, clear_storage


@pytest.fixture
def client():
    clear_storage()
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"X-User-Id": "10"}


@pytest.fixture
def sample_task():
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "status": "todo",
        "priority": 3
    }


def test_create_task_success(client, auth_headers, sample_task):
    response = client.post("/tasks/", json=sample_task, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == sample_task["title"]
    assert data["description"] == sample_task["description"]
    assert data["status"] == sample_task["status"]
    assert data["priority"] == sample_task["priority"]
    assert data["owner_id"] == 10


def test_create_task_invalid_title_too_short(client, auth_headers):
    task_data = {
        "title": "ab",
        "description": "Test",
        "status": "todo",
        "priority": 3
    }
    response = client.post("/tasks/", json=task_data, headers=auth_headers)

    assert response.status_code == 422


def test_create_task_no_auth_header(client, sample_task):
    response = client.post("/tasks/", json=sample_task)

    assert response.status_code == 401
    assert "X-User-Id header is required" in response.json()["detail"]


def test_create_task_invalid_auth_header(client, sample_task):
    response = client.post("/tasks/", json=sample_task, headers={"X-User-Id": "invalid"})

    assert response.status_code == 401
    assert "must be a valid integer" in response.json()["detail"]


def test_user_sees_only_own_tasks(client, auth_headers):
    task1 = {"title": "Task for user 10", "description": "", "status": "todo", "priority": 3}
    client.post("/tasks/", json=task1, headers={"X-User-Id": "10"})

    task2 = {"title": "Task for user 20", "description": "", "status": "todo", "priority": 3}
    client.post("/tasks/", json=task2, headers={"X-User-Id": "20"})

    response = client.get("/tasks/", headers={"X-User-Id": "10"})

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task for user 10"
    assert tasks[0]["owner_id"] == 10


def test_filter_tasks_by_status(client, auth_headers):
    client.post("/tasks/", json={"title": "Todo task", "description": "", "status": "todo", "priority": 3},
                headers=auth_headers)
    client.post("/tasks/", json={"title": "Done task", "description": "", "status": "done", "priority": 3},
                headers=auth_headers)
    client.post("/tasks/",
                json={"title": "In progress task", "description": "", "status": "in_progress", "priority": 3},
                headers=auth_headers)

    response = client.get("/tasks/?status=todo", headers=auth_headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "todo"


def test_filter_tasks_by_min_priority(client, auth_headers):
    client.post("/tasks/", json={"title": "Priority 1", "description": "", "status": "todo", "priority": 1},
                headers=auth_headers)
    client.post("/tasks/", json={"title": "Priority 3", "description": "", "status": "todo", "priority": 3},
                headers=auth_headers)
    client.post("/tasks/", json={"title": "Priority 5", "description": "", "status": "todo", "priority": 5},
                headers=auth_headers)

    response = client.get("/tasks/?min_priority=3", headers=auth_headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    priorities = [t["priority"] for t in tasks]
    assert all(p >= 3 for p in priorities)


def test_filter_tasks_by_both_status_and_priority(client, auth_headers):
    client.post("/tasks/", json={"title": "Todo high", "description": "", "status": "todo", "priority": 5},
                headers=auth_headers)
    client.post("/tasks/", json={"title": "Todo low", "description": "", "status": "todo", "priority": 2},
                headers=auth_headers)
    client.post("/tasks/", json={"title": "Done high", "description": "", "status": "done", "priority": 5},
                headers=auth_headers)

    response = client.get("/tasks/?status=todo&min_priority=4", headers=auth_headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Todo high"


def test_update_task_status_success(client, auth_headers, sample_task):
    create_response = client.post("/tasks/", json=sample_task, headers=auth_headers)
    task_id = create_response.json()["id"]

    update_response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "done"},
        headers=auth_headers
    )

    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["status"] == "done"
    assert updated_task["id"] == task_id


def test_update_status_task_not_found(client, auth_headers):
    response = client.patch(
        "/tasks/999/status",
        json={"status": "done"},
        headers=auth_headers
    )

    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]


def test_get_other_users_task_returns_404(client, auth_headers):
    create_response = client.post(
        "/tasks/",
        json={"title": "User 10 task", "description": "", "status": "todo", "priority": 3},
        headers={"X-User-Id": "10"}
    )
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "20"})

    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]


def test_delete_task_success(client, auth_headers, sample_task):
    create_response = client.post("/tasks/", json=sample_task, headers=auth_headers)
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}", headers=auth_headers)

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_delete_non_existent_task(client, auth_headers):
    response = client.delete("/tasks/999", headers=auth_headers)

    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]


def test_delete_other_users_task_returns_404(client, auth_headers):
    create_response = client.post(
        "/tasks/",
        json={"title": "User 10 task", "description": "", "status": "todo", "priority": 3},
        headers={"X-User-Id": "10"}
    )
    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "20"})

    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]


def test_get_single_task_success(client, auth_headers, sample_task):
    create_response = client.post("/tasks/", json=sample_task, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}", headers=auth_headers)

    assert response.status_code == 200
    task = response.json()
    assert task["id"] == task_id
    assert task["title"] == sample_task["title"]


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_empty_tasks_list_returns_empty_array(client, auth_headers):
    response = client.get("/tasks/", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_create_task_without_description(client, auth_headers):
    task_data = {
        "title": "Task without description",
        "status": "todo",
        "priority": 5
    }
    response = client.post("/tasks/", json=task_data, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["description"] is None