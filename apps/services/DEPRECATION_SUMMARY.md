# Service Deprecation Implementation Summary

This document summarizes the deprecation notices added to services in the SAHOOL platform.

## Deprecated Services

### 1. weather-advanced → weather-service

- **Service Path**: `/home/user/sahool-unified-v15-idp/apps/services/weather-advanced`
- **Port**: 8092
- **Replacement**: `weather-service` (port 8108)
- **Deprecation Date**: 2025-01-01
- **Sunset Date**: 2025-06-01

### 2. crop-health-ai → crop-intelligence-service

- **Service Path**: `/home/user/sahool-unified-v15-idp/apps/services/crop-health-ai`
- **Port**: 8095
- **Replacement**: `crop-intelligence-service` (port 8095)
- **Deprecation Date**: 2025-01-01
- **Sunset Date**: 2025-06-01

### 3. satellite-service → vegetation-analysis-service

- **Service Path**: `/home/user/sahool-unified-v15-idp/apps/services/satellite-service`
- **Port**: 8090
- **Replacement**: `vegetation-analysis-service` (port 8090)
- **Deprecation Date**: 2025-01-01
- **Sunset Date**: 2025-06-01

### 4. crop-health → crop-intelligence-service

- **Service Path**: `/home/user/sahool-unified-v15-idp/apps/services/crop-health`
- **Port**: 8100
- **Replacement**: `crop-intelligence-service` (port 8095)
- **Deprecation Date**: 2026-01-06
- **Sunset Date**: 2026-06-01
- **Features Migrated**: Zone-based health monitoring, vegetation indices (NDVI, EVI, NDRE, LCI, NDWI, SAVI), VRT export

### 5. ndvi-engine → vegetation-analysis-service

- **Service Path**: `/home/user/sahool-unified-v15-idp/apps/services/ndvi-engine`
- **Port**: 8107
- **Replacement**: `vegetation-analysis-service` (port 8090)
- **Deprecation Date**: 2026-01-06
- **Sunset Date**: 2026-06-01
- **Features Migrated**: NDVI computation, vegetation indices, zone analysis, anomaly detection

## Changes Implemented

For each service, the following changes were made:

### 1. Module Docstring Updates

Added deprecation notice to the top of each `main.py` file:

```python
"""
⚠️ DEPRECATED: This service is deprecated and will be removed in a future release.
Please use '<replacement-service>' instead.
"""
```

### 2. Startup Logging

Added deprecation warnings that are logged when the service starts:

```python
logger.warning("=" * 80)
logger.warning("⚠️  DEPRECATION WARNING")
logger.warning("=" * 80)
logger.warning("This service (<service-name>) is DEPRECATED and will be removed in a future release.")
logger.warning("Please migrate to '<replacement-service>' instead.")
logger.warning("Replacement service: <replacement-service>")
logger.warning("Deprecation date: 2025-01-01")
logger.warning("=" * 80)
```

### 3. HTTP Response Headers

Added middleware to include deprecation headers in all API responses:

```python
@app.middleware("http")
async def add_deprecation_header(request: Request, call_next):
    """Add deprecation headers to all responses"""
    response = await call_next(request)
    response.headers["X-API-Deprecated"] = "true"
    response.headers["X-API-Deprecation-Date"] = "2025-01-01"
    response.headers["X-API-Deprecation-Info"] = "This service is deprecated. Use <replacement> instead."
    response.headers["X-API-Sunset"] = "2025-06-01"
    response.headers["Link"] = '<http://<replacement-service>:<port>>; rel="successor-version"'
    response.headers["Deprecation"] = "true"
    return response
```

### 4. FastAPI Description Updates

Updated the FastAPI app description to include deprecation notice:

```python
app = FastAPI(
    title="...",
    description="⚠️ DEPRECATED - Use <replacement-service> instead. ...",
    ...
)
```

### 5. README Updates

All three services already had deprecation notices at the top of their README.md files:

```markdown
# ⚠️ DEPRECATED - Use <replacement-service> instead

This service has been deprecated and merged into `<replacement-service>`.
Please update your references to use `<replacement-service>` on port <port>.
```

## HTTP Headers Reference

Clients consuming these deprecated services will receive the following HTTP headers with every response:

| Header                   | Value                                                | Description                            |
| ------------------------ | ---------------------------------------------------- | -------------------------------------- |
| `X-API-Deprecated`       | `true`                                               | Indicates the API is deprecated        |
| `X-API-Deprecation-Date` | `2025-01-01`                                         | When the deprecation was announced     |
| `X-API-Deprecation-Info` | Service-specific message                             | Human-readable deprecation message     |
| `X-API-Sunset`           | `2025-06-01`                                         | Expected date when API will be removed |
| `Link`                   | `<http://replacement:port>; rel="successor-version"` | Link to replacement service            |
| `Deprecation`            | `true`                                               | Standard deprecation header (RFC 8594) |

## Migration Guide

### For API Consumers

1. **Check HTTP Headers**: All responses now include deprecation headers. Update your monitoring to detect these.

2. **Update Service URLs**:
   - `weather-advanced` → `weather-service`
   - `crop-health-ai` → `crop-intelligence-service`
   - `satellite-service` → `vegetation-analysis-service`

3. **Timeline**:
   - **Now**: Services are deprecated but fully functional
   - **2025-01-01**: Official deprecation date
   - **2025-06-01**: Target sunset date (services may be removed)

### For Service Operators

1. **Monitor Usage**: Track requests to deprecated services via logs and metrics
2. **Communicate**: Notify stakeholders about the deprecation
3. **Plan Removal**: Schedule removal of deprecated services after sunset date

## Example Response Headers

```http
HTTP/1.1 200 OK
content-type: application/json
x-api-deprecated: true
x-api-deprecation-date: 2025-01-01
x-api-deprecation-info: This service is deprecated. Use weather-service instead.
x-api-sunset: 2025-06-01
link: <http://weather-service:8108>; rel="successor-version"
deprecation: true

{
  "status": "healthy",
  "service": "weather-advanced",
  ...
}
```

## Testing Deprecation Notices

### Test Startup Warnings

```bash
# Start each service and check logs for deprecation warnings
docker-compose logs weather-advanced | grep "DEPRECATION WARNING"
docker-compose logs crop-health-ai | grep "DEPRECATION WARNING"
docker-compose logs satellite-service | grep "DEPRECATION WARNING"
```

### Test HTTP Headers

```bash
# Check response headers include deprecation notices
curl -I http://localhost:8092/healthz | grep -i deprecat
curl -I http://localhost:8095/healthz | grep -i deprecat
curl -I http://localhost:8090/healthz | grep -i deprecat
```

### Test API Documentation

```bash
# Check Swagger docs include deprecation in description
curl http://localhost:8092/docs
curl http://localhost:8095/docs
curl http://localhost:8090/docs
```

## Next Steps

1. **Update Documentation**: Ensure all documentation references the new services
2. **Update Client Libraries**: Update any client libraries or SDKs
3. **Notify Users**: Send deprecation notices to all API consumers
4. **Monitor Migration**: Track usage of deprecated vs new services
5. **Plan Removal**: Schedule actual removal of deprecated services after sunset date

## Related Standards

- [RFC 8594 - The Sunset HTTP Header Field](https://datatracker.ietf.org/doc/html/rfc8594)
- [Deprecation HTTP Header (draft)](https://tools.ietf.org/id/draft-dalal-deprecation-header-01.html)

---

**Implementation Date**: 2025-12-31
**Author**: Claude Code
**Status**: Complete
