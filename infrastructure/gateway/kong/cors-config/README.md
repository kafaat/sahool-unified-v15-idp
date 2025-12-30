# CORS Configuration System

## Overview

This directory contains environment-specific CORS (Cross-Origin Resource Sharing) configurations for the SAHOOL Platform Kong API Gateway.

## Environment Files

- **`cors-development.yml`** - Development environment configuration
  - Allows localhost origins (ports 3000, 8000, 8080)
  - Includes development domains (dev.sahool.app)
  - Max age: 1 hour (3600s)
  - Most permissive settings for easier development

- **`cors-staging.yml`** - Staging/QA environment configuration
  - Allows staging domains (staging.sahool.app, qa.sahool.app)
  - Limited localhost access for testing
  - Max age: 2 hours (7200s)
  - Moderate security settings

- **`cors-production.yml`** - Production environment configuration
  - **NO localhost origins allowed**
  - Only production domains (sahool.app, sahool.com)
  - Max age: 24 hours (86400s)
  - Strictest security settings

## Configuration Structure

Each CORS configuration file contains:

```yaml
cors:
  origins:              # Allowed origins
    - https://example.com
  methods:              # Allowed HTTP methods
    - GET
    - POST
    - PUT
    - DELETE
    - PATCH
    - OPTIONS
  headers:              # Allowed request headers
    - Accept
    - Authorization
    - Content-Type
  exposed_headers:      # Headers exposed to the client
    - X-Request-ID
  credentials: true     # Allow credentials (cookies, auth)
  max_age: 3600        # Preflight cache duration (seconds)
  preflight_continue: false
```

## Usage

### 1. Set Environment Variable

Set the `CORS_ENVIRONMENT` variable in your `.env` file:

```bash
# For development
CORS_ENVIRONMENT=development

# For staging
CORS_ENVIRONMENT=staging

# For production
CORS_ENVIRONMENT=production
```

### 2. Apply Configuration Manually

Run the configuration script:

```bash
# From Kong directory
cd /infrastructure/gateway/kong
./scripts/apply-cors-config.sh

# Or specify environment explicitly
./scripts/apply-cors-config.sh production
```

### 3. Automatic Application on Startup

The CORS configuration is automatically applied when Kong starts via Docker Compose, based on the `CORS_ENVIRONMENT` variable.

## Adding New Origins

### Development Environment

Edit `cors-development.yml` and add your origin:

```yaml
cors:
  origins:
    - http://localhost:3000
    - http://localhost:4200    # New origin
```

### Staging Environment

Edit `cors-staging.yml`:

```yaml
cors:
  origins:
    - https://staging.sahool.app
    - https://test.sahool.app  # New origin
```

### Production Environment

**⚠️ IMPORTANT:** Be very careful when adding production origins. Only add trusted domains.

Edit `cors-production.yml`:

```yaml
cors:
  origins:
    - https://sahool.app
    - https://partner.example.com  # New trusted partner domain
```

## Security Best Practices

1. **Never use wildcards (`*`) in production**
   - Always specify exact origins

2. **Use HTTPS in production**
   - All production origins should use `https://`
   - HTTP origins should only be used in development

3. **Minimize exposed headers**
   - Only expose headers that are absolutely necessary
   - Remove sensitive headers from `exposed_headers`

4. **Review origins regularly**
   - Audit the list of allowed origins periodically
   - Remove any origins that are no longer needed

5. **Credentials flag**
   - Set `credentials: false` if you don't need cookies/auth headers
   - Only enable for trusted origins

## Troubleshooting

### CORS Errors in Browser

If you see CORS errors in the browser console:

1. Check that your origin is listed in the appropriate environment file
2. Verify the `CORS_ENVIRONMENT` variable matches your current environment
3. Ensure Kong has been reloaded/restarted after configuration changes
4. Check browser console for the exact error message

### Common Issues

**Issue:** "Origin not allowed"
- **Solution:** Add your origin to the appropriate CORS config file

**Issue:** "Method not allowed"
- **Solution:** Add the HTTP method to the `methods` list

**Issue:** "Header not allowed"
- **Solution:** Add the header to the `headers` list

**Issue:** Changes not taking effect
- **Solution:** Restart Kong or run `docker exec kong-gateway kong reload`

## Testing CORS Configuration

### Using curl

Test a preflight request:

```bash
curl -X OPTIONS http://localhost:8000/api/v1/health \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

Expected response headers:
- `Access-Control-Allow-Origin: http://localhost:3000`
- `Access-Control-Allow-Methods: GET, POST, ...`
- `Access-Control-Allow-Headers: Content-Type, ...`

### Using JavaScript

```javascript
fetch('http://localhost:8000/api/v1/health', {
  method: 'GET',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json'
  }
})
  .then(response => console.log('Success:', response))
  .catch(error => console.error('CORS Error:', error));
```

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ENVIRONMENT` | `development` | CORS environment configuration to use |
| `KONG_CORS_ORIGINS` | Auto-generated | Comma-separated list of allowed origins |
| `KONG_CORS_METHODS` | Auto-generated | Comma-separated list of allowed methods |
| `KONG_CORS_HEADERS` | Auto-generated | Comma-separated list of allowed headers |
| `KONG_CORS_EXPOSED_HEADERS` | Auto-generated | Comma-separated list of exposed headers |
| `KONG_CORS_CREDENTIALS` | Auto-generated | Allow credentials (true/false) |
| `KONG_CORS_MAX_AGE` | Auto-generated | Preflight cache duration in seconds |

## Related Documentation

- [Kong CORS Plugin Documentation](https://docs.konghq.com/hub/kong-inc/cors/)
- [MDN CORS Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [SAHOOL Platform Security Guidelines](../../docs/security/README.md)

## Support

For issues or questions:
- Open an issue in the project repository
- Contact the DevOps team
- Check Kong logs: `docker logs kong-gateway`
