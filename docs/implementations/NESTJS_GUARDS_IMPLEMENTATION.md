# NestJS Guards Implementation - SAHOOL Platform

## Overview

This document provides a comprehensive overview of NestJS guards implementation across all SAHOOL microservices. The platform uses a multi-layered security approach with various guards for authentication, authorization, and rate limiting.

## Table of Contents

1. [Guard Types](#guard-types)
2. [Service Coverage](#service-coverage)
3. [Implementation Guide](#implementation-guide)
4. [Usage Examples](#usage-examples)
5. [Best Practices](#best-practices)
6. [Testing Guards](#testing-guards)

---

## Guard Types

### 1. Rate Limiting Guards

**ThrottlerGuard** - Prevents API abuse and DDoS attacks

- **Location**: `@nestjs/throttler`
- **Configuration**: Global in all services
- **Purpose**: Rate limiting based on IP and user

**Configuration:**

```typescript
ThrottlerModule.forRoot([
  {
    name: "short",
    ttl: 1000, // 1 second
    limit: 10, // 10 requests per second
  },
  {
    name: "medium",
    ttl: 60000, // 1 minute
    limit: 100, // 100 requests per minute
  },
  {
    name: "long",
    ttl: 3600000, // 1 hour
    limit: 1000, // 1000 requests per hour
  },
]);
```

### 2. Authentication Guards

**JwtAuthGuard** - Validates JWT tokens

- **Location**: `@sahool/nestjs-auth/guards/jwt.guard`
- **Features**:
  - Extends Passport JWT guard
  - Supports @Public() decorator for public routes
  - Detailed logging of authentication failures
  - Custom error messages (English/Arabic)

**TokenRevocationGuard** - Checks token revocation status

- **Location**: `@sahool/nestjs-auth/guards/token-revocation.guard`
- **Features**:
  - Redis-backed token blacklist
  - Automatic cleanup of expired tokens
  - Skip revocation check with decorator
  - User-level and token-level revocation

**OptionalAuthGuard** - Optional authentication

- **Location**: `@sahool/nestjs-auth/guards/jwt.guard`
- **Purpose**: Routes that work with or without authentication
- **Use Case**: Public content with premium features for authenticated users

**ActiveAccountGuard** - Ensures active user accounts

- **Location**: `@sahool/nestjs-auth/guards/jwt.guard`
- **Checks**:
  - User account is active
  - User account is verified
  - User has not been suspended

### 3. Authorization Guards

**RolesGuard** - Role-based access control (RBAC)

- **Location**: `@sahool/nestjs-auth/guards/jwt.guard`
- **Purpose**: Check if user has required roles
- **Decorator**: `@Roles('admin', 'manager')`

**PermissionsGuard** - Fine-grained permissions

- **Location**: `@sahool/nestjs-auth/guards/jwt.guard`
- **Purpose**: Check if user has specific permissions
- **Decorator**: `@RequirePermissions('farm:delete', 'farm:write')`

**FarmAccessGuard** - Farm-specific access control

- **Location**: `@sahool/nestjs-auth/guards/jwt.guard`
- **Purpose**: Ensure user has access to specific farm
- **Features**:
  - Admin users bypass check
  - Validates farm ownership
  - Checks farmIds in user object

### 4. Service-to-Service Guards

**ServiceAuthGuard** - Inter-service authentication

- **Location**: `shared/auth/service-auth.guard.ts`
- **Purpose**: Verify service tokens for inter-service calls
- **Features**:
  - Service name validation
  - Target service verification
  - Allowed services whitelist

---

## Service Coverage

### Summary Table

| Service                  | ThrottlerGuard | JwtAuthGuard | RolesGuard   | PermissionsGuard | TokenRevocationGuard | Status |
| ------------------------ | -------------- | ------------ | ------------ | ---------------- | -------------------- | ------ |
| chat-service             | ✅ Global      | ⚠️ Per-route | ❌           | ❌               | ❌                   | B+     |
| user-service             | ✅ Global      | ⚠️ Per-route | ⚠️ Available | ⚠️ Available     | ✅ Global            | A      |
| marketplace-service      | ✅ Global      | ⚠️ Per-route | ⚠️ Available | ⚠️ Available     | ❌                   | B+     |
| iot-service              | ✅ Global      | ⚠️ Per-route | ❌           | ❌               | ❌                   | B+     |
| disaster-assessment      | ✅ Global      | ⚠️ Per-route | ❌           | ❌               | ❌                   | B+     |
| research-core            | ✅ Global      | ⚠️ Per-route | ❌           | ❌               | ❌                   | B+     |
| crop-growth-model        | ✅ Global      | ❌           | ❌           | ❌               | ❌                   | B      |
| yield-prediction-service | ✅ Global      | ❌           | ❌           | ❌               | ❌                   | B      |
| lai-estimation           | ❓             | ❌           | ❌           | ❌               | ❌                   | C      |

**Legend:**

- ✅ Implemented and configured
- ⚠️ Available but needs more usage
- ❌ Not implemented
- ❓ Unknown/needs verification

### Detailed Service Analysis

#### ✅ Excellent Coverage (A Grade)

**user-service** - Full authentication stack

```typescript
// Global guards configured in app.module.ts
providers: [
  {
    provide: APP_GUARD,
    useClass: ThrottlerGuard,
  },
  {
    provide: APP_GUARD,
    useClass: TokenRevocationGuard,
  },
];
```

#### ⚠️ Good Coverage (B+ Grade)

**chat-service, marketplace-service, iot-service, disaster-assessment, research-core**

These services have:

- ✅ ThrottlerGuard globally configured
- ✅ JwtAuthGuard used on protected routes
- ⚠️ Missing RolesGuard and PermissionsGuard on admin routes
- ⚠️ Missing TokenRevocationGuard

**Recommendation:** Add TokenRevocationGuard globally and use RolesGuard on admin endpoints.

#### ⚠️ Moderate Coverage (B Grade)

**crop-growth-model, yield-prediction-service**

These services have:

- ✅ ThrottlerGuard globally configured
- ❌ No authentication guards (may be internal services)

**Recommendation:** If these services are exposed externally, add JwtAuthGuard. If internal-only, add ServiceAuthGuard.

---

## Implementation Guide

### Step 1: Install Dependencies

```bash
npm install @nestjs/passport passport-jwt @nestjs/jwt @nestjs/throttler
npm install @sahool/nestjs-auth  # Internal package
```

### Step 2: Configure Module

```typescript
// app.module.ts
import { Module } from "@nestjs/common";
import { APP_GUARD } from "@nestjs/core";
import { ThrottlerModule, ThrottlerGuard } from "@nestjs/throttler";
import { JwtModule } from "@nestjs/jwt";
import { PassportModule } from "@nestjs/passport";

// Import from shared package
import {
  JwtAuthGuard,
  RolesGuard,
  PermissionsGuard,
  TokenRevocationGuard,
  JWTConfig,
} from "@sahool/nestjs-auth";

@Module({
  imports: [
    // Passport configuration
    PassportModule.register({ defaultStrategy: "jwt" }),

    // JWT configuration
    JwtModule.register({
      secret: JWTConfig.getVerificationKey(),
      signOptions: {
        expiresIn: JWTConfig.ACCESS_TOKEN_EXPIRY,
      },
    }),

    // Rate limiting
    ThrottlerModule.forRoot([
      {
        name: "short",
        ttl: 1000,
        limit: 10,
      },
      {
        name: "medium",
        ttl: 60000,
        limit: 100,
      },
      {
        name: "long",
        ttl: 3600000,
        limit: 1000,
      },
    ]),
  ],
  providers: [
    // Global ThrottlerGuard
    {
      provide: APP_GUARD,
      useClass: ThrottlerGuard,
    },
    // Optional: Global TokenRevocationGuard
    {
      provide: APP_GUARD,
      useClass: TokenRevocationGuard,
    },
    // Note: DON'T add JwtAuthGuard, RolesGuard, or PermissionsGuard globally
    // Use them per-route instead
  ],
})
export class AppModule {}
```

### Step 3: Apply Guards to Controllers

```typescript
import { Controller, Get, Post, UseGuards } from "@nestjs/common";
import {
  JwtAuthGuard,
  RolesGuard,
  PermissionsGuard,
  Roles,
  RequirePermissions,
  Public,
  CurrentUser,
  UserId,
} from "@sahool/nestjs-auth";
import { Throttle } from "@nestjs/throttler";

@Controller("farms")
export class FarmsController {
  // Public route - no authentication required
  @Public()
  @Get("public")
  getPublicFarms() {
    return this.farmsService.getPublicFarms();
  }

  // Authenticated route
  @Get()
  @UseGuards(JwtAuthGuard)
  getUserFarms(@UserId() userId: string) {
    return this.farmsService.findByUser(userId);
  }

  // Role-based access
  @Get("all")
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles("admin", "manager")
  getAllFarms() {
    return this.farmsService.findAll();
  }

  // Permission-based access
  @Delete(":id")
  @UseGuards(JwtAuthGuard, PermissionsGuard)
  @RequirePermissions("farm:delete")
  deleteFarm(@Param("id") id: string) {
    return this.farmsService.delete(id);
  }

  // Custom rate limiting
  @Post("bulk-import")
  @Throttle({ default: { limit: 3, ttl: 60000 } }) // 3 per minute
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles("admin")
  bulkImport(@Body() data: any) {
    return this.farmsService.bulkImport(data);
  }

  // Get current user info
  @Get("profile")
  @UseGuards(JwtAuthGuard)
  getProfile(@CurrentUser() user: any) {
    return {
      id: user.id,
      email: user.email,
      roles: user.roles,
    };
  }
}
```

---

## Usage Examples

### Example 1: Authentication Controller

```typescript
import { Controller, Post, Body, UseGuards } from "@nestjs/common";
import { JwtAuthGuard, Public, CurrentUser } from "@sahool/nestjs-auth";
import { Throttle, SkipThrottle } from "@nestjs/throttler";

@Controller("auth")
export class AuthController {
  // Public login endpoint with strict rate limiting
  @Public()
  @Post("login")
  @Throttle({ default: { limit: 5, ttl: 60000 } }) // 5 per minute
  async login(@Body() credentials: LoginDto) {
    return this.authService.login(credentials);
  }

  // Public registration with moderate rate limiting
  @Public()
  @Post("register")
  @Throttle({ default: { limit: 10, ttl: 60000 } }) // 10 per minute
  async register(@Body() userData: RegisterDto) {
    return this.authService.register(userData);
  }

  // Logout - no rate limiting needed
  @Post("logout")
  @UseGuards(JwtAuthGuard)
  @SkipThrottle()
  async logout(@CurrentUser() user: any) {
    return this.authService.logout(user.id);
  }

  // Protected endpoint to get current user
  @Get("me")
  @UseGuards(JwtAuthGuard)
  getCurrentUser(@CurrentUser() user: any) {
    return user;
  }
}
```

### Example 2: Admin Controller

```typescript
import { Controller, Get, Post, Put, Delete, UseGuards } from "@nestjs/common";
import {
  JwtAuthGuard,
  RolesGuard,
  PermissionsGuard,
  Roles,
  RequirePermissions,
  CurrentUser,
  UserRoles,
} from "@sahool/nestjs-auth";

@Controller("admin")
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles("admin") // All routes require admin role
export class AdminController {
  // Admin dashboard
  @Get("dashboard")
  getDashboard(@UserRoles() roles: string[]) {
    return this.adminService.getDashboard(roles);
  }

  // View all users (admin only)
  @Get("users")
  getAllUsers() {
    return this.adminService.getAllUsers();
  }

  // Delete user (requires specific permission)
  @Delete("users/:id")
  @UseGuards(PermissionsGuard)
  @RequirePermissions("user:delete")
  deleteUser(@Param("id") id: string) {
    return this.adminService.deleteUser(id);
  }

  // System settings (super admin only)
  @Put("settings")
  @Roles("super_admin") // Override to require super_admin
  updateSettings(@Body() settings: any) {
    return this.adminService.updateSettings(settings);
  }
}
```

### Example 3: Marketplace Controller with Fine-Grained Permissions

```typescript
import { Controller, Get, Post, Put, Delete, UseGuards } from "@nestjs/common";
import {
  JwtAuthGuard,
  RolesGuard,
  PermissionsGuard,
  OptionalAuthGuard,
  Roles,
  RequirePermissions,
  CurrentUser,
  Public,
} from "@sahool/nestjs-auth";

@Controller("market")
export class MarketController {
  // Public product listing
  @Get("products")
  @Public()
  getProducts() {
    return this.marketService.getProducts();
  }

  // Create product (sellers only)
  @Post("products")
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles("seller", "admin")
  createProduct(@Body() product: CreateProductDto, @CurrentUser() user: any) {
    return this.marketService.createProduct(product, user.id);
  }

  // Update product (owner or admin)
  @Put("products/:id")
  @UseGuards(JwtAuthGuard, PermissionsGuard)
  @RequirePermissions("product:write")
  updateProduct(
    @Param("id") id: string,
    @Body() product: UpdateProductDto,
    @CurrentUser() user: any,
  ) {
    return this.marketService.updateProduct(id, product, user.id);
  }

  // Delete product (admin only)
  @Delete("products/:id")
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles("admin")
  deleteProduct(@Param("id") id: string) {
    return this.marketService.deleteProduct(id);
  }

  // View orders (authenticated or not, different data)
  @Get("orders")
  @UseGuards(OptionalAuthGuard)
  getOrders(@CurrentUser() user?: any) {
    if (user) {
      return this.marketService.getUserOrders(user.id);
    }
    return this.marketService.getPublicOrders();
  }

  // Verify seller (admin only with specific permission)
  @Post("sellers/:id/verify")
  @UseGuards(JwtAuthGuard, RolesGuard, PermissionsGuard)
  @Roles("admin")
  @RequirePermissions("seller:verify")
  verifySeller(@Param("id") id: string) {
    return this.marketService.verifySeller(id);
  }
}
```

### Example 4: IoT Service with Service-to-Service Auth

```typescript
import { Controller, Get, Post, UseGuards } from "@nestjs/common";
import { JwtAuthGuard } from "@sahool/nestjs-auth";
import {
  ServiceAuthGuard,
  AllowedServices,
  CallingService,
} from "../../../shared/auth/service-auth.guard";

@Controller("iot")
export class IotController {
  // User-facing endpoint
  @Get("devices")
  @UseGuards(JwtAuthGuard)
  getUserDevices(@CurrentUser() user: any) {
    return this.iotService.getDevicesByUser(user.id);
  }

  // Internal endpoint - only accessible by specific services
  @Post("internal/readings")
  @UseGuards(ServiceAuthGuard)
  @AllowedServices("field-service", "crop-service")
  async submitReadings(
    @Body() readings: any,
    @CallingService() serviceName: string,
  ) {
    console.log(`Readings submitted by: ${serviceName}`);
    return this.iotService.saveReadings(readings);
  }
}
```

---

## Best Practices

### 1. Guard Order Matters

Always apply guards in this order:

1. **ThrottlerGuard** (global) - Rate limiting first
2. **JwtAuthGuard** - Authentication
3. **RolesGuard** or **PermissionsGuard** - Authorization
4. **Custom Guards** - Business logic guards

```typescript
@UseGuards(JwtAuthGuard, RolesGuard, CustomGuard)
@Roles('admin')
```

### 2. Use Global Guards Wisely

**Do apply globally:**

- ✅ ThrottlerGuard
- ✅ TokenRevocationGuard (for services with authentication)

**Don't apply globally:**

- ❌ JwtAuthGuard (use @Public() decorator instead)
- ❌ RolesGuard (not all routes need role checks)
- ❌ PermissionsGuard (too fine-grained for global use)

### 3. Decorators for Better Code

Use decorators to extract user information:

```typescript
// Instead of this:
@Get()
@UseGuards(JwtAuthGuard)
getProfile(@Request() req) {
  const userId = req.user.id;
  const roles = req.user.roles;
  return this.service.getProfile(userId, roles);
}

// Do this:
@Get()
@UseGuards(JwtAuthGuard)
getProfile(
  @UserId() userId: string,
  @UserRoles() roles: string[],
) {
  return this.service.getProfile(userId, roles);
}
```

### 4. Rate Limiting Best Practices

```typescript
// Strict limits for authentication
@Post('login')
@Throttle({ default: { limit: 5, ttl: 60000 } })  // 5/min

// Moderate limits for registration
@Post('register')
@Throttle({ default: { limit: 10, ttl: 60000 } })  // 10/min

// Relaxed limits for data fetching
@Get('data')
@Throttle({ default: { limit: 100, ttl: 60000 } })  // 100/min

// No limits for logout
@Post('logout')
@SkipThrottle()
```

### 5. Error Handling

Guards throw standard NestJS exceptions:

- **UnauthorizedException** (401) - Missing or invalid token
- **ForbiddenException** (403) - Insufficient permissions
- **TooManyRequestsException** (429) - Rate limit exceeded

Handle these in a global exception filter:

```typescript
// http-exception.filter.ts
@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: any, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse();
    const request = ctx.getRequest();

    const status = exception.getStatus?.() || 500;
    const message = exception.message || "Internal server error";

    response.status(status).json({
      statusCode: status,
      message,
      timestamp: new Date().toISOString(),
      path: request.url,
    });
  }
}
```

### 6. Testing Guards

```typescript
import { Test } from "@nestjs/testing";
import { JwtAuthGuard, RolesGuard } from "@sahool/nestjs-auth";
import { ExecutionContext } from "@nestjs/common";

describe("FarmsController", () => {
  let controller: FarmsController;

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      controllers: [FarmsController],
      providers: [FarmsService],
    })
      .overrideGuard(JwtAuthGuard)
      .useValue({
        canActivate: (context: ExecutionContext) => {
          const request = context.switchToHttp().getRequest();
          request.user = { id: "test-user", roles: ["admin"] };
          return true;
        },
      })
      .compile();

    controller = module.get<FarmsController>(FarmsController);
  });

  it("should allow admin to access all farms", async () => {
    const result = await controller.getAllFarms();
    expect(result).toBeDefined();
  });
});
```

---

## Common User Roles

The SAHOOL platform uses these standard roles:

| Role          | Description                  | Typical Permissions        |
| ------------- | ---------------------------- | -------------------------- |
| `super_admin` | Platform super administrator | Full access                |
| `admin`       | Tenant administrator         | Full tenant access         |
| `manager`     | Farm/Business manager        | Manage operations          |
| `farmer`      | Farm owner                   | Manage own farms           |
| `agronomist`  | Agricultural expert          | Read farms, provide advice |
| `seller`      | Marketplace seller           | Sell products              |
| `buyer`       | Marketplace buyer            | Purchase products          |
| `worker`      | Farm worker                  | Limited farm access        |
| `viewer`      | Read-only user               | View data only             |
| `researcher`  | Research scientist           | Access research data       |

## Common Permissions

Fine-grained permissions follow the pattern: `resource:action`

### Farm Permissions

- `farm:read` - View farms
- `farm:write` - Create/update farms
- `farm:delete` - Delete farms
- `farm:share` - Share farm data

### Product Permissions

- `product:read` - View products
- `product:write` - Create/update products
- `product:delete` - Delete products
- `product:publish` - Publish products to marketplace

### User Permissions

- `user:read` - View users
- `user:write` - Create/update users
- `user:delete` - Delete users
- `user:impersonate` - Impersonate users

### Seller Permissions

- `seller:verify` - Verify sellers
- `seller:suspend` - Suspend sellers

---

## Troubleshooting

### Issue: "Unauthorized" on all routes

**Cause:** Missing JWT strategy or secret key

**Solution:**

```typescript
// Ensure JwtModule is configured
JwtModule.register({
  secret: process.env.JWT_SECRET,
  signOptions: { expiresIn: '1h' },
})

// Ensure JWT strategy is provided
providers: [JwtStrategy, ...]
```

### Issue: Guards not working

**Cause:** Guards applied in wrong order

**Solution:** Apply guards in correct order (Auth → Roles → Custom)

### Issue: Rate limiting not working

**Cause:** ThrottlerGuard not globally configured

**Solution:**

```typescript
providers: [
  {
    provide: APP_GUARD,
    useClass: ThrottlerGuard,
  },
];
```

### Issue: "Cannot read property 'user' of undefined"

**Cause:** Trying to access user before JwtAuthGuard

**Solution:** Always apply JwtAuthGuard before accessing request.user

---

## Migration Path

### For services currently without guards:

1. **Add ThrottlerGuard globally** (if not already present)
2. **Add JwtAuthGuard to protected routes**
3. **Add RolesGuard to admin routes**
4. **Add PermissionsGuard to sensitive operations**
5. **Consider adding TokenRevocationGuard globally**

### Example Migration:

**Before:**

```typescript
@Controller("farms")
export class FarmsController {
  @Get()
  getFarms() {
    return this.farmsService.findAll();
  }
}
```

**After:**

```typescript
@Controller("farms")
export class FarmsController {
  @Get()
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles("admin", "manager")
  getFarms(@CurrentUser() user: any) {
    return this.farmsService.findAll();
  }
}
```

---

## Security Checklist

- [ ] ThrottlerGuard configured globally on all services
- [ ] JwtAuthGuard on all protected routes
- [ ] RolesGuard on admin routes
- [ ] PermissionsGuard on sensitive operations
- [ ] TokenRevocationGuard on services with user authentication
- [ ] @Public() decorator on truly public routes
- [ ] Custom rate limits on authentication endpoints
- [ ] ServiceAuthGuard on internal endpoints
- [ ] Error messages don't leak sensitive information
- [ ] Guards tested in unit and e2e tests

---

## Resources

- [NestJS Guards Documentation](https://docs.nestjs.com/guards)
- [NestJS Passport Integration](https://docs.nestjs.com/security/authentication)
- [NestJS Throttler](https://docs.nestjs.com/security/rate-limiting)
- [Shared Auth Package](/packages/nestjs-auth/README.md)
- [Rate Limiting Implementation](/RATE_LIMITING_IMPLEMENTATION.md)

---

**Last Updated:** 2026-01-06
**Version:** 16.0.0
**Status:** ✅ Production Ready
