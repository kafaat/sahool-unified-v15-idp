# Migration Guide

This guide helps you migrate existing services to use the shared `@sahool/nestjs-auth` module.

## Table of Contents

1. [Migration from marketplace-service](#migration-from-marketplace-service)
2. [Migration from custom auth implementations](#migration-from-custom-auth-implementations)
3. [Step-by-step migration](#step-by-step-migration)
4. [Common Issues](#common-issues)

## Migration from marketplace-service

The marketplace-service has a simple JWT auth implementation that can be completely replaced with the shared module.

### Before (marketplace-service)

```typescript
// apps/services/marketplace-service/src/auth/jwt-auth.guard.ts
import { Injectable, CanActivate, ExecutionContext, UnauthorizedException } from '@nestjs/common';
import * as jwt from 'jsonwebtoken';

@Injectable()
export class JwtAuthGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const authHeader = request.headers.authorization;

    if (!authHeader) {
      throw new UnauthorizedException('Missing authorization header');
    }

    const [type, token] = authHeader.split(' ');

    if (type !== 'Bearer' || !token) {
      throw new UnauthorizedException('Invalid authorization format');
    }

    try {
      const secret = process.env.JWT_SECRET_KEY || process.env.JWT_SECRET;
      const decoded = jwt.verify(token, secret) as jwt.JwtPayload;

      request.user = {
        id: decoded.sub || decoded.user_id,
        email: decoded.email,
        roles: decoded.roles || [],
        tenantId: decoded.tenant_id,
      };

      return true;
    } catch (error) {
      throw new UnauthorizedException('Authentication failed');
    }
  }
}

// apps/services/marketplace-service/src/app.module.ts
import { JwtAuthGuard, OptionalJwtAuthGuard } from './auth/jwt-auth.guard';

@Module({
  providers: [JwtAuthGuard, OptionalJwtAuthGuard],
})
export class AppModule {}
```

### After (using shared module)

```typescript
// apps/services/marketplace-service/src/app.module.ts
import { Module } from '@nestjs/common';
import { AuthModule } from '@sahool/nestjs-auth';
import { RedisModule } from '@liaoliaots/nestjs-redis';

@Module({
  imports: [
    RedisModule.forRoot({
      config: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379'),
        password: process.env.REDIS_PASSWORD,
      },
    }),
    AuthModule.forRoot({
      enableUserValidation: true,
      enableTokenRevocation: true,
    }),
  ],
  // Remove JwtAuthGuard from providers
})
export class AppModule {}
```

### Update Controllers

**Before:**
```typescript
import { JwtAuthGuard } from './auth/jwt-auth.guard';

@Controller('market')
@UseGuards(JwtAuthGuard)
export class MarketController {
  @Get()
  findAll(@Request() req) {
    const userId = req.user.id;
    return this.marketService.findAll(userId);
  }
}
```

**After:**
```typescript
import { JwtAuthGuard, CurrentUser, UserId } from '@sahool/nestjs-auth';

@Controller('market')
@UseGuards(JwtAuthGuard)
export class MarketController {
  @Get()
  findAll(@UserId() userId: string) {
    return this.marketService.findAll(userId);
  }

  // Or use CurrentUser for full user object
  @Get('user-info')
  getUserInfo(@CurrentUser() user: any) {
    return {
      id: user.id,
      email: user.email,
      roles: user.roles,
      tenantId: user.tenantId,
    };
  }
}
```

### Remove Old Auth Files

```bash
# Delete the old auth guard
rm apps/services/marketplace-service/src/auth/jwt-auth.guard.ts

# Delete auth directory if empty
rmdir apps/services/marketplace-service/src/auth/
```

## Migration from Custom Auth Implementations

If your service has a custom auth implementation, follow these steps:

### Step 1: Identify Current Auth Components

List all auth-related files:
```bash
# Find auth guards
find your-service/src -name "*guard.ts" -o -name "*auth*.ts"

# Find auth modules
find your-service/src -name "*auth*.module.ts"

# Find JWT strategies
find your-service/src -name "*strategy.ts"
```

### Step 2: Map to Shared Module Features

| Your Implementation | Shared Module Equivalent |
|-------------------|-------------------------|
| JWT Guard | `JwtAuthGuard` |
| Roles Guard | `RolesGuard` |
| Permissions Guard | `PermissionsGuard` |
| Optional Auth | `OptionalAuthGuard` |
| JWT Strategy | `JwtStrategy` |
| User Decorator | `@CurrentUser()` |
| Roles Decorator | `@Roles()` |
| Public Decorator | `@Public()` |

### Step 3: Update Dependencies

```bash
# Add Redis module if not already present
npm install @liaoliaots/nestjs-redis ioredis
```

Update `package.json`:
```json
{
  "dependencies": {
    "@sahool/nestjs-auth": "workspace:*",
    "@liaoliaots/nestjs-redis": "^9.0.0",
    "ioredis": "^5.0.0"
  }
}
```

### Step 4: Update Module Imports

**Before:**
```typescript
import { Module } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';
import { PassportModule } from '@nestjs/passport';
import { JwtStrategy } from './auth/jwt.strategy';
import { JwtAuthGuard } from './auth/jwt-auth.guard';

@Module({
  imports: [
    PassportModule.register({ defaultStrategy: 'jwt' }),
    JwtModule.register({
      secret: process.env.JWT_SECRET,
      signOptions: { expiresIn: '1h' },
    }),
  ],
  providers: [JwtStrategy, JwtAuthGuard],
  exports: [JwtStrategy, JwtAuthGuard],
})
export class AuthModule {}
```

**After:**
```typescript
import { Module } from '@nestjs/common';
import { AuthModule } from '@sahool/nestjs-auth';
import { RedisModule } from '@liaoliaots/nestjs-redis';

@Module({
  imports: [
    RedisModule.forRoot({
      config: {
        host: process.env.REDIS_HOST,
        port: parseInt(process.env.REDIS_PORT),
      },
    }),
    AuthModule.forRoot(),
  ],
})
export class AppModule {}
```

### Step 5: Update Imports in Controllers

**Before:**
```typescript
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { RolesGuard } from '../auth/roles.guard';
import { Roles } from '../auth/roles.decorator';
import { User } from '../auth/user.decorator';
```

**After:**
```typescript
import {
  JwtAuthGuard,
  RolesGuard,
  Roles,
  CurrentUser,
} from '@sahool/nestjs-auth';
```

### Step 6: Update Decorator Usage

**Before:**
```typescript
@Get('profile')
getProfile(@User() user) {
  return user;
}
```

**After:**
```typescript
@Get('profile')
getProfile(@CurrentUser() user) {
  return user;
}
```

### Step 7: Clean Up Old Files

```bash
# Remove old auth module
rm -rf src/auth/

# Update imports across the codebase
# Use your IDE's refactoring tools or:
grep -r "from './auth/" src/
grep -r "from '../auth/" src/
```

## Step-by-Step Migration

### For Any Service

#### 1. Install and Configure Redis

```typescript
// src/app.module.ts
import { RedisModule } from '@liaoliaots/nestjs-redis';

@Module({
  imports: [
    RedisModule.forRoot({
      config: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379'),
        password: process.env.REDIS_PASSWORD,
        db: parseInt(process.env.REDIS_DB || '0'),
      },
    }),
  ],
})
```

#### 2. Add Auth Module

```typescript
import { AuthModule } from '@sahool/nestjs-auth';

@Module({
  imports: [
    // ... RedisModule
    AuthModule.forRoot({
      enableUserValidation: true,
      enableTokenRevocation: true,
    }),
  ],
})
```

#### 3. Update Controller Imports

Search and replace in all controller files:

```typescript
// Old
import { JwtAuthGuard } from '../auth/jwt-auth.guard';

// New
import { JwtAuthGuard } from '@sahool/nestjs-auth';
```

#### 4. Update Decorator Usage

```typescript
// Old patterns
@Request() req → req.user.id

// New patterns
@UserId() userId: string
@CurrentUser() user: any
@UserRoles() roles: string[]
@TenantId() tenantId: string
```

#### 5. Implement User Repository (Optional but Recommended)

```typescript
// src/users/user.repository.ts
import { Injectable } from '@nestjs/common';
import { IUserRepository, UserValidationData } from '@sahool/nestjs-auth';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class UserRepository implements IUserRepository {
  constructor(private prisma: PrismaService) {}

  async getUserValidationData(userId: string): Promise<UserValidationData | null> {
    // Implement based on your database schema
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
      select: {
        id: true,
        email: true,
        isActive: true,
        isVerified: true,
        roles: true,
        tenantId: true,
      },
    });

    if (!user) return null;

    return {
      userId: user.id,
      email: user.email,
      isActive: user.isActive,
      isVerified: user.isVerified,
      roles: user.roles,
      tenantId: user.tenantId,
    };
  }

  async updateLastLogin(userId: string): Promise<void> {
    await this.prisma.user.update({
      where: { id: userId },
      data: { lastLoginAt: new Date() },
    });
  }
}

// Update app.module.ts
import { UserRepository } from './users/user.repository';

@Module({
  imports: [
    AuthModule.forRoot({
      userRepository: new UserRepository(prismaService),
    }),
  ],
})
```

#### 6. Test the Migration

```bash
# Run unit tests
npm run test

# Run E2E tests
npm run test:e2e

# Start the service
npm run start:dev

# Test authentication
curl -H "Authorization: Bearer <token>" http://localhost:3000/api/protected
```

#### 7. Remove Old Auth Code

```bash
# Backup first
git add .
git commit -m "Backup before removing old auth code"

# Remove old auth files
rm -rf src/auth/

# Verify no broken imports
npm run build
```

## Common Issues

### Issue 1: Missing Redis Connection

**Error:**
```
Error: Redis connection failed
```

**Solution:**
```typescript
// Ensure Redis is configured
RedisModule.forRoot({
  config: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379'),
  },
})

// Or disable features that require Redis
AuthModule.forRoot({
  enableUserValidation: false,
  enableTokenRevocation: false,
})
```

### Issue 2: JWT Secret Not Found

**Error:**
```
Error: JWT_SECRET must be at least 32 characters
```

**Solution:**
```bash
# Add to .env
JWT_SECRET_KEY=your-secret-key-at-least-32-characters-long
```

### Issue 3: Import Errors

**Error:**
```
Cannot find module '@sahool/nestjs-auth'
```

**Solution:**
```bash
# Ensure the package is in workspace
npm install

# Or link manually
cd packages/nestjs-auth
npm link

cd ../../apps/services/your-service
npm link @sahool/nestjs-auth
```

### Issue 4: User Object Shape Changed

**Error:**
```
Property 'userId' does not exist on type 'User'
```

**Solution:**
The shared module uses consistent user object shape:
```typescript
{
  id: string;           // User ID (use this, not userId)
  roles: string[];
  tenantId?: string;
  permissions: string[];
  tokenId?: string;
}

// Update your code
// Before: user.userId
// After: user.id
```

### Issue 5: Decorators Not Working

**Error:**
```
@CurrentUser() is not a function
```

**Solution:**
```typescript
// Ensure you're importing from the correct location
import { CurrentUser } from '@sahool/nestjs-auth';

// Not from your old auth module
// import { CurrentUser } from './auth/decorators';
```

## Rollback Plan

If you need to rollback:

```bash
# Revert to previous commit
git revert HEAD

# Or restore specific files
git checkout HEAD~1 -- src/auth/

# Reinstall dependencies
npm install
```

## Verification Checklist

After migration, verify:

- [ ] All controllers compile without errors
- [ ] Unit tests pass
- [ ] E2E tests pass
- [ ] Authentication works with valid tokens
- [ ] Invalid tokens are rejected
- [ ] Role-based access works
- [ ] Permission-based access works
- [ ] Public routes are accessible
- [ ] Protected routes require authentication
- [ ] User object has correct shape
- [ ] Redis connection works
- [ ] Token revocation works (if enabled)
- [ ] User validation works (if enabled)

## Support

If you encounter issues during migration:

1. Check the [README.md](./README.md) for configuration options
2. Review [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md) for patterns
3. Compare with marketplace-service migration
4. Check `/shared/auth/` documentation
5. Contact the platform team

## Next Steps

After successful migration:

1. Update service documentation
2. Train team on new auth module
3. Monitor for authentication errors
4. Consider enabling global guard for better security
5. Implement custom user repository for production
6. Enable token revocation for sensitive operations
