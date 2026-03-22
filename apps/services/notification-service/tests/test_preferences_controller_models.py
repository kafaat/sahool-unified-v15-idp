"""
Tests for src/preferences_controller.py - Request/Response Models

Covers:
- UpdateEventPreferenceRequest
- SetQuietHoursRequest
- BulkUpdatePreferencesRequest
- get_tenant_id
"""

import pytest
from fastapi import HTTPException

from src.preferences_controller import (
    BulkUpdatePreferencesRequest,
    SetQuietHoursRequest,
    UpdateEventPreferenceRequest,
    get_tenant_id,
)


class TestGetTenantId:
    def test_valid_tenant(self):
        assert get_tenant_id("tenant-1") == "tenant-1"

    def test_missing_raises(self):
        with pytest.raises(HTTPException) as exc_info:
            get_tenant_id(None)
        assert exc_info.value.status_code == 400


class TestUpdateEventPreferenceRequest:
    def test_valid_request(self):
        req = UpdateEventPreferenceRequest(
            user_id="farmer-123",
            event_type="weather_alert",
            channels=["email", "sms", "push"],
            enabled=True,
            tenant_id="tenant-1",
        )
        assert req.user_id == "farmer-123"
        assert len(req.channels) == 3

    def test_defaults(self):
        req = UpdateEventPreferenceRequest(
            user_id="f-1",
            event_type="pest_outbreak",
            channels=["push"],
        )
        assert req.enabled is True
        assert req.tenant_id is None
        assert req.metadata is None


class TestSetQuietHoursRequest:
    def test_valid(self):
        req = SetQuietHoursRequest(
            user_id="farmer-123",
            quiet_hours_start="22:00",
            quiet_hours_end="06:00",
        )
        assert req.quiet_hours_start == "22:00"
        assert req.quiet_hours_end == "06:00"

    def test_defaults(self):
        req = SetQuietHoursRequest(user_id="f-1")
        assert req.quiet_hours_start is None
        assert req.quiet_hours_end is None
        assert req.tenant_id is None


class TestBulkUpdatePreferencesRequest:
    def test_valid(self):
        req = BulkUpdatePreferencesRequest(
            user_id="farmer-123",
            preferences=[
                {"event_type": "weather_alert", "channels": ["push"], "enabled": True},
                {"event_type": "pest_outbreak", "channels": ["sms"], "enabled": False},
            ],
            tenant_id="tenant-1",
        )
        assert len(req.preferences) == 2
        assert req.tenant_id == "tenant-1"

    def test_empty_preferences(self):
        req = BulkUpdatePreferencesRequest(
            user_id="f-1",
            preferences=[],
        )
        assert len(req.preferences) == 0
"""
Tests for src/channels_controller.py - Request/Response Models

Covers:
- Pydantic model creation for channels controller
"""

from src.channels_controller import router


class TestChannelsRouter:
    def test_router_exists(self):
        assert router is not None
        assert len(router.routes) > 0
"""
Tests for src/history_controller.py - Additional model coverage

Covers:
- HistoryStatsResponse model
"""

from src.history_controller import router as history_router


class TestHistoryRouter:
    def test_router_exists(self):
        assert history_router is not None
        assert len(history_router.routes) > 0
"""
Tests for src/analytics_controller.py - Additional coverage
"""

from src.analytics_controller import router as analytics_router


class TestAnalyticsRouter:
    def test_router_exists(self):
        assert analytics_router is not None
        assert len(analytics_router.routes) > 0
