# @sahool/nestjs-auth - Package Overview

## Summary

This is a comprehensive, production-ready authentication module for SAHOOL NestJS microservices. It consolidates auth logic from across the platform into a single, reusable package.

## Package Structure

```
@sahool/nestjs-auth/
├── src/
│   ├── auth.module.ts                    # Main module with forRoot() and forRootAsync()
│   ├── index.ts                          # Public API exports
│   │
│   ├── guards/
│   │   ├── jwt.guard.ts                  # 6 guards: JWT, Roles, Permissions, Farm, Optional, Active
│   │   └── token-revocation.guard.ts     # Token revocation guard + interceptor
│   │
│   ├── strategies/
│   │   └── jwt.strategy.ts               # Passport JWT strategy with user validation
│   │
│   ├── services/
│   │   ├── user-validation.service.ts    # User validation with Redis caching
│   │   └── token-revocation.ts           # Redis-based token revocation
│   │
│   ├── decorators/
│   │   └── index.ts                      # 14 custom decorators
│   │
│   ├── config/
│   │   └── jwt.config.ts                 # JWT configuration + error messages
│   │
│   └── interfaces/
│       └── index.ts                      # TypeScript interfaces and types
│
├── README.md                             # Main documentation
├── USAGE_EXAMPLES.md                     # Code examples and patterns
├── MIGRATION_GUIDE.md                    # Migration from custom auth
├── INTEGRATION_EXAMPLE.md                # Complete marketplace-service example
├── CHANGELOG.md                          # Version history
├── package.json                          # NPM package config
├── tsconfig.json                         # TypeScript config
├── .npmignore                            # NPM publish config
└── .gitignore                            # Git ignore rules
```

## Key Features

### 1. Guards (6 types)

- **JwtAuthGuard**: Basic JWT authentication
- **RolesGuard**: Role-based access control
- **PermissionsGuard**: Permission-based access control
- **FarmAccessGuard**: Domain-specific farm access
- **OptionalAuthGuard**: Optional authentication
- **ActiveAccountGuard**: Active account validation

### 2. Decorators (14 types)

- `@Public()` - Mark routes as public
- `@Roles()` - Require specific roles
- `@RequirePermissions()` - Require specific permissions
- `@CurrentUser()` - Get current user
- `@UserId()` - Get user ID
- `@UserRoles()` - Get user roles
- `@TenantId()` - Get tenant ID
- `@UserPermissions()` - Get user permissions
- `@AuthToken()` - Get raw JWT token
- `@RequestLanguage()` - Get language preference
- Plus helper functions: `hasRole()`, `hasAnyRole()`, `hasPermission()`, `hasAnyPermission()`

### 3. Services (2 types)

- **UserValidationService**: Validates users with Redis caching
- **RedisTokenRevocationStore**: Manages token revocation

### 4. Configuration

- Environment-based JWT config
- Support for HS256 and RS256 algorithms
- Configurable token expiration
- Redis configuration
- Rate limiting support

### 5. Documentation

- 5 comprehensive markdown files
- 100+ code examples
- Complete API reference
- Migration guides
- Troubleshooting tips

## Quick Start

### Installation (Workspace)

```bash
# Already available in workspace
cd apps/services/your-service

# Add to package.json
{
  "dependencies": {
    "@sahool/nestjs-auth": "workspace:*"
  }
}

npm install
```

### Basic Usage

```typescript
// app.module.ts
import { AuthModule } from "@sahool/nestjs-auth";

@Module({
  imports: [
    AuthModule.forRoot({
      enableUserValidation: true,
      enableTokenRevocation: true,
    }),
  ],
})
export class AppModule {}

// controller.ts
import { JwtAuthGuard, CurrentUser, UserId } from "@sahool/nestjs-auth";

@Controller("api")
@UseGuards(JwtAuthGuard)
export class ApiController {
  @Get("profile")
  getProfile(@CurrentUser() user: any) {
    return user;
  }
}
```

## Files Summary

### Source Files (10 TypeScript files)

1. `auth.module.ts` (240 lines) - Main module
2. `index.ts` (70 lines) - Public API
3. `guards/jwt.guard.ts` (334 lines) - 6 guards
4. `guards/token-revocation.guard.ts` (268 lines) - Revocation guard
5. `strategies/jwt.strategy.ts` (195 lines) - JWT strategy
6. `services/user-validation.service.ts` (216 lines) - User validation
7. `services/token-revocation.ts` (~500 lines) - Token revocation
8. `decorators/index.ts` (343 lines) - 14 decorators
9. `config/jwt.config.ts` (259 lines) - Configuration
10. `interfaces/index.ts` (6 lines) - Type exports

### Documentation Files (5 files)

1. `README.md` (500+ lines) - Main documentation
2. `USAGE_EXAMPLES.md` (600+ lines) - Code examples
3. `MIGRATION_GUIDE.md` (500+ lines) - Migration guide
4. `INTEGRATION_EXAMPLE.md` (400+ lines) - Complete example
5. `CHANGELOG.md` (100+ lines) - Version history

**Total**: ~4,000 lines of code and documentation

## Comparison: Before vs After

### Before (marketplace-service)

```typescript
// Custom auth guard (100 lines)
src/auth/jwt-auth.guard.ts

// Limited features:
- Basic JWT validation
- Simple user object
- No roles/permissions
- No token revocation
- No user validation
- No caching
```

### After (shared module)

```typescript
// Just import and use
import { AuthModule } from '@sahool/nestjs-auth';

// Full features:
✅ JWT validation (HS256/RS256)
✅ User validation with DB
✅ Redis caching
✅ Token revocation
✅ Role-based access
✅ Permission-based access
✅ Multi-tenant support
✅ 14 custom decorators
✅ 6 guard types
✅ Bilingual errors
✅ Full TypeScript types
✅ Production-ready
```

## Dependencies

### Required Peer Dependencies

- @nestjs/common ^10.0.0
- @nestjs/core ^10.0.0
- @nestjs/jwt ^10.0.0
- @nestjs/passport ^10.0.0
- passport ^0.7.0
- passport-jwt ^4.0.0
- jsonwebtoken ^9.0.0
- ioredis ^5.0.0
- @liaoliaots/nestjs-redis ^9.0.0
- rxjs ^7.0.0

### Why These Dependencies?

- **NestJS**: Core framework
- **Passport**: Authentication middleware
- **JWT**: Token handling
- **Redis**: Caching and revocation
- **RxJS**: Reactive extensions

## Usage Across Services

This module can be used by all NestJS services in the SAHOOL platform:

### Currently Migrated

- ✅ marketplace-service (example provided)

### Can Be Migrated

- 🔄 field-service
- 🔄 alert-service
- 🔄 notification-service
- 🔄 inventory-service
- 🔄 satellite-service
- 🔄 chat-service
- 🔄 billing-core
- 🔄 And 40+ more services...

## Environment Variables

Required `.env` configuration:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_ISSUER=sahool-platform
JWT_AUDIENCE=sahool-api

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Features
TOKEN_REVOCATION_ENABLED=true
```

## Testing

### Unit Tests

```typescript
import { AuthModule } from "@sahool/nestjs-auth";

const module = await Test.createTestingModule({
  imports: [
    AuthModule.forRoot({
      enableUserValidation: false,
      enableTokenRevocation: false,
      validateConfig: false,
    }),
  ],
}).compile();
```

### E2E Tests

```typescript
// Test authentication flow
it("should authenticate with valid token", () => {
  return request(app.getHttpServer())
    .get("/protected")
    .set("Authorization", `Bearer ${validToken}`)
    .expect(200);
});
```

## Security Features

1. **JWT Validation**: Verify token signature, expiration, issuer, audience
2. **User Validation**: Check user exists and is active in database
3. **Token Revocation**: Blacklist compromised tokens
4. **Role-Based Access**: Control access by user roles
5. **Permission-Based Access**: Fine-grained permissions
6. **Active Account Check**: Ensure account is active and verified
7. **Rate Limiting**: Support for rate limiting (configurable)
8. **Audit Logging**: Log authentication attempts
9. **Multi-Tenant**: Tenant isolation support
10. **Secure Defaults**: Secure configuration out of the box

## Performance

- **Redis Caching**: User validation cached for 5 minutes
- **O(1) Lookups**: Redis-based token revocation
- **Lazy Loading**: Services loaded only when needed
- **Async/Await**: Non-blocking operations
- **Connection Pooling**: Efficient Redis connections

## Best Practices

1. ✅ Use environment variables for secrets
2. ✅ Enable user validation in production
3. ✅ Enable token revocation for sensitive apps
4. ✅ Use RS256 in production
5. ✅ Implement user repository interface
6. ✅ Use decorators for clean code
7. ✅ Combine guards for complex access control
8. ✅ Test with auth disabled in unit tests
9. ✅ Use E2E tests for guard behavior
10. ✅ Monitor authentication failures

## Support & Maintenance

### Documentation

- README.md - Getting started
- USAGE_EXAMPLES.md - Code patterns
- MIGRATION_GUIDE.md - Migration help
- INTEGRATION_EXAMPLE.md - Complete example
- CHANGELOG.md - Version history

### Getting Help

1. Check documentation files
2. Review example implementations
3. Check `/shared/auth/` for more examples
4. Contact SAHOOL platform team

## Future Enhancements

Planned features:

- Refresh token support
- Rate limiting middleware
- API key authentication
- OAuth2 support
- Two-factor authentication (2FA)
- Session management
- Audit logging
- RBAC management UI
- GraphQL support
- WebSocket authentication
- Service-to-service auth

## License

MIT

## Contributors

SAHOOL Platform Team

---

**Version**: 1.0.0
**Created**: 2024-12-31
**Status**: Production Ready ✅
