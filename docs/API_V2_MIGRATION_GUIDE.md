# API v2 Migration Guide

## Overview

This guide helps you migrate from SAHOOL API v1 to v2. The v2 API introduces several improvements including enhanced response formats, better error handling, improved pagination, and more robust request tracking.

## Timeline

| Date       | Milestone                                      |
| ---------- | ---------------------------------------------- |
| 2025-01-06 | v2 API Released                                |
| 2025-06-30 | v1 API Deprecated (deprecation warnings added) |
| 2026-01-01 | v1 Rate limits reduced                         |
| 2026-06-30 | v1 API Sunset (removed completely)             |

## Breaking Changes

### 1. Base URL Change

```diff
- GET https://api.sahool.app/api/v1/users
+ GET https://api.sahool.app/api/v2/users
```

### 2. Response Format

#### Success Response

**v1:**

```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed"
}
```

**v2:**

```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed",
  "version": "2",
  "timestamp": "2026-01-06T10:30:00Z",
  "meta": {
    "requestId": "req_123456"
  }
}
```

**Required Changes:**

- Update response parsing to handle `version`, `timestamp`, and `meta` fields
- Use `meta.requestId` for request tracing and support tickets

#### Error Response

**v1:**

```json
{
  "success": false,
  "message": "Error occurred"
}
```

**v2:**

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error occurred",
    "details": "Detailed error description",
    "field": "fieldName",
    "timestamp": "2026-01-06T10:30:00Z"
  },
  "version": "2",
  "meta": {
    "requestId": "req_123456",
    "documentation": "https://docs.sahool.app/errors/ERROR_CODE"
  }
}
```

**Required Changes:**

- Update error handling to use `error.code` instead of parsing `message`
- Use `error.field` to identify which field caused the error
- Reference `meta.documentation` for error details

### 3. Pagination

#### Query Parameters

**v1:**

```http
GET /api/v1/users?skip=0&take=20
```

**v2:**

```http
GET /api/v2/users?page=1&limit=20
```

**Required Changes:**

```typescript
// v1
const skip = (page - 1) * pageSize;
const url = `/api/v1/users?skip=${skip}&take=${pageSize}`;

// v2
const url = `/api/v2/users?page=${page}&limit=${pageSize}`;
```

#### Response Format

**v1:**

```json
{
  "success": true,
  "data": [...],
  "count": 100
}
```

**v2:**

```json
{
  "success": true,
  "data": [...],
  "version": "2",
  "timestamp": "2026-01-06T10:30:00Z",
  "meta": {
    "requestId": "req_123456",
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "totalPages": 5,
      "hasNext": true,
      "hasPrev": false
    }
  }
}
```

**Required Changes:**

- Use `meta.pagination.total` instead of `count`
- Use `meta.pagination.hasNext` and `hasPrev` for navigation
- Calculate current page using `meta.pagination.page`

### 4. Sorting

**v2 New Feature:**

```http
GET /api/v2/users?page=1&limit=20&sort=createdAt&order=desc
```

Supported sort orders:

- `asc` - Ascending
- `desc` - Descending

### 5. Date Format

**v1:** Mixed formats (ISO 8601, custom formats)
**v2:** Strict ISO 8601 with timezone

```diff
- "createdAt": "2026-01-06 10:30:00"
+ "createdAt": "2026-01-06T10:30:00Z"
```

**Required Changes:**

```typescript
// Parse dates using ISO 8601
const date = new Date(response.data.createdAt); // Always works in v2
```

### 6. Field Naming

**v2:** Strict camelCase for all JSON properties

```diff
- "user_id": "123"
+ "userId": "123"

- "created_at": "2026-01-06T10:30:00Z"
+ "createdAt": "2026-01-06T10:30:00Z"
```

## Migration Steps

### Step 1: Update Client Library

If using the SAHOOL JavaScript client:

```bash
npm install @sahool/client@latest
```

```typescript
// v1
import { SahoolClient } from "@sahool/client";
const client = new SahoolClient({ version: "v1" });

// v2
import { SahoolClient } from "@sahool/client";
const client = new SahoolClient({ version: "v2" });
```

### Step 2: Update Base URL

```typescript
// v1
const BASE_URL = "https://api.sahool.app/api/v1";

// v2
const BASE_URL = "https://api.sahool.app/api/v2";
```

### Step 3: Update Response Handlers

```typescript
// v1 Response Handler
async function getUsersV1() {
  const response = await fetch(`${BASE_URL}/users`);
  const { success, data, message } = await response.json();

  if (!success) {
    throw new Error(message);
  }

  return data;
}

// v2 Response Handler
async function getUsersV2() {
  const response = await fetch(`${BASE_URL}/users`);
  const { success, data, error, meta } = await response.json();

  if (!success) {
    const err = new Error(error.message);
    err.code = error.code;
    err.field = error.field;
    err.requestId = meta.requestId;
    throw err;
  }

  return data;
}
```

### Step 4: Update Pagination Logic

```typescript
// v1 Pagination
interface V1PaginationParams {
  skip: number;
  take: number;
}

function getV1Users(page: number, pageSize: number) {
  const skip = (page - 1) * pageSize;
  return fetch(`${BASE_URL}/users?skip=${skip}&take=${pageSize}`);
}

// v2 Pagination
interface V2PaginationParams {
  page: number;
  limit: number;
}

function getV2Users(page: number, limit: number) {
  return fetch(`${BASE_URL}/users?page=${page}&limit=${limit}`);
}

// v2 Pagination State Management
interface PaginationState {
  currentPage: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

function handlePaginationResponse(response: V2Response) {
  const pagination: PaginationState = {
    currentPage: response.meta.pagination.page,
    totalPages: response.meta.pagination.totalPages,
    hasNext: response.meta.pagination.hasNext,
    hasPrev: response.meta.pagination.hasPrev,
  };

  return pagination;
}
```

### Step 5: Update Error Handling

```typescript
// v1 Error Handling
try {
  const response = await fetch(`${BASE_URL}/users/123`);
  const { success, message } = await response.json();

  if (!success) {
    // Generic error handling
    alert(message);
  }
} catch (error) {
  console.error(error);
}

// v2 Error Handling
try {
  const response = await fetch(`${BASE_URL}/users/123`);
  const { success, error, meta } = await response.json();

  if (!success) {
    // Structured error handling
    switch (error.code) {
      case "USER_NOT_FOUND":
        alert("User not found");
        break;
      case "UNAUTHORIZED":
        redirectToLogin();
        break;
      case "VALIDATION_ERROR":
        displayFieldError(error.field, error.message);
        break;
      default:
        alert(`Error: ${error.message} (Request ID: ${meta.requestId})`);
    }
  }
} catch (error) {
  console.error("Network error:", error);
}
```

### Step 6: Add Request Tracking

```typescript
// v2: Track requests for support
async function makeRequest(url: string, options: RequestInit = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      // Optional: Send request ID for tracing
      "X-Request-ID": generateRequestId(),
    },
  });

  const data = await response.json();

  // Log request ID for debugging
  console.log("Request ID:", data.meta.requestId);

  // Store request ID for support tickets
  if (!response.ok) {
    localStorage.setItem("lastFailedRequestId", data.meta.requestId);
  }

  return data;
}
```

## Testing Your Migration

### 1. Parallel Testing

Run both v1 and v2 in parallel to verify consistency:

```typescript
async function testMigration() {
  const [v1Response, v2Response] = await Promise.all([
    fetch("https://api.sahool.app/api/v1/users/123"),
    fetch("https://api.sahool.app/api/v2/users/123"),
  ]);

  const v1Data = await v1Response.json();
  const v2Data = await v2Response.json();

  // Compare data (accounting for format differences)
  console.log("v1:", v1Data.data);
  console.log("v2:", v2Data.data);
}
```

### 2. Feature Parity Check

Ensure all v1 features are available in v2:

```typescript
const endpoints = [
  "/users",
  "/fields",
  "/weather",
  "/satellite",
  // ... all your endpoints
];

for (const endpoint of endpoints) {
  const v1 = await fetch(`https://api.sahool.app/api/v1${endpoint}`);
  const v2 = await fetch(`https://api.sahool.app/api/v2${endpoint}`);

  if (v1.ok && !v2.ok) {
    console.error(`Endpoint missing in v2: ${endpoint}`);
  }
}
```

### 3. Load Testing

Test v2 performance before full migration:

```bash
# Using Apache Bench
ab -n 1000 -c 10 https://api.sahool.app/api/v2/users

# Using k6
k6 run load-test-v2.js
```

## Rollback Plan

If you encounter issues during migration:

### 1. Quick Rollback

```typescript
// Use environment variable for easy switching
const API_VERSION = process.env.API_VERSION || "v2";
const BASE_URL = `https://api.sahool.app/api/${API_VERSION}`;
```

### 2. Gradual Rollout

```typescript
// Route percentage of traffic to v2
function getApiVersion() {
  const rolloutPercentage = 10; // Start with 10%
  const random = Math.random() * 100;
  return random < rolloutPercentage ? "v2" : "v1";
}

const version = getApiVersion();
const BASE_URL = `https://api.sahool.app/api/${version}`;
```

### 3. Feature Flags

```typescript
// Use feature flags for gradual migration
const features = {
  useV2Users: true,
  useV2Fields: false,
  useV2Weather: false,
};

const usersUrl = features.useV2Users ? "/api/v2/users" : "/api/v1/users";
```

## Common Issues

### Issue 1: Date Parsing Errors

**Problem:** Dates not parsing correctly

**Solution:**

```typescript
// Always use ISO 8601 parser
const date = new Date(dateString); // Works for ISO 8601

// For v1 dates, convert first
function parseV1Date(dateStr: string) {
  return dateStr.replace(" ", "T") + "Z";
}
```

### Issue 2: Pagination Confusion

**Problem:** Wrong page displayed after migration

**Solution:**

```typescript
// v1 to v2 conversion
function convertV1ToV2Pagination(skip: number, take: number) {
  return {
    page: Math.floor(skip / take) + 1,
    limit: take,
  };
}

// v2 to v1 conversion (if needed for rollback)
function convertV2ToV1Pagination(page: number, limit: number) {
  return {
    skip: (page - 1) * limit,
    take: limit,
  };
}
```

### Issue 3: Error Code Handling

**Problem:** Error messages not displaying correctly

**Solution:**

```typescript
// Create error code mapping
const ERROR_MESSAGES = {
  USER_NOT_FOUND: "المستخدم غير موجود",
  UNAUTHORIZED: "غير مصرح",
  VALIDATION_ERROR: "خطأ في التحقق",
};

function getErrorMessage(errorCode: string) {
  return ERROR_MESSAGES[errorCode] || "حدث خطأ غير متوقع";
}
```

## Support

If you need help with migration:

- Documentation: https://docs.sahool.app/api/v2
- Support Email: support@sahool.app
- Developer Forum: https://community.sahool.app
- Migration Workshop: Contact us to schedule

## Appendix

### Complete Migration Checklist

- [ ] Update base URL to v2
- [ ] Update response format handling
- [ ] Update error handling with error codes
- [ ] Update pagination (skip/take to page/limit)
- [ ] Add sorting parameters where needed
- [ ] Update date parsing to ISO 8601
- [ ] Add request ID tracking
- [ ] Update field names to camelCase
- [ ] Test all endpoints in v2
- [ ] Update documentation
- [ ] Train team on new API
- [ ] Monitor error rates after migration
- [ ] Remove v1 code after sunset date

### Error Code Reference

| Code                | Description                       | HTTP Status |
| ------------------- | --------------------------------- | ----------- |
| USER_NOT_FOUND      | User does not exist               | 404         |
| FIELD_NOT_FOUND     | Field does not exist              | 404         |
| UNAUTHORIZED        | Missing or invalid authentication | 401         |
| FORBIDDEN           | Insufficient permissions          | 403         |
| VALIDATION_ERROR    | Request data validation failed    | 400         |
| RATE_LIMIT_EXCEEDED | Too many requests                 | 429         |
| INTERNAL_ERROR      | Server error                      | 500         |

---

**Last Updated:** 2026-01-06
**Version:** 1.0.0
