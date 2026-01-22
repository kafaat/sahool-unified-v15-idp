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
   npm run dev
   ```

## How It Works

The admin app verifies JWT tokens from the user-service using:
- **Secret**: `JWT_SECRET` or `JWT_SECRET_KEY` environment variable
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Issuer**: `sahool-platform`
- **Audience**: `sahool-api`

## Troubleshooting

### "JWT_SECRET is not configured" Error
- Ensure `.env.local` exists in `apps/admin` directory
- Verify `JWT_SECRET` is set and matches root `.env` file
- Restart the Next.js dev server

### "Token verification failed" Error
- Check that JWT_SECRET matches between admin app and user-service
- Verify the token issuer is "sahool-platform"
- Verify the token audience is "sahool-api"
- Check browser console and server logs for detailed error messages

### Token Payload Mismatch
If you see errors about missing fields (`role`, `tenant_id`), the user-service may need updates:
- User-service should generate tokens with `role` (string) not `roles` (array)
- User-service should use `tenant_id` not `tid`
