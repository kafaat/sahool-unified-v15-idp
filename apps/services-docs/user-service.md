# User Service Documentation

## Service Overview

| Property | Value |
|----------|-------|
| **Service Name** | user-service |
| **Type** | Node.js / NestJS |
| **Port** | 3025 |
| **Version** | 16.0.0 |
| **Description** | User management, authentication, and authorization service for SAHOOL platform |
| **Arabic Name** | خدمة إدارة المستخدمين |

### Purpose

The user-service handles all user-related operations including:
- User registration and authentication (JWT-based)
- User profile management
- Role-based access control (RBAC)
- Session management with token revocation
- Multi-tenant user isolation
- Email and phone verification
- Password reset (email and OTP-based)
- Account lockout protection

### Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | NestJS 10.4.x |
| Language | TypeScript 5.7.x |
| ORM | Prisma 5.22.x |
| Database | PostgreSQL 16+ (via PgBouncer) |
| Cache | Redis 7.x (token revocation) |
| Authentication | Passport.js + JWT |
| Validation | class-validator, class-transformer |
| API Documentation | Swagger/OpenAPI |
| Password Hashing | bcryptjs (12 rounds) |

---

## API Endpoints

### Authentication Endpoints (Public)

#### POST /api/v1/auth/login
Login with email and password.

**Rate Limit:** 5 requests/minute

**Request Body:**
```json
{
  "email": "user@sahool.com",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 1800,
  "token_type": "Bearer",
  "user": {
    "id": "usr_123456",
    "email": "user@sahool.com",
    "firstName": "Ahmed",
    "lastName": "Ali",
    "role": "FARMER",
    "tenantId": "tenant_123"
  }
}
```

**Error Responses:**
- `401`: Invalid credentials, account locked, or user inactive
- `429`: Too many login attempts

---

#### POST /api/v1/auth/register
Register a new user account.

**Rate Limit:** 10 requests/minute

**Request Body:**
```json
{
  "email": "farmer@sahool.com",
  "password": "SecurePassword123!",
  "firstName": "Ahmed",
  "lastName": "Mohammed",
  "phone": "+967712345678",
  "tenantId": "tenant_123"
}
```

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| email | string | Yes | Valid email format |
| password | string | Yes | Min 8 chars, uppercase, lowercase, number, special char |
| firstName | string | Yes | 2-50 characters |
| lastName | string | Yes | 2-50 characters |
| phone | string | No | Yemen phone format (+967XXXXXXXXX) |
| tenantId | string | No | Defaults to 'a0000000-0000-0000-0000-000000000001' |

**Response (201):**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_in": 1800,
  "token_type": "Bearer",
  "user": {
    "id": "usr_123456",
    "email": "farmer@sahool.com",
    "firstName": "Ahmed",
    "lastName": "Mohammed",
    "role": "FARMER",
    "tenantId": "default-tenant"
  }
}
```

**Notes:**
- New users get `FARMER` role by default
- Status is set to `ACTIVE` for immediate login
- Email verification is not enforced (emailVerified: false)

---

#### POST /api/v1/auth/forgot-password
Request password reset email.

**Rate Limit:** 3 requests/minute

**Request Body:**
```json
{
  "email": "user@sahool.com"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "If an account with that email exists, a password reset link has been sent."
}
```

**Security:** Always returns success to prevent email enumeration.

---

#### POST /api/v1/auth/reset-password
Reset password using token from email.

**Rate Limit:** 5 requests/minute

**Request Body:**
```json
{
  "token": "abc123def456...",
  "newPassword": "NewSecurePassword123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Password has been reset successfully. Please login with your new password."
}
```

**Notes:**
- Token valid for 1 hour
- All existing refresh tokens are revoked on password reset
- Failed login attempts are reset

---

#### POST /api/v1/auth/send-otp
Send OTP for password reset or phone verification.

**Rate Limit:** 3 requests/minute

**Request Body:**
```json
{
  "identifier": "+967712345678",
  "channel": "sms",
  "purpose": "password_reset",
  "language": "ar"
}
```

| Field | Type | Required | Options |
|-------|------|----------|---------|
| identifier | string | Yes | Phone number or email |
| channel | string | Yes | `sms`, `whatsapp`, `telegram`, `email` |
| purpose | string | Yes | `password_reset`, `verify_phone` |
| language | string | No | Language code (default: 'en') |

**Response (200):**
```json
{
  "success": true,
  "message": "OTP has been sent successfully.",
  "expiresIn": 300
}
```

**Dependency:** Requires notification-service at `NOTIFICATION_SERVICE_URL`

---

#### POST /api/v1/auth/verify-otp
Verify OTP and get reset token.

**Rate Limit:** 5 requests/minute

**Request Body:**
```json
{
  "identifier": "+967712345678",
  "otpCode": "123456",
  "purpose": "password_reset"
}
```

**Response (200 - password_reset):**
```json
{
  "success": true,
  "message": "OTP verified successfully. Use the reset token to set a new password.",
  "resetToken": "abc123def456..."
}
```

**Response (200 - verify_phone):**
```json
{
  "success": true,
  "message": "Phone number verified successfully.",
  "verified": true
}
```

---

#### POST /api/v1/auth/refresh
Refresh access token with rotation.

**Rate Limit:** 10 requests/minute

**Request Body:**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_in": 1800,
  "token_type": "Bearer"
}
```

**Security Features:**
- Refresh token rotation (old token marked as used)
- Token reuse detection (invalidates entire token family)
- User status validation

---

### Authentication Endpoints (Protected)

#### POST /api/v1/auth/logout
Logout and revoke current token.

**Authentication:** Bearer token required

**Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

#### POST /api/v1/auth/logout-all
Logout from all devices.

**Authentication:** Bearer token required

**Response (200):**
```json
{
  "success": true,
  "message": "Logged out from all devices successfully"
}
```

---

#### POST /api/v1/auth/me
Get current authenticated user information.

**Authentication:** Bearer token required

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "usr_123456",
    "email": "user@sahool.com",
    "roles": ["FARMER"],
    "tenantId": "tenant_123"
  }
}
```

---

### User Management Endpoints (Protected)

#### POST /api/v1/users
Create a new user (Admin/Manager only for role assignment).

**Authentication:** Bearer token required

**Request Body:**
```json
{
  "tenantId": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "firstName": "Ahmed",
  "lastName": "Mohammed",
  "phone": "+967712345678",
  "role": "FARMER",
  "status": "PENDING",
  "emailVerified": false,
  "phoneVerified": false
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "...",
    "email": "user@example.com",
    "firstName": "Ahmed",
    "lastName": "Mohammed",
    "role": "FARMER",
    "status": "PENDING",
    "createdAt": "...",
    "updatedAt": "..."
  },
  "message": "User created successfully"
}
```

---

#### GET /api/v1/users
Get all users (Admin/Manager only).

**Authentication:** Bearer token required
**Authorization:** ADMIN or MANAGER role

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| tenantId | string | Filter by tenant |
| role | string | Filter by role (ADMIN, MANAGER, FARMER, WORKER, VIEWER) |
| status | string | Filter by status (ACTIVE, INACTIVE, SUSPENDED, PENDING) |
| skip | number | Pagination offset |
| take | number | Page size (max 100, default 20) |

**Response (200):**
```json
{
  "success": true,
  "data": [...],
  "count": 25,
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 25,
    "totalPages": 2,
    "hasNext": true,
    "hasPrev": false
  }
}
```

---

#### GET /api/v1/users/:id
Get a user by ID.

**Authentication:** Bearer token required
**Authorization:** Own data or ADMIN role

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "...",
    "email": "user@example.com",
    "firstName": "Ahmed",
    "lastName": "Mohammed",
    "phone": "+967712345678",
    "role": "FARMER",
    "status": "ACTIVE",
    "emailVerified": true,
    "phoneVerified": false,
    "lastLoginAt": "2024-01-20T10:30:00Z",
    "tenantId": "...",
    "profile": {
      "id": "...",
      "avatarUrl": "...",
      "address": "...",
      "city": "...",
      "region": "..."
    },
    "sessions": [...]
  }
}
```

---

#### GET /api/v1/users/email/:email
Get a user by email (Admin/Manager only).

**Authentication:** Bearer token required
**Authorization:** ADMIN or MANAGER role
**Rate Limit:** 10 requests/minute

---

#### PUT /api/v1/users/:id
Update a user.

**Authentication:** Bearer token required
**Authorization:** Own data or ADMIN role

**Request Body:** (all fields optional)
```json
{
  "email": "new@example.com",
  "password": "NewPassword123!",
  "firstName": "Ahmed",
  "lastName": "Mohammed",
  "phone": "+967712345678",
  "role": "MANAGER",
  "status": "ACTIVE",
  "emailVerified": true,
  "phoneVerified": true
}
```

---

#### DELETE /api/v1/users/:id
Soft delete a user (sets status to INACTIVE).

**Authentication:** Bearer token required
**Authorization:** Own data or ADMIN role

---

#### DELETE /api/v1/users/:id/hard
Permanently delete a user (Admin only).

**Authentication:** Bearer token required
**Authorization:** ADMIN role only

---

#### GET /api/v1/users/stats/count/:tenantId
Get user count by tenant (Admin/Manager only).

**Authentication:** Bearer token required
**Authorization:** ADMIN or MANAGER role

**Response (200):**
```json
{
  "success": true,
  "data": { "count": 150 }
}
```

---

#### GET /api/v1/users/stats/active
Get active users count (Admin/Manager only).

**Authentication:** Bearer token required
**Authorization:** ADMIN or MANAGER role

**Response (200):**
```json
{
  "success": true,
  "data": { "count": 120 }
}
```

---

### Health Endpoints

#### GET /api/v1/health
Basic health check.

**Response (200):**
```json
{
  "success": true,
  "service": "user-service",
  "version": "16.0.0",
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00Z",
  "uptime": 86400
}
```

---

#### GET /api/v1/healthz
Kubernetes liveness probe.

---

#### GET /api/v1/readyz
Kubernetes readiness probe with dependency checks.

**Response (200):**
```json
{
  "success": true,
  "service": "user-service",
  "version": "16.0.0",
  "status": "healthy",
  "timestamp": "...",
  "uptime": 86400,
  "dependencies": {
    "database": "connected",
    "redis": "connected"
  }
}
```

**Status Values:**
- `healthy`: All dependencies connected
- `degraded`: Database connected, Redis disconnected
- `unhealthy`: Database disconnected (returns 503)

---

## Database Schema

### User Model

```prisma
model User {
  id                  String        @id @default(uuid())
  tenantId            String        @map("tenant_id")
  email               String        @unique
  phone               String?
  passwordHash        String        @map("password_hash")
  firstName           String        @map("first_name")
  lastName            String        @map("last_name")
  role                UserRole      @default(VIEWER)
  status              UserStatus    @default(PENDING)
  emailVerified       Boolean       @default(false)
  phoneVerified       Boolean       @default(false)
  lastLoginAt         DateTime?
  createdAt           DateTime      @default(now())
  updatedAt           DateTime      @updatedAt

  // Account lockout
  failedLoginAttempts Int           @default(0)
  lockoutUntil        DateTime?
  lastFailedLoginAt   DateTime?

  // Password reset
  passwordResetToken  String?
  passwordResetExpiry DateTime?

  // Relations
  profile             UserProfile?
  sessions            UserSession[]
  refreshTokens       RefreshToken[]
  assignedRoles       Role[]
}
```

### UserProfile Model

```prisma
model UserProfile {
  id          String    @id @default(uuid())
  userId      String    @unique
  nationalId  String?
  dateOfBirth DateTime?
  address     String?
  city        String?
  region      String?
  country     String?   @default("SA")
  avatarUrl   String?
  createdAt   DateTime  @default(now())
  updatedAt   DateTime  @updatedAt

  user        User      @relation(...)
}
```

### UserSession Model

```prisma
model UserSession {
  id        String   @id @default(uuid())
  userId    String
  token     String   @unique
  ipAddress String?
  userAgent String?
  expiresAt DateTime
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  user      User     @relation(...)
}
```

### RefreshToken Model

```prisma
model RefreshToken {
  id         String   @id @default(uuid())
  userId     String
  jti        String   @unique
  family     String
  token      String   @unique  // SHA-256 hash
  expiresAt  DateTime
  revoked    Boolean  @default(false)
  used       Boolean  @default(false)
  usedAt     DateTime?
  replacedBy String?
  createdAt  DateTime @default(now())

  user       User     @relation(...)
}
```

### Role Model

```prisma
model Role {
  id          String   @id @default(uuid())
  name        String   @unique
  permissions Json
  isSystem    Boolean  @default(false)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  users       User[]
}
```

### Enums

```typescript
enum UserRole {
  ADMIN    // Full system access
  MANAGER  // Manage users and operations
  FARMER   // Farm owner access
  WORKER   // Farm worker access
  VIEWER   // Read-only access
}

enum UserStatus {
  ACTIVE     // Can access the system
  INACTIVE   // Deactivated
  SUSPENDED  // Temporarily suspended
  PENDING    // Registration pending approval
}
```

---

## NATS Events

**Note:** This service does NOT currently publish or subscribe to NATS events. All communication is synchronous HTTP/REST.

### Recommended Events to Implement

For future integration with the SAHOOL event architecture:

| Subject | Direction | Payload |
|---------|-----------|---------|
| `sahool.{tenant_id}.user.created` | Publish | `{ userId, email, role, tenantId }` |
| `sahool.{tenant_id}.user.updated` | Publish | `{ userId, changes }` |
| `sahool.{tenant_id}.user.deleted` | Publish | `{ userId, deletedAt }` |
| `sahool.{tenant_id}.auth.login` | Publish | `{ userId, ip, userAgent, timestamp }` |
| `sahool.{tenant_id}.auth.logout` | Publish | `{ userId, sessionId, timestamp }` |
| `sahool.{tenant_id}.auth.password_reset` | Publish | `{ userId, timestamp }` |

---

## Service Dependencies

### Internal Services

| Service | URL | Purpose |
|---------|-----|---------|
| notification-service | `NOTIFICATION_SERVICE_URL` (default: http://notification-service:8110) | OTP delivery via SMS/WhatsApp/Telegram/Email |

### External Infrastructure

| Component | Connection | Purpose |
|-----------|------------|---------|
| PostgreSQL | `DATABASE_URL` via PgBouncer | User data storage |
| Redis | `REDIS_URL` | Token revocation store, session management |

---

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string (via PgBouncer) | `postgresql://user:pass@pgbouncer:6432/sahool?sslmode=require` |
| `JWT_SECRET_KEY` | JWT signing secret (min 32 chars in production) | `your-32-character-secret-key-here` |

### Optional (with defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 3025 | Service port |
| `NODE_ENV` | development | Environment (development/staging/production) |
| `REDIS_URL` | redis://localhost:6379 | Redis connection URL |
| `REDIS_HOST` | localhost | Redis host (if REDIS_URL not set) |
| `REDIS_PORT` | 6379 | Redis port |
| `REDIS_PASSWORD` | - | Redis password |
| `REDIS_DB` | 0 | Redis database number |
| `JWT_SECRET` | - | Alias for JWT_SECRET_KEY |
| `JWT_ALGORITHM` | HS256 | JWT algorithm (only HS256 supported) |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Access token TTL |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | 7 | Refresh token TTL |
| `JWT_ISSUER` | sahool-platform | JWT issuer claim |
| `JWT_AUDIENCE` | sahool-api | JWT audience claim |
| `NOTIFICATION_SERVICE_URL` | http://notification-service:8110 | Notification service URL |
| `CORS_ALLOWED_ORIGINS` | (multiple defaults) | Comma-separated CORS origins |
| `RATE_LIMIT_ENABLED` | true | Enable/disable rate limiting |
| `RATE_LIMIT_REQUESTS` | 100 | Requests per window |
| `RATE_LIMIT_WINDOW_SECONDS` | 60 | Rate limit window |
| `TOKEN_REVOCATION_ENABLED` | true | Enable token revocation |

### Email Configuration (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_HOST` | - | SMTP server host |
| `SMTP_PORT` | 587 | SMTP server port |
| `SMTP_USER` | - | SMTP username |
| `SMTP_PASSWORD` | - | SMTP password |
| `EMAIL_FROM` | noreply@sahool.app | Sender email address |
| `FRONTEND_URL` | https://app.sahool.app | Frontend URL for reset links |

---

## Security Features

### Authentication

- **JWT with JTI**: Each token has a unique identifier for revocation
- **Token Rotation**: Refresh tokens are rotated on each use
- **Token Family**: Tracks token lineage for reuse detection
- **Fail-Closed**: Redis unavailability denies access (security over availability)

### Account Protection

- **Account Lockout**: 5 failed attempts locks account for 30 minutes
- **Progressive Delay**: 0s, 2s, 4s, 8s, 16s delays after each failed attempt
- **Password Hashing**: bcryptjs with 12 salt rounds

### Token Revocation

Tokens can be revoked at three levels:
1. **Token-level**: Individual JTI blacklisting
2. **User-level**: All tokens issued before revocation timestamp
3. **Tenant-level**: All tenant tokens issued before revocation timestamp

Redis keys:
- `revoked:token:{jti}` - Individual token revocation
- `revoked:user:{userId}` - User-wide revocation
- `revoked:tenant:{tenantId}` - Tenant-wide revocation

### Input Validation

- Email format validation
- Yemen phone number validation (+967XXXXXXXXX)
- Strong password requirements (uppercase, lowercase, number, special char)
- HTML/XSS sanitization on text fields
- Request body whitelisting (forbidNonWhitelisted)

### Rate Limiting (Throttler)

| Tier | Limit | Window |
|------|-------|--------|
| Short | 10 requests | 1 second |
| Medium | 100 requests | 1 minute |
| Long | 1000 requests | 1 hour |

Endpoint-specific limits:
- Login: 5/minute
- Register: 10/minute
- Forgot Password: 3/minute
- Send OTP: 3/minute

---

## Recommended Fixes and Improvements

### Critical Issues

1. **Missing NATS Integration**
   - Service should publish user events for audit trail and system integration
   - Recommendation: Add event publishing for user CRUD and auth events

2. **DATABASE_URL_DIRECT Not Utilized**
   - Prisma schema defines `directUrl` but it's not set in environment
   - Impact: Migrations may fail through PgBouncer
   - Fix: Add `DATABASE_URL_DIRECT` to docker-compose

### Security Improvements

3. **Email Verification Not Enforced**
   - Users can login without verifying email
   - Consider: Add configuration option to require email verification

4. **Phone Verification Incomplete**
   - `phoneVerified` field exists but verification flow requires notification-service
   - Ensure notification-service OTP endpoints are properly integrated

5. **Token Revocation on Password Change**
   - Currently revokes database refresh tokens but not Redis-cached access tokens
   - Consider: Also revoke user-level tokens in Redis on password change

### Code Quality

6. **Missing Tenant Validation**
   - Users can specify arbitrary tenantId during registration
   - Consider: Validate tenant exists before user creation

7. **Inconsistent Error Response Format**
   - Some endpoints return `{ success, message }`, others `{ success, data }`
   - Consider: Standardize response format across all endpoints

8. **Missing Audit Logging**
   - No audit trail for sensitive operations (password changes, role changes)
   - Recommendation: Integrate with audit-service

### Performance

9. **Database Query Optimization**
   - `findAll` uses `orderBy: createdAt: desc` without index
   - Consider: Add index on `(tenantId, createdAt)` for common query pattern

10. **Redis Connection Pooling**
    - Current implementation creates single Redis connection
    - Consider: Use connection pooling for high-traffic scenarios

---

## Admin Portal Integration Notes

### Data Available for Admin UI

#### User Management Page

| Field | Editable | Notes |
|-------|----------|-------|
| ID | No | Display only |
| Email | Yes | Must be unique |
| First Name | Yes | 2-50 chars |
| Last Name | Yes | 2-50 chars |
| Phone | Yes | Yemen format |
| Role | Yes | Dropdown: ADMIN, MANAGER, FARMER, WORKER, VIEWER |
| Status | Yes | Dropdown: ACTIVE, INACTIVE, SUSPENDED, PENDING |
| Email Verified | Yes | Toggle |
| Phone Verified | Yes | Toggle |
| Last Login | No | Display only |
| Created At | No | Display only |
| Tenant ID | No | Display, filter only |

#### User Profile (Expandable)

| Field | Editable | Notes |
|-------|----------|-------|
| Avatar URL | Yes | Image upload needed |
| Address | Yes | Text field |
| City | Yes | Text field |
| Region | Yes | Text field |
| National ID | Yes | Sensitive data |
| Date of Birth | Yes | Date picker |

#### User Sessions (Read-only)

| Field | Notes |
|-------|-------|
| Session ID | Display |
| IP Address | Display |
| User Agent | Parse for device info |
| Expires At | Show expiry status |

### Recommended Admin Features

1. **User List View**
   - Paginated table with filters (tenant, role, status)
   - Search by email/name
   - Bulk status change (activate/deactivate multiple)
   - Export to CSV

2. **User Detail View**
   - Profile editing form
   - Password reset button (sends email)
   - Force logout (revoke all tokens)
   - Session management (view/revoke sessions)
   - Activity log (requires audit-service integration)

3. **User Creation Form**
   - All required fields
   - Role assignment (admin only)
   - Tenant selection (for multi-tenant admin)
   - Send welcome email option

4. **Statistics Dashboard**
   - Active users count (GET /users/stats/active)
   - Users per tenant (GET /users/stats/count/:tenantId)
   - Registration trends (requires new endpoint)
   - Login activity (requires audit-service)

### API Integration Examples

```typescript
// List users with filters
const response = await fetch('/api/v1/users?tenantId=xxx&status=ACTIVE&take=20&skip=0', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Update user status
const response = await fetch('/api/v1/users/user-id', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ status: 'SUSPENDED' })
});

// Force logout user
const response = await fetch('/api/v1/auth/logout-all', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${userToken}` }
});
// Note: Admin cannot logout other users - this requires admin endpoint

// Hard delete user (admin only)
const response = await fetch('/api/v1/users/user-id/hard', {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${adminToken}` }
});
```

### Missing Admin Endpoints

The following endpoints would improve admin functionality:

1. `POST /api/v1/admin/users/:id/logout` - Force logout any user (admin)
2. `POST /api/v1/admin/users/:id/reset-password` - Admin-initiated password reset
3. `GET /api/v1/admin/users/:id/sessions` - Get user's active sessions
4. `DELETE /api/v1/admin/users/:id/sessions/:sessionId` - Revoke specific session
5. `GET /api/v1/admin/stats/registrations` - Registration statistics over time
6. `GET /api/v1/admin/stats/logins` - Login statistics over time

---

## File Structure

```
apps/services/user-service/
├── Dockerfile
├── package.json
├── tsconfig.json
├── nest-cli.json
├── prisma/
│   └── schema.prisma           # Database schema
├── src/
│   ├── main.ts                 # Application entry point
│   ├── app.module.ts           # Root module
│   ├── auth/
│   │   ├── auth.module.ts      # Auth module
│   │   ├── auth.controller.ts  # Auth endpoints
│   │   ├── auth.service.ts     # Auth business logic
│   │   ├── jwt.strategy.ts     # Passport JWT strategy
│   │   ├── jwt-auth.guard.ts   # JWT authentication guard
│   │   ├── roles.guard.ts      # Role-based access guard
│   │   └── roles.decorator.ts  # @Roles decorator
│   ├── users/
│   │   ├── users.module.ts     # Users module
│   │   ├── users.controller.ts # Users endpoints
│   │   ├── users.service.ts    # Users business logic
│   │   └── dto/
│   │       ├── create-user.dto.ts
│   │       └── update-user.dto.ts
│   ├── health/
│   │   └── health.controller.ts # Health check endpoints
│   ├── prisma/
│   │   ├── prisma.module.ts
│   │   └── prisma.service.ts    # Database connection
│   └── utils/
│       ├── auth-decorators.ts   # @CurrentUser, @TenantId, etc.
│       ├── db-utils.ts          # Pagination utilities
│       ├── http-exception.filter.ts
│       ├── jwt.config.ts        # JWT configuration
│       ├── request-logging.interceptor.ts
│       ├── token-revocation.ts  # Redis token store
│       ├── token-revocation.guard.ts
│       └── validation.ts        # Custom validators
└── tests/
    └── *.spec.ts               # Test files
```

---

## Related Documentation

- Kong Gateway Configuration: `/config/kong/kong.yml`
- Docker Compose: `/docker-compose.yml` (user-service section)
- Shared Auth Library: `/shared/auth/`
- API Gateway Docs: `/docs/API_GATEWAY.md`
