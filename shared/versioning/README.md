# API Versioning Utilities

This module provides utilities for implementing API versioning in SAHOOL platform services.

## Overview

The versioning utilities support both URI-based and header-based API versioning with automatic deprecation warnings for older versions.

## Components

### Base Controllers

#### BaseControllerV1
Provides v1-specific response formats and utilities (deprecated).

```typescript
import { Controller } from '@nestjs/common';
import { BaseControllerV1 } from '@sahool/versioning';

@Controller({ path: 'users', version: '1' })
export class UsersV1Controller extends BaseControllerV1 {
  @Get()
  async findAll() {
    this.logDeprecationWarning('/api/v1/users');

    const users = await this.usersService.findAll();

    return this.success(users, 'Users retrieved successfully');
  }
}
```

#### BaseControllerV2
Provides v2-specific response formats and utilities (current).

```typescript
import { Controller, Get } from '@nestjs/common';
import { BaseControllerV2, RequestId } from '@sahool/versioning';

@Controller({ path: 'users', version: '2' })
export class UsersV2Controller extends BaseControllerV2 {
  @Get()
  async findAll(
    @RequestId() requestId: string,
    @Query('page') page?: string,
    @Query('limit') limit?: string,
  ) {
    const { page: p, limit: l, skip } = this.parsePaginationParams(page, limit);

    const [users, total] = await this.usersService.findAllWithCount(skip, l);

    return this.paginated(users, p, l, total, requestId);
  }
}
```

### Decorators

#### @ApiV1 / @ApiV2
Mark controllers with version-specific metadata.

```typescript
import { ApiV1, ApiV2 } from '@sahool/versioning';

@ApiV1('Users')
@Controller({ path: 'users', version: '1' })
export class UsersV1Controller {}

@ApiV2('Users')
@Controller({ path: 'users', version: '2' })
export class UsersV2Controller {}
```

#### @ApiDeprecated
Mark specific methods as deprecated.

```typescript
import { ApiDeprecated } from '@sahool/versioning';

@Get('legacy-endpoint')
@ApiDeprecated('Use /api/v2/users instead', '/api/v2/users')
async legacyEndpoint() {
  // ...
}
```

#### @RequestId
Extract or generate request ID.

```typescript
import { RequestId } from '@sahool/versioning';

@Get()
async findAll(@RequestId() requestId: string) {
  console.log('Request ID:', requestId);
  // ...
}
```

### Interceptors

#### DeprecationInterceptor
Automatically adds deprecation headers to v1 responses.

```typescript
import { Module } from '@nestjs/common';
import { APP_INTERCEPTOR } from '@nestjs/core';
import { DeprecationInterceptor } from '@sahool/versioning';

@Module({
  providers: [
    {
      provide: APP_INTERCEPTOR,
      useClass: DeprecationInterceptor,
    },
  ],
})
export class AppModule {}
```

## Response Formats

### V1 Response Format (Deprecated)

```typescript
{
  "success": true,
  "data": { ... },
  "message": "Operation completed"
}
```

### V2 Response Format (Current)

```typescript
{
  "success": true,
  "data": { ... },
  "message": "Operation completed",
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

## Error Formats

### V1 Error Format (Deprecated)

```typescript
{
  "success": false,
  "message": "Error message"
}
```

### V2 Error Format (Current)

```typescript
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

## Deprecation Headers

When accessing v1 endpoints, the following headers are automatically added:

```http
X-API-Deprecated: true
X-API-Deprecation-Date: 2025-06-30
X-API-Sunset-Date: 2026-06-30
X-API-Deprecation-Info: https://docs.sahool.app/api/deprecation/v1
Link: </api/v2/users>; rel="successor-version"
Warning: 299 - "API version 1 is deprecated and will be removed on 2026-06-30"
```

## Version Negotiation

Version can be specified in multiple ways (in order of priority):

1. **URI Version** (highest priority)
   ```
   GET /api/v2/users
   ```

2. **X-API-Version Header**
   ```http
   GET /api/users
   X-API-Version: 2
   ```

3. **Accept Header**
   ```http
   GET /api/users
   Accept: application/vnd.sahool.v2+json
   ```

4. **Default Version** (lowest priority)
   - Defaults to v2

## Best Practices

1. **Always use base controllers** for consistent response formats
2. **Use RequestId decorator** for request tracing
3. **Log deprecation warnings** when v1 endpoints are accessed
4. **Provide migration paths** in deprecation messages
5. **Test both versions** to ensure backward compatibility

## Migration Example

### Step 1: Create v1 controller (maintain existing behavior)

```typescript
@ApiV1('Users')
@Controller({ path: 'users', version: '1' })
export class UsersV1Controller extends BaseControllerV1 {
  constructor(private usersService: UsersService) {
    super();
  }

  @Get()
  async findAll(
    @Query('skip') skip?: string,
    @Query('take') take?: string,
  ) {
    this.logDeprecationWarning('/api/v1/users');

    const users = await this.usersService.findAll({
      skip: skip ? parseInt(skip) : 0,
      take: take ? parseInt(take) : 20,
    });

    return this.success(users);
  }
}
```

### Step 2: Create v2 controller (with enhancements)

```typescript
@ApiV2('Users')
@Controller({ path: 'users', version: '2' })
export class UsersV2Controller extends BaseControllerV2 {
  constructor(private usersService: UsersService) {
    super();
  }

  @Get()
  async findAll(
    @RequestId() requestId: string,
    @Query('page') page?: string,
    @Query('limit') limit?: string,
    @Query('sort') sort?: string,
    @Query('order') order?: string,
  ) {
    const { page: p, limit: l, skip } = this.parsePaginationParams(page, limit);
    const { field, order: o } = this.parseSortParams(sort, order);

    const [users, total] = await this.usersService.findAllWithCount(
      skip,
      l,
      field,
      o,
    );

    return this.paginated(users, p, l, total, requestId);
  }
}
```

### Step 3: Enable versioning in main.ts

```typescript
import { VersioningType } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.enableVersioning({
    type: VersioningType.URI,
    defaultVersion: '2',
  });

  // ... rest of configuration
}
```

## Testing

### Test v1 response format

```typescript
describe('UsersV1Controller', () => {
  it('should return v1 format', async () => {
    const response = await request(app)
      .get('/api/v1/users')
      .expect(200);

    expect(response.body).toHaveProperty('success');
    expect(response.body).toHaveProperty('data');
    expect(response.headers['x-api-deprecated']).toBe('true');
  });
});
```

### Test v2 response format

```typescript
describe('UsersV2Controller', () => {
  it('should return v2 format', async () => {
    const response = await request(app)
      .get('/api/v2/users')
      .expect(200);

    expect(response.body).toHaveProperty('version', '2');
    expect(response.body).toHaveProperty('meta');
    expect(response.body.meta).toHaveProperty('requestId');
  });
});
```

## Support

For questions or issues, please refer to:
- [API Versioning Strategy](/docs/API_VERSIONING_STRATEGY.md)
- [Migration Guide](/docs/API_V2_MIGRATION_GUIDE.md)
- [SAHOOL Documentation](https://docs.sahool.app)
