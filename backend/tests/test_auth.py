"""
Tests for /api/v1/auth/* endpoints.
Covers: register, login, me, plan update, usage.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


class TestRegister:
    def test_register_success(self, client: TestClient):
        resp = client.post("/api/v1/auth/register", json={
            "email": "newuser@test.com",
            "password": "strongpassword",
            "full_name": "New User",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "newuser@test.com"
        assert "id" in data
        assert "hashed_password" not in data  # never leak

    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        resp = client.post("/api/v1/auth/register", json={
            "email": test_user.email,
            "password": "anotherpassword",
        })
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    def test_register_missing_email(self, client: TestClient):
        resp = client.post("/api/v1/auth/register", json={"password": "password"})
        assert resp.status_code == 422  # Pydantic validation


class TestLogin:
    def test_login_success(self, client: TestClient, test_user: User):
        resp = client.post(
            "/api/v1/auth/login",
            data={"username": test_user.email, "password": "testpassword123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient, test_user: User):
        resp = client.post(
            "/api/v1/auth/login",
            data={"username": test_user.email, "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 401

    def test_login_unknown_user(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/login",
            data={"username": "ghost@test.com", "password": "whatever"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 401


class TestMe:
    def test_get_me_authenticated(self, client: TestClient, test_user: User, auth_headers: dict):
        resp = client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == test_user.email

    def test_get_me_unauthenticated(self, client: TestClient):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401


class TestPlanUpdate:
    def test_update_plan_valid(self, client: TestClient, auth_headers: dict):
        resp = client.put("/api/v1/auth/plan", json={"plan": "agency"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["plan"] == "agency"

    def test_update_plan_invalid(self, client: TestClient, auth_headers: dict):
        resp = client.put("/api/v1/auth/plan", json={"plan": "enterprise_ultra"}, headers=auth_headers)
        assert resp.status_code == 400

    def test_update_plan_unauthenticated(self, client: TestClient):
        resp = client.put("/api/v1/auth/plan", json={"plan": "pro"})
        assert resp.status_code == 401


class TestUsage:
    def test_get_usage_authenticated(self, client: TestClient, auth_headers: dict):
        resp = client.get("/api/v1/auth/usage", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "tokens_used" in data
        assert "token_limit" in data
        assert "plan" in data

    def test_get_usage_unauthenticated(self, client: TestClient):
        resp = client.get("/api/v1/auth/usage")
        assert resp.status_code == 401
