# Refresh Token Rotation Implementation

## Overview

This document describes the refresh token rotation security feature implemented in the SAHOOL authentication system. Refresh token rotation is a security best practice that mitigates the risk of token theft and replay attacks.

## Problem Statement

**Before:** Refresh tokens could be reused indefinitely until expiration, making them vulnerable to:

- Token theft and replay attacks
- Unauthorized access if a token is compromised
- No detection mechanism for token reuse

## Solution

**After:** Implemented automatic refresh token rotation with:

1. **One-time use tokens:** Each refresh token can only be used once
2. **Token family tracking:** All rotated tokens share a family ID
3. **Reuse detection:** Detects when a used token is replayed
4. **Family invalidation:** Invalidates all tokens in a family when reuse is detected
5. **Dual storage:** Tokens stored in both PostgreSQL (persistence) and Redis (fast blacklisting)

## Architecture

### Token Family Flow

```
Login
  └─> Token Family A created
      ├─> Refresh Token 1 (JTI: abc123, Family: A)
      └─> Access Token 1

First Refresh
  ├─> Token 1 marked as USED
  ├─> Token 1 added to Redis blacklist (5 min TTL)
  └─> New tokens generated
      ├─> Refresh Token 2 (JTI: def456, Family: A)
      └─> Access Token 2

Second Refresh
  ├─> Token 2 marked as USED
  ├─> Token 2 added to Redis blacklist
  └─> New tokens generated
      ├─> Refresh Token 3 (JTI: ghi789, Family: A)
      └─> Access Token 3

Reuse Attack (using Token 1 again)
  ├─> Detect Token 1 is already USED
  ├─> Invalidate ENTIRE Family A
  │   ├─> Mark all tokens in family as REVOKED (PostgreSQL)
  │   └─> Blacklist all tokens in family (Redis)
  └─> Throw UnauthorizedException
```

## Implementation Details

### 1. Database Schema Updates

**File:** `/home/user/sahool-unified-v15-idp/apps/services/user-service/prisma/schema.prisma`

Added to `RefreshToken` model:

- `jti`: Unique JWT ID for token identification
- `family`: Token family ID for rotation tracking
- `used`: Boolean flag indicating if token was used
- `usedAt`: Timestamp of when token was used
- `replacedBy`: JTI of the replacement token

```prisma
model RefreshToken {
  id          String   @id @default(uuid())
  userId      String   @map("user_id")
  jti         String   @unique
  family      String   // Token family for rotation tracking
  token       String   @unique
  expiresAt   DateTime @map("expires_at")
  revoked     Boolean  @default(false)
  used        Boolean  @default(false)
  usedAt      DateTime? @map("used_at")
  replacedBy  String?  @map("replaced_by")
  createdAt   DateTime @default(now()) @map("created_at")

  user        User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@index([jti])
  @@index([family])
  @@index([token])
  @@index([expiresAt])
  @@map("refresh_tokens")
}
```

### 2. JWT Payload Updates

**File:** `/home/user/sahool-unified-v15-idp/apps/services/user-service/src/auth/auth.service.ts`

Added `family` field to JwtPayload for refresh tokens:

```typescript
export interface JwtPayload {
  sub: string;
  email: string;
  roles: string[];
  tid?: string;
  jti: string;
  type: "access" | "refresh";
  family?: string; // Token family for refresh token rotation
  iat?: number;
  exp?: number;
}
```

### 3. Token Generation with Family

Updated `generateTokens()` method:

- Accepts optional `family` parameter
- Generates new family ID on initial login
- Reuses family ID on token rotation
- Stores refresh token in PostgreSQL with family information

```typescript
private async generateTokens(
  user: any,
  family?: string,
): Promise<{
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
}> {
  const tokenFamily = family || uuidv4();

  // ... token generation ...

  // Store refresh token in database
  await this.prisma.refreshToken.create({
    data: {
      userId: user.id,
      jti: refreshJti,
      family: tokenFamily,
      token: refresh_token,
      expiresAt,
    },
  });
}
```

### 4. Token Family Invalidation

New method `invalidateTokenFamily()`:

- Marks all tokens in family as revoked in PostgreSQL
- Blacklists all tokens in family in Redis
- Logs security warning

```typescript
private async invalidateTokenFamily(family: string): Promise<void> {
  // Mark all tokens in family as revoked in database
  await this.prisma.refreshToken.updateMany({
    where: { family },
    data: { revoked: true },
  });

  // Get all tokens in family to revoke in Redis
  const familyTokens = await this.prisma.refreshToken.findMany({
    where: { family },
    select: { jti: true },
  });

  // Revoke each token in Redis
  const revokePromises = familyTokens.map((token) =>
    this.revocationStore.revokeToken(token.jti, {
      expiresIn: JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
      reason: 'token_reuse_detected',
    }),
  );

  await Promise.all(revokePromises);
}
```

### 5. Refresh Token Rotation

Completely rewritten `refreshToken()` method:

**Security Checks:**

1. Verify JWT signature and expiration
2. Verify token type is 'refresh'
3. Check token exists in database
4. **Check if token was already used (reuse detection)**
5. Check if token is revoked
6. Check if token is expired
7. Verify user account is still active

**Rotation Process:**

1. Mark current token as USED in database
2. Store `replacedBy` JTI for audit trail
3. Blacklist old token in Redis (5 min TTL for detection window)
4. Generate new token pair with same family
5. Return new access and refresh tokens

**Reuse Detection:**

```typescript
// Check if token was already used (replay attack detection)
if (storedToken.used) {
  this.logger.error(
    `Token reuse detected! Token: ${payload.jti.substring(0, 8)}..., Family: ${payload.family?.substring(0, 8)}...`,
  );

  // Invalidate entire token family
  if (payload.family) {
    await this.invalidateTokenFamily(payload.family);
  }

  throw new UnauthorizedException(
    "Token reuse detected - all tokens in family have been invalidated",
  );
}
```

### 6. API Updates

**Controller:** `/home/user/sahool-unified-v15-idp/apps/services/user-service/src/auth/auth.controller.ts`

Updated `/auth/refresh` endpoint to return new refresh token:

```typescript
@ApiResponse({
  status: 200,
  description: 'Token refreshed successfully with rotation',
  schema: {
    type: 'object',
    properties: {
      access_token: { type: 'string' },
      refresh_token: { type: 'string' }, // NEW: rotated refresh token
      expires_in: { type: 'number' },
      token_type: { type: 'string' },
    },
  },
})
async refreshToken(@Body() refreshTokenDto: RefreshTokenDto) {
  return this.authService.refreshToken(refreshTokenDto.refreshToken);
}
```

### 7. Frontend Updates

**Admin App:** `/home/user/sahool-unified-v15-idp/apps/admin/src/app/api/auth/refresh/route.ts`

Updated to store new refresh token in cookies:

```typescript
// Update refresh token (always rotated now)
if (data.refresh_token) {
  cookieStore.set("sahool_admin_refresh_token", data.refresh_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    maxAge: 604800, // 7 days
    path: "/",
  });
}
```

## Security Benefits

### 1. Token Reuse Detection

- Each token can only be used once
- Reuse triggers immediate security response
- All related tokens are invalidated

### 2. Reduced Attack Window

- Used tokens blacklisted in Redis for 5 minutes
- Detects concurrent reuse attempts
- Fast response time for security events

### 3. Audit Trail

- Complete history of token rotation in database
- `replacedBy` field tracks token lineage
- Security logs for all reuse attempts

### 4. Family-based Invalidation

- Single compromised token doesn't invalidate all user sessions
- Only affected token family is invalidated
- Other login sessions remain valid

## Configuration

### Environment Variables

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis Configuration (for token blacklisting)
REDIS_URL=redis://localhost:6379/0
# OR
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=optional-password
```

### Token Expiration Times

- **Access Token:** 30 minutes (default)
- **Refresh Token:** 7 days (default)
- **Used Token Blacklist TTL:** 5 minutes (detection window)

## Migration

### 1. Run Prisma Migration

```bash
cd apps/services/user-service
npx prisma migrate dev --name add_refresh_token_rotation
```

Or run the SQL migration manually:

```bash
psql -U your_user -d your_database -f prisma/migrations/add_refresh_token_rotation.sql
```

### 2. Generate Prisma Client

```bash
npx prisma generate
```

### 3. Restart Services

```bash
# Restart user service
docker-compose restart user-service

# Or if running locally
npm run dev
```

## Testing

### Test Token Rotation

```bash
# 1. Login
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@sahool.com","password":"password123"}'

# Response:
# {
#   "access_token": "eyJ...",
#   "refresh_token": "eyJ...",
#   "expires_in": 1800,
#   "token_type": "Bearer"
# }

# 2. Refresh token (first time - should work)
curl -X POST http://localhost:3000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refreshToken":"eyJ..."}'

# Response:
# {
#   "access_token": "eyJ...",
#   "refresh_token": "eyJ...",  # NEW rotated token
#   "expires_in": 1800,
#   "token_type": "Bearer"
# }

# 3. Try to reuse old refresh token (should fail)
curl -X POST http://localhost:3000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refreshToken":"eyJ..."}'  # Old token

# Response:
# {
#   "statusCode": 401,
#   "message": "Token reuse detected - all tokens in family have been invalidated"
# }
```

### Test Database State

```sql
-- Check refresh tokens for a user
SELECT id, jti, family, used, used_at, replaced_by, revoked, created_at
FROM refresh_tokens
WHERE user_id = 'your-user-id'
ORDER BY created_at DESC;

-- Check token family
SELECT jti, used, revoked, created_at, replaced_by
FROM refresh_tokens
WHERE family = 'family-id'
ORDER BY created_at DESC;
```

### Test Redis Blacklist

```bash
# Connect to Redis
redis-cli

# Check for revoked tokens
KEYS revoked:token:*

# Check specific token
GET revoked:token:your-jti-here

# Check TTL
TTL revoked:token:your-jti-here
```

## Monitoring

### Key Metrics to Monitor

1. **Token Reuse Attempts:** Count of reuse detection events
2. **Family Invalidations:** Number of families invalidated
3. **Token Rotation Rate:** Successful refreshes per time period
4. **Failed Refresh Attempts:** Invalid/expired/revoked tokens

### Log Messages

**Successful Rotation:**

```
Token refreshed for user: usr_123, Old JTI: abc123..., New JTI: def456...
```

**Reuse Detection:**

```
Token reuse detected! Token: abc123..., Family: xyz789...
Token family invalidated due to reuse detection: family=xyz789...
```

## Best Practices

### Client Implementation

1. **Always store new refresh token** returned from refresh endpoint
2. **Never reuse old refresh tokens** after rotation
3. **Handle 401 errors** by redirecting to login
4. **Implement retry logic** with exponential backoff
5. **Use secure storage** (httpOnly cookies for web, secure storage for mobile)

### Server Configuration

1. **Set appropriate TTLs** based on security requirements
2. **Monitor reuse attempts** for security anomalies
3. **Clean up expired tokens** periodically from database
4. **Use Redis for fast blacklisting** to reduce database load
5. **Log all security events** for audit trail

## Troubleshooting

### Issue: "Token reuse detected" on legitimate requests

**Cause:** Race condition - client made concurrent refresh requests

**Solution:**

- Implement request queuing on client side
- Use mutex/lock for refresh operations
- Increase Redis TTL for detection window

### Issue: All user sessions invalidated unexpectedly

**Cause:** Token reuse in one session invalidated entire family

**Solution:**

- Each login creates a NEW family
- Different devices/sessions have different families
- Only the compromised session is invalidated

### Issue: High Redis memory usage

**Cause:** Many used tokens in Redis

**Solution:**

- Reduce detection window TTL (currently 5 minutes)
- Implement Redis eviction policy (LRU)
- Monitor and adjust based on usage patterns

## References

- [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
- [Refresh Token Rotation](https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation)
- [OWASP Token Security](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)

## Files Modified

1. `/home/user/sahool-unified-v15-idp/apps/services/user-service/prisma/schema.prisma`
2. `/home/user/sahool-unified-v15-idp/apps/services/user-service/src/auth/auth.service.ts`
3. `/home/user/sahool-unified-v15-idp/apps/services/user-service/src/auth/auth.controller.ts`
4. `/home/user/sahool-unified-v15-idp/apps/admin/src/app/api/auth/refresh/route.ts`

## Files Created

1. `/home/user/sahool-unified-v15-idp/apps/services/user-service/prisma/migrations/add_refresh_token_rotation.sql`
2. `/home/user/sahool-unified-v15-idp/docs/REFRESH_TOKEN_ROTATION.md`
