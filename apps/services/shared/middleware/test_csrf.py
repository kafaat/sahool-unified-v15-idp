"""
CSRF Protection Middleware Tests
اختبارات ميدلوير حماية CSRF

Comprehensive tests for the CSRF protection middleware.
"""

import time
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from .csrf import CSRFConfig, CSRFProtection, get_csrf_token


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def basic_app():
    """Create a basic FastAPI app with CSRF protection"""
    app = FastAPI()
    app.add_middleware(CSRFProtection)

    @app.get("/form")
    async def get_form(request: Request):
        return {"csrf_token": get_csrf_token(request)}

    @app.post("/submit")
    async def submit_form(data: dict):
        return {"status": "success", "data": data}

    @app.put("/update")
    async def update_data(data: dict):
        return {"status": "updated", "data": data}

    @app.delete("/delete")
    async def delete_data():
        return {"status": "deleted"}

    return app


@pytest.fixture
def custom_app():
    """Create app with custom CSRF configuration"""
    app = FastAPI()

    config = CSRFConfig(
        secret_key="test-secret-key-12345",
        cookie_name="custom_csrf",
        header_name="X-Custom-CSRF",
        cookie_secure=False,  # For testing
        exclude_paths=["/health", "/webhook"],
        trusted_origins=["https://trusted.example.com"],
    )

    app.add_middleware(CSRFProtection, config=config)

    @app.get("/form")
    async def get_form(request: Request):
        return {"status": "ok"}

    @app.post("/submit")
    async def submit_form(data: dict):
        return {"status": "success"}

    @app.post("/webhook")
    async def webhook(data: dict):
        return {"status": "webhook_received"}

    return app


# ============================================================================
# Token Generation Tests
# ============================================================================

def test_csrf_cookie_set_on_get_request(basic_app):
    """Test that CSRF cookie is set on GET requests"""
    client = TestClient(basic_app)
    response = client.get("/form")

    assert response.status_code == 200
    assert "csrf_token" in response.cookies
    assert len(response.cookies["csrf_token"]) > 0


def test_csrf_token_format(basic_app):
    """Test that CSRF token has correct format (random.timestamp.signature)"""
    client = TestClient(basic_app)
    response = client.get("/form")

    token = response.cookies.get("csrf_token")
    assert token is not None

    parts = token.split(".")
    assert len(parts) == 3  # random_value, timestamp, signature
    assert len(parts[0]) > 0  # random value
    assert parts[1].isdigit()  # timestamp
    assert len(parts[2]) == 64  # SHA256 hex digest


def test_csrf_cookie_attributes(basic_app):
    """Test that CSRF cookie has correct security attributes"""
    client = TestClient(basic_app)
    response = client.get("/form")

    # Note: TestClient doesn't expose all cookie attributes
    # This would be better tested with actual HTTP client
    assert "csrf_token" in response.cookies


# ============================================================================
# Token Validation Tests
# ============================================================================

def test_post_without_csrf_token_fails(basic_app):
    """Test that POST request without CSRF token is rejected"""
    client = TestClient(basic_app)

    response = client.post("/submit", json={"data": "test"})

    assert response.status_code == 403
    assert "CSRF_VALIDATION_FAILED" in response.json()["error"]["code"]


def test_post_with_missing_cookie_fails(basic_app):
    """Test that POST request with header but no cookie fails"""
    client = TestClient(basic_app)

    response = client.post(
        "/submit",
        json={"data": "test"},
        headers={"X-CSRF-Token": "fake-token"}
    )

    assert response.status_code == 403
    assert "cookie not found" in response.json()["error"]["details"]["reason"].lower()


def test_post_with_mismatched_tokens_fails(basic_app):
    """Test that POST request with mismatched tokens fails"""
    client = TestClient(basic_app)

    # Get valid token
    get_response = client.get("/form")
    valid_token = get_response.cookies.get("csrf_token")

    # Use different token in header
    response = client.post(
        "/submit",
        json={"data": "test"},
        headers={"X-CSRF-Token": "different-token"},
        cookies={"csrf_token": valid_token}
    )

    assert response.status_code == 403
    assert "mismatch" in response.json()["error"]["details"]["reason"].lower()


def test_post_with_valid_csrf_token_succeeds(basic_app):
    """Test that POST request with valid CSRF token succeeds"""
    client = TestClient(basic_app)

    # Get CSRF token
    get_response = client.get("/form")
    csrf_token = get_response.cookies.get("csrf_token")

    # Use token in POST request
    response = client.post(
        "/submit",
        json={"data": "test"},
        headers={"X-CSRF-Token": csrf_token},
        cookies={"csrf_token": csrf_token}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_put_request_requires_csrf_token(basic_app):
    """Test that PUT requests also require CSRF token"""
    client = TestClient(basic_app)

    # Without token - should fail
    response = client.put("/update", json={"data": "test"})
    assert response.status_code == 403

    # With token - should succeed
    get_response = client.get("/form")
    csrf_token = get_response.cookies.get("csrf_token")

    response = client.put(
        "/update",
        json={"data": "test"},
        headers={"X-CSRF-Token": csrf_token},
        cookies={"csrf_token": csrf_token}
    )
    assert response.status_code == 200


def test_delete_request_requires_csrf_token(basic_app):
    """Test that DELETE requests require CSRF token"""
    client = TestClient(basic_app)

    # Without token - should fail
    response = client.delete("/delete")
    assert response.status_code == 403

    # With token - should succeed
    get_response = client.get("/form")
    csrf_token = get_response.cookies.get("csrf_token")

    response = client.delete(
        "/delete",
        headers={"X-CSRF-Token": csrf_token},
        cookies={"csrf_token": csrf_token}
    )
    assert response.status_code == 200


# ============================================================================
# Bearer Token Bypass Tests
# ============================================================================

def test_bearer_token_bypasses_csrf(basic_app):
    """Test that requests with Bearer token bypass CSRF validation"""
    client = TestClient(basic_app)

    # POST with Bearer token, no CSRF token
    response = client.post(
        "/submit",
        json={"data": "test"},
        headers={"Authorization": "Bearer fake-jwt-token"}
    )

    # Should not fail with CSRF error
    # (May fail with auth error, but that's different)
    # Since our test app doesn't validate Bearer tokens, it should succeed
    assert response.status_code == 200


def test_bearer_token_case_insensitive(basic_app):
    """Test that Bearer token check is case insensitive"""
    client = TestClient(basic_app)

    # Try different cases
    for auth_header in ["Bearer token", "bearer token", "BEARER token"]:
        response = client.post(
            "/submit",
            json={"data": "test"},
            headers={"Authorization": auth_header}
        )
        assert response.status_code == 200


# ============================================================================
# Path Exclusion Tests
# ============================================================================

def test_excluded_paths_skip_csrf(custom_app):
    """Test that excluded paths don't require CSRF token"""
    client = TestClient(custom_app)

    # Webhook endpoint is excluded
    response = client.post("/webhook", json={"data": "test"})
    assert response.status_code == 200


def test_custom_cookie_and_header_names(custom_app):
    """Test custom cookie and header names"""
    client = TestClient(custom_app)

    # Get token (should be in custom cookie)
    get_response = client.get("/form")
    csrf_token = get_response.cookies.get("custom_csrf")
    assert csrf_token is not None

    # Use custom header name
    response = client.post(
        "/submit",
        json={"data": "test"},
        headers={"X-Custom-CSRF": csrf_token},
        cookies={"custom_csrf": csrf_token}
    )
    assert response.status_code == 200


# ============================================================================
# Token Expiration Tests
# ============================================================================

def test_expired_token_rejected():
    """Test that expired CSRF tokens are rejected"""
    app = FastAPI()

    # Configure with very short expiration
    config = CSRFConfig(
        secret_key="test-key",
        cookie_max_age=1,  # 1 second
        cookie_secure=False,
    )

    app.add_middleware(CSRFProtection, config=config)

    @app.get("/form")
    async def get_form():
        return {"status": "ok"}

    @app.post("/submit")
    async def submit_form(data: dict):
        return {"status": "success"}

    client = TestClient(app)

    # Get token
    get_response = client.get("/form")
    csrf_token = get_response.cookies.get("csrf_token")

    # Wait for token to expire
    time.sleep(2)

    # Try to use expired token
    response = client.post(
        "/submit",
        json={"data": "test"},
        headers={"X-CSRF-Token": csrf_token},
        cookies={"csrf_token": csrf_token}
    )

    assert response.status_code == 403
    assert "expired" in response.json()["error"]["details"]["reason"].lower()


# ============================================================================
# Safe Methods Tests
# ============================================================================

def test_safe_methods_dont_require_csrf(basic_app):
    """Test that safe methods (GET, HEAD, OPTIONS) don't require CSRF"""
    client = TestClient(basic_app)

    # GET should work without CSRF token
    response = client.get("/form")
    assert response.status_code == 200

    # HEAD should work
    response = client.head("/form")
    assert response.status_code == 200

    # OPTIONS should work
    response = client.options("/form")
    assert response.status_code == 200


# ============================================================================
# Helper Function Tests
# ============================================================================

def test_get_csrf_token_helper(basic_app):
    """Test the get_csrf_token helper function"""
    client = TestClient(basic_app)

    # Make request to set cookie
    response = client.get("/form")

    # Token should be in response
    assert response.json()["csrf_token"] is not None


# ============================================================================
# Security Tests
# ============================================================================

def test_invalid_token_signature_rejected():
    """Test that tokens with invalid signatures are rejected"""
    app = FastAPI()

    config = CSRFConfig(
        secret_key="test-key-12345",
        cookie_secure=False,
    )

    app.add_middleware(CSRFProtection, config=config)

    @app.get("/form")
    async def get_form():
        return {"status": "ok"}

    @app.post("/submit")
    async def submit_form(data: dict):
        return {"status": "success"}

    client = TestClient(app)

    # Create a fake token with wrong signature
    fake_token = "randomvalue.1234567890.fakesignature1234567890abcdef1234567890abcdef1234567890abcdef"

    response = client.post(
        "/submit",
        json={"data": "test"},
        headers={"X-CSRF-Token": fake_token},
        cookies={"csrf_token": fake_token}
    )

    assert response.status_code == 403
    assert "signature" in response.json()["error"]["details"]["reason"].lower()


def test_malformed_token_rejected(basic_app):
    """Test that malformed tokens are rejected"""
    client = TestClient(basic_app)

    malformed_tokens = [
        "invalid",
        "only.two.parts",
        "too.many.parts.here.invalid",
        "",
        ".",
        "..",
    ]

    for token in malformed_tokens:
        response = client.post(
            "/submit",
            json={"data": "test"},
            headers={"X-CSRF-Token": token},
            cookies={"csrf_token": token}
        )
        assert response.status_code == 403


# ============================================================================
# Integration Tests
# ============================================================================

def test_multiple_requests_with_same_token(basic_app):
    """Test that the same token can be used for multiple requests"""
    client = TestClient(basic_app)

    # Get token
    get_response = client.get("/form")
    csrf_token = get_response.cookies.get("csrf_token")

    # Use token for multiple requests
    for _ in range(3):
        response = client.post(
            "/submit",
            json={"data": "test"},
            headers={"X-CSRF-Token": csrf_token},
            cookies={"csrf_token": csrf_token}
        )
        assert response.status_code == 200


def test_token_refresh_on_successful_request(basic_app):
    """Test that token can be refreshed"""
    client = TestClient(basic_app)

    # Get initial token
    get_response = client.get("/form")
    first_token = get_response.cookies.get("csrf_token")

    # Make successful POST
    post_response = client.post(
        "/submit",
        json={"data": "test"},
        headers={"X-CSRF-Token": first_token},
        cookies={"csrf_token": first_token}
    )

    assert post_response.status_code == 200

    # New token may be set in response
    # (implementation may refresh or keep same token)


# ============================================================================
# Error Response Tests
# ============================================================================

def test_csrf_error_response_format(basic_app):
    """Test that CSRF errors return correct response format"""
    client = TestClient(basic_app)

    response = client.post("/submit", json={"data": "test"})

    assert response.status_code == 403
    json_data = response.json()

    # Check response structure
    assert "success" in json_data
    assert json_data["success"] is False
    assert "error" in json_data
    assert "code" in json_data["error"]
    assert "message" in json_data["error"]
    assert "message_ar" in json_data["error"]
    assert "details" in json_data["error"]


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
