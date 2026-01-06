# NestJS Guards - Quick Reference Card

## 🚀 Quick Start

### Import Guards and Decorators
```typescript
import {
  JwtAuthGuard,
  RolesGuard,
  PermissionsGuard,
  Roles,
  RequirePermissions,
  Public,
  CurrentUser,
  UserId,
} from '@sahool/nestjs-auth';
import { Throttle, SkipThrottle } from '@nestjs/throttler';
```

## 📋 Common Patterns

### Public Route
```typescript
@Get('public-data')
@Public()
getData() {
  return this.service.getPublicData();
}
```

### Protected Route (Authenticated Users Only)
```typescript
@Get('profile')
@UseGuards(JwtAuthGuard)
getProfile(@CurrentUser() user: any) {
  return this.service.getProfile(user.id);
}
```

### Admin Only Route
```typescript
@Get('admin/users')
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
getAllUsers() {
  return this.service.getAllUsers();
}
```

### Multiple Roles
```typescript
@Post('products')
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('seller', 'admin', 'manager')
createProduct(@Body() dto: CreateProductDto) {
  return this.service.create(dto);
}
```

### Permission-Based Access
```typescript
@Delete('farms/:id')
@UseGuards(JwtAuthGuard, PermissionsGuard)
@RequirePermissions('farm:delete')
deleteFarm(@Param('id') id: string) {
  return this.service.delete(id);
}
```

### Multiple Permissions
```typescript
@Put('settings')
@UseGuards(JwtAuthGuard, PermissionsGuard)
@RequirePermissions('settings:write', 'settings:admin')
updateSettings(@Body() dto: any) {
  return this.service.updateSettings(dto);
}
```

### Custom Rate Limiting
```typescript
@Post('login')
@Public()
@Throttle({ default: { limit: 5, ttl: 60000 } }) // 5 per minute
login(@Body() credentials: LoginDto) {
  return this.authService.login(credentials);
}
```

### Skip Rate Limiting
```typescript
@Post('logout')
@UseGuards(JwtAuthGuard)
@SkipThrottle()
logout() {
  return this.authService.logout();
}
```

### Optional Authentication
```typescript
@Get('content')
@UseGuards(OptionalAuthGuard)
getContent(@CurrentUser() user?: any) {
  if (user) {
    return this.service.getPremiumContent();
  }
  return this.service.getFreeContent();
}
```

## 🎯 User Data Extraction

### Get User ID
```typescript
@Get('my-data')
@UseGuards(JwtAuthGuard)
getMyData(@UserId() userId: string) {
  return this.service.getUserData(userId);
}
```

### Get Full User Object
```typescript
@Get('profile')
@UseGuards(JwtAuthGuard)
getProfile(@CurrentUser() user: any) {
  return {
    id: user.id,
    email: user.email,
    roles: user.roles,
  };
}
```

### Get User Roles
```typescript
@Get('dashboard')
@UseGuards(JwtAuthGuard)
getDashboard(@UserRoles() roles: string[]) {
  if (roles.includes('admin')) {
    return this.service.getAdminDashboard();
  }
  return this.service.getUserDashboard();
}
```

### Get Specific User Property
```typescript
@Get('email')
@UseGuards(JwtAuthGuard)
getEmail(@CurrentUser('email') email: string) {
  return { email };
}
```

### Get Tenant ID
```typescript
@Get('data')
@UseGuards(JwtAuthGuard)
getData(@TenantId() tenantId: string) {
  return this.service.getDataByTenant(tenantId);
}
```

### Get User Permissions
```typescript
@Get('features')
@UseGuards(JwtAuthGuard)
getFeatures(@UserPermissions() permissions: string[]) {
  return this.service.getEnabledFeatures(permissions);
}
```

## 🔒 Security Patterns

### Admin or Owner
```typescript
@Put('farms/:id')
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
updateFarm(
  @Param('id') farmId: string,
  @CurrentUser() user: any,
  @Body() dto: UpdateFarmDto,
) {
  // Admin can update any farm
  // OR farm owner can update their farm (checked in service)
  return this.service.update(farmId, dto, user.id);
}
```

### Resource Ownership Check (in service)
```typescript
// In service
async updateFarm(farmId: string, dto: UpdateFarmDto, userId: string) {
  const farm = await this.prisma.farm.findUnique({ where: { id: farmId } });

  if (farm.userId !== userId) {
    throw new ForbiddenException('You do not own this farm');
  }

  return this.prisma.farm.update({ where: { id: farmId }, data: dto });
}
```

### Combine Guards
```typescript
@Delete('products/:id')
@UseGuards(JwtAuthGuard, RolesGuard, PermissionsGuard)
@Roles('admin', 'manager')
@RequirePermissions('product:delete')
deleteProduct(@Param('id') id: string) {
  // User must be admin OR manager
  // AND have product:delete permission
  return this.service.delete(id);
}
```

## 📊 Rate Limiting Patterns

### Authentication Endpoints
```typescript
// Login - Strict limit
@Post('login')
@Throttle({ default: { limit: 5, ttl: 60000 } })

// Register - Moderate limit
@Post('register')
@Throttle({ default: { limit: 10, ttl: 60000 } })

// Password reset - Very strict
@Post('forgot-password')
@Throttle({ default: { limit: 3, ttl: 60000 } })

// Token refresh - Relaxed
@Post('refresh')
@Throttle({ default: { limit: 10, ttl: 60000 } })
```

### Data Operations
```typescript
// Read operations - Relaxed
@Get('data')
@Throttle({ default: { limit: 100, ttl: 60000 } })

// Write operations - Moderate
@Post('data')
@Throttle({ default: { limit: 50, ttl: 60000 } })

// Bulk operations - Strict
@Post('bulk-import')
@Throttle({ default: { limit: 3, ttl: 60000 } })
```

## 🎭 Controller-Level Guards

### Apply to All Routes
```typescript
@Controller('admin')
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
export class AdminController {
  // All routes require admin role

  @Get('users')
  getUsers() { }

  @Get('stats')
  getStats() { }
}
```

### Override for Specific Route
```typescript
@Controller('admin')
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
export class AdminController {

  @Get('users')
  getUsers() { }

  // Public endpoint in admin controller
  @Get('public-stats')
  @Public()
  getPublicStats() { }

  // Super admin only
  @Delete('system')
  @Roles('super_admin')
  deleteSystem() { }
}
```

## 🧪 Testing Guards

### Mock JwtAuthGuard
```typescript
const mockJwtAuthGuard = {
  canActivate: jest.fn((context: ExecutionContext) => {
    const request = context.switchToHttp().getRequest();
    request.user = { id: 'test-user', roles: ['admin'] };
    return true;
  }),
};

const module = await Test.createTestingModule({
  controllers: [FarmsController],
})
  .overrideGuard(JwtAuthGuard)
  .useValue(mockJwtAuthGuard)
  .compile();
```

### Mock RolesGuard
```typescript
const mockRolesGuard = {
  canActivate: jest.fn(() => true),
};

const module = await Test.createTestingModule({
  controllers: [AdminController],
})
  .overrideGuard(RolesGuard)
  .useValue(mockRolesGuard)
  .compile();
```

## 🚨 Common Errors

### 401 Unauthorized
- Missing `Authorization` header
- Invalid JWT token
- Expired token
- Token not yet valid (nbf claim)

### 403 Forbidden
- User doesn't have required role
- User doesn't have required permission
- Account is disabled or not verified

### 429 Too Many Requests
- Rate limit exceeded
- Wait for TTL to reset

## 📚 Standard Roles

| Role | Description |
|------|-------------|
| `super_admin` | Platform super administrator |
| `admin` | Tenant administrator |
| `manager` | Farm/Business manager |
| `farmer` | Farm owner |
| `seller` | Marketplace seller |
| `buyer` | Marketplace buyer |
| `agronomist` | Agricultural expert |
| `researcher` | Research scientist |
| `worker` | Farm worker |
| `viewer` | Read-only user |

## 🔑 Standard Permissions

| Permission | Description |
|------------|-------------|
| `farm:read` | View farms |
| `farm:write` | Create/update farms |
| `farm:delete` | Delete farms |
| `product:read` | View products |
| `product:write` | Create/update products |
| `product:delete` | Delete products |
| `user:read` | View users |
| `user:write` | Create/update users |
| `user:delete` | Delete users |
| `settings:read` | View settings |
| `settings:write` | Update settings |

## 💡 Pro Tips

1. **Always apply guards in order**: Auth → Roles → Permissions
2. **Don't apply JwtAuthGuard globally**: Use `@Public()` decorator instead
3. **Use decorators for cleaner code**: `@UserId()` instead of `@Request() req`
4. **Test with and without guards**: Override guards in tests
5. **Log authentication failures**: Use built-in logging in JwtAuthGuard
6. **Cache role/permission lookups**: Reduce database queries
7. **Use custom decorators**: Create domain-specific decorators

## 📖 More Information

- [Full Documentation](/NESTJS_GUARDS_IMPLEMENTATION.md)
- [Improvement Summary](/GUARDS_IMPROVEMENT_SUMMARY.md)
- [Rate Limiting Guide](/RATE_LIMITING_IMPLEMENTATION.md)

---

**Last Updated:** 2026-01-06
**Version:** 1.0.0
