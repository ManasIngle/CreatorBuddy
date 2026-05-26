"""
Tests for /api/v1/channels/* endpoints.
Mocks YouTube API calls so no real credentials are needed.
Covers: connect, list, get, re-analyze, plan limit enforcement.
"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.channel import Channel


MOCK_YT_DATA = {
    "youtube_channel_id": "UC_test_channel_001",
    "title": "Test Channel",
    "description": "A test channel",
    "thumbnail_url": "https://example.com/thumb.jpg",
    "subscriber_count": 10000,
    "video_count": 50,
    "view_count": 500000,
    "country": "US",
    "uploads_playlist_id": "UU_test_channel_001",
}


def _make_channel(db: Session, user: User, yt_id: str = "UC_existing_001") -> Channel:
    ch = Channel(
        user_id=user.id,
        youtube_channel_id=yt_id,
        title="Existing Channel",
        subscriber_count=5000,
        video_count=20,
        analysis_status="done",
    )
    db.add(ch)
    db.commit()
    db.refresh(ch)
    return ch


class TestConnectChannel:
    @patch(
        "app.routers.channels.fetch_channel_details_cached",
        new_callable=AsyncMock,
        return_value=MOCK_YT_DATA,
    )
    def test_connect_success(self, mock_yt, client: TestClient, auth_headers: dict):
        with patch("app.routers.channels.run_full_channel_analysis"):
            resp = client.post(
                "/api/v1/channels/connect",
                json={"youtube_channel_id": "UC_test_channel_001"},
                headers=auth_headers,
            )
        assert resp.status_code == 201
        data = resp.json()
        assert data["youtube_channel_id"] == "UC_test_channel_001"
        assert data["title"] == "Test Channel"

    @patch(
        "app.routers.channels.fetch_channel_details_cached",
        new_callable=AsyncMock,
        return_value=MOCK_YT_DATA,
    )
    def test_connect_duplicate(
        self, mock_yt, client: TestClient, auth_headers: dict,
        test_user: User, db: Session
    ):
        _make_channel(db, test_user, "UC_test_channel_001")
        resp = client.post(
            "/api/v1/channels/connect",
            json={"youtube_channel_id": "UC_test_channel_001"},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "already connected" in resp.json()["detail"].lower()

    def test_connect_unauthenticated(self, client: TestClient):
        resp = client.post(
            "/api/v1/channels/connect",
            json={"youtube_channel_id": "UCsome_channel"},
        )
        assert resp.status_code == 401


class TestPlanLimitChannels:
    @patch(
        "app.routers.channels.fetch_channel_details_cached",
        new_callable=AsyncMock,
        return_value={**MOCK_YT_DATA, "youtube_channel_id": "UC_second_001"},
    )
    def test_free_plan_channel_limit(
        self, mock_yt, client: TestClient, free_auth_headers: dict,
        free_user: User, db: Session
    ):
        """Free plan allows 1 channel — second connect should be blocked."""
        _make_channel(db, free_user, "UC_already_connected")
        resp = client.post(
            "/api/v1/channels/connect",
            json={"youtube_channel_id": "UC_second_001"},
            headers=free_auth_headers,
        )
        assert resp.status_code == 403
        assert "limit" in resp.json()["detail"].lower()


class TestListChannels:
    def test_list_empty(self, client: TestClient, auth_headers: dict):
        resp = client.get("/api/v1/channels/", headers=auth_headers)
        assert resp.status_code == 200

    def test_list_with_channels(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        _make_channel(db, test_user, "UC_list_001")
        resp = client.get("/api/v1/channels/", headers=auth_headers)
        assert resp.status_code == 200

    def test_list_unauthenticated(self, client: TestClient):
        resp = client.get("/api/v1/channels/")
        assert resp.status_code == 401


class TestGetChannel:
    def test_get_own_channel(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        ch = _make_channel(db, test_user)
        resp = client.get(f"/api/v1/channels/{ch.id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == str(ch.id)

    def test_get_other_users_channel_is_404(
        self, client: TestClient, auth_headers: dict,
        free_user: User, db: Session
    ):
        """Should return 404 not 403 — never confirm existence for other users."""
        other_channel = _make_channel(db, free_user, "UC_other_user_ch")
        resp = client.get(f"/api/v1/channels/{other_channel.id}", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_nonexistent_channel(self, client: TestClient, auth_headers: dict):
        resp = client.get(
            "/api/v1/channels/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert resp.status_code == 404
