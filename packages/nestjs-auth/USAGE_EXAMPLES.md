# Usage Examples

This document provides practical examples of using `@sahool/nestjs-auth` in your NestJS services.

## Table of Contents

1. [Basic Setup](#basic-setup)
2. [Controller Examples](#controller-examples)
3. [Service Integration](#service-integration)
4. [Custom User Repository](#custom-user-repository)
5. [Token Revocation](#token-revocation)
6. [Testing](#testing)

## Basic Setup

### 1. Simple Integration (Recommended for most services)

```typescript
// src/app.module.ts
import { Module } from "@nestjs/common";
import { AuthModule } from "@sahool/nestjs-auth";
import { RedisModule } from "@liaoliaots/nestjs-redis";

@Module({
  imports: [
    // Redis module (required for user validation and token revocation)
    RedisModule.forRoot({
      config: {
        host: process.env.REDIS_HOST || "localhost",
        port: parseInt(process.env.REDIS_PORT || "6379"),
        password: process.env.REDIS_PASSWORD,
        db: parseInt(process.env.REDIS_DB || "0"),
      },
    }),

    // Auth module with defaults
    AuthModule.forRoot({
      enableUserValidation: true,
      enableTokenRevocation: true,
    }),
  ],
})
export class AppModule {}
```

### 2. With Global Guard (All routes protected by default)

```typescript
// src/app.module.ts
import { Module } from "@nestjs/common";
import { AuthModule } from "@sahool/nestjs-auth";

@Module({
  imports: [
    AuthModule.forRoot({
      enableGlobalGuard: true, // All routes require authentication
      enableUserValidation: true,
    }),
  ],
})
export class AppModule {}
```

### 3. With Custom JWT Options

```typescript
// src/app.module.ts
import { Module } from "@nestjs/common";
import { AuthModule } from "@sahool/nestjs-auth";

@Module({
  imports: [
    AuthModule.forRoot({
      jwtOptions: {
        secret: process.env.JWT_SECRET,
        signOptions: {
          expiresIn: "2h",
          issuer: "my-service",
          audience: "my-api",
        },
      },
    }),
  ],
})
export class AppModule {}
```

## Controller Examples

### Basic Protected Controller

```typescript
// src/farms/farms.controller.ts
import { Controller, Get, Post, Body, UseGuards } from "@nestjs/common";
import { JwtAuthGuard, CurrentUser, UserId } from "@sahool/nestjs-auth";
import { FarmsService } from "./farms.service";

@Controller("farms")
@UseGuards(JwtAuthGuard) // Protect all routes in this controller
export class FarmsController {
  constructor(private readonly farmsService: FarmsService) {}

  // Get current user's farms
  @Get()
  async getMyFarms(@UserId() userId: string) {
    return this.farmsService.findByUser(userId);
  }

  // Get full user object
  @Get("user-info")
  async getUserInfo(@CurrentUser() user: any) {
    return {
      id: user.id,
      roles: user.roles,
      permissions: user.permissions,
      tenantId: user.tenantId,
    };
  }

  // Create farm
  @Post()
  async createFarm(@Body() createFarmDto: any, @UserId() userId: string) {
    return this.farmsService.create({
      ...createFarmDto,
      ownerId: userId,
    });
  }
}
```

### Role-Based Access Control

```typescript
// src/admin/admin.controller.ts
import { Controller, Get, Delete, Param, UseGuards } from "@nestjs/common";
import {
  JwtAuthGuard,
  RolesGuard,
  Roles,
  UserRoles,
} from "@sahool/nestjs-auth";

@Controller("admin")
@UseGuards(JwtAuthGuard, RolesGuard) // Apply guards to all routes
export class AdminController {
  constructor(private readonly adminService: AdminService) {}

  // Only admins can access
  @Roles("admin")
  @Get("users")
  async getAllUsers() {
    return this.adminService.findAllUsers();
  }

  // Admins and managers can access
  @Roles("admin", "manager")
  @Get("reports")
  async getReports(@UserRoles() roles: string[]) {
    // Customize based on role
    if (roles.includes("admin")) {
      return this.adminService.getFullReports();
    }
    return this.adminService.getBasicReports();
  }

  // Only super admins can delete
  @Roles("super_admin")
  @Delete("users/:id")
  async deleteUser(@Param("id") id: string) {
    return this.adminService.deleteUser(id);
  }
}
```

### Permission-Based Access Control

```typescript
// src/resources/resources.controller.ts
import { Controller, Get, Post, Put, Delete, UseGuards } from "@nestjs/common";
import {
  JwtAuthGuard,
  PermissionsGuard,
  RequirePermissions,
  UserPermissions,
} from "@sahool/nestjs-auth";

@Controller("resources")
@UseGuards(JwtAuthGuard, PermissionsGuard)
export class ResourcesController {
  constructor(private readonly resourcesService: ResourcesService) {}

  @RequirePermissions("resource:read")
  @Get()
  async findAll(@UserPermissions() permissions: string[]) {
    return this.resourcesService.findAll(permissions);
  }

  @RequirePermissions("resource:create")
  @Post()
  async create(@Body() data: any) {
    return this.resourcesService.create(data);
  }

  @RequirePermissions("resource:update")
  @Put(":id")
  async update(@Param("id") id: string, @Body() data: any) {
    return this.resourcesService.update(id, data);
  }

  @RequirePermissions("resource:delete")
  @Delete(":id")
  async remove(@Param("id") id: string) {
    return this.resourcesService.remove(id);
  }
}
```

### Public and Optional Authentication

```typescript
// src/content/content.controller.ts
import { Controller, Get, Post, UseGuards } from "@nestjs/common";
import {
  JwtAuthGuard,
  OptionalAuthGuard,
  Public,
  CurrentUser,
} from "@sahool/nestjs-auth";

@Controller("content")
export class ContentController {
  constructor(private readonly contentService: ContentService) {}

  // Completely public - no auth required
  @Public()
  @Get("public")
  async getPublicContent() {
    return this.contentService.getPublicContent();
  }

  // Optional auth - different content based on authentication
  @UseGuards(OptionalAuthGuard)
  @Get("mixed")
  async getMixedContent(@CurrentUser() user?: any) {
    if (user) {
      return this.contentService.getAuthenticatedContent(user.id);
    }
    return this.contentService.getGuestContent();
  }

  // Protected route
  @UseGuards(JwtAuthGuard)
  @Get("premium")
  async getPremiumContent(@CurrentUser() user: any) {
    return this.contentService.getPremiumContent(user.id);
  }
}
```

### Multi-Tenant Support

```typescript
// src/data/data.controller.ts
import { Controller, Get, UseGuards } from "@nestjs/common";
import { JwtAuthGuard, TenantId, CurrentUser } from "@sahool/nestjs-auth";

@Controller("data")
@UseGuards(JwtAuthGuard)
export class DataController {
  constructor(private readonly dataService: DataService) {}

  // Automatically filter by tenant
  @Get()
  async findAll(@TenantId() tenantId: string) {
    return this.dataService.findByTenant(tenantId);
  }

  // Access tenant from user object
  @Get("tenant-info")
  async getTenantInfo(@CurrentUser() user: any) {
    return {
      tenantId: user.tenantId,
      userId: user.id,
      roles: user.roles,
    };
  }
}
```

## Service Integration

### Using Auth in Services

```typescript
// src/farms/farms.service.ts
import { Injectable, ForbiddenException } from "@nestjs/common";
import { hasRole, hasPermission } from "@sahool/nestjs-auth";

@Injectable()
export class FarmsService {
  // Check permissions in service logic
  async deleteFarm(farmId: string, user: any) {
    // Check if user is admin or farm owner
    if (!hasRole(user, "admin")) {
      const farm = await this.findOne(farmId);
      if (farm.ownerId !== user.id) {
        throw new ForbiddenException("You can only delete your own farms");
      }
    }

    return this.farmRepository.delete(farmId);
  }

  // Check multiple permissions
  async performSensitiveAction(user: any) {
    const requiredPermissions = ["farm:delete", "farm:manage"];

    const hasPermissions = requiredPermissions.every((perm) =>
      hasPermission(user, perm),
    );

    if (!hasPermissions) {
      throw new ForbiddenException("Insufficient permissions");
    }

    // Perform action
  }
}
```

## Custom User Repository

```typescript
// src/users/user.repository.ts
import { Injectable } from "@nestjs/common";
import { IUserRepository, UserValidationData } from "@sahool/nestjs-auth";
import { PrismaService } from "../prisma/prisma.service";

@Injectable()
export class UserRepository implements IUserRepository {
  constructor(private readonly prisma: PrismaService) {}

  async getUserValidationData(
    userId: string,
  ): Promise<UserValidationData | null> {
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

// In app.module.ts
import { UserRepository } from "./users/user.repository";

@Module({
  imports: [
    AuthModule.forRoot({
      enableUserValidation: true,
      userRepository: new UserRepository(prismaService), // Pass instance
    }),
  ],
})
export class AppModule {}
```

## Token Revocation

```typescript
// src/auth/auth.service.ts
import { Injectable } from "@nestjs/common";
import { JwtService } from "@nestjs/jwt";
import { RedisTokenRevocationStore } from "@sahool/nestjs-auth";

@Injectable()
export class AuthService {
  constructor(
    private readonly jwtService: JwtService,
    private readonly revocationStore: RedisTokenRevocationStore,
  ) {}

  // Logout single session
  async logout(token: string) {
    const decoded = this.jwtService.decode(token) as any;

    await this.revocationStore.revokeToken(decoded.jti, {
      expiresIn: decoded.exp - Math.floor(Date.now() / 1000),
      reason: "User logout",
      userId: decoded.sub,
    });

    return { message: "Logged out successfully" };
  }

  // Logout all sessions
  async logoutAllDevices(userId: string) {
    await this.revocationStore.revokeAllUserTokens(userId, {
      reason: "Logout all devices",
    });

    return { message: "Logged out from all devices" };
  }

  // Revoke on password change
  async changePassword(userId: string, newPassword: string) {
    // Update password in database
    await this.updateUserPassword(userId, newPassword);

    // Revoke all existing tokens
    await this.revocationStore.revokeAllUserTokens(userId, {
      reason: "Password changed",
    });

    return { message: "Password changed. Please login again." };
  }

  // Revoke on security incident
  async handleSecurityIncident(userId: string) {
    await this.revocationStore.revokeAllUserTokens(userId, {
      reason: "Security incident",
    });

    // Notify user
    await this.notifyUser(userId, "Security alert: All sessions terminated");
  }

  // Check if token is revoked
  async isTokenRevoked(token: string): Promise<boolean> {
    const decoded = this.jwtService.decode(token) as any;

    const result = await this.revocationStore.isRevoked({
      jti: decoded.jti,
      userId: decoded.sub,
      tenantId: decoded.tid,
      issuedAt: decoded.iat,
    });

    return result.isRevoked;
  }
}
```

## Testing

### Unit Testing with Auth Module

```typescript
// src/farms/farms.controller.spec.ts
import { Test, TestingModule } from "@nestjs/testing";
import { AuthModule } from "@sahool/nestjs-auth";
import { FarmsController } from "./farms.controller";
import { FarmsService } from "./farms.service";

describe("FarmsController", () => {
  let controller: FarmsController;
  let service: FarmsService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      imports: [
        // Disable user validation and revocation for testing
        AuthModule.forRoot({
          enableUserValidation: false,
          enableTokenRevocation: false,
          validateConfig: false,
        }),
      ],
      controllers: [FarmsController],
      providers: [
        {
          provide: FarmsService,
          useValue: {
            findByUser: jest.fn(),
            create: jest.fn(),
          },
        },
      ],
    }).compile();

    controller = module.get<FarmsController>(FarmsController);
    service = module.get<FarmsService>(FarmsService);
  });

  it("should be defined", () => {
    expect(controller).toBeDefined();
  });

  describe("getMyFarms", () => {
    it("should return user farms", async () => {
      const userId = "user-123";
      const farms = [{ id: "farm-1", name: "Test Farm" }];

      jest.spyOn(service, "findByUser").mockResolvedValue(farms);

      const result = await controller.getMyFarms(userId);

      expect(result).toEqual(farms);
      expect(service.findByUser).toHaveBeenCalledWith(userId);
    });
  });
});
```

### E2E Testing

```typescript
// test/auth.e2e-spec.ts
import { Test } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";
import * as request from "supertest";
import { AppModule } from "../src/app.module";

describe("Authentication (e2e)", () => {
  let app: INestApplication;
  let authToken: string;

  beforeAll(async () => {
    const moduleFixture = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it("/auth/login (POST) - should login and return token", async () => {
    const response = await request(app.getHttpServer())
      .post("/auth/login")
      .send({
        email: "test@example.com",
        password: "password123",
      })
      .expect(200);

    authToken = response.body.accessToken;
    expect(authToken).toBeDefined();
  });

  it("/farms (GET) - should fail without token", async () => {
    await request(app.getHttpServer()).get("/farms").expect(401);
  });

  it("/farms (GET) - should succeed with token", async () => {
    await request(app.getHttpServer())
      .get("/farms")
      .set("Authorization", `Bearer ${authToken}`)
      .expect(200);
  });

  it("/admin/users (GET) - should fail without admin role", async () => {
    await request(app.getHttpServer())
      .get("/admin/users")
      .set("Authorization", `Bearer ${authToken}`)
      .expect(403);
  });
});
```

## Best Practices

1. **Use guards at controller level** when all routes need the same protection
2. **Combine guards** for complex access control (JWT + Roles + Permissions)
3. **Use decorators** for clean, readable code
4. **Implement user repository** for production deployments
5. **Enable token revocation** for sensitive applications
6. **Use RS256** in production for better security
7. **Test with auth disabled** for unit tests
8. **Use E2E tests** to verify guard behavior
9. **Handle errors gracefully** in your services
10. **Log authentication failures** for security monitoring
