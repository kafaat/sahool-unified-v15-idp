"""
WeChat Service Test Fixtures
============================
Shared fixtures for testing WeChat service endpoints.

Author: SAHOOL Platform Team
"""

import os
import sys

# Add service root to path for src imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import sys
from datetime import datetime
from typing import Generator
from unittest.mock import MagicMock

import pytest

# Ensure test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["DATABASE_URL"] = ""
os.environ["NATS_URL"] = ""
os.environ["REDIS_URL"] = ""
os.environ["WECHAT_APP_ID"] = ""
os.environ["WECHAT_APP_SECRET"] = ""


# ===============================================================================
# Mock User Class
# ===============================================================================


class MockUser:
    """Mock User model for authentication."""

    def __init__(self, tenant_id: str = "test-tenant"):
        self.id = "test-user-id"
        self.email = "test@example.com"
        self.tenant_id = tenant_id
        self.roles = ["user"]
        self.permissions = []
        self.is_active = True
        self.is_verified = True
        self.farm_ids = []

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def has_any_role(self, *roles: str) -> bool:
        return any(role in self.roles for role in roles)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def has_farm_access(self, farm_id: str) -> bool:
        return farm_id in self.farm_ids


# ===============================================================================
# Mock Auth Module
# ===============================================================================


def mock_get_current_user():
    """Dependency override for get_current_user."""
    return MockUser(tenant_id="test-tenant")


mock_auth_deps = MagicMock()
mock_auth_deps.get_current_user = mock_get_current_user

mock_auth_models = MagicMock()
mock_auth_models.User = MockUser

# Patch before importing main
sys.modules["shared.auth.dependencies"] = mock_auth_deps
sys.modules["shared.auth.models"] = mock_auth_models


# ===============================================================================
# Test Fixtures
# ===============================================================================


@pytest.fixture(scope="session")
def mock_user():
    """Create a mock user for testing."""
    return MockUser(tenant_id="test-tenant")


@pytest.fixture
def sample_fetch_request():
    """Sample message fetch request data."""
    return {
        "chat_id": "chat_001",
        "tenant_id": "test-tenant",
        "limit": 50,
        "before_timestamp": None,
        "after_timestamp": None,
        "message_types": None,
    }


@pytest.fixture
def sample_send_request():
    """Sample message send request data."""
    return {
        "chat_id": "chat_001",
        "tenant_id": "test-tenant",
        "message_type": "text",
        "content": "Hello, how is the crop doing?",
        "media_url": None,
        "reply_to_id": None,
        "metadata": None,
    }


@pytest.fixture
def sample_contact_request():
    """Sample contact add request data."""
    return {
        "wechat_id": "farmer_wechat_001",
        "tenant_id": "test-tenant",
        "contact_type": "friend",
        "greeting_message": "Hello! I would like to connect.",
        "greeting_message_ar": "مرحبا! أود التواصل.",
        "notes": "Wheat farmer from Riyadh",
        "tags": ["farmer", "wheat"],
    }


@pytest.fixture
def sample_moment_request():
    """Sample moment publish request data."""
    return {
        "tenant_id": "test-tenant",
        "content": "Great harvest this season!",
        "content_ar": "حصاد رائع هذا الموسم!",
        "media_urls": ["https://example.com/image1.jpg"],
        "location": "Riyadh Farm",
        "location_ar": "مزرعة الرياض",
        "visibility": "friends",
        "visible_to": None,
        "link_url": None,
        "link_title": None,
    }


@pytest.fixture
def sample_summarize_request():
    """Sample chat summarize request data."""
    return {
        "chat_id": "chat_001",
        "tenant_id": "test-tenant",
        "time_range_hours": 24,
        "max_messages": 500,
        "language": "en",
        "include_participants": True,
        "include_timeline": False,
    }


@pytest.fixture
def sample_insights_request():
    """Sample chat insights request data."""
    return {
        "chat_id": "chat_001",
        "tenant_id": "test-tenant",
        "insight_types": ["sentiment", "topic", "action_items"],
        "time_range_hours": 24,
        "language": "en",
    }
