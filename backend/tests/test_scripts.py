"""
Tests for /api/v1/scripts/* endpoints.
Mocks the ScriptGenerator so no LLM calls are made.
Covers: generate, list, get, delete, plan-limit enforcement.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.script import Script


MOCK_TITLES = [{"title": "How to Grow on YouTube in 2024", "ctr_prediction": 8.5}]
MOCK_HOOK = "Most creators never reach 1000 subscribers because they make this one mistake..."
MOCK_SCRIPT = {"full_script": "## Intro\n\nHey everyone...", "estimated_duration": "10 minutes"}


def _seed_scripts(db: Session, user: User, count: int):
    for i in range(count):
        s = Script(
            user_id=user.id,
            topic=f"Test topic {i}",
            generation_status="done",
        )
        db.add(s)
    db.commit()


class TestGenerateScript:
    @patch("app.routers.scripts.ScriptGenerator.generate_titles", return_value=MOCK_TITLES)
    @patch("app.routers.scripts.ScriptGenerator.generate_hook", return_value=MOCK_HOOK)
    @patch("app.routers.scripts.ScriptGenerator.generate_full_script", return_value=MOCK_SCRIPT)
    def test_generate_success(self, mock_fs, mock_hook, mock_titles, client, auth_headers):
        resp = client.post(
            "/api/v1/scripts/generate",
            json={"topic": "How to grow on YouTube", "target_duration_minutes": 10},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["topic"] == "How to grow on YouTube"
        assert data["generation_status"] == "done"

    def test_generate_unauthenticated(self, client: TestClient):
        resp = client.post(
            "/api/v1/scripts/generate",
            json={"topic": "Something"},
        )
        assert resp.status_code == 401

    def test_generate_free_plan_limit_enforced(
        self, client: TestClient, free_auth_headers: dict,
        free_user: User, db: Session
    ):
        """Free plan: 3 scripts/month. 4th should be blocked."""
        _seed_scripts(db, free_user, 3)
        resp = client.post(
            "/api/v1/scripts/generate",
            json={"topic": "The 4th script"},
            headers=free_auth_headers,
        )
        assert resp.status_code == 403
        detail = resp.json()["detail"]
        # detail may be dict (new format) or string (old format)
        if isinstance(detail, dict):
            assert detail["code"] == "PLAN_LIMIT_EXCEEDED"
        else:
            assert "limit" in detail.lower()


class TestListScripts:
    def test_list_empty(self, client: TestClient, auth_headers: dict):
        resp = client.get("/api/v1/scripts/", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_only_own_scripts(
        self, client: TestClient, auth_headers: dict,
        test_user: User, free_user: User, db: Session
    ):
        _seed_scripts(db, test_user, 2)
        _seed_scripts(db, free_user, 3)  # should not be visible
        resp = client.get("/api/v1/scripts/", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestGetScript:
    def test_get_own_script(
        self, client: TestClient, auth_headers: dict,
        test_user: User, db: Session
    ):
        _seed_scripts(db, test_user, 1)
        script_id = db.query(Script).filter(Script.user_id == test_user.id).first().id
        resp = client.get(f"/api/v1/scripts/{script_id}", headers=auth_headers)
        assert resp.status_code == 200

    def test_get_other_users_script_is_404(
        self, client: TestClient, auth_headers: dict,
        free_user: User, db: Session
    ):
        _seed_scripts(db, free_user, 1)
        script_id = db.query(Script).filter(Script.user_id == free_user.id).first().id
        resp = client.get(f"/api/v1/scripts/{script_id}", headers=auth_headers)
        assert resp.status_code == 404


class TestDeleteScript:
    def test_delete_own_script(
        self, client: TestClient, auth_headers: dict,
        test_user: User, db: Session
    ):
        _seed_scripts(db, test_user, 1)
        script_id = db.query(Script).filter(Script.user_id == test_user.id).first().id
        resp = client.delete(f"/api/v1/scripts/{script_id}", headers=auth_headers)
        assert resp.status_code == 204

    def test_delete_other_users_script_is_404(
        self, client: TestClient, auth_headers: dict,
        free_user: User, db: Session
    ):
        _seed_scripts(db, free_user, 1)
        script_id = db.query(Script).filter(Script.user_id == free_user.id).first().id
        resp = client.delete(f"/api/v1/scripts/{script_id}", headers=auth_headers)
        assert resp.status_code == 404
