# API Versioning Quick Reference

## Quick Start

### 1. Enable Versioning in Your Service

**File:** `src/main.ts`

```typescript
import { VersioningType } from '@nestjs/common';

app.enableVersioning({
  type: VersioningType.URI,
  defaultVersion: '2',
});
```

### 2. Create v2 Controller

**File:** `src/users/users.v2.controller.ts`

```typescript
import { Controller, Get, Query } from '@nestjs/common';
import { BaseControllerV2, ApiV2, RequestId } from '@sahool/versioning';

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
  ) {
    const { page: p, limit: l, skip } = this.parsePaginationParams(page, limit);
    const [users, total] = await this.usersService.findAllWithCount(skip, l);
    return this.paginated(users, p, l, total, requestId);
  }
}
```

### 3. Add Deprecation to v1 Controller (Optional)

**File:** `src/users/users.v1.controller.ts`

```typescript
import { Controller, Get, UseInterceptors } from '@nestjs/common';
import { BaseControllerV1, ApiV1, DeprecationInterceptor } from '@sahool/versioning';

@ApiV1('Users')
@Controller({ path: 'users', version: '1' })
@UseInterceptors(DeprecationInterceptor)
export class UsersV1Controller extends BaseControllerV1 {
  @Get()
  async findAll() {
    this.logDeprecationWarning('GET /api/v1/users');
    const users = await this.usersService.findAll();
    return this.success(users);
  }
}
```

## API Endpoint URLs

### v1 (Deprecated)
```
GET  /api/v1/users
POST /api/v1/users
GET  /api/v1/users/:id
PUT  /api/v1/users/:id
DELETE /api/v1/users/:id
```

### v2 (Current)
```
GET  /api/v2/users
POST /api/v2/users
GET  /api/v2/users/:id
PUT  /api/v2/users/:id
PATCH /api/v2/users/:id
DELETE /api/v2/users/:id
```

## Response Formats

### v1 Success Response
```json
{
  "success": true,
  "data": {...}
}
```

### v2 Success Response
```json
{
  "success": true,
  "data": {...},
  "version": "2",
  "timestamp": "2026-01-06T10:30:00Z",
  "meta": {
    "requestId": "req_123456"
  }
}
```

### v1 Error Response
```json
{
  "success": false,
  "message": "Error message"
}
```

### v2 Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message",
    "details": "Details",
    "timestamp": "2026-01-06T10:30:00Z"
  },
  "version": "2",
  "meta": {
    "requestId": "req_123456",
    "documentation": "https://docs.sahool.app/errors/ERROR_CODE"
  }
}
```

## Pagination

### v1 Pagination
```typescript
// Request
GET /api/v1/users?skip=0&take=20

// Response
{
  "success": true,
  "data": [...],
  "count": 100
}
```

### v2 Pagination
```typescript
// Request
GET /api/v2/users?page=1&limit=20&sort=createdAt&order=desc

// Response
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

## Base Controller Methods

### BaseControllerV1

```typescript
// Success response
this.success(data, message?)

// Error response
this.error(message, error?)

// Paginated response
this.paginated(data, { skip, take, count }, message?)

// Log deprecation
this.logDeprecationWarning(endpoint)
```

### BaseControllerV2

```typescript
// Success response
this.success(data, requestId, message?, meta?)

// Error response
this.error(code, message, requestId, details?, field?)

// Paginated response
this.paginated(data, page, limit, total, requestId, message?)

// Parse pagination
this.parsePaginationParams(page?, limit?)
// Returns: { page, limit, skip }

// Parse sorting
this.parseSortParams(sort?, order?)
// Returns: { field, order }

// Calculate skip
this.calculateSkip(page, limit)
```

## Common Patterns

### Simple GET Endpoint

```typescript
@Get(':id')
async findOne(
  @Param('id') id: string,
  @RequestId() requestId: string,
) {
  const user = await this.usersService.findOne(id);

  if (!user) {
    return this.error('USER_NOT_FOUND', 'User not found', requestId);
  }

  return this.success(user, requestId);
}
```

### Paginated List

```typescript
@Get()
async findAll(
  @RequestId() requestId: string,
  @Query('page') page?: string,
  @Query('limit') limit?: string,
) {
  const { page: p, limit: l, skip } = this.parsePaginationParams(page, limit);
  const [items, total] = await this.service.findAllWithCount(skip, l);
  return this.paginated(items, p, l, total, requestId);
}
```

### Create Endpoint

```typescript
@Post()
async create(
  @Body() createDto: CreateDto,
  @RequestId() requestId: string,
) {
  const item = await this.service.create(createDto);
  return this.success(item, requestId, 'Created successfully');
}
```

### Update Endpoint

```typescript
@Patch(':id')
async update(
  @Param('id') id: string,
  @Body() updateDto: UpdateDto,
  @RequestId() requestId: string,
) {
  const item = await this.service.update(id, updateDto);

  if (!item) {
    return this.error('NOT_FOUND', 'Item not found', requestId);
  }

  return this.success(item, requestId, 'Updated successfully');
}
```

## Decorators

### @ApiV1 / @ApiV2
```typescript
@ApiV1('ResourceName')  // For v1 controllers
@ApiV2('ResourceName')  // For v2 controllers
```

### @RequestId
```typescript
async method(@RequestId() requestId: string) {
  // requestId is automatically extracted or generated
}
```

### @ApiDeprecated
```typescript
@ApiDeprecated('Reason', '/api/v2/alternative')
```

## Version Negotiation

### Priority Order
1. **URI Version** (Highest)
   ```
   GET /api/v2/users
   ```

2. **X-API-Version Header**
   ```
   GET /api/users
   X-API-Version: 2
   ```

3. **Accept Header**
   ```
   GET /api/users
   Accept: application/vnd.sahool.v2+json
   ```

4. **Default Version** (v2)

## Testing

### cURL Examples

```bash
# Test v2 endpoint
curl https://api.sahool.app/api/v2/users

# Test v1 endpoint (with deprecation headers)
curl -I https://api.sahool.app/api/v1/users

# Test header versioning
curl -H "X-API-Version: 2" https://api.sahool.app/api/users

# Test pagination
curl "https://api.sahool.app/api/v2/users?page=1&limit=10"

# Test sorting
curl "https://api.sahool.app/api/v2/users?sort=createdAt&order=desc"
```

### Unit Test Example

```typescript
describe('UsersV2Controller', () => {
  it('should return v2 format', async () => {
    const response = await controller.findAll('req_123', '1', '20');

    expect(response).toHaveProperty('version', '2');
    expect(response).toHaveProperty('timestamp');
    expect(response.meta).toHaveProperty('requestId', 'req_123');
    expect(response.meta.pagination).toBeDefined();
  });
});
```

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `USER_NOT_FOUND` | User does not exist | 404 |
| `FIELD_NOT_FOUND` | Field does not exist | 404 |
| `UNAUTHORIZED` | Missing/invalid auth | 401 |
| `FORBIDDEN` | Insufficient permissions | 403 |
| `VALIDATION_ERROR` | Invalid request data | 400 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `INTERNAL_ERROR` | Server error | 500 |

## Deprecation Timeline

| Date | Event |
|------|-------|
| 2025-01-06 | v2 Released |
| 2025-06-30 | v1 Deprecated |
| 2026-01-01 | v1 Rate limits reduced |
| 2026-06-30 | v1 Removed (Sunset) |

## Kong Configuration

### v2 Route Example
```yaml
- name: service-v2
  url: http://service:3000
  tags: [v2, current]
  routes:
    - name: service-v2-route
      paths: [/api/v2/resource]
      strip_path: false
  plugins:
    - name: response-transformer
      config:
        add:
          headers:
            - "X-API-Version: 2"
```

### v1 Route with Deprecation
```yaml
- name: service-v1
  url: http://service:3000
  tags: [v1, deprecated]
  routes:
    - name: service-v1-route
      paths: [/api/v1/resource]
      strip_path: false
  plugins:
    - name: response-transformer
      config:
        add:
          headers:
            - "X-API-Deprecated: true"
            - "X-API-Sunset-Date: 2026-06-30"
            - "Link: </api/v2/resource>; rel=\"successor-version\""
    - name: rate-limiting
      config:
        minute: 50  # Reduced from 100
```

## Common Issues

### Issue: Request ID not showing

**Solution:**
```typescript
// Make sure to use @RequestId() decorator
async findAll(@RequestId() requestId: string) { ... }
```

### Issue: Pagination not working

**Solution:**
```typescript
// Use parsePaginationParams helper
const { page, limit, skip } = this.parsePaginationParams(page, limit);
```

### Issue: Deprecation headers not appearing

**Solution:**
```typescript
// Add DeprecationInterceptor to module
@Module({
  providers: [
    {
      provide: APP_INTERCEPTOR,
      useClass: DeprecationInterceptor,
    },
  ],
})
```

## Resources

- **Strategy:** `/docs/API_VERSIONING_STRATEGY.md`
- **Migration Guide:** `/docs/API_V2_MIGRATION_GUIDE.md`
- **Examples:** `/docs/examples/versioning/`
- **Utilities:** `/shared/versioning/`

## Support

- Documentation: https://docs.sahool.app/api/v2
- Email: support@sahool.app
- Forum: https://community.sahool.app

---

**Last Updated:** 2026-01-06
**Version:** 1.0.0
