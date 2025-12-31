# @sahool/nestjs-auth

Shared authentication module for SAHOOL NestJS microservices. This module provides a comprehensive, production-ready authentication system with JWT support, role-based access control, token revocation, and more.

## Features

- **JWT Authentication** with RS256/HS256 algorithm support
- **Role-Based Access Control (RBAC)** with custom decorators
- **Permission-Based Access Control**
- **Token Revocation** with Redis backend
- **User Validation** with Redis caching for performance
- **Multiple Guard Types** (JWT, Roles, Permissions, Farm Access, Optional Auth, Active Account)
- **Custom Decorators** for easy usage
- **Bilingual Error Messages** (English/Arabic)
- **TypeScript** with full type definitions

## Installation

This is a workspace package, so it's available directly within the monorepo:

```bash
# No installation needed - it's in the workspace
```

For external use, add to `package.json`:

```json
{
  "dependencies": {
    "@sahool/nestjs-auth": "workspace:*"
  }
}
```

## Peer Dependencies

Make sure you have these installed in your service:

```json
{
  "@nestjs/common": "^10.0.0",
  "@nestjs/core": "^10.0.0",
  "@nestjs/jwt": "^10.0.0",
  "@nestjs/passport": "^10.0.0",
  "passport": "^0.7.0",
  "passport-jwt": "^4.0.0",
  "jsonwebtoken": "^9.0.0",
  "ioredis": "^5.0.0",
  "@liaoliaots/nestjs-redis": "^9.0.0",
  "rxjs": "^7.0.0"
}
```

## Quick Start

### 1. Basic Setup

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { AuthModule } from '@sahool/nestjs-auth';

@Module({
  imports: [
    // Simple setup with defaults
    AuthModule.forRoot(),
  ],
})
export class AppModule {}
```

### 2. Setup with User Validation

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { AuthModule } from '@sahool/nestjs-auth';
import { UserRepository } from './users/user.repository';

@Module({
  imports: [
    AuthModule.forRoot({
      enableUserValidation: true,
      userRepository: new UserRepository(),
    }),
  ],
})
export class AppModule {}
```

### 3. Protect Routes with Guards

```typescript
// farms.controller.ts
import { Controller, Get, UseGuards } from '@nestjs/common';
import { JwtAuthGuard, RolesGuard, Roles, CurrentUser } from '@sahool/nestjs-auth';

@Controller('farms')
@UseGuards(JwtAuthGuard, RolesGuard)
export class FarmsController {
  @Get()
  @Roles('farmer', 'admin')
  async findAll(@CurrentUser() user: any) {
    return this.farmsService.findByUser(user.id);
  }
}
```

### 4. Use Decorators

```typescript
import {
  Controller,
  Get,
  Post,
  UseGuards,
} from '@nestjs/common';
import {
  JwtAuthGuard,
  Public,
  CurrentUser,
  UserId,
  UserRoles,
  Roles,
  RequirePermissions,
  PermissionsGuard,
} from '@sahool/nestjs-auth';

@Controller('api')
@UseGuards(JwtAuthGuard)
export class ApiController {
  // Public route (no authentication required)
  @Public()
  @Get('public')
  getPublic() {
    return { message: 'Public data' };
  }

  // Protected route
  @Get('profile')
  getProfile(@CurrentUser() user: any) {
    return user;
  }

  // Get just the user ID
  @Get('me')
  getMe(@UserId() userId: string) {
    return { userId };
  }

  // Role-based access
  @Roles('admin', 'manager')
  @UseGuards(RolesGuard)
  @Get('admin')
  adminOnly(@UserRoles() roles: string[]) {
    return { roles };
  }

  // Permission-based access
  @RequirePermissions('farm:delete')
  @UseGuards(PermissionsGuard)
  @Post('delete-farm')
  deleteFarm() {
    return { deleted: true };
  }
}
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256  # or RS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_ISSUER=sahool-platform
JWT_AUDIENCE=sahool-api

# For RS256 algorithm
JWT_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----
JWT_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----

# Redis Configuration (for user validation and token revocation)
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=optional-password

# Token Revocation
TOKEN_REVOCATION_ENABLED=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
```

### Module Options

```typescript
interface AuthModuleOptions {
  // JWT configuration (optional, uses env vars if not provided)
  jwtOptions?: JwtModuleOptions;

  // Enable user validation service (requires Redis and UserRepository)
  enableUserValidation?: boolean; // default: true

  // Enable token revocation checking (requires Redis)
  enableTokenRevocation?: boolean; // default: true

  // User repository for database lookups
  userRepository?: IUserRepository;

  // Enable global authentication guard
  enableGlobalGuard?: boolean; // default: false

  // Validate JWT config on startup
  validateConfig?: boolean; // default: true
}
```

## Advanced Usage

### Global Authentication Guard

Make all routes protected by default:

```typescript
AuthModule.forRoot({
  enableGlobalGuard: true,
})
```

Then use `@Public()` decorator for public routes:

```typescript
@Controller('auth')
export class AuthController {
  @Public()
  @Post('login')
  login(@Body() credentials: LoginDto) {
    return this.authService.login(credentials);
  }

  @Public()
  @Post('register')
  register(@Body() data: RegisterDto) {
    return this.authService.register(data);
  }
}
```

### Async Configuration

Use async configuration when you need to inject dependencies:

```typescript
import { ConfigModule, ConfigService } from '@nestjs/config';

@Module({
  imports: [
    AuthModule.forRootAsync({
      imports: [ConfigModule],
      useFactory: async (configService: ConfigService) => ({
        jwtOptions: {
          secret: configService.get('JWT_SECRET'),
          signOptions: {
            expiresIn: configService.get('JWT_EXPIRES_IN'),
          },
        },
        enableUserValidation: true,
      }),
      inject: [ConfigService],
    }),
  ],
})
export class AppModule {}
```

### Implementing User Repository

The `IUserRepository` interface needs to be implemented for user validation:

```typescript
import { Injectable } from '@nestjs/common';
import { IUserRepository, UserValidationData } from '@sahool/nestjs-auth';
import { PrismaService } from './prisma.service';

@Injectable()
export class UserRepository implements IUserRepository {
  constructor(private prisma: PrismaService) {}

  async getUserValidationData(userId: string): Promise<UserValidationData | null> {
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
      select: {
        id: true,
        email: true,
        isActive: true,
        isVerified: true,
        roles: true,
        tenantId: true,
        isDeleted: true,
        isSuspended: true,
      },
    });

    if (!user) {
      return null;
    }

    return {
      userId: user.id,
      email: user.email,
      isActive: user.isActive,
      isVerified: user.isVerified,
      roles: user.roles,
      tenantId: user.tenantId,
      isDeleted: user.isDeleted,
      isSuspended: user.isSuspended,
    };
  }

  async updateLastLogin(userId: string): Promise<void> {
    await this.prisma.user.update({
      where: { id: userId },
      data: { lastLoginAt: new Date() },
    });
  }
}
```

### Token Revocation

To use token revocation:

```typescript
import { Injectable } from '@nestjs/common';
import { RedisTokenRevocationStore } from '@sahool/nestjs-auth';

@Injectable()
export class AuthService {
  constructor(
    private revocationStore: RedisTokenRevocationStore,
  ) {}

  async logout(token: string, userId: string) {
    // Revoke specific token
    await this.revocationStore.revokeToken('token-jti', {
      expiresIn: 3600,
      reason: 'User logout',
      userId,
    });
  }

  async logoutAllDevices(userId: string) {
    // Revoke all user tokens
    await this.revocationStore.revokeAllUserTokens(userId, {
      reason: 'Logout all devices',
    });
  }

  async changePassword(userId: string) {
    // Revoke all user tokens after password change
    await this.revocationStore.revokeAllUserTokens(userId, {
      reason: 'Password changed',
    });
  }
}
```

## Available Guards

### JwtAuthGuard
Basic JWT authentication guard. Validates JWT token and attaches user to request.

```typescript
@UseGuards(JwtAuthGuard)
@Get('protected')
getProtected(@CurrentUser() user: any) {
  return user;
}
```

### RolesGuard
Checks if user has required roles. Use with `@Roles()` decorator.

```typescript
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin', 'manager')
@Get('admin')
adminOnly() {
  return { message: 'Admin only' };
}
```

### PermissionsGuard
Checks if user has required permissions. Use with `@RequirePermissions()` decorator.

```typescript
@UseGuards(JwtAuthGuard, PermissionsGuard)
@RequirePermissions('farm:delete', 'farm:write')
@Delete('farm/:id')
deleteFarm(@Param('id') id: string) {
  return this.farmService.delete(id);
}
```

### FarmAccessGuard
Checks if user has access to specific farm (domain-specific guard).

```typescript
@UseGuards(JwtAuthGuard, FarmAccessGuard)
@Get('farms/:farmId/fields')
getFields(@Param('farmId') farmId: string) {
  return this.fieldsService.findByFarm(farmId);
}
```

### OptionalAuthGuard
Allows both authenticated and unauthenticated requests.

```typescript
@UseGuards(OptionalAuthGuard)
@Get('content')
getContent(@CurrentUser() user?: any) {
  if (user) {
    return this.contentService.getPremiumContent();
  }
  return this.contentService.getPublicContent();
}
```

### ActiveAccountGuard
Ensures user account is active and verified.

```typescript
@UseGuards(JwtAuthGuard, ActiveAccountGuard)
@Get('profile')
getProfile(@CurrentUser() user: any) {
  return this.profileService.get(user.id);
}
```

### TokenRevocationGuard
Checks if token has been revoked (use globally or per-route).

```typescript
// Global usage
@Module({
  providers: [
    {
      provide: APP_GUARD,
      useClass: TokenRevocationGuard,
    },
  ],
})

// Per-route usage
@UseGuards(TokenRevocationGuard)
@Get('protected')
getProtected() {
  return { message: 'Protected' };
}
```

## Available Decorators

- `@Public()` - Mark route as public (no authentication)
- `@Roles(...roles)` - Require specific roles
- `@RequirePermissions(...permissions)` - Require specific permissions
- `@CurrentUser(property?)` - Get current user or user property
- `@UserId()` - Get current user ID
- `@UserRoles()` - Get current user roles
- `@TenantId()` - Get current tenant ID
- `@UserPermissions()` - Get current user permissions
- `@AuthToken()` - Get raw JWT token
- `@RequestLanguage()` - Get request language preference
- `@SkipRevocationCheck()` - Skip token revocation check

## Error Messages

All errors are available in English and Arabic:

```typescript
{
  INVALID_TOKEN: {
    en: 'Invalid authentication token',
    ar: 'رمز المصادقة غير صالح',
    code: 'invalid_token'
  },
  EXPIRED_TOKEN: {
    en: 'Authentication token has expired',
    ar: 'انتهت صلاحية رمز المصادقة',
    code: 'expired_token'
  },
  // ... more errors
}
```

## Migration Guide

### From marketplace-service auth

If you're migrating from the marketplace-service implementation:

**Before:**
```typescript
// marketplace-service/src/auth/jwt-auth.guard.ts
import { JwtAuthGuard, OptionalJwtAuthGuard } from './auth/jwt-auth.guard';

@Module({
  providers: [JwtAuthGuard, OptionalJwtAuthGuard],
})
```

**After:**
```typescript
import { AuthModule, JwtAuthGuard, OptionalAuthGuard } from '@sahool/nestjs-auth';

@Module({
  imports: [AuthModule.forRoot()],
})
```

## Testing

```typescript
import { Test } from '@nestjs/testing';
import { AuthModule } from '@sahool/nestjs-auth';

describe('MyService', () => {
  beforeEach(async () => {
    const module = await Test.createTestingModule({
      imports: [
        AuthModule.forRoot({
          enableUserValidation: false,
          enableTokenRevocation: false,
        }),
      ],
      providers: [MyService],
    }).compile();

    service = module.get<MyService>(MyService);
  });

  it('should work', () => {
    expect(service).toBeDefined();
  });
});
```

## Architecture

```
@sahool/nestjs-auth/
├── src/
│   ├── auth.module.ts           # Main module
│   ├── guards/
│   │   ├── jwt.guard.ts         # JWT & RBAC guards
│   │   └── token-revocation.guard.ts
│   ├── strategies/
│   │   └── jwt.strategy.ts      # Passport JWT strategy
│   ├── services/
│   │   ├── user-validation.service.ts
│   │   └── token-revocation.ts
│   ├── decorators/
│   │   └── index.ts             # Custom decorators
│   ├── config/
│   │   └── jwt.config.ts        # Configuration
│   ├── interfaces/
│   │   └── index.ts             # TypeScript interfaces
│   └── index.ts                 # Public API
├── package.json
├── tsconfig.json
└── README.md
```

## Best Practices

1. **Always use environment variables** for secrets
2. **Enable user validation** in production for security
3. **Use role guards** for coarse-grained access control
4. **Use permission guards** for fine-grained access control
5. **Revoke tokens** on logout, password change, and security events
6. **Use RS256** in production for better security
7. **Enable global guard** for better security defaults
8. **Implement proper error handling** in your services

## Support

For issues or questions:
- Check the shared auth documentation in `/shared/auth/`
- Review example implementations in other services
- Contact the SAHOOL platform team

## License

MIT
