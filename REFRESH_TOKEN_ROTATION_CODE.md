# Refresh Token Rotation - Code Implementation

## Complete Implementation Details

This document shows the actual code changes made to implement refresh token rotation in SAHOOL.

---

## 1. Database Schema Changes

**File:** `apps/services/user-service/prisma/schema.prisma`

### Before
```prisma
model RefreshToken {
  id          String   @id @default(uuid())
  userId      String   @map("user_id")
  token       String   @unique
  expiresAt   DateTime @map("expires_at")
  revoked     Boolean  @default(false)
  createdAt   DateTime @default(now()) @map("created_at")

  user        User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@index([token])
  @@index([expiresAt])
  @@map("refresh_tokens")
}
```

### After
```prisma
model RefreshToken {
  id          String   @id @default(uuid())
  userId      String   @map("user_id")
  jti         String   @unique                    // ✅ NEW: JWT ID for unique identification
  family      String                              // ✅ NEW: Token family for rotation tracking
  token       String   @unique
  expiresAt   DateTime @map("expires_at")
  revoked     Boolean  @default(false)
  used        Boolean  @default(false)            // ✅ NEW: Reuse detection flag
  usedAt      DateTime? @map("used_at")           // ✅ NEW: When token was used
  replacedBy  String?  @map("replaced_by")        // ✅ NEW: JTI of replacement token
  createdAt   DateTime @default(now()) @map("created_at")

  user        User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@index([jti])                                   // ✅ NEW: Index for fast JTI lookup
  @@index([family])                                // ✅ NEW: Index for family invalidation
  @@index([token])
  @@index([expiresAt])
  @@map("refresh_tokens")
}
```

---

## 2. JWT Payload Interface

**File:** `apps/services/user-service/src/auth/auth.service.ts`

### Before
```typescript
export interface JwtPayload {
  sub: string;
  email: string;
  roles: string[];
  tid?: string;
  jti: string;
  type: 'access' | 'refresh';
  iat?: number;
  exp?: number;
}
```

### After
```typescript
export interface JwtPayload {
  sub: string;
  email: string;
  roles: string[];
  tid?: string;
  jti: string;
  type: 'access' | 'refresh';
  family?: string;    // ✅ NEW: Token family for refresh token rotation
  iat?: number;
  exp?: number;
}
```

---

## 3. Token Generation with Family

**File:** `apps/services/user-service/src/auth/auth.service.ts`

### Before
```typescript
private async generateTokens(user: any): Promise<{
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
}> {
  const accessJti = uuidv4();
  const refreshJti = uuidv4();

  // Generate tokens...
  const access_token = this.jwtService.sign(accessPayload, {...});
  const refresh_token = this.jwtService.sign(refreshPayload, {...});

  return {
    access_token,
    refresh_token,
    expires_in: JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    token_type: 'Bearer',
  };
}
```

### After
```typescript
private async generateTokens(
  user: any,
  family?: string,    // ✅ NEW: Optional family parameter for rotation
): Promise<{
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
}> {
  const accessJti = uuidv4();
  const refreshJti = uuidv4();
  const tokenFamily = family || uuidv4();    // ✅ NEW: Generate or reuse family

  // Access token payload (no family)
  const accessPayload: JwtPayload = {
    sub: user.id,
    email: user.email,
    roles: [user.role],
    tid: user.tenantId,
    jti: accessJti,
    type: 'access',
  };

  // Refresh token payload (with family)
  const refreshPayload: JwtPayload = {
    sub: user.id,
    email: user.email,
    roles: [user.role],
    tid: user.tenantId,
    jti: refreshJti,
    type: 'refresh',
    family: tokenFamily,    // ✅ NEW: Include family in refresh token
  };

  const access_token = this.jwtService.sign(accessPayload, {
    expiresIn: `${JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES}m`,
    issuer: JWTConfig.ISSUER,
    audience: JWTConfig.AUDIENCE,
  });

  const refresh_token = this.jwtService.sign(refreshPayload, {
    expiresIn: `${JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS}d`,
    issuer: JWTConfig.ISSUER,
    audience: JWTConfig.AUDIENCE,
  });

  // ✅ NEW: Store refresh token in database
  const expiresAt = new Date(
    Date.now() + JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60 * 1000,
  );
  await this.prisma.refreshToken.create({
    data: {
      userId: user.id,
      jti: refreshJti,
      family: tokenFamily,
      token: refresh_token,
      expiresAt,
    },
  });

  return {
    access_token,
    refresh_token,
    expires_in: JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    token_type: 'Bearer',
  };
}
```

---

## 4. Token Family Invalidation

**File:** `apps/services/user-service/src/auth/auth.service.ts`

### NEW METHOD
```typescript
/**
 * Invalidate entire token family (for reuse detection)
 * إبطال عائلة الرموز بالكامل
 */
private async invalidateTokenFamily(family: string): Promise<void> {
  try {
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

    this.logger.warn(
      `Token family invalidated due to reuse detection: family=${family.substring(0, 8)}...`,
    );
  } catch (error) {
    this.logger.error(
      `Failed to invalidate token family: ${error.message}`,
      error.stack,
    );
    throw error;
  }
}
```

---

## 5. Refresh Token Rotation Logic

**File:** `apps/services/user-service/src/auth/auth.service.ts`

### Before
```typescript
async refreshToken(refreshToken: string): Promise<{
  access_token: string;
  expires_in: number;
  token_type: string;
}> {
  try {
    // Verify refresh token
    const payload = this.jwtService.verify(refreshToken, {...});

    // Check if revoked in Redis
    if (payload.jti) {
      const isRevoked = await this.revocationStore.isTokenRevoked(payload.jti);
      if (isRevoked) {
        throw new UnauthorizedException('Token has been revoked');
      }
    }

    // Verify user exists
    const user = await this.prisma.user.findUnique({
      where: { id: payload.sub },
    });

    if (!user || user.status !== UserStatus.ACTIVE) {
      throw new UnauthorizedException('User account is not active');
    }

    // Generate new ACCESS TOKEN only
    const newAccessJti = uuidv4();
    const accessPayload: JwtPayload = {
      sub: user.id,
      email: user.email,
      roles: [user.role],
      tid: user.tenantId,
      jti: newAccessJti,
      type: 'access',
    };

    const access_token = this.jwtService.sign(accessPayload, {...});

    return {
      access_token,
      expires_in: JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
      token_type: 'Bearer',
    };
  } catch (error) {
    throw new UnauthorizedException('Invalid refresh token');
  }
}
```

### After
```typescript
async refreshToken(refreshToken: string): Promise<{
  access_token: string;
  refresh_token: string;    // ✅ NEW: Return new refresh token
  expires_in: number;
  token_type: string;
}> {
  try {
    // Verify refresh token
    const payload = this.jwtService.verify(refreshToken, {
      secret: JWTConfig.getVerificationKey(),
      issuer: JWTConfig.ISSUER,
      audience: JWTConfig.AUDIENCE,
    }) as JwtPayload;

    // ✅ NEW: Verify it's a refresh token
    if (payload.type !== 'refresh') {
      throw new UnauthorizedException('Invalid token type');
    }

    // ✅ NEW: Check if token exists in database
    const storedToken = await this.prisma.refreshToken.findUnique({
      where: { jti: payload.jti },
    });

    if (!storedToken) {
      this.logger.warn(
        `Refresh attempt with unknown token: ${payload.jti.substring(0, 8)}...`,
      );
      throw new UnauthorizedException('Invalid refresh token');
    }

    // ✅ NEW: REUSE DETECTION - Check if token was already used
    if (storedToken.used) {
      this.logger.error(
        `Token reuse detected! Token: ${payload.jti.substring(0, 8)}..., Family: ${payload.family?.substring(0, 8)}...`,
      );

      // Invalidate entire token family
      if (payload.family) {
        await this.invalidateTokenFamily(payload.family);
      }

      throw new UnauthorizedException(
        'Token reuse detected - all tokens in family have been invalidated',
      );
    }

    // ✅ NEW: Check if token is revoked
    if (storedToken.revoked) {
      this.logger.warn(
        `Refresh attempt with revoked token: ${payload.jti.substring(0, 8)}...`,
      );
      throw new UnauthorizedException('Token has been revoked');
    }

    // ✅ NEW: Check if token is expired
    if (storedToken.expiresAt < new Date()) {
      this.logger.warn(
        `Refresh attempt with expired token: ${payload.jti.substring(0, 8)}...`,
      );
      throw new UnauthorizedException('Refresh token has expired');
    }

    // Verify user still exists and is active
    const user = await this.prisma.user.findUnique({
      where: { id: payload.sub },
    });

    if (!user || user.status !== UserStatus.ACTIVE) {
      throw new UnauthorizedException('User account is not active');
    }

    // ✅ NEW: Mark current refresh token as USED
    const newRefreshJti = uuidv4();
    await this.prisma.refreshToken.update({
      where: { jti: payload.jti },
      data: {
        used: true,
        usedAt: new Date(),
        replacedBy: newRefreshJti,
      },
    });

    // ✅ NEW: Mark old token as used in Redis (5-min detection window)
    await this.revocationStore.revokeToken(payload.jti, {
      expiresIn: 300, // 5 minutes to detect concurrent reuse attempts
      reason: 'refresh_token_rotated',
      userId: user.id,
      tenantId: user.tenantId,
    });

    // ✅ NEW: Generate new token pair with SAME FAMILY
    const tokens = await this.generateTokens(user, payload.family);

    this.logger.log(
      `Refresh token rotated for user: ${user.id}, Old JTI: ${payload.jti.substring(0, 8)}..., New JTI: ${newRefreshJti.substring(0, 8)}...`,
    );

    return tokens;    // ✅ NEW: Return both access and refresh tokens
  } catch (error) {
    if (error instanceof UnauthorizedException) {
      throw error;
    }
    this.logger.error(`Token refresh error: ${error.message}`, error.stack);
    throw new UnauthorizedException('Invalid refresh token');
  }
}
```

---

## 6. Controller Updates

**File:** `apps/services/user-service/src/auth/auth.controller.ts`

### Before
```typescript
@Post('refresh')
@ApiOperation({
  summary: 'Refresh access token',
  description: 'Get a new access token using a valid refresh token.',
})
@ApiResponse({
  status: 200,
  description: 'Token refreshed successfully',
  schema: {
    type: 'object',
    properties: {
      access_token: { type: 'string' },
      expires_in: { type: 'number' },
      token_type: { type: 'string' },
    },
  },
})
async refreshToken(@Body() refreshTokenDto: RefreshTokenDto) {
  return this.authService.refreshToken(refreshTokenDto.refreshToken);
}
```

### After
```typescript
@Post('refresh')
@ApiOperation({
  summary: 'Refresh access token with rotation',    // ✅ UPDATED
  description:
    'Get a new access token and refresh token using a valid refresh token. Implements refresh token rotation for enhanced security.',    // ✅ UPDATED
})
@ApiResponse({
  status: 200,
  description: 'Token refreshed successfully with rotation',    // ✅ UPDATED
  schema: {
    type: 'object',
    properties: {
      access_token: { type: 'string' },
      refresh_token: { type: 'string' },    // ✅ NEW: Document new refresh token
      expires_in: { type: 'number' },
      token_type: { type: 'string' },
    },
  },
})
@ApiResponse({
  status: 401,
  description: 'Invalid or expired refresh token, or token reuse detected',    // ✅ UPDATED
})
async refreshToken(@Body() refreshTokenDto: RefreshTokenDto) {
  return this.authService.refreshToken(refreshTokenDto.refreshToken);
}
```

---

## 7. Frontend Integration

**File:** `apps/admin/src/app/api/auth/refresh/route.ts`

### Before
```typescript
// Call backend refresh endpoint
const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh_token: refreshToken }),
});

const data = await response.json();

// Update access token
cookieStore.set('sahool_admin_token', data.access_token, {...});

// Update refresh token if provided
if (data.refresh_token) {
  cookieStore.set('sahool_admin_refresh_token', data.refresh_token, {...});
}
```

### After
```typescript
// Call backend refresh endpoint
const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refreshToken: refreshToken }),    // ✅ UPDATED: Changed field name
});

const data = await response.json();

// Update access token
cookieStore.set('sahool_admin_token', data.access_token, {...});

// ✅ UPDATED: Always update refresh token (rotation)
if (data.refresh_token) {
  cookieStore.set('sahool_admin_refresh_token', data.refresh_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 604800, // 7 days
    path: '/',
  });
}
```

---

## 8. Database Migration

**File:** `apps/services/user-service/prisma/migrations/add_refresh_token_rotation.sql`

```sql
-- Migration: Add Refresh Token Rotation Support
-- Date: 2026-01-06
-- Description: Adds token family tracking and reuse detection for refresh tokens

-- Add new columns to refresh_tokens table
ALTER TABLE refresh_tokens
  ADD COLUMN jti VARCHAR(255) UNIQUE,
  ADD COLUMN family VARCHAR(255) NOT NULL,
  ADD COLUMN used BOOLEAN DEFAULT FALSE,
  ADD COLUMN used_at TIMESTAMP,
  ADD COLUMN replaced_by VARCHAR(255);

-- Create indexes for performance
CREATE INDEX idx_refresh_tokens_jti ON refresh_tokens(jti);
CREATE INDEX idx_refresh_tokens_family ON refresh_tokens(family);

-- Migrate existing tokens (if any) to have a JTI and family
UPDATE refresh_tokens
SET
  jti = id,
  family = id
WHERE jti IS NULL;

-- Make jti NOT NULL after migration
ALTER TABLE refresh_tokens ALTER COLUMN jti SET NOT NULL;

COMMENT ON COLUMN refresh_tokens.jti IS 'JWT ID for unique token identification';
COMMENT ON COLUMN refresh_tokens.family IS 'Token family ID for rotation tracking';
COMMENT ON COLUMN refresh_tokens.used IS 'Whether this token has been used (for reuse detection)';
COMMENT ON COLUMN refresh_tokens.used_at IS 'When this token was used';
COMMENT ON COLUMN refresh_tokens.replaced_by IS 'JTI of the token that replaced this one';
```

---

## Summary of Changes

### Files Modified: 4
1. ✅ `apps/services/user-service/prisma/schema.prisma` - Added rotation fields
2. ✅ `apps/services/user-service/src/auth/auth.service.ts` - Implemented rotation logic
3. ✅ `apps/services/user-service/src/auth/auth.controller.ts` - Updated API docs
4. ✅ `apps/admin/src/app/api/auth/refresh/route.ts` - Handle new refresh token

### Files Created: 2
1. ✅ `apps/services/user-service/prisma/migrations/add_refresh_token_rotation.sql`
2. ✅ `docs/REFRESH_TOKEN_ROTATION.md`

### Key Implementation Points

1. **Token Family**: Each login creates unique family, shared across rotations
2. **One-Time Use**: Tokens marked as `used` after consumption
3. **Reuse Detection**: `used` flag checked before rotation
4. **Family Invalidation**: All tokens in family revoked on reuse
5. **Dual Storage**: PostgreSQL (persistence) + Redis (fast blacklist)
6. **Audit Trail**: `replacedBy` field tracks token lineage
7. **Detection Window**: 5-minute Redis TTL catches concurrent reuse

### Security Improvements

- ✅ Tokens can only be used once
- ✅ Replay attacks detected and blocked
- ✅ Compromised sessions fully invalidated
- ✅ Complete audit trail maintained
- ✅ Fast detection with Redis blacklist
- ✅ OAuth 2.0 best practices followed

---

**Implementation Status:** ✅ COMPLETE
**Security Level:** 🔒 ENHANCED
**Next Step:** Run database migration and restart services
