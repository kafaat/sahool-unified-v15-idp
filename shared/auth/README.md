# SAHOOL Platform JWT Authentication

Shared JWT authentication and authorization middleware for SAHOOL platform services (both Python/FastAPI and TypeScript/NestJS).

## Overview

This module provides:

- **JWT token creation and verification** (HS256 and RS256 algorithms)
- **FastAPI dependencies** for authentication and authorization
- **NestJS guards and strategies** for Passport authentication
- **Role-based access control (RBAC)**
- **Permission-based access control**
- **Rate limiting middleware**
- **Bilingual error messages** (English and Arabic)

## Features

- Stateless JWT authentication
- Access and refresh tokens
- Token revocation support (with JTI)
- Multi-tenant support
- Farm-level access control
- Configurable token expiration
- Security headers middleware
- Rate limiting
- Arabic and English error messages

## Installation

### Python (FastAPI)

```bash
pip install pyjwt fastapi python-multipart
```

### TypeScript (NestJS)

```bash
npm install @nestjs/jwt @nestjs/passport passport passport-jwt
npm install -D @types/passport-jwt
```

## Configuration

Set the following environment variables:

```bash
# Required
JWT_SECRET_KEY="your-secret-key-here-min-32-chars"

# Optional
JWT_ALGORITHM="HS256"                    # or RS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES="30"
JWT_REFRESH_TOKEN_EXPIRE_DAYS="7"
JWT_ISSUER="sahool-platform"
JWT_AUDIENCE="sahool-api"

# For RS256 (asymmetric encryption)
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----..."
JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."

# Rate Limiting
RATE_LIMIT_ENABLED="true"
RATE_LIMIT_REQUESTS="100"
RATE_LIMIT_WINDOW_SECONDS="60"

# Redis (for token revocation)
REDIS_URL="redis://localhost:6379"
```

---

## Python (FastAPI) Usage

### 1. Basic Authentication

```python
from fastapi import FastAPI, Depends
from shared.auth import get_current_user, User

app = FastAPI()

@app.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return {"user_id": user.id, "roles": user.roles}
```

### 2. Role-Based Access Control

```python
from shared.auth import require_roles, User

@app.post("/admin/settings")
async def update_settings(
    settings: dict,
    user: User = Depends(require_roles("admin"))
):
    return {"message": "Settings updated"}

# Multiple roles (user needs at least one)
@app.get("/reports")
async def get_reports(
    user: User = Depends(require_roles("admin", "manager"))
):
    return {"reports": [...]}
```

### 3. Permission-Based Access Control

```python
from shared.auth import require_permissions, User

@app.delete("/farms/{farm_id}")
async def delete_farm(
    farm_id: str,
    user: User = Depends(require_permissions("farm:delete"))
):
    return {"message": "Farm deleted"}
```

### 4. Farm Access Control

```python
from shared.auth import require_farm_access, User

@app.get("/farms/{farm_id}/fields")
async def get_farm_fields(
    farm_id: str,
    user: User = Depends(require_farm_access())
):
    # User has access to this farm
    return {"fields": [...]}
```

### 5. Creating Tokens

```python
from shared.auth import create_token_pair

# Login endpoint
@app.post("/auth/login")
async def login(credentials: LoginDto):
    # Authenticate user
    user = authenticate(credentials)

    # Create tokens
    tokens = create_token_pair(
        user_id=user.id,
        roles=user.roles,
        tenant_id=user.tenant_id,
        permissions=["farm:read", "farm:write"]
    )

    return tokens
    # Returns:
    # {
    #   "access_token": "eyJ...",
    #   "refresh_token": "eyJ...",
    #   "token_type": "bearer",
    #   "expires_in": 1800
    # }
```

### 6. Refreshing Tokens

```python
from shared.auth import refresh_access_token, verify_token

@app.post("/auth/refresh")
async def refresh(refresh_token: str):
    # Verify refresh token
    payload = verify_token(refresh_token)

    # Get updated user roles/permissions from database
    user = get_user_by_id(payload.user_id)

    # Create new access token
    new_token = refresh_access_token(
        refresh_token=refresh_token,
        roles=user.roles,
        permissions=user.permissions
    )

    return {"access_token": new_token}
```

### 7. Adding Middleware

```python
from fastapi import FastAPI
from shared.auth import JWTAuthMiddleware, RateLimitMiddleware

app = FastAPI()

# Add JWT authentication middleware
app.add_middleware(
    JWTAuthMiddleware,
    exclude_paths=["/health", "/docs", "/auth/login"],
    require_auth=False  # Set to True to require auth on all routes
)

# Add rate limiting
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,
    exclude_paths=["/health"]
)
```

### 8. Optional Authentication

```python
from typing import Optional
from shared.auth import get_optional_user, User

@app.get("/content")
async def get_content(user: Optional[User] = Depends(get_optional_user)):
    if user:
        return {"content": "premium content", "user": user.email}
    return {"content": "public content"}
```

### 9. Rate Limiting

```python
from shared.auth import rate_limit_dependency, User

@app.post("/api/heavy-operation")
async def heavy_operation(
    user: User = Depends(rate_limit_dependency)
):
    return {"message": "Operation completed"}
```

---

## TypeScript (NestJS) Usage

### 1. Module Setup

```typescript
// auth.module.ts
import { Module } from "@nestjs/common";
import { JwtModule } from "@nestjs/jwt";
import { PassportModule } from "@nestjs/passport";
import { JwtStrategy } from "@shared/auth/jwt.strategy";
import { JWTConfig } from "@shared/auth/config";

@Module({
  imports: [
    PassportModule,
    JwtModule.register({
      secret: JWTConfig.SECRET,
      signOptions: JWTConfig.getJwtOptions().signOptions,
    }),
  ],
  providers: [JwtStrategy],
  exports: [JwtStrategy, JwtModule],
})
export class AuthModule {}
```

### 2. Basic Authentication

```typescript
import { Controller, Get, UseGuards } from "@nestjs/common";
import { JwtAuthGuard } from "@shared/auth/jwt.guard";
import { CurrentUser } from "@shared/auth/decorators";
import { AuthenticatedUser } from "@shared/auth/jwt.strategy";

@Controller("profile")
@UseGuards(JwtAuthGuard)
export class ProfileController {
  @Get()
  getProfile(@CurrentUser() user: AuthenticatedUser) {
    return { userId: user.id, roles: user.roles };
  }
}
```

### 3. Public Routes

```typescript
import { Public } from "@shared/auth/decorators";

@Controller("auth")
export class AuthController {
  @Public()
  @Post("login")
  login(@Body() credentials: LoginDto) {
    return this.authService.login(credentials);
  }
}
```

### 4. Role-Based Access Control

```typescript
import { UseGuards } from "@nestjs/common";
import { JwtAuthGuard, RolesGuard } from "@shared/auth/jwt.guard";
import { Roles } from "@shared/auth/decorators";

@Controller("admin")
@UseGuards(JwtAuthGuard, RolesGuard)
export class AdminController {
  @Roles("admin", "manager")
  @Get("settings")
  getSettings() {
    return this.adminService.getSettings();
  }
}
```

### 5. Permission-Based Access Control

```typescript
import { PermissionsGuard } from "@shared/auth/jwt.guard";
import { RequirePermissions } from "@shared/auth/decorators";

@Controller("farms")
@UseGuards(JwtAuthGuard, PermissionsGuard)
export class FarmsController {
  @RequirePermissions("farm:delete")
  @Delete(":id")
  deleteFarm(@Param("id") id: string) {
    return this.farmsService.delete(id);
  }
}
```

### 6. Farm Access Control

```typescript
import { FarmAccessGuard } from "@shared/auth/jwt.guard";

@Controller("farms")
@UseGuards(JwtAuthGuard, FarmAccessGuard)
export class FarmsController {
  @Get(":farmId/fields")
  getFields(@Param("farmId") farmId: string) {
    return this.fieldsService.findByFarm(farmId);
  }
}
```

### 7. Using Decorators

```typescript
import {
  CurrentUser,
  UserId,
  UserRoles,
  TenantId,
  RequestLanguage,
} from "@shared/auth/decorators";

@Controller("dashboard")
export class DashboardController {
  @Get()
  getDashboard(
    @UserId() userId: string,
    @UserRoles() roles: string[],
    @TenantId() tenantId: string,
    @RequestLanguage() lang: string,
  ) {
    return {
      userId,
      roles,
      tenantId,
      language: lang,
    };
  }
}
```

### 8. Creating Tokens

```typescript
import { JwtService } from "@nestjs/jwt";
import { JWTConfig } from "@shared/auth/config";

@Injectable()
export class AuthService {
  constructor(private jwtService: JwtService) {}

  async login(user: User) {
    const payload = {
      sub: user.id,
      roles: user.roles,
      permissions: user.permissions,
      tid: user.tenantId,
      jti: randomUUID(),
    };

    return {
      access_token: this.jwtService.sign(payload),
      refresh_token: this.jwtService.sign(
        { sub: user.id, tid: user.tenantId, type: "refresh" },
        { expiresIn: `${JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS}d` },
      ),
      token_type: "bearer",
      expires_in: JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    };
  }
}
```

### 9. Optional Authentication

```typescript
import { OptionalAuthGuard } from "@shared/auth/jwt.guard";

@Controller("content")
export class ContentController {
  @Get()
  @UseGuards(OptionalAuthGuard)
  getContent(@CurrentUser() user?: AuthenticatedUser) {
    if (user) {
      return this.contentService.getPremiumContent();
    }
    return this.contentService.getPublicContent();
  }
}
```

### 10. Global Guards

```typescript
// main.ts
import { APP_GUARD } from "@nestjs/core";
import { JwtAuthGuard } from "@shared/auth/jwt.guard";

@Module({
  providers: [
    {
      provide: APP_GUARD,
      useClass: JwtAuthGuard,
    },
  ],
})
export class AppModule {}

// Now all routes require authentication by default
// Use @Public() decorator to make routes public
```

---

## Error Messages

All authentication errors include bilingual messages (English and Arabic):

### Python

```python
from shared.auth import AuthErrors

# Access error messages
AuthErrors.INVALID_TOKEN.en  # "Invalid authentication token"
AuthErrors.INVALID_TOKEN.ar  # "رمز المصادقة غير صالح"
AuthErrors.INVALID_TOKEN.code  # "invalid_token"
```

### TypeScript

```typescript
import { AuthErrors } from "@shared/auth/config";

// Access error messages
AuthErrors.INVALID_TOKEN.en; // "Invalid authentication token"
AuthErrors.INVALID_TOKEN.ar; // "رمز المصادقة غير صالح"
AuthErrors.INVALID_TOKEN.code; // "invalid_token"
```

### Available Error Messages

- `INVALID_TOKEN` - Invalid authentication token
- `EXPIRED_TOKEN` - Token has expired
- `MISSING_TOKEN` - Token is missing
- `INVALID_CREDENTIALS` - Invalid credentials
- `INSUFFICIENT_PERMISSIONS` - Insufficient permissions
- `ACCOUNT_DISABLED` - Account has been disabled
- `ACCOUNT_NOT_VERIFIED` - Account is not verified
- `TOKEN_REVOKED` - Token has been revoked
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INVALID_ISSUER` - Invalid token issuer
- `INVALID_AUDIENCE` - Invalid token audience

---

## Permissions

The following permissions are available:

### Farm Management

- `farm:read` - Read farm data
- `farm:write` - Create/update farms
- `farm:delete` - Delete farms

### Field Management

- `field:read` - Read field data
- `field:write` - Create/update fields
- `field:delete` - Delete fields

### Crop Management

- `crop:read` - Read crop data
- `crop:write` - Create/update crops
- `crop:delete` - Delete crops

### Weather & Climate

- `weather:read` - Read weather data
- `weather:subscribe` - Subscribe to weather updates

### Advisory Services

- `advisory:read` - Read advisory content
- `advisory:request` - Request personalized advice

### Analytics & Reports

- `analytics:read` - View analytics
- `analytics:export` - Export reports

### User Management

- `user:read` - Read user data
- `user:write` - Create/update users
- `user:delete` - Delete users

### Admin Operations

- `admin:access` - Access admin panel
- `admin:settings` - Modify system settings
- `admin:billing` - Manage billing

### Equipment Management

- `equipment:read` - Read equipment data
- `equipment:write` - Create/update equipment
- `equipment:delete` - Delete equipment

### Precision Agriculture

- `vra:read`, `vra:write` - Variable Rate Application
- `spray:read`, `spray:write` - Spray Timing
- `gdd:read` - Growing Degree Days
- `rotation:read`, `rotation:write` - Crop Rotation
- `profitability:read` - Profitability Analysis

---

## Security Best Practices

1. **Use strong secrets**: Minimum 32 characters for `JWT_SECRET_KEY`
2. **Use RS256 in production**: Asymmetric encryption is more secure
3. **Short token expiration**: Keep access tokens short-lived (15-30 minutes)
4. **Implement token revocation**: Use Redis for revoked token storage
5. **Enable rate limiting**: Prevent brute force attacks
6. **Use HTTPS only**: Never send tokens over HTTP
7. **Rotate secrets regularly**: Change JWT secrets periodically
8. **Validate on every request**: Don't skip token verification
9. **Implement refresh tokens**: Allow users to get new access tokens
10. **Log authentication events**: Monitor for suspicious activity

---

## Testing

### Python

```python
import pytest
from shared.auth import create_access_token, verify_token

def test_token_creation():
    token = create_access_token(
        user_id="user123",
        roles=["farmer"],
        permissions=["farm:read"]
    )
    assert token is not None

def test_token_verification():
    token = create_access_token(
        user_id="user123",
        roles=["farmer"]
    )
    payload = verify_token(token)
    assert payload.user_id == "user123"
    assert "farmer" in payload.roles
```

### TypeScript

```typescript
import { JwtService } from "@nestjs/jwt";
import { Test } from "@nestjs/testing";
import { JWTConfig } from "@shared/auth/config";

describe("JWT Authentication", () => {
  let jwtService: JwtService;

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [
        {
          provide: JwtService,
          useValue: new JwtService({
            secret: JWTConfig.SECRET,
          }),
        },
      ],
    }).compile();

    jwtService = module.get<JwtService>(JwtService);
  });

  it("should create and verify token", () => {
    const payload = { sub: "user123", roles: ["farmer"] };
    const token = jwtService.sign(payload);
    const decoded = jwtService.verify(token);

    expect(decoded.sub).toBe("user123");
    expect(decoded.roles).toContain("farmer");
  });
});
```

---

## License

Internal use only - SAHOOL Platform
