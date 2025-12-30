# CSRF Protection Integration Guide

## Quick Start: Adding CSRF to Existing Service

This guide shows how to add CSRF protection to an existing SAHOOL service.

---

## Step 1: Update Service Configuration

### For Field Service (Example)

Edit `/apps/services/field-service/src/main.py`:

```python
from fastapi import FastAPI
from apps.services.shared.middleware import CSRFProtection, CSRFConfig
import os

app = FastAPI(title="SAHOOL Field Service")

# Add CSRF protection
csrf_config = CSRFConfig(
    secret_key=os.getenv("CSRF_SECRET_KEY", "change-me-in-production"),
    cookie_secure=os.getenv("ENVIRONMENT", "development") == "production",
    cookie_samesite="lax",
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

# IMPORTANT: Add CSRF middleware AFTER CORS middleware
# Middleware order matters!
app.add_middleware(CSRFProtection, config=csrf_config)
```

### Environment Variables

Add to your `.env` file:

```bash
# CSRF Configuration
CSRF_SECRET_KEY=your-secret-key-here-minimum-32-chars-random
ENVIRONMENT=production
FRONTEND_URL=https://app.sahool.com
ADMIN_URL=https://admin.sahool.com
```

**Generate a secure secret key:**

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## Step 2: Update Existing Endpoints

### Before CSRF Protection

```python
@app.post("/fields")
async def create_field(field: FieldCreate, tenant_id: str = Depends(get_tenant_id)):
    # No CSRF protection
    return {"id": "field-123"}
```

### After CSRF Protection

```python
from fastapi import Request
from apps.services.shared.middleware import get_csrf_token

@app.post("/fields")
async def create_field(
    request: Request,
    field: FieldCreate,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Create a new field.

    For API clients (mobile apps):
        - Use Bearer token authentication
        - CSRF check is automatically skipped

    For web browsers:
        - CSRF token must be included in X-CSRF-Token header
        - Token is available in csrf_token cookie
    """
    return {"id": "field-123"}

@app.get("/fields/{field_id}")
async def get_field(request: Request, field_id: str):
    """
    Get field details.
    CSRF token is automatically set in cookie on this GET request.
    """
    return {
        "id": field_id,
        "name": "My Field",
        # Optionally include token in response for JavaScript apps
        "csrf_token": get_csrf_token(request)
    }
```

---

## Step 3: Update Frontend

### React/Next.js Integration

Create a CSRF hook:

```typescript
// hooks/useCsrfToken.ts
import { useState, useEffect } from 'react';
import Cookies from 'js-cookie';

export function useCsrfToken() {
    const [csrfToken, setCsrfToken] = useState<string | null>(null);

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
                })
                .catch(console.error);
        }
    }, []);

    return csrfToken;
}
```

Configure Axios:

```typescript
// lib/api.ts
import axios from 'axios';
import Cookies from 'js-cookie';

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL,
    withCredentials: true,
});

// Add CSRF token to all requests
api.interceptors.request.use(config => {
    const csrfToken = Cookies.get('csrf_token');
    if (csrfToken) {
        config.headers['X-CSRF-Token'] = csrfToken;
    }
    return config;
});

export default api;
```

Use in components:

```typescript
// components/FieldForm.tsx
import { useCsrfToken } from '@/hooks/useCsrfToken';
import api from '@/lib/api';

export function FieldForm() {
    const csrfToken = useCsrfToken();

    const handleSubmit = async (data: FieldData) => {
        if (!csrfToken) {
            console.error('CSRF token not available');
            return;
        }

        try {
            const response = await api.post('/fields', data);
            console.log('Field created:', response.data);
        } catch (error) {
            console.error('Failed to create field:', error);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            {/* form fields */}
        </form>
    );
}
```

---

## Step 4: Update API Client (Mobile Apps)

### For Mobile Apps Using Bearer Tokens

**No changes required!** CSRF protection is automatically bypassed for requests with Bearer tokens.

```typescript
// mobile/api/client.ts
import axios from 'axios';

const mobileApi = axios.create({
    baseURL: 'https://api.sahool.com',
});

// Add Bearer token to requests
mobileApi.interceptors.request.use(config => {
    const token = getStoredAuthToken(); // Your token storage
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
});

// This works without CSRF token
export async function createField(fieldData: FieldData) {
    const response = await mobileApi.post('/fields', fieldData);
    return response.data;
}
```

---

## Step 5: Test the Integration

### Manual Testing

```bash
# 1. Get CSRF token
curl -c cookies.txt https://api.sahool.com/api/fields

# 2. Extract token
TOKEN=$(grep csrf_token cookies.txt | awk '{print $7}')

# 3. Test POST without token (should fail)
curl -X POST https://api.sahool.com/api/fields \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Field"}'

# Expected: 403 Forbidden

# 4. Test POST with token (should succeed)
curl -X POST https://api.sahool.com/api/fields \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $TOKEN" \
  -d '{"name": "Test Field"}'

# Expected: 200 OK

# 5. Test with Bearer token (should succeed, no CSRF needed)
curl -X POST https://api.sahool.com/api/fields \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Field"}'

# Expected: 200 OK (if auth token is valid)
```

### Automated Tests

```python
# tests/test_csrf_integration.py
from fastapi.testclient import TestClient
from apps.services.field_service.main import app

client = TestClient(app)

def test_csrf_protection_on_post():
    """Test that POST requests require CSRF token"""
    # Without token - should fail
    response = client.post("/fields", json={"name": "Test"})
    assert response.status_code == 403

    # Get token
    get_response = client.get("/fields/123")
    csrf_token = get_response.cookies.get("csrf_token")

    # With token - should succeed
    response = client.post(
        "/fields",
        json={"name": "Test"},
        headers={"X-CSRF-Token": csrf_token},
        cookies={"csrf_token": csrf_token}
    )
    assert response.status_code in [200, 201]

def test_bearer_token_bypasses_csrf():
    """Test that Bearer token auth bypasses CSRF"""
    response = client.post(
        "/fields",
        json={"name": "Test"},
        headers={"Authorization": "Bearer fake-token"}
    )
    # Should not fail with CSRF error
    assert response.status_code != 403 or "CSRF" not in response.text
```

---

## Step 6: Deploy to Production

### Deployment Checklist

- [ ] Set strong `CSRF_SECRET_KEY` in production environment
- [ ] Set `cookie_secure=True` (HTTPS only)
- [ ] Configure `trusted_origins` with your production domains
- [ ] Use `cookie_samesite="strict"` for maximum security
- [ ] Update frontend to send CSRF tokens
- [ ] Test all forms and API endpoints
- [ ] Monitor CSRF validation errors in logs
- [ ] Document CSRF requirements for API consumers

### Kubernetes/Docker Configuration

```yaml
# deployment.yaml
env:
  - name: CSRF_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: csrf-secrets
        key: secret-key
  - name: ENVIRONMENT
    value: "production"
  - name: FRONTEND_URL
    value: "https://app.sahool.com"
  - name: ADMIN_URL
    value: "https://admin.sahool.com"
```

### Secret Generation

```bash
# Generate CSRF secret
kubectl create secret generic csrf-secrets \
  --from-literal=secret-key=$(python3 -c "import secrets; print(secrets.token_hex(32))")
```

---

## Step 7: Monitor and Maintain

### Logging

CSRF middleware logs warnings for failed validations:

```
WARNING - CSRF validation failed: CSRF token mismatch between cookie and header
  path=/api/fields
  method=POST
  client=192.168.1.100
```

### Metrics (Optional)

Track CSRF validation failures:

```python
from prometheus_client import Counter

csrf_failures = Counter(
    'csrf_validation_failures_total',
    'Total CSRF validation failures',
    ['endpoint', 'reason']
)

# In your monitoring middleware
if response.status_code == 403 and 'CSRF' in response.body:
    csrf_failures.labels(
        endpoint=request.url.path,
        reason='csrf_validation_failed'
    ).inc()
```

### Troubleshooting

**Common issues and solutions:**

| Issue | Cause | Solution |
|-------|-------|----------|
| Cookie not set | Secure flag on HTTP | Set `cookie_secure=False` in development |
| Token mismatch | Clock skew | Check server time sync |
| Constant failures | Wrong secret key | Verify secret key is consistent across instances |
| Frontend not sending token | CORS issues | Check CORS configuration, ensure `credentials: 'include'` |

---

## Rollback Plan

If you need to rollback CSRF protection:

1. **Disable middleware** (comment out):
   ```python
   # app.add_middleware(CSRFProtection, config=csrf_config)
   ```

2. **Deploy updated service**

3. **Monitor** for any issues

4. **Re-enable** when ready:
   - Fix any issues
   - Update frontend
   - Re-enable middleware
   - Deploy

---

## Migration Timeline (Recommended)

### Week 1: Preparation
- Add CSRF middleware to services (disabled)
- Update frontend code
- Test in development

### Week 2: Staging Deployment
- Enable CSRF in staging
- Full integration testing
- Fix any issues

### Week 3: Production Deployment
- Enable CSRF in production
- Monitor closely
- Have rollback ready

### Week 4: Stabilization
- Monitor logs and metrics
- Address edge cases
- Document learnings

---

## Service-Specific Examples

### Field Service

```python
# apps/services/field-service/src/main.py
from apps.services.shared.middleware import CSRFProtection, CSRFConfig
import os

csrf_config = CSRFConfig(
    secret_key=os.getenv("CSRF_SECRET_KEY"),
    cookie_secure=os.getenv("ENVIRONMENT") == "production",
    exclude_paths=["/health", "/healthz", "/docs"],
)

app.add_middleware(CSRFProtection, config=csrf_config)
```

### Weather Service

```python
# apps/services/weather-service/src/main.py
csrf_config = CSRFConfig(
    secret_key=os.getenv("CSRF_SECRET_KEY"),
    exclude_paths=[
        "/health",
        "/webhook/weather-update",  # External webhooks
    ],
)

app.add_middleware(CSRFProtection, config=csrf_config)
```

### Admin Service

```python
# apps/admin/api/main.py
csrf_config = CSRFConfig(
    secret_key=os.getenv("CSRF_SECRET_KEY"),
    cookie_samesite="strict",  # Stricter for admin
    cookie_max_age=1800,  # 30 minutes for admin
)

app.add_middleware(CSRFProtection, config=csrf_config)
```

---

## Best Practices

1. **Always use HTTPS in production** - CSRF tokens in cookies should only be sent over secure connections
2. **Use strong secret keys** - Generate with `secrets.token_hex(32)` or similar
3. **Rotate secrets periodically** - Change CSRF secret key every 6-12 months
4. **Monitor validation failures** - Set up alerts for unusual CSRF failure rates
5. **Document for API consumers** - Clearly document CSRF requirements
6. **Test thoroughly** - Test all state-changing endpoints
7. **Use SameSite cookies** - Set to "strict" or "lax" for additional protection
8. **Keep tokens short-lived** - 1-2 hours is reasonable for most applications

---

## Support & Resources

- **Documentation**: `/apps/services/shared/middleware/CSRF_README.md`
- **Examples**: `/apps/services/shared/middleware/csrf_example.py`
- **Tests**: `/apps/services/shared/middleware/test_csrf.py`
- **Source Code**: `/apps/services/shared/middleware/csrf.py`

---

## Next Steps

1. Choose a service to add CSRF protection
2. Follow this integration guide
3. Test thoroughly in development
4. Deploy to staging
5. Monitor and adjust
6. Deploy to production
7. Repeat for other services

Good luck! 🔒
