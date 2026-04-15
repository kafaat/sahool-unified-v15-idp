"""
Tests for src/channels_controller.py - Request Models

Covers:
- AddChannelRequest
- VerifyChannelRequest
- UpdateChannelStatusRequest
- get_tenant_id
"""

import pytest
from fastapi import HTTPException

try:
    from src.channels_controller import (
        AddChannelRequest,
        UpdateChannelStatusRequest,
        VerifyChannelRequest,
        get_tenant_id,
    )
except BaseException as e:
    if isinstance(e, (KeyboardInterrupt, SystemExit, GeneratorExit)):
        raise
    pytest.skip("notification-service dependencies not available", allow_module_level=True)


class TestGetTenantId:
    def test_valid(self):
        assert get_tenant_id("t-1") == "t-1"

    def test_none_raises(self):
        with pytest.raises(HTTPException) as exc_info:
            get_tenant_id(None)
        assert exc_info.value.status_code == 400


class TestAddChannelRequest:
    def test_valid(self):
        req = AddChannelRequest(
            user_id="farmer-123",
            channel_type="email",
            address="farmer@example.com",
            tenant_id="t-1",
            metadata={"device": "web"},
        )
        assert req.user_id == "farmer-123"
        assert req.channel_type == "email"

    def test_defaults(self):
        req = AddChannelRequest(
            user_id="f-1",
            channel_type="push",
            address="fcm-token",
        )
        assert req.tenant_id is None
        assert req.metadata is None


class TestVerifyChannelRequest:
    def test_valid(self):
        req = VerifyChannelRequest(
            channel_id="550e8400-e29b-41d4-a716-446655440000",
            verification_code="123456",
            user_id="farmer-123",
        )
        assert req.verification_code == "123456"


class TestUpdateChannelStatusRequest:
    def test_enable(self):
        req = UpdateChannelStatusRequest(
            channel_id="550e8400-e29b-41d4-a716-446655440000",
            user_id="farmer-123",
            enabled=True,
        )
        assert req.enabled is True

    def test_disable(self):
        req = UpdateChannelStatusRequest(
            channel_id="550e8400-e29b-41d4-a716-446655440000",
            user_id="farmer-123",
            enabled=False,
        )
        assert req.enabled is False
