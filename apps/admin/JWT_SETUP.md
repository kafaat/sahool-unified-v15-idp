# JWT Token Verification Setup

## Quick Setup

1. **Copy environment file**:
   ```bash
   cd apps/admin
   cp .env.example .env.local
   ```

2. **Configure JWT_SECRET**:
   - Open `.env.local`
   - Set `JWT_SECRET` to match `JWT_SECRET_KEY` in root `.env` file
   - Example: `JWT_SECRET=change_this_jwt_secret_key_at_least_32_characters_long`

3. **Restart the dev server**:
   ```bash
   pnpm dev
   ```

## How It Works

The admin app verifies JWT tokens from the user-service using:
- **Secret**: `JWT_SECRET` or `JWT_SECRET_KEY` environment variable
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Issuer**: `sahool-platform` (via `JWT_ISSUER`)
- **Audience**: `sahool-users` (via `JWT_AUDIENCE`)

## Token Payload

The middleware handles both legacy and current JWT formats:

```typescript
// Current format (user-service)
{
  sub: "user-id",
  email: "user@example.com",
  roles: ["ADMIN"],       // Array — mapped to admin/supervisor/viewer
  tid: "tenant-id"        // Alternative tenant ID field
}

// Legacy format (still supported)
{
  sub: "user-id",
  email: "user@example.com",
  role: "admin",           // Singular string
  tenant_id: "tenant-id"
}
```

### Role Mapping

| Backend Value               | Admin Panel Role |
| --------------------------- | ---------------- |
| `ADMIN`, `ADMINISTRATOR`   | `admin`          |
| `SUPERVISOR`, `MANAGER`    | `supervisor`     |
| `FARMER`, `VIEWER`, others | `viewer`         |

## Troubleshooting

### "JWT_SECRET is not configured" Error
- Ensure `.env.local` exists in `apps/admin` directory
- Verify `JWT_SECRET` is set and matches root `.env` file
- Restart the Next.js dev server

### "Token verification failed" Error
- Check that `JWT_SECRET` matches between admin app and user-service
- Verify the token issuer is `sahool-platform`
- Verify the token audience is `sahool-users`
- Check browser console and server logs for detailed error messages

### Unauthorized Redirects After Login
If users are redirected to `/dashboard?error=unauthorized` after login:
- Most likely cause: JWT uses `roles` array but middleware expected `role` string
- This has been fixed — middleware now handles both `roles` (array) and `role` (string)
- Clear browser cookies and try again
