"""
CSRF Protection Usage Examples
أمثلة استخدام حماية CSRF

This file demonstrates how to use the CSRF protection middleware in FastAPI services.
"""

import os
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse

from .csrf import CSRFConfig, CSRFProtection, get_csrf_token


# ============================================================================
# Example 1: Basic CSRF Protection Setup
# ============================================================================

def example_basic_setup():
    """
    Basic CSRF protection setup with default configuration.
    إعداد أساسي لحماية CSRF مع الإعدادات الافتراضية.
    """
    app = FastAPI(title="CSRF Protected Service")

    # Add CSRF protection middleware with defaults
    app.add_middleware(CSRFProtection)

    @app.get("/form")
    async def get_form(request: Request):
        """
        Render a form with CSRF token.
        CSRF token is automatically set in cookie by middleware.
        """
        csrf_token = get_csrf_token(request)
        return HTMLResponse(f"""
            <html>
                <body>
                    <h1>Submit Form</h1>
                    <form method="POST" action="/submit">
                        <input type="hidden" name="csrf_token" value="{csrf_token}">
                        <input type="text" name="data" placeholder="Enter data">
                        <button type="submit">Submit</button>
                    </form>

                    <script>
                        // For AJAX requests, send CSRF token in header
                        const csrfToken = "{csrf_token}";

                        fetch('/api/data', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                                'X-CSRF-Token': csrfToken
                            }},
                            body: JSON.stringify({{data: 'test'}})
                        }});
                    </script>
                </body>
            </html>
        """)

    @app.post("/submit")
    async def submit_form(
        request: Request,
        data: str = Form(...)
    ):
        """
        Process form submission.
        CSRF token is automatically validated by middleware.
        """
        return {"status": "success", "data": data}

    return app


# ============================================================================
# Example 2: Advanced Configuration
# ============================================================================

def example_advanced_config():
    """
    CSRF protection with custom configuration.
    حماية CSRF مع إعدادات مخصصة.
    """
    app = FastAPI(title="Advanced CSRF Protection")

    # Custom CSRF configuration
    csrf_config = CSRFConfig(
        secret_key=os.getenv("CSRF_SECRET_KEY", "your-secret-key-change-in-production"),
        token_name="csrf_token",
        header_name="X-CSRF-Token",
        cookie_name="csrf_token",
        cookie_secure=True,  # HTTPS only
        cookie_httponly=True,  # Cannot be accessed by JavaScript
        cookie_samesite="strict",  # Strict same-site policy
        cookie_max_age=3600,  # 1 hour
        exclude_paths=[
            "/health",
            "/docs",
            "/api/webhooks",  # Webhooks don't need CSRF
        ],
        trusted_origins=[
            "https://app.sahool.com",
            "https://admin.sahool.com",
        ],
    )

    app.add_middleware(CSRFProtection, config=csrf_config)

    @app.post("/api/data")
    async def create_data(request: Request, data: dict):
        """Protected endpoint - CSRF token required"""
        return {"status": "created", "data": data}

    return app


# ============================================================================
# Example 3: Hybrid Auth (Bearer Token + Cookie)
# ============================================================================

def example_hybrid_auth():
    """
    Service with both Bearer token authentication and cookie-based sessions.
    CSRF protection is automatically skipped for Bearer token requests.

    خدمة مع مصادقة Bearer token ومصادقة الجلسات القائمة على ملفات تعريف الارتباط.
    يتم تخطي حماية CSRF تلقائياً لطلبات Bearer token.
    """
    app = FastAPI(title="Hybrid Auth Service")

    # Add CSRF protection
    # Bearer token requests are automatically excluded
    app.add_middleware(CSRFProtection)

    @app.post("/api/data")
    async def create_data_api(
        request: Request,
        data: dict,
        authorization: str = Depends(lambda r: r.headers.get("Authorization"))
    ):
        """
        API endpoint that accepts Bearer token.
        No CSRF token required when using Bearer authentication.

        Example:
            curl -X POST https://api.sahool.com/api/data \
                -H "Authorization: Bearer <token>" \
                -H "Content-Type: application/json" \
                -d '{"key": "value"}'
        """
        if authorization and authorization.startswith("Bearer "):
            # Bearer token auth - CSRF automatically skipped by middleware
            return {"status": "created", "auth": "bearer", "data": data}
        else:
            # Cookie-based auth - CSRF token was validated
            return {"status": "created", "auth": "cookie", "data": data}

    @app.post("/web/submit")
    async def submit_web_form(request: Request, data: dict):
        """
        Web form endpoint using cookie-based session.
        CSRF token required in X-CSRF-Token header.

        Example:
            fetch('/web/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': getCsrfToken()  // from cookie
                },
                body: JSON.stringify({key: 'value'})
            })
        """
        return {"status": "success", "data": data}

    return app


# ============================================================================
# Example 4: Multi-Service Setup
# ============================================================================

def example_field_service_with_csrf():
    """
    Example of adding CSRF protection to the field service.
    مثال على إضافة حماية CSRF لخدمة الحقول.
    """
    app = FastAPI(title="SAHOOL Field Service with CSRF")

    # CSRF configuration for field service
    csrf_config = CSRFConfig(
        secret_key=os.getenv("CSRF_SECRET_KEY"),
        cookie_secure=os.getenv("ENVIRONMENT", "development") == "production",
        cookie_samesite="lax",  # Allows some cross-origin requests
        exclude_paths=[
            "/health",
            "/healthz",
            "/readyz",
            "/docs",
            "/redoc",
            "/openapi.json",
        ],
        trusted_origins=[
            os.getenv("FRONTEND_URL", "https://app.sahool.com"),
            os.getenv("ADMIN_URL", "https://admin.sahool.com"),
        ],
    )

    app.add_middleware(CSRFProtection, config=csrf_config)

    # Example protected endpoints
    @app.post("/fields")
    async def create_field(request: Request, field_data: dict):
        """
        Create field endpoint.

        For API clients (mobile apps, etc.):
            - Use Bearer token authentication
            - CSRF check is automatically skipped

        For web browsers:
            - CSRF token must be included in X-CSRF-Token header
            - Token is automatically set in cookie on GET requests
        """
        return {"status": "created", "field_id": "field-123"}

    @app.put("/fields/{field_id}")
    async def update_field(request: Request, field_id: str, field_data: dict):
        """Update field - CSRF protected for browser requests"""
        return {"status": "updated", "field_id": field_id}

    @app.delete("/fields/{field_id}")
    async def delete_field(request: Request, field_id: str):
        """Delete field - CSRF protected for browser requests"""
        return {"status": "deleted", "field_id": field_id}

    @app.get("/fields/{field_id}")
    async def get_field(request: Request, field_id: str):
        """
        Get field - no CSRF validation (safe method).
        CSRF token cookie will be set automatically.
        """
        return {
            "field_id": field_id,
            "name": "Test Field",
            "csrf_token": get_csrf_token(request)  # Include in response if needed
        }

    return app


# ============================================================================
# Example 5: Testing CSRF Protection
# ============================================================================

async def example_test_csrf_protection():
    """
    Example test cases for CSRF protection.
    أمثلة على حالات الاختبار لحماية CSRF.
    """
    from fastapi.testclient import TestClient

    app = example_basic_setup()
    client = TestClient(app)

    # Test 1: GET request sets CSRF cookie
    response = client.get("/form")
    assert response.status_code == 200
    assert "csrf_token" in response.cookies

    # Test 2: POST without CSRF token fails
    response = client.post("/submit", data={"data": "test"})
    assert response.status_code == 403
    assert "CSRF_VALIDATION_FAILED" in response.json()["error"]["code"]

    # Test 3: POST with valid CSRF token succeeds
    # First, get the token
    get_response = client.get("/form")
    csrf_token = get_response.cookies.get("csrf_token")

    # Then use it in POST request
    response = client.post(
        "/submit",
        data={"data": "test"},
        headers={"X-CSRF-Token": csrf_token},
        cookies={"csrf_token": csrf_token}
    )
    assert response.status_code == 200

    # Test 4: Bearer token request bypasses CSRF
    response = client.post(
        "/submit",
        json={"data": "test"},
        headers={"Authorization": "Bearer fake-token"}
    )
    # This would succeed (CSRF is skipped), but may fail on auth validation
    # depending on your authentication implementation

    print("All CSRF tests passed!")


# ============================================================================
# Example 6: Frontend Integration
# ============================================================================

def example_frontend_integration():
    """
    Example of how frontend should handle CSRF tokens.

    JavaScript/React/Vue Integration:
    """
    frontend_code = '''
    // ========================================
    // Vanilla JavaScript
    // ========================================

    // Get CSRF token from cookie
    function getCsrfToken() {
        const name = 'csrf_token=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const ca = decodedCookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i].trim();
            if (c.indexOf(name) === 0) {
                return c.substring(name.length, c.length);
            }
        }
        return null;
    }

    // Make CSRF-protected request
    async function makeProtectedRequest(url, data) {
        const csrfToken = getCsrfToken();

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfToken
            },
            credentials: 'include',  // Include cookies
            body: JSON.stringify(data)
        });

        return response.json();
    }

    // Usage
    makeProtectedRequest('/api/fields', {
        name: 'My Field',
        area: 10.5
    }).then(result => {
        console.log('Field created:', result);
    });


    // ========================================
    // React/Axios
    // ========================================

    import axios from 'axios';
    import Cookies from 'js-cookie';

    // Configure axios to send CSRF token
    axios.defaults.xsrfCookieName = 'csrf_token';
    axios.defaults.xsrfHeaderName = 'X-CSRF-Token';
    axios.defaults.withCredentials = true;

    // Alternative: Add interceptor
    axios.interceptors.request.use(config => {
        const csrfToken = Cookies.get('csrf_token');
        if (csrfToken) {
            config.headers['X-CSRF-Token'] = csrfToken;
        }
        return config;
    });

    // Make request
    const createField = async (fieldData) => {
        const response = await axios.post('/api/fields', fieldData);
        return response.data;
    };


    // ========================================
    // React Hook
    // ========================================

    import { useState, useEffect } from 'react';
    import Cookies from 'js-cookie';

    function useCsrfToken() {
        const [csrfToken, setCsrfToken] = useState(null);

        useEffect(() => {
            // Get token from cookie
            const token = Cookies.get('csrf_token');
            setCsrfToken(token);

            // If token doesn't exist, fetch any GET endpoint to generate it
            if (!token) {
                fetch('/api/fields', { credentials: 'include' })
                    .then(() => {
                        const newToken = Cookies.get('csrf_token');
                        setCsrfToken(newToken);
                    });
            }
        }, []);

        return csrfToken;
    }

    // Use in component
    function FieldForm() {
        const csrfToken = useCsrfToken();

        const handleSubmit = async (formData) => {
            await fetch('/api/fields', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': csrfToken
                },
                credentials: 'include',
                body: JSON.stringify(formData)
            });
        };

        return (
            <form onSubmit={handleSubmit}>
                {/* form fields */}
            </form>
        );
    }
    '''

    return frontend_code


if __name__ == "__main__":
    """
    Run examples
    """
    import uvicorn

    # Run basic example
    app = example_field_service_with_csrf()

    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                  CSRF Protection Example                       ║
    ║                                                                ║
    ║  Test the CSRF protection:                                     ║
    ║                                                                ║
    ║  1. GET request (sets CSRF cookie):                            ║
    ║     curl -c cookies.txt http://localhost:8000/fields/123       ║
    ║                                                                ║
    ║  2. POST without CSRF token (should fail):                     ║
    ║     curl -X POST http://localhost:8000/fields \\               ║
    ║          -H "Content-Type: application/json" \\                ║
    ║          -d '{"name": "Test"}'                                 ║
    ║                                                                ║
    ║  3. POST with CSRF token (should succeed):                     ║
    ║     TOKEN=$(grep csrf_token cookies.txt | awk '{print $7}')    ║
    ║     curl -X POST http://localhost:8000/fields \\               ║
    ║          -b cookies.txt \\                                     ║
    ║          -H "Content-Type: application/json" \\                ║
    ║          -H "X-CSRF-Token: $TOKEN" \\                          ║
    ║          -d '{"name": "Test"}'                                 ║
    ║                                                                ║
    ║  4. POST with Bearer token (bypasses CSRF):                    ║
    ║     curl -X POST http://localhost:8000/fields \\               ║
    ║          -H "Authorization: Bearer <token>" \\                 ║
    ║          -H "Content-Type: application/json" \\                ║
    ║          -d '{"name": "Test"}'                                 ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(app, host="0.0.0.0", port=8000)
