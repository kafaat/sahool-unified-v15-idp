# CSRF Protection Middleware

## Overview

The CSRF (Cross-Site Request Forgery) protection middleware provides secure token-based validation for state-changing operations in FastAPI services. This implementation uses the **Double Submit Cookie** pattern with **HMAC signing** for enhanced security.

### Key Features

✅ **Automatic Token Generation**: CSRF tokens are automatically generated and set in secure cookies
✅ **State-Changing Protection**: Validates tokens on POST, PUT, DELETE, and PATCH requests
✅ **Bearer Token Bypass**: Automatically excludes API requests using Bearer token authentication
✅ **Secure Cookies**: Supports Secure, HttpOnly, and SameSite cookie attributes
✅ **HMAC Signing**: Tokens are cryptographically signed to prevent tampering
✅ **Token Expiration**: Configurable token lifetime with automatic validation
✅ **Flexible Configuration**: Customizable paths, headers, and security settings
✅ **Referer Validation**: Optional referer/origin checking for additional security

---

## How It Works

### Double Submit Cookie Pattern

1. **Token Generation**: When a user makes a GET request, a CSRF token is generated and set in a secure cookie
2. **Token Submission**: For state-changing requests (POST/PUT/DELETE), the client must send the token in the `X-CSRF-Token` header
3. **Token Validation**: The middleware validates that:
   - The token exists in both cookie and header
   - Both tokens match exactly
   - The token signature is valid (HMAC)
   - The token has not expired
   - The referer/origin is trusted (optional)

### Token Format

```
{random_value}.{timestamp}.{hmac_signature}
```

- **random_value**: 32-byte URL-safe random string
- **timestamp**: Unix timestamp when token was created
- **hmac_signature**: SHA-256 HMAC signature of `random_value.timestamp`

---

## Installation

The middleware is already included in the shared middleware package:

```python
from apps.services.shared.middleware import CSRFProtection, CSRFConfig, get_csrf_token
```

---

## Basic Usage

### 1. Add Middleware to FastAPI App

```python
from fastapi import FastAPI
from apps.services.shared.middleware import CSRFProtection

app = FastAPI()

# Add CSRF protection with default configuration
app.add_middleware(CSRFProtection)
```

### 2. Protected Endpoints

```python
from fastapi import Request

@app.post("/api/fields")
async def create_field(request: Request, field_data: dict):
    """
    This endpoint is automatically protected by CSRF middleware.
    Clients must include X-CSRF-Token header with valid token.
    """
    return {"status": "created", "data": field_data}
```

### 3. Getting CSRF Token

```python
from apps.services.shared.middleware import get_csrf_token

@app.get("/api/fields")
async def list_fields(request: Request):
    """
    CSRF token is automatically set in cookie on GET requests.
    You can also include it in the response if needed.
    """
    return {
        "fields": [...],
        "csrf_token": get_csrf_token(request)  # Optional
    }
```

---

## Advanced Configuration

### Custom Configuration

```python
from apps.services.shared.middleware import CSRFProtection, CSRFConfig
import os

app = FastAPI()

csrf_config = CSRFConfig(
    # Secret key for HMAC signing (MUST be kept secret)
    secret_key=os.getenv("CSRF_SECRET_KEY", "change-in-production"),

    # Cookie configuration
    cookie_name="csrf_token",
    cookie_path="/",
    cookie_domain=None,  # Current domain
    cookie_secure=True,  # HTTPS only
    cookie_httponly=True,  # Not accessible via JavaScript
    cookie_samesite="strict",  # Strict same-site policy
    cookie_max_age=3600,  # 1 hour

    # Token configuration
    token_name="csrf_token",
    header_name="X-CSRF-Token",

    # Safe methods (don't require CSRF validation)
    safe_methods={"GET", "HEAD", "OPTIONS", "TRACE"},

    # Paths to exclude from CSRF protection
    exclude_paths=[
        "/health",
        "/docs",
        "/api/webhooks",  # Webhooks from external services
    ],

    # Additional security
    require_referer_check=True,
    trusted_origins=[
        "https://app.sahool.com",
        "https://admin.sahool.com",
    ],
)

app.add_middleware(CSRFProtection, config=csrf_config)
```

### Environment-Based Configuration

```python
import os

csrf_config = CSRFConfig(
    secret_key=os.getenv("CSRF_SECRET_KEY"),
    cookie_secure=os.getenv("ENVIRONMENT") == "production",
    cookie_samesite="lax" if os.getenv("ENVIRONMENT") == "development" else "strict",
    trusted_origins=os.getenv("TRUSTED_ORIGINS", "").split(","),
)
```

---

## Frontend Integration

### JavaScript (Vanilla)

```javascript
// Get CSRF token from cookie
function getCsrfToken() {
    const name = 'csrf_token=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookies = decodedCookie.split(';');

    for(let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name)) {
            return cookie.substring(name.length);
        }
    }
    return null;
}

// Make CSRF-protected request
async function createField(fieldData) {
    const csrfToken = getCsrfToken();

    const response = await fetch('/api/fields', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken
        },
        credentials: 'include',  // Include cookies
        body: JSON.stringify(fieldData)
    });

    return response.json();
}
```

### React with Axios

```javascript
import axios from 'axios';
import Cookies from 'js-cookie';

// Configure axios defaults
axios.defaults.withCredentials = true;

// Add CSRF token to all requests
axios.interceptors.request.use(config => {
    const csrfToken = Cookies.get('csrf_token');
    if (csrfToken) {
        config.headers['X-CSRF-Token'] = csrfToken;
    }
    return config;
});

// Usage
const createField = async (fieldData) => {
    const response = await axios.post('/api/fields', fieldData);
    return response.data;
};
```

### React Hook

```javascript
import { useState, useEffect } from 'react';
import Cookies from 'js-cookie';

function useCsrfToken() {
    const [csrfToken, setCsrfToken] = useState(null);

    useEffect(() => {
        const token = Cookies.get('csrf_token');

        if (token) {
            setCsrfToken(token);
        } else {
            // Fetch any GET endpoint to generate token
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

    return <form onSubmit={handleSubmit}>...</form>;
}
```

### Vue.js

```javascript
import axios from 'axios';

export default {
    data() {
        return {
            csrfToken: null
        }
    },
    mounted() {
        this.csrfToken = this.getCookie('csrf_token');
    },
    methods: {
        getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
        },
        async createField(fieldData) {
            const response = await axios.post('/api/fields', fieldData, {
                headers: {
                    'X-CSRF-Token': this.csrfToken
                },
                withCredentials: true
            });
            return response.data;
        }
    }
}
```

---

## API Client Integration

### Mobile Apps & API Clients

For API clients (mobile apps, desktop apps, server-to-server), use **Bearer token authentication** instead of CSRF tokens:

```bash
# Bearer token authentication automatically bypasses CSRF
curl -X POST https://api.sahool.com/api/fields \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Field", "area": 10.5}'
```

The CSRF middleware automatically **skips validation** for requests with `Authorization: Bearer` header.

### cURL Examples

```bash
# 1. Get CSRF token (sets cookie)
curl -c cookies.txt https://api.sahool.com/api/fields

# 2. Extract token from cookie
TOKEN=$(grep csrf_token cookies.txt | awk '{print $7}')

# 3. Make protected request
curl -X POST https://api.sahool.com/api/fields \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $TOKEN" \
  -d '{"name": "My Field", "area": 10.5}'
```

---

## Testing

### Unit Tests

```python
from fastapi.testclient import TestClient

def test_csrf_protection():
    client = TestClient(app)

    # Get CSRF token
    get_response = client.get("/api/fields")
    csrf_token = get_response.cookies.get("csrf_token")

    # Use token in POST request
    post_response = client.post(
        "/api/fields",
        json={"name": "Test Field"},
        headers={"X-CSRF-Token": csrf_token},
        cookies={"csrf_token": csrf_token}
    )

    assert post_response.status_code == 200
```

### Integration Tests

```python
import pytest
from apps.services.shared.middleware import CSRFProtection

@pytest.fixture
def app_with_csrf():
    app = FastAPI()
    app.add_middleware(CSRFProtection)
    return app

def test_bearer_token_bypasses_csrf(app_with_csrf):
    client = TestClient(app_with_csrf)

    # No CSRF token needed with Bearer auth
    response = client.post(
        "/api/fields",
        json={"name": "Test"},
        headers={"Authorization": "Bearer fake-token"}
    )

    # Should not fail with CSRF error
    assert response.status_code != 403
```

---

## Security Considerations

### Best Practices

1. **Use HTTPS in Production**: Always set `cookie_secure=True` in production
2. **Strong Secret Key**: Use a cryptographically strong secret key (32+ bytes)
3. **Rotate Secret Keys**: Periodically rotate your CSRF secret key
4. **SameSite Strict**: Use `cookie_samesite="strict"` for maximum protection
5. **Short Expiration**: Keep token lifetime reasonable (1-2 hours)
6. **CORS Configuration**: Properly configure CORS for your trusted origins

### What CSRF Protection Prevents

✅ Prevents malicious websites from making requests on behalf of authenticated users
✅ Protects against one-click attacks (clickjacking)
✅ Validates request origin and authenticity

### What CSRF Protection Does NOT Prevent

❌ Does not prevent XSS (Cross-Site Scripting) attacks
❌ Does not validate user permissions (use authorization middleware)
❌ Does not prevent SQL injection or other injection attacks

---

## Troubleshooting

### Common Issues

#### 1. CSRF Validation Failed

**Error**: `CSRF token validation failed`

**Solutions**:
- Ensure cookie is being sent with request (`credentials: 'include'`)
- Verify token is in `X-CSRF-Token` header
- Check token hasn't expired
- Confirm cookie and header tokens match

#### 2. CSRF Cookie Not Set

**Error**: `CSRF cookie not found`

**Solutions**:
- Make a GET request first to generate token
- Check cookie settings (domain, path, secure)
- Verify browser accepts cookies
- Check `cookie_secure` setting matches your protocol (HTTP/HTTPS)

#### 3. Token Mismatch

**Error**: `CSRF token mismatch between cookie and header`

**Solutions**:
- Ensure you're reading cookie value correctly
- Check for URL encoding issues
- Verify cookie is being sent back to server

#### 4. Bearer Token Not Bypassing CSRF

**Issue**: API requests with Bearer token still require CSRF

**Solutions**:
- Ensure `Authorization` header is formatted correctly: `Bearer <token>`
- Check middleware order (CSRF should be after CORS)
- Verify Bearer token is being sent in request

### Debug Mode

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("apps.services.shared.middleware.csrf")
logger.setLevel(logging.DEBUG)
```

---

## Migration Guide

### Adding CSRF to Existing Service

1. **Add middleware to your FastAPI app**:
   ```python
   from apps.services.shared.middleware import CSRFProtection, CSRFConfig

   csrf_config = CSRFConfig(
       secret_key=os.getenv("CSRF_SECRET_KEY"),
       cookie_secure=os.getenv("ENVIRONMENT") == "production",
   )

   app.add_middleware(CSRFProtection, config=csrf_config)
   ```

2. **Update frontend to send CSRF token**:
   - Add token to all state-changing requests
   - Read token from cookie
   - Send in `X-CSRF-Token` header

3. **Test thoroughly**:
   - Verify all forms work
   - Test API endpoints
   - Check mobile app compatibility

4. **Monitor in production**:
   - Watch for CSRF validation errors
   - Check cookie delivery
   - Verify token expiration settings

---

## Configuration Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `secret_key` | str | auto-generated | Secret key for HMAC signing |
| `token_name` | str | `"csrf_token"` | Name of token in request body/form |
| `header_name` | str | `"X-CSRF-Token"` | Name of CSRF header |
| `cookie_name` | str | `"csrf_token"` | Name of CSRF cookie |
| `cookie_path` | str | `"/"` | Cookie path |
| `cookie_domain` | str | `None` | Cookie domain (current domain if None) |
| `cookie_secure` | bool | `True` | Use Secure flag (HTTPS only) |
| `cookie_httponly` | bool | `True` | Use HttpOnly flag |
| `cookie_samesite` | str | `"strict"` | SameSite attribute (strict/lax/none) |
| `cookie_max_age` | int | `3600` | Cookie max age in seconds |
| `safe_methods` | Set[str] | `{"GET", "HEAD", "OPTIONS", "TRACE"}` | Methods that don't require CSRF |
| `exclude_paths` | List[str] | `["/health", "/docs", ...]` | Paths excluded from CSRF |
| `require_referer_check` | bool | `True` | Check Referer/Origin header |
| `trusted_origins` | List[str] | `[]` | Trusted origins for CORS |

---

## Support

For issues or questions:
- Check the test file: `test_csrf.py`
- Review examples: `csrf_example.py`
- Contact platform team

---

## License

Part of SAHOOL Unified Platform v15+
