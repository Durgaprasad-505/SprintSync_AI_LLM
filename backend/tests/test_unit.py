"""Unit tests — happy paths for auth and task CRUD."""
import pytest
from tests.conftest import auth_headers


class TestAuth:
    def test_register_and_login(self, client):
        """Happy path: register a user, then login to get a JWT."""
        # Register
        resp = client.post(
            "/auth/register",
            json={"email": "new@test.com", "username": "newuser", "password": "pass123"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["is_admin"] is False

        # Login
        resp = client.post("/auth/token", data={"username": "newuser", "password": "pass123"})
        assert resp.status_code == 200
        token_data = resp.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, regular_user):
        """Wrong password returns 401."""
        resp = client.post("/auth/token", data={"username": "testuser", "password": "wrong"})
        assert resp.status_code == 401

    def test_get_me(self, client, user_token):
        """Authenticated user can fetch their own profile."""
        resp = client.get("/users/me", headers=auth_headers(user_token))
        assert resp.status_code == 200
        assert resp.json()["username"] == "testuser"


class TestTasks:
    def test_create_and_list_tasks(self, client, user_token):
        """Happy path: create a task and list it back."""
        headers = auth_headers(user_token)

        # Create
        resp = client.post(
            "/tasks/",
            json={"title": "Write docs", "description": "Document the API endpoints.", "total_minutes": 30},
            headers=headers,
        )
        assert resp.status_code == 201
        task = resp.json()
        assert task["title"] == "Write docs"
        assert task["status"] == "backlog"
        assert task["total_minutes"] == 30

        # List
        resp = client.get("/tasks/", headers=headers)
        assert resp.status_code == 200
        tasks = resp.json()
        assert len(tasks) == 1
        assert tasks[0]["id"] == task["id"]

    def test_status_transition_happy_path(self, client, user_token):
        """backlog → in_progress transition succeeds."""
        headers = auth_headers(user_token)

        resp = client.post("/tasks/", json={"title": "Feature X"}, headers=headers)
        task_id = resp.json()["id"]

        resp = client.post(
            f"/tasks/{task_id}/transition",
            json={"new_status": "in_progress"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "in_progress"

    def test_invalid_status_transition(self, client, user_token):
        """backlog → done (invalid) returns 400."""
        headers = auth_headers(user_token)

        resp = client.post("/tasks/", json={"title": "Feature Y"}, headers=headers)
        task_id = resp.json()["id"]

        resp = client.post(
            f"/tasks/{task_id}/transition",
            json={"new_status": "done"},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_update_task(self, client, user_token):
        """PATCH task updates fields correctly."""
        headers = auth_headers(user_token)
        resp = client.post("/tasks/", json={"title": "Old title"}, headers=headers)
        task_id = resp.json()["id"]

        resp = client.patch(
            f"/tasks/{task_id}",
            json={"title": "New title", "total_minutes": 90},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "New title"
        assert data["total_minutes"] == 90

    def test_delete_task(self, client, user_token):
        """DELETE removes task, subsequent GET returns 404."""
        headers = auth_headers(user_token)
        resp = client.post("/tasks/", json={"title": "Temp task"}, headers=headers)
        task_id = resp.json()["id"]

        resp = client.delete(f"/tasks/{task_id}", headers=headers)
        assert resp.status_code == 204

        resp = client.get(f"/tasks/{task_id}", headers=headers)
        assert resp.status_code == 404
