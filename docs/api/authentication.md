# Authentication APIs

# واجهات برمجة تطبيقات المصادقة

## Overview | نظرة عامة

SAHOOL uses JWT (JSON Web Tokens) for authentication. All API requests (except authentication endpoints) require a valid JWT token in the Authorization header.

تستخدم منصة سحول JWT للمصادقة. جميع طلبات API (باستثناء نقاط المصادقة) تتطلب رمز JWT صالح في رأس التفويض.

## Authentication Flow | تدفق المصادقة

```mermaid
sequenceDiagram
    Client->>API: POST /auth/login (email, password)
    API->>Client: {access_token, refresh_token}
    Client->>API: GET /api/resource (Authorization: Bearer token)
    API->>Client: Resource data
    Client->>API: POST /auth/refresh (refresh_token)
    API->>Client: {new_access_token}
```

## Token Types | أنواع الرموز

### Access Token

- **Purpose:** Authenticate API requests
- **Lifetime:** 1 hour (3600 seconds)
- **Format:** JWT
- **Usage:** Include in `Authorization: Bearer <token>` header

### Refresh Token

- **Purpose:** Obtain new access tokens
- **Lifetime:** 7 days
- **Format:** JWT
- **Usage:** POST to `/auth/refresh` endpoint

## Endpoints | نقاط النهاية

### 1. Login | تسجيل الدخول

**Endpoint:** `POST /auth/login`
**Rate Limit:** 5 requests/minute
**Authentication:** Not required

#### Request Body

```json
{
  "email": "farmer@example.com",
  "password": "secure_password"
}
```

#### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user-123",
    "email": "farmer@example.com",
    "name": "Ahmed Al-Farmer",
    "tenant_id": "tenant-456",
    "roles": ["farmer"]
  }
}
```

#### Error Responses

| Status | Error Code            | Description               |
| ------ | --------------------- | ------------------------- |
| 401    | `invalid_credentials` | Invalid email or password |
| 429    | `rate_limit_exceeded` | Too many login attempts   |
| 400    | `invalid_request`     | Missing or invalid fields |

#### Example

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@example.com",
    "password": "secure_password"
  }'
```

### 2. Register | التسجيل

**Endpoint:** `POST /auth/register`
**Rate Limit:** 10 requests/minute
**Authentication:** Not required

#### Request Body

```json
{
  "email": "newfarmer@example.com",
  "password": "secure_password",
  "full_name": "محمد المزارع",
  "phone": "+967777123456",
  "governorate": "sanaa",
  "farm_size_hectares": 5.5
}
```

#### Response

```json
{
  "message": "Registration successful. Please check your email for verification.",
  "message_ar": "تم التسجيل بنجاح. يرجى التحقق من بريدك الإلكتروني للتحقق.",
  "user_id": "user-789"
}
```

### 3. Refresh Token | تحديث الرمز

**Endpoint:** `POST /auth/refresh`
**Rate Limit:** 10 requests/minute
**Authentication:** Refresh token required

#### Request Body

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 4. Logout | تسجيل الخروج

**Endpoint:** `POST /auth/logout`
**Authentication:** Required

Invalidates the current refresh token and optionally blacklists the access token.

#### Request Headers

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Response

```json
{
  "message": "Logout successful",
  "message_ar": "تم تسجيل الخروج بنجاح"
}
```

### 5. Forgot Password | نسيت كلمة المرور

**Endpoint:** `POST /auth/forgot-password`
**Rate Limit:** 3 requests/minute
**Authentication:** Not required

#### Request Body

```json
{
  "email": "farmer@example.com"
}
```

#### Response

```json
{
  "message": "If the email exists, a password reset link has been sent.",
  "message_ar": "إذا كان البريد الإلكتروني موجودًا، فقد تم إرسال رابط إعادة تعيين كلمة المرور."
}
```

### 6. Reset Password | إعادة تعيين كلمة المرور

**Endpoint:** `POST /auth/reset-password`
**Rate Limit:** 5 requests/minute
**Authentication:** Reset token required

#### Request Body

```json
{
  "token": "reset-token-from-email",
  "new_password": "new_secure_password"
}
```

## JWT Token Structure | هيكل رمز JWT

### Access Token Payload

```json
{
  "sub": "user-123",
  "type": "access",
  "email": "farmer@example.com",
  "tenant_id": "tenant-456",
  "roles": ["farmer"],
  "permissions": ["read:fields", "write:fields"],
  "iat": 1640000000,
  "exp": 1640003600,
  "iss": "sahool-auth",
  "aud": "sahool-api"
}
```

### Token Claims

| Claim         | Description                 |
| ------------- | --------------------------- |
| `sub`         | User ID (subject)           |
| `type`        | Token type (access/refresh) |
| `email`       | User email                  |
| `tenant_id`   | Organization/tenant ID      |
| `roles`       | User roles array            |
| `permissions` | User permissions array      |
| `iat`         | Issued at timestamp         |
| `exp`         | Expiration timestamp        |
| `iss`         | Issuer (sahool-auth)        |
| `aud`         | Audience (sahool-api)       |

## Using Tokens | استخدام الرموز

### In HTTP Headers

```bash
curl -X GET http://localhost:8090/v1/fields \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### In JavaScript/TypeScript

```typescript
const token = localStorage.getItem("access_token");

const response = await fetch("http://localhost:8090/v1/fields", {
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
});
```

### In Python

```python
import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

response = requests.get(
    "http://localhost:8090/v1/fields",
    headers={"Authorization": f"Bearer {token}"}
)
```

## API Keys | مفاتيح API

For service-to-service communication, use API keys:

### Request Header

```
X-API-Key: sahool_sk_live_abc123def456
```

### Example

```bash
curl -X GET http://localhost:8090/v1/internal/metrics \
  -H "X-API-Key: sahool_sk_live_abc123def456"
```

## Security Best Practices | أفضل ممارسات الأمان

1. **Store tokens securely**
   - Use httpOnly cookies for web applications
   - Use secure storage for mobile apps
   - Never store tokens in localStorage for sensitive data

2. **Refresh tokens proactively**
   - Refresh access token before expiration
   - Implement automatic token refresh

3. **Handle token expiration**
   - Catch 401 errors
   - Redirect to login or refresh token
   - Clear invalid tokens

4. **Protect API keys**
   - Never commit API keys to version control
   - Rotate keys periodically
   - Use different keys for different environments

5. **Use HTTPS**
   - Always use HTTPS in production
   - Never send tokens over HTTP

## Rate Limiting | حدود المعدل

Authentication endpoints have strict rate limits:

| Endpoint                | Rate Limit  | Window   |
| ----------------------- | ----------- | -------- |
| `/auth/login`           | 5 requests  | 1 minute |
| `/auth/register`        | 10 requests | 1 minute |
| `/auth/forgot-password` | 3 requests  | 1 minute |
| `/auth/reset-password`  | 5 requests  | 1 minute |
| `/auth/refresh`         | 10 requests | 1 minute |

### Rate Limit Headers

```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 45
```

### Rate Limit Exceeded Response

```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many login attempts. Please try again later.",
  "message_ar": "عدد كبير جدًا من محاولات تسجيل الدخول. يرجى المحاولة مرة أخرى لاحقًا.",
  "retry_after": 45
}
```

## Roles and Permissions | الأدوار والصلاحيات

### Roles

| Role         | Description                      |
| ------------ | -------------------------------- |
| `farmer`     | Regular farmer user              |
| `agronomist` | Agricultural expert              |
| `admin`      | Platform administrator           |
| `service`    | Service account for integrations |

### Permissions

Permissions follow the pattern: `action:resource`

Examples:

- `read:fields` - View field information
- `write:fields` - Create/update fields
- `delete:fields` - Delete fields
- `manage:users` - Manage user accounts
- `view:analytics` - Access analytics data

---

_Last updated: {datetime.now().strftime('%Y-%m-%d')}_
