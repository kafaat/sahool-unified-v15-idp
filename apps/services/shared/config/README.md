# SAHOOL Services - Shared Configuration
# تكوينات مشتركة لخدمات سهول

This directory contains centralized configuration modules used across all SAHOOL microservices.

## CORS Configuration

### File: `cors_config.py`

Centralized CORS (Cross-Origin Resource Sharing) configuration with secure defaults.

#### Features

- **Environment-based configuration**: Automatically selects appropriate origins based on `ENVIRONMENT` variable
- **Production security**: Prevents wildcard (*) origins in production
- **Explicit whitelisting**: All allowed origins are explicitly listed
- **Logging and monitoring**: Logs CORS configuration and security warnings
- **Easy integration**: Single function call to configure any FastAPI service

#### Allowed Origins

**Production:**
- `https://sahool.app`
- `https://admin.sahool.app`
- `https://api.sahool.app`
- `https://www.sahool.app`

**Development:**
- `http://localhost:3000`
- `http://localhost:3001`
- `http://localhost:5173`
- `http://localhost:8080`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:3001`
- `http://127.0.0.1:5173`
- `http://127.0.0.1:8080`

**Staging:**
- `https://staging.sahool.app`
- `https://admin-staging.sahool.app`
- `https://api-staging.sahool.app`

#### Usage

```python
from cors_config import setup_cors_middleware

app = FastAPI(title="My Service")
setup_cors_middleware(app)
```

#### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name | `production`, `staging`, `development` |
| `CORS_ORIGINS` | Custom comma-separated origins (overrides defaults) | `https://example.com,https://app.example.com` |

#### Security Features

1. **No wildcard in production**: Automatically blocks wildcard (*) origins in production
2. **Explicit whitelisting**: All origins must be explicitly listed
3. **Credential security**: Properly configured credential support with origin validation
4. **Security warnings**: Logs critical warnings if insecure configuration detected

#### Services Using This Configuration

1. **Alert Service** (`apps/services/alert-service/src/main.py`)
   - Port: 8107
   - Agricultural alerts and warnings management

2. **Field Service** (`apps/services/field-service/src/main.py`)
   - Port: 3000
   - Field management and geographic boundaries

3. **NDVI Processor** (`apps/services/ndvi-processor/src/main.py`)
   - Port: 8101
   - Satellite image processing and NDVI calculation

4. **Crop Health AI** (`apps/services/crop-health-ai/src/main.py`)
   - Port: 8095
   - AI-powered plant disease diagnosis

## Migration from Wildcard CORS

### Before (Insecure)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ Security vulnerability!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### After (Secure)

```python
from cors_config import setup_cors_middleware

setup_cors_middleware(app)  # ✅ Secure, environment-aware configuration
```

## Configuration Functions

### `get_allowed_origins() -> List[str]`

Returns the list of allowed origins based on environment.

**Priority:**
1. `CORS_ORIGINS` environment variable
2. Environment-specific defaults (`ENVIRONMENT` variable)
3. Development origins (safest fallback)

### `setup_cors_middleware(app: FastAPI, **kwargs) -> None`

Configures CORS middleware with secure defaults.

**Parameters:**
- `app`: FastAPI application instance
- `allowed_origins`: Custom origins list (optional)
- `allow_credentials`: Allow credentials (default: True)
- `allowed_methods`: HTTP methods (default: GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD)
- `allowed_headers`: Request headers (default: Authorization, Content-Type, etc.)
- `expose_headers`: Response headers to expose (default: X-Request-ID, X-Correlation-ID, etc.)
- `max_age`: Preflight cache duration in seconds (default: 3600)

### `get_cors_config() -> dict`

Returns current CORS configuration as a dictionary for debugging.

**Returns:**
```python
{
    "environment": "production",
    "allowed_origins": ["https://sahool.app", ...],
    "cors_origins_env": "not set",
    "has_wildcard": false,
    "origin_count": 4
}
```

### `validate_origin(origin: str) -> bool`

Validates if an origin is in the allowed list.

## Testing

### Development Environment

```bash
# Uses development origins automatically
export ENVIRONMENT=development
python -m uvicorn main:app --reload
```

### Production Environment

```bash
# Uses production origins
export ENVIRONMENT=production
python -m uvicorn main:app
```

### Custom Origins

```bash
# Override with custom origins
export CORS_ORIGINS="https://custom1.sahool.app,https://custom2.sahool.app"
python -m uvicorn main:app
```

## Security Best Practices

1. **Never use wildcard (*) in production**
   - Exposes your API to all domains
   - Allows credential theft
   - Enables CSRF attacks

2. **Always use HTTPS in production**
   - All production origins use `https://`
   - HTTP only allowed in development

3. **Explicitly list all origins**
   - Each domain must be individually whitelisted
   - No patterns or wildcards

4. **Monitor CORS logs**
   - Check for security warnings in logs
   - Review CORS configuration regularly

5. **Keep credentials enabled only when needed**
   - Required for cookie-based authentication
   - Required for Authorization header

## Version History

- **v1.0.0** (2024-12-24): Initial centralized CORS configuration
  - Migrated from wildcard to explicit whitelisting
  - Added environment-based configuration
  - Implemented security warnings and validation

## Support

For questions or issues with CORS configuration:
1. Check service logs for CORS-related warnings
2. Verify `ENVIRONMENT` variable is set correctly
3. Ensure origins are properly formatted (include protocol: `https://`)
4. Review FastAPI CORS documentation: https://fastapi.tiangolo.com/tutorial/cors/

## Related Files

- `/home/user/sahool-unified-v15-idp/apps/services/shared/config/cors_config.py` - Main CORS configuration
- `/home/user/sahool-unified-v15-idp/shared/middleware/cors.py` - Alternative CORS setup (older, uses sahool.io)
