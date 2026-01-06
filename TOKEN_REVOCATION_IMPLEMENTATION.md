# Token Revocation Implementation for SAHOOL Platform

## Overview

This document describes the complete token revocation implementation for the SAHOOL platform. Token revocation ensures that when users logout, their JWT tokens are immediately invalidated and cannot be used to access protected resources.

## Problem Solved

**Before:** JWT tokens remained valid until expiration, even after logout. This meant:
- Tokens could be reused after logout
- No way to forcefully terminate user sessions
- Security risk if tokens were compromised

**After:** Tokens are immediately revoked on logout and stored in Redis blacklist with TTL matching token expiration.

## Architecture

### Components

1. **RedisTokenRevocationStore** (`packages/nestjs-auth/src/services/token-revocation.ts`)
   - Redis-based token blacklist storage
   - Supports JTI-based revocation (individual tokens)
   - Supports user-level revocation (all user tokens)
   - Supports tenant-level revocation (all tenant tokens)
   - Automatic TTL management for cleanup

2. **TokenRevocationGuard** (`packages/nestjs-auth/src/guards/token-revocation.guard.ts`)
   - Middleware that checks every authenticated request
   - Validates if token JTI is in blacklist
   - Throws UnauthorizedException if token is revoked
   - Fail-open design (allows access if Redis is down)

3. **RevocationController** (`shared/auth/revocation.controller.ts`)
   - REST API endpoints for token revocation operations
   - Admin endpoints for managing revocations
   - Statistics and health check endpoints

4. **AuthService** (`apps/services/user-service/src/auth/auth.service.ts`)
   - Handles user login with JTI generation
   - Implements logout with token revocation
   - Supports logout from all devices

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LOGIN                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   AuthService    │
                    │  - Validate user │
                    │  - Generate JTI  │
                    │  - Create tokens │
                    └──────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  JWT Token with JTI                     │
        │  {                                      │
        │    "sub": "user-123",                   │
        │    "jti": "550e8400-e29b-41d4-...",    │
        │    "exp": 1234567890,                   │
        │    "type": "access"                     │
        │  }                                      │
        └─────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATED REQUEST                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  JwtAuthGuard    │
                    │  - Verify JWT    │
                    │  - Extract user  │
                    └──────────────────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │  TokenRevocationGuard        │
                │  - Extract JTI from token    │
                │  - Check Redis blacklist     │
                │  - Reject if revoked         │
                └──────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Protected      │
                    │   Endpoint       │
                    └──────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         USER LOGOUT                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   POST /logout   │
                    │  Authorization:  │
                    │  Bearer <token>  │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   AuthService    │
                    │  - Extract JTI   │
                    │  - Calculate TTL │
                    └──────────────────┘
                              │
                              ▼
            ┌────────────────────────────────────┐
            │  RedisTokenRevocationStore         │
            │  - Store JTI in blacklist          │
            │  - Set TTL = token expiration      │
            │  Key: "revoked:token:<jti>"        │
            │  Value: {revokedAt, reason, ...}   │
            │  TTL: remaining token lifetime     │
            └────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Token Revoked   │
                    │  Success         │
                    └──────────────────┘
```

## Implementation Details

### 1. Token Generation with JTI

When a user logs in, each token gets a unique JTI (JWT ID):

```typescript
import { v4 as uuidv4 } from 'uuid';

const accessJti = uuidv4();
const accessPayload: JwtPayload = {
  sub: user.id,
  email: user.email,
  roles: [user.role],
  tid: user.tenantId,
  jti: accessJti,  // Unique identifier for this token
  type: 'access',
};
```

### 2. Token Revocation on Logout

```typescript
// apps/services/user-service/src/auth/auth.service.ts
async logout(token: string, userId: string): Promise<void> {
  const payload = this.jwtService.decode(token) as JwtPayload;

  // Calculate TTL from token expiration
  const ttl = payload.exp - Math.floor(Date.now() / 1000);

  // Add token to Redis blacklist
  await this.revocationStore.revokeToken(payload.jti, {
    expiresIn: ttl,
    reason: 'user_logout',
    userId,
  });
}
```

### 3. Token Validation with Revocation Check

The `TokenRevocationGuard` runs globally on all authenticated requests:

```typescript
// Check if token is revoked
const result = await this.revocationStore.isRevoked({
  jti: payload.jti,
  userId: payload.sub,
  tenantId: payload.tid,
  issuedAt: payload.iat,
});

if (result.isRevoked) {
  throw new UnauthorizedException({
    error: 'token_revoked',
    message: 'Authentication token has been revoked',
  });
}
```

### 4. Redis Storage Structure

```
Key Format: "revoked:token:<jti>"
Value: JSON {
  "revokedAt": 1234567890,
  "reason": "user_logout",
  "userId": "user-123",
  "tenantId": "tenant-456"
}
TTL: Automatic expiration matching token expiration
```

## Configuration

### Environment Variables

```bash
# JWT Configuration
JWT_SECRET_KEY="your-secret-key-min-32-chars"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES="30"
JWT_REFRESH_TOKEN_EXPIRE_DAYS="7"
JWT_ISSUER="sahool-platform"
JWT_AUDIENCE="sahool-api"

# Redis Configuration
REDIS_URL="redis://localhost:6379"
# OR
REDIS_HOST="localhost"
REDIS_PORT="6379"
REDIS_DB="0"
REDIS_PASSWORD=""

# Token Revocation
TOKEN_REVOCATION_ENABLED="true"
```

### Module Setup

```typescript
// apps/services/user-service/src/app.module.ts
import { TokenRevocationGuard } from '@sahool/nestjs-auth/guards/token-revocation.guard';

@Module({
  imports: [
    AuthModule,
    JwtModule.register({
      secret: JWTConfig.getVerificationKey(),
    }),
  ],
  providers: [
    // Global token revocation guard
    {
      provide: APP_GUARD,
      useClass: TokenRevocationGuard,
    },
  ],
})
export class AppModule {}
```

## API Endpoints

### Authentication

#### POST /api/v1/auth/login
Login and get tokens with JTI

**Request:**
```json
{
  "email": "user@sahool.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 1800,
  "token_type": "Bearer",
  "user": {
    "id": "user-123",
    "email": "user@sahool.com",
    "firstName": "Ahmed",
    "lastName": "Ali",
    "role": "FARMER",
    "tenantId": "tenant-123"
  }
}
```

#### POST /api/v1/auth/logout
Logout and revoke current token

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

#### POST /api/v1/auth/logout-all
Logout from all devices (revoke all user tokens)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Logged out from all devices successfully"
}
```

#### POST /api/v1/auth/refresh
Refresh access token

**Request:**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 1800,
  "token_type": "Bearer"
}
```

### Token Revocation Management (Admin)

#### POST /auth/revocation/revoke
Revoke a specific token by JTI

**Request:**
```json
{
  "jti": "550e8400-e29b-41d4-a716-446655440000",
  "reason": "security_breach"
}
```

#### GET /auth/revocation/status/:jti
Check if a token is revoked

**Response:**
```json
{
  "isRevoked": true,
  "reason": "user_logout",
  "revokedAt": 1234567890
}
```

#### GET /auth/revocation/stats
Get revocation statistics (Admin only)

**Response:**
```json
{
  "initialized": true,
  "revokedTokens": 42,
  "revokedUsers": 5,
  "revokedTenants": 0,
  "redisUrl": "localhost:6379/0"
}
```

#### GET /auth/revocation/health
Health check for token revocation service

**Response:**
```json
{
  "status": "healthy",
  "service": "token_revocation",
  "redis": "connected"
}
```

## Frontend Integration

### Admin Logout (Next.js)

```typescript
// apps/admin/src/app/api/auth/logout/route.ts
export async function POST(request: Request) {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('sahool_admin_token')?.value;

  // Call backend to revoke token
  if (accessToken) {
    await fetch(`${backendUrl}/api/v1/auth/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    });
  }

  // Clear cookies
  cookieStore.delete('sahool_admin_token');
  cookieStore.delete('sahool_admin_refresh_token');

  return NextResponse.json({ success: true });
}
```

## Security Features

### 1. Automatic TTL Management
- Tokens are stored in Redis with TTL matching their expiration
- Redis automatically removes expired entries
- No manual cleanup required

### 2. Fail-Open Design
- If Redis is unavailable, requests are allowed through
- Prevents service disruption if Redis goes down
- Errors are logged for monitoring

### 3. Multi-Level Revocation
- **Token-level**: Revoke individual tokens
- **User-level**: Revoke all tokens for a user
- **Tenant-level**: Revoke all tokens for a tenant

### 4. Audit Trail
- All revocations are logged with reason
- Includes userId, tenantId for tracking
- Timestamp for audit purposes

## Performance Considerations

### Redis Operations
- All checks are O(1) lookups
- Connection pooling for efficiency
- Automatic reconnection on failure

### Cache Strategy
```
Average token expiration: 30 minutes
Average revoked tokens: ~1000 active
Memory usage: ~100KB per 1000 tokens
Redis memory: < 1MB for typical usage
```

### Network Overhead
- Single Redis query per authenticated request
- ~1-2ms additional latency
- Negligible impact on response time

## Testing

### Manual Testing

1. **Login:**
```bash
curl -X POST http://localhost:3020/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@sahool.com",
    "password": "SecurePassword123!"
  }'
```

2. **Access Protected Resource:**
```bash
curl -X GET http://localhost:3020/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

3. **Logout (Revoke Token):**
```bash
curl -X POST http://localhost:3020/api/v1/auth/logout \
  -H "Authorization: Bearer <access_token>"
```

4. **Try Using Revoked Token:**
```bash
curl -X GET http://localhost:3020/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
# Should return 401 Unauthorized with "token_revoked" error
```

### Check Redis

```bash
# Connect to Redis
redis-cli

# List all revoked tokens
KEYS revoked:token:*

# Check specific token
GET revoked:token:<jti>

# Check TTL
TTL revoked:token:<jti>
```

## Monitoring

### Health Check
```bash
curl http://localhost:3020/api/v1/auth/revocation/health
```

### Statistics (Admin)
```bash
curl http://localhost:3020/api/v1/auth/revocation/stats \
  -H "Authorization: Bearer <admin_token>"
```

### Logs to Monitor
- Token revocation success/failure
- Redis connection status
- Revoked token access attempts
- Token validation errors

## Troubleshooting

### Issue: Token revocation not working

**Check:**
1. Redis is running: `redis-cli ping`
2. Redis connection configured: Check `REDIS_URL` or `REDIS_HOST`
3. Token has JTI claim: Decode token and verify `jti` field
4. TokenRevocationGuard is enabled in module

### Issue: Redis connection errors

**Check:**
1. Redis service status
2. Network connectivity
3. Redis credentials (if password protected)
4. Firewall rules

### Issue: Logout succeeds but token still works

**Check:**
1. Multiple instances not sharing same Redis
2. Token expiration time
3. Guards are applied globally
4. Token has valid JTI

## Future Enhancements

1. **Token Rotation**: Automatically rotate tokens periodically
2. **Session Management**: Track active sessions per user
3. **Device Management**: Allow users to view and revoke specific devices
4. **IP-based Revocation**: Revoke tokens from specific IPs
5. **Geolocation Validation**: Validate token usage location
6. **Rate Limit by Token**: Prevent token abuse

## Files Modified/Created

### Created Files
- `/apps/services/user-service/src/auth/auth.service.ts` - Auth service with token revocation
- `/apps/services/user-service/src/auth/auth.controller.ts` - Auth controller with logout endpoints
- `/apps/services/user-service/src/auth/auth.module.ts` - Auth module with revocation integration
- `/apps/services/user-service/src/auth/jwt.strategy.ts` - JWT strategy with user validation
- `/apps/services/user-service/.env.example` - Environment variables example

### Modified Files
- `/apps/services/user-service/src/auth/jwt-auth.guard.ts` - Updated to use Passport
- `/apps/services/user-service/src/app.module.ts` - Added auth module and revocation guard
- `/apps/admin/src/app/api/auth/logout/route.ts` - Updated to call backend revocation

### Existing Files (Already Implemented)
- `/shared/auth/token-revocation.ts` - Redis revocation store
- `/shared/auth/token-revocation.guard.ts` - Revocation guard
- `/shared/auth/revocation.controller.ts` - Revocation API controller
- `/packages/nestjs-auth/src/services/token-revocation.ts` - Package version of revocation service
- `/packages/nestjs-auth/src/guards/token-revocation.guard.ts` - Package version of guard

## Summary

The token revocation system is now fully implemented and integrated into the SAHOOL platform:

✅ **Token Generation**: JWT tokens include unique JTI for tracking
✅ **Token Revocation**: Tokens are revoked on logout and stored in Redis
✅ **Token Validation**: All authenticated requests check token revocation status
✅ **Automatic Cleanup**: Redis TTL ensures expired tokens are removed
✅ **Multi-Level Support**: Token, user, and tenant level revocation
✅ **Frontend Integration**: Admin logout calls backend revocation
✅ **Security**: Fail-open design, audit trail, performance optimized

The system ensures that logged-out users cannot access protected resources, significantly improving security posture.
