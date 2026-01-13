# API Versioning Strategy for SAHOOL Platform

## Overview

This document outlines the comprehensive API versioning strategy for the SAHOOL agricultural platform. The strategy implements both URI-based and header-based versioning to ensure backward compatibility while enabling continuous evolution of the API.

## Version History

| Version | Status     | Release Date | Support End Date | Notes                                              |
| ------- | ---------- | ------------ | ---------------- | -------------------------------------------------- |
| v1      | Deprecated | 2024-01-01   | 2026-06-30       | Legacy version - deprecation warnings active       |
| v2      | Current    | 2026-01-06   | Active           | Enhanced versioning with improved response formats |

## Versioning Strategy

### 1. URI-Based Versioning (Primary)

**Format:** `/api/v{version}/{resource}`

**Examples:**

- `/api/v1/users`
- `/api/v2/users`
- `/api/v1/fields`
- `/api/v2/fields`

**Advantages:**

- Clear and explicit
- Easy to cache
- Simple to understand
- Browser-friendly

### 2. Header-Based Versioning (Secondary)

**Header:** `X-API-Version: {version}`

**Examples:**

```http
GET /api/users HTTP/1.1
Host: api.sahool.app
X-API-Version: 2
Authorization: Bearer <token>
```

**Advantages:**

- Keeps URLs clean
- Flexible for different clients
- Easy to implement content negotiation

### 3. Accept Header Versioning (Alternative)

**Header:** `Accept: application/vnd.sahool.v{version}+json`

**Example:**

```http
GET /api/users HTTP/1.1
Host: api.sahool.app
Accept: application/vnd.sahool.v2+json
Authorization: Bearer <token>
```

## Version Negotiation Priority

1. **URI version** (highest priority) - `/api/v2/users`
2. **X-API-Version header** - `X-API-Version: 2`
3. **Accept header** - `Accept: application/vnd.sahool.v2+json`
4. **Default version** (lowest priority) - Defaults to latest stable (v2)

## API Changes Between Versions

### v1 to v2 Breaking Changes

#### 1. Response Format Standardization

**v1 Response:**

```json
{
  "success": true,
  "data": { ... },
  "message": "User created successfully"
}
```

**v2 Response:**

```json
{
  "success": true,
  "data": { ... },
  "message": "User created successfully",
  "version": "2",
  "timestamp": "2026-01-06T10:30:00Z",
  "meta": {
    "requestId": "req_123456",
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "hasNext": true
    }
  }
}
```

#### 2. Error Format Enhancement

**v1 Error:**

```json
{
  "success": false,
  "message": "User not found"
}
```

**v2 Error:**

```json
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User not found",
    "details": "No user exists with ID: 123",
    "field": "userId",
    "timestamp": "2026-01-06T10:30:00Z"
  },
  "version": "2",
  "meta": {
    "requestId": "req_123456",
    "documentation": "https://docs.sahool.app/errors/USER_NOT_FOUND"
  }
}
```

#### 3. Date Format Standardization

- **v1:** Mixed formats (ISO 8601, custom formats)
- **v2:** Strict ISO 8601 format with timezone (e.g., `2026-01-06T10:30:00Z`)

#### 4. Pagination Enhancement

**v1 Pagination:**

```http
GET /api/v1/users?skip=0&take=20
```

**v2 Pagination:**

```http
GET /api/v2/users?page=1&limit=20&sort=createdAt&order=desc
```

#### 5. Field Naming Conventions

- **v1:** Mixed camelCase and snake_case
- **v2:** Strict camelCase for JSON properties

## Deprecation Strategy

### Deprecation Timeline

1. **Announcement Phase** (0-3 months)
   - Announce deprecation via changelog and documentation
   - Add deprecation warnings in API responses
   - No breaking changes

2. **Warning Phase** (3-12 months)
   - Add `X-API-Deprecated` header to v1 responses
   - Include deprecation notice in API documentation
   - Provide migration guide

3. **Sunset Phase** (12-18 months)
   - Gradually reduce rate limits for deprecated endpoints
   - Send notifications to API consumers
   - Provide sunset date

4. **End-of-Life** (18+ months)
   - Remove deprecated endpoints
   - Return 410 Gone for deprecated endpoints

### Deprecation Headers

**Deprecated Endpoint Response:**

```http
HTTP/1.1 200 OK
X-API-Deprecated: true
X-API-Deprecation-Date: 2025-06-30
X-API-Sunset-Date: 2026-06-30
X-API-Deprecation-Info: https://docs.sahool.app/api/deprecation/v1
Link: </api/v2/users>; rel="successor-version"
```

## Implementation Guidelines

### NestJS Configuration

#### 1. Enable Versioning in main.ts

```typescript
import { VersioningType } from "@nestjs/common";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Enable URI versioning
  app.enableVersioning({
    type: VersioningType.URI,
    defaultVersion: "2",
  });

  // Or enable header versioning
  app.enableVersioning({
    type: VersioningType.HEADER,
    header: "X-API-Version",
    defaultVersion: "2",
  });

  // Or enable multiple versioning types
  app.enableVersioning({
    type: VersioningType.CUSTOM,
    extractor: (request) => {
      // Check URI first
      if (request.url.match(/\/api\/v(\d+)\//)) {
        return request.url.match(/\/api\/v(\d+)\//)[1];
      }
      // Check header
      if (request.headers["x-api-version"]) {
        return request.headers["x-api-version"];
      }
      // Check accept header
      if (request.headers.accept?.includes("vnd.sahool.v")) {
        return request.headers.accept.match(/vnd\.sahool\.v(\d+)/)[1];
      }
      // Default to v2
      return "2";
    },
  });
}
```

#### 2. Version-Specific Controllers

```typescript
// V1 Controller (Deprecated)
@ApiTags("Users (v1 - Deprecated)")
@Controller({ path: "users", version: "1" })
export class UsersV1Controller {
  @Get()
  @ApiDeprecated("Use v2 endpoint instead")
  async findAll() {
    // v1 implementation
  }
}

// V2 Controller (Current)
@ApiTags("Users (v2)")
@Controller({ path: "users", version: "2" })
export class UsersV2Controller {
  @Get()
  async findAll() {
    // v2 implementation
  }
}
```

### Kong API Gateway Configuration

#### Route Configuration

```yaml
services:
  # V1 Service (Deprecated)
  - name: user-service-v1
    url: http://user-service:3020
    tags:
      - v1
      - deprecated
    routes:
      - name: user-service-v1-route
        paths:
          - /api/v1/users
        strip_path: false
    plugins:
      - name: response-transformer
        config:
          add:
            headers:
              - "X-API-Version: 1"
              - "X-API-Deprecated: true"
              - "X-API-Deprecation-Date: 2025-06-30"
              - "X-API-Sunset-Date: 2026-06-30"
              - "X-API-Deprecation-Info: https://docs.sahool.app/api/deprecation/v1"
              - 'Link: </api/v2/users>; rel="successor-version"'
      - name: rate-limiting
        config:
          minute: 50 # Reduced from 100 for deprecated endpoints
          hour: 2000 # Reduced from 5000

  # V2 Service (Current)
  - name: user-service-v2
    url: http://user-service:3020
    tags:
      - v2
      - current
    routes:
      - name: user-service-v2-route
        paths:
          - /api/v2/users
        strip_path: false
    plugins:
      - name: response-transformer
        config:
          add:
            headers:
              - "X-API-Version: 2"
      - name: rate-limiting
        config:
          minute: 100
          hour: 5000
```

## Migration Guide

### For API Consumers

#### Step 1: Update Base URL

```diff
- const BASE_URL = 'https://api.sahool.app/api/v1';
+ const BASE_URL = 'https://api.sahool.app/api/v2';
```

#### Step 2: Update Response Handling

```typescript
// v1
const response = await fetch("/api/v1/users");
const { success, data, message } = await response.json();

// v2
const response = await fetch("/api/v2/users");
const { success, data, message, version, meta } = await response.json();
```

#### Step 3: Update Error Handling

```typescript
// v1
if (!response.ok) {
  const { success, message } = await response.json();
  throw new Error(message);
}

// v2
if (!response.ok) {
  const { error, meta } = await response.json();
  throw new Error(
    `${error.code}: ${error.message} (RequestId: ${meta.requestId})`,
  );
}
```

### For Service Developers

#### Step 1: Create v2 Controller

1. Duplicate existing controller
2. Update version in decorator
3. Implement v2-specific changes
4. Add deprecation warnings to v1 controller

#### Step 2: Update DTOs

1. Create versioned DTOs (e.g., `CreateUserV2Dto`)
2. Update validation rules
3. Add API schema decorators

#### Step 3: Test Both Versions

1. Maintain test suites for both versions
2. Add integration tests for version negotiation
3. Test deprecation warnings

## Best Practices

### 1. Backward Compatibility

- Never break existing v1 endpoints
- Add new fields as optional in v1
- Use feature flags for gradual rollout

### 2. Documentation

- Maintain separate API docs for each version
- Highlight differences between versions
- Provide migration examples

### 3. Monitoring

- Track version usage metrics
- Monitor deprecation warnings
- Alert on high v1 usage near sunset date

### 4. Communication

- Announce changes via changelog
- Email API consumers about deprecations
- Provide migration support

## Testing Strategy

### Unit Tests

```typescript
describe("UserController v2", () => {
  it("should return v2 response format", async () => {
    const response = await request(app).get("/api/v2/users").expect(200);

    expect(response.body).toHaveProperty("version", "2");
    expect(response.body).toHaveProperty("meta");
    expect(response.body.meta).toHaveProperty("requestId");
  });
});
```

### Integration Tests

```typescript
describe("Version Negotiation", () => {
  it("should use URI version over header version", async () => {
    const response = await request(app)
      .get("/api/v1/users")
      .set("X-API-Version", "2")
      .expect(200);

    expect(response.headers["x-api-version"]).toBe("1");
    expect(response.headers["x-api-deprecated"]).toBe("true");
  });
});
```

## Monitoring and Metrics

### Key Metrics to Track

1. **Version Distribution**
   - Percentage of requests per version
   - Trend over time

2. **Deprecation Impact**
   - Number of consumers using deprecated endpoints
   - Rate of migration to v2

3. **Error Rates**
   - Compare error rates between versions
   - Track migration-related issues

4. **Performance**
   - Response time comparison
   - Resource usage per version

## References

- [NestJS Versioning Documentation](https://docs.nestjs.com/techniques/versioning)
- [REST API Versioning Best Practices](https://www.restapitutorial.com/lessons/versioning.html)
- [Semantic Versioning](https://semver.org/)

## Appendix

### Supported HTTP Methods by Version

| Endpoint | v1 Methods             | v2 Methods                    |
| -------- | ---------------------- | ----------------------------- |
| /users   | GET, POST, PUT, DELETE | GET, POST, PUT, PATCH, DELETE |
| /fields  | GET, POST, PUT, DELETE | GET, POST, PUT, PATCH, DELETE |
| /weather | GET                    | GET, POST                     |

### Response Time SLA

| Version | Target P50 | Target P95 | Target P99 |
| ------- | ---------- | ---------- | ---------- |
| v1      | 100ms      | 500ms      | 1000ms     |
| v2      | 80ms       | 400ms      | 800ms      |

---

**Document Version:** 1.0.0
**Last Updated:** 2026-01-06
**Next Review:** 2026-04-06
