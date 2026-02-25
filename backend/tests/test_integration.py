"""Integration tests — /ai/suggest with deterministic stub."""
import pytest
from tests.conftest import auth_headers


class TestAISuggestIntegration:
    """
    These tests hit /ai/suggest end-to-end (through the full FastAPI stack)
    using the deterministic stub (USE_AI_STUB=true set in conftest.py).
    No real OpenAI calls are made, ensuring tests are fast and repeatable in CI.
    """

    def test_suggest_description_stub(self, client, user_token):
        """
        Integration: /ai/suggest?mode=description returns a stub description
        containing the submitted title.
        """
        headers = auth_headers(user_token)
        resp = client.post(
            "/ai/suggest?mode=description&title=Implement+search+feature",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["source"] in ("stub", "stub-fallback")
        assert "description" in data
        assert len(data["description"]) > 10  # non-empty description
        assert data["title"] == "Implement search feature"

    def test_suggest_daily_plan_stub(self, client, user_token):
        """
        Integration: /ai/suggest?mode=daily_plan returns a stub plan
        with the expected structure.
        """
        headers = auth_headers(user_token)

        # First create a task so the user has something to plan around
        client.post(
            "/tasks/",
            json={"title": "Morning standup prep", "total_minutes": 15},
            headers=headers,
        )

        resp = client.post("/ai/suggest?mode=daily_plan", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["source"] in ("stub", "stub-fallback")
        assert "plan" in data
        assert isinstance(data["plan"], list)
        assert len(data["plan"]) > 0
        # Each plan item must have time and activity
        for item in data["plan"]:
            assert "time" in item
            assert "activity" in item

    def test_suggest_description_missing_title(self, client, user_token):
        """mode=description without title returns 400."""
        headers = auth_headers(user_token)
        resp = client.post("/ai/suggest?mode=description", headers=headers)
        assert resp.status_code == 400

    def test_suggest_unauthenticated(self, client):
        """Unauthenticated request to /ai/suggest returns 401."""
        resp = client.post("/ai/suggest?mode=description&title=Test")
        assert resp.status_code == 401
