"""
Test Code Review Service API endpoints

Mocks:
- CodeReviewService (Ollama health, review_code, available models)
- get_current_user (auth bypass)
- TenantContextMiddleware (X-Tenant-ID header required)
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)
from src.main import ModelInfo, app

from shared.auth.dependencies import get_current_user

# Valid UUID for TenantContextMiddleware
TEST_TENANT_ID = "00000000-0000-0000-0000-000000000001"
HEADERS = {"X-Tenant-ID": TEST_TENANT_ID}


# Fake user for auth bypass
class FakeUser:
    id = "test-user"
    tenant_id = TEST_TENANT_ID
    email = "test@example.com"
    roles = ["admin"]


async def _fake_current_user():
    return FakeUser()


def _make_mock_service():
    """Build a mock CodeReviewService with correct async methods."""
    svc = MagicMock()
    svc.check_ollama_health = AsyncMock(return_value=True)
    svc.get_available_models.return_value = [
        ModelInfo(name="codellama:7b", url="http://localhost:11434", available=True, priority=0),
    ]
    svc.settings.enable_cache = False
    svc.github = None
    svc.review_code = AsyncMock(
        return_value={
            "summary": "Test review completed successfully",
            "critical_issues": [],
            "suggestions": ["Consider adding comments"],
            "security_concerns": [],
            "score": 85,
            "model_used": "codellama:7b",
            "cached": False,
        }
    )
    return svc


@pytest.fixture
def client():
    """Create test client with mocked service."""
    mock_svc = _make_mock_service()
    app.dependency_overrides[get_current_user] = _fake_current_user
    with patch("src.main.get_service", return_value=mock_svc):
        yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "code-review-service"
    assert "status" in data
    assert "ollama_connected" in data
    assert "version" in data


def test_review_code_endpoint(client):
    """Test code review endpoint"""
    response = client.post(
        "/review",
        json={
            "code": "def hello():\n    print('world')",
            "language": "python",
            "filename": "test.py",
        },
        headers=HEADERS,
    )

    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "critical_issues" in data
    assert "suggestions" in data
    assert "security_concerns" in data
    assert "score" in data
    assert isinstance(data["score"], int)
    assert 0 <= data["score"] <= 100


def test_review_code_without_language(client):
    """Test code review without specifying language"""
    response = client.post(
        "/review",
        json={"code": "console.log('hello');"},
        headers=HEADERS,
    )

    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "score" in data


def test_review_code_with_all_fields(client):
    """Test code review with all optional fields"""
    response = client.post(
        "/review",
        json={
            "code": "function test() { return 42; }",
            "language": "javascript",
            "filename": "test.js",
        },
        headers=HEADERS,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["score"] >= 0
    assert data["score"] <= 100


def test_review_file_not_found(client):
    """Test file review with non-existent file"""
    response = client.post(
        "/review/file",
        json={"file_path": "nonexistent/file.py"},
        headers=HEADERS,
    )

    # The file won't exist, so this should return 404
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
