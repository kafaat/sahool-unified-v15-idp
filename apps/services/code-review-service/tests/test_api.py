"""
Test Code Review Service API endpoints
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_ollama():
    """Mock Ollama API responses"""
    with (
        patch("src.main.CodeReviewService.check_ollama_health") as mock_health,
        patch("src.main.CodeReviewService.review_code") as mock_review,
    ):

        # Mock health check
        async def health_check():
            return True

        mock_health.return_value = AsyncMock(return_value=True)()

        # Mock code review
        async def review_code(code, language=None, filename=None):
            return {
                "summary": "Test review completed successfully",
                "critical_issues": [],
                "suggestions": ["Consider adding comments"],
                "security_concerns": [],
                "score": 85,
            }

        mock_review.return_value = AsyncMock(
            return_value={
                "summary": "Test review completed successfully",
                "critical_issues": [],
                "suggestions": ["Consider adding comments"],
                "security_concerns": [],
                "score": 85,
            }
        )()

        yield mock_health, mock_review


@pytest.fixture
def client():
    """Create test client"""
    # Import after mocking
    from src.main import app

    return TestClient(app)


def test_health_endpoint(mock_ollama, client):
    """Test health check endpoint"""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "code-review-service"
    assert "status" in data
    assert "ollama_connected" in data
    assert "version" in data


def test_review_code_endpoint(mock_ollama, client):
    """Test code review endpoint"""
    response = client.post(
        "/review",
        json={
            "code": "def hello():\n    print('world')",
            "language": "python",
            "filename": "test.py",
        },
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


def test_review_code_without_language(mock_ollama, client):
    """Test code review without specifying language"""
    response = client.post("/review", json={"code": "console.log('hello');"})

    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "score" in data


def test_review_code_with_all_fields(mock_ollama, client):
    """Test code review with all optional fields"""
    response = client.post(
        "/review",
        json={
            "code": "function test() { return 42; }",
            "language": "javascript",
            "filename": "test.js",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["score"] >= 0
    assert data["score"] <= 100


def test_review_file_not_found(mock_ollama, client):
    """Test file review with non-existent file"""
    response = client.post("/review/file", json={"file_path": "nonexistent/file.py"})

    # The file won't exist, so this should return 404
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
