# Authentication API Integration Guide

## Overview

The SAHOOL mobile app authentication service has been updated to use **real API endpoints** instead of simulated responses. The service now supports both production API calls and development mock mode.

## Key Changes

### 1. Real API Integration

The authentication service now makes actual HTTP requests to the backend API:

- **Login**: `POST /api/v1/auth/login`
- **Token Refresh**: `POST /api/v1/auth/refresh`
- **Logout**: `POST /api/v1/auth/logout`

### 2. Environment-Based Configuration

The service automatically detects the environment and uses appropriate endpoints:

- **Production**: `https://api.sahool.app/api/v1`
- **Staging**: `https://api-staging.sahool.app/api/v1`
- **Development**: `http://10.0.2.2:8000/api/v1` (configurable via ENV)

### 3. Automatic Fallback to Mock Mode

In development, if the API is unavailable, the service automatically falls back to mock mode:

```dart
// API call fails due to network error
→ Automatically falls back to mock authentication
→ Logs warning: "API unavailable, falling back to mock mode"
```

## Usage

### Production Builds

Production builds **always** use real API endpoints. No configuration needed:

```bash
# Build for production
flutter build apk --release
flutter build ios --release
```

### Development with Real API

By default, development builds will attempt to use the real API:

```bash
# Run with default settings (tries API, falls back to mock if unavailable)
flutter run
```

### Development with Mock Mode (Force)

To explicitly force mock mode in development:

```bash
# Force mock authentication
flutter run --dart-define=USE_MOCK_AUTH=true
```

## API Response Format

The authentication service expects the following response format from the API:

### Login Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "user": {
    "id": "user_123",
    "email": "farmer@sahool.app",
    "name": "أحمد المزارع",
    "role": "farmer",
    "tenant_id": "tenant_1",
    "phone": "+967777123456",
    "avatar_url": "https://..."
  }
}
```

Alternative formats are also supported:
- `accessToken` (camelCase)
- `expiresIn` (camelCase)
- `tenantId` (camelCase)

### Token Refresh Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

## Error Handling

The service handles various API errors and converts them to user-friendly Arabic messages:

| HTTP Status | Arabic Message | English |
|-------------|----------------|---------|
| 401/403 | البريد الإلكتروني أو كلمة المرور غير صحيحة | Invalid credentials |
| Network Error | لا يوجد اتصال بالإنترنت | No internet connection |
| 500+ | حدث خطأ في الخادم | Server error |
| Timeout | انتهت مهلة الاتصال | Connection timeout |

## Environment Configuration

Configure API endpoints in `.env` file or via dart-define:

```env
# Environment (development, staging, production)
ENV=development

# API Base URL (optional override)
API_BASE_URL=http://10.0.2.2:8000/api/v1

# Development host (for Android emulator)
DEV_HOST=10.0.2.2

# Force mock mode (development only)
USE_MOCK_AUTH=false
```

## Security Features

### Production Security

In production builds, the following security features are automatically enabled:

1. **Certificate Pinning**: SSL certificate validation
2. **Request Signing**: HMAC-based request signatures
3. **Security Headers**: Validation of response headers
4. **Token Encryption**: Secure storage of tokens

### Development Security

In debug builds:

- Certificate pinning is **disabled** (for local development)
- Request signing is **optional**
- Mock mode is **available** as fallback

## Testing

### Integration Tests

Integration tests will work with both real API and mock mode:

```dart
// Tests automatically use mock mode
testWidgets('Login with valid credentials', (tester) async {
  // Test implementation
  // Mock mode is used automatically in tests
});
```

### Manual Testing

1. **Test with Real API**:
   ```bash
   # Ensure backend is running
   flutter run
   ```

2. **Test with Mock Mode**:
   ```bash
   flutter run --dart-define=USE_MOCK_AUTH=true
   ```

3. **Test API Failure Handling**:
   ```bash
   # Stop backend server
   flutter run
   # App should automatically fall back to mock mode
   ```

## Logging

The authentication service provides detailed logging:

```
[AUTH] Login attempt (email: user@example.com)
[AUTH] Logging in via API
[HTTP] POST /api/v1/auth/login
[HTTP] 200 /api/v1/auth/login
[AUTH] API login successful (userId: user_123)
[AUTH] Token refresh scheduled in 55 minutes
```

In case of fallback to mock mode:
```
[AUTH] Login attempt (email: user@example.com)
[AUTH] Logging in via API
[HTTP] POST /api/v1/auth/login
[HTTP] Connection timeout
[AUTH] API unavailable, falling back to mock mode
[AUTH] Using MOCK login (development only)
[AUTH] Mock login successful
```

## Migration Notes

### For Developers

1. **No code changes required** in UI components
2. Authentication service interface remains the same
3. Existing integration tests continue to work
4. Add backend URL configuration in `.env` file

### For Backend Developers

Ensure your API endpoints match the expected format:

- `POST /api/v1/auth/login` - Accept email/password, return tokens and user
- `POST /api/v1/auth/refresh` - Accept refresh_token, return new tokens
- `POST /api/v1/auth/logout` - Invalidate current session

## Troubleshooting

### "API unavailable, falling back to mock mode"

**Cause**: Backend API is not accessible

**Solutions**:
1. Check if backend server is running
2. Verify `DEV_HOST` in `.env` matches your local IP
3. For Android emulator, use `10.0.2.2`
4. For iOS simulator, use `localhost`
5. For physical device, use your machine's IP address

### "Certificate pinning failed"

**Cause**: SSL certificate mismatch (production only)

**Solutions**:
1. Verify you're connecting to the correct domain
2. Check if certificate pins in `CertificateConfig` are up to date
3. In development, certificate pinning is disabled by default

### "Invalid credentials" on correct password

**Cause**: API response format mismatch

**Solutions**:
1. Check API response matches expected format
2. Verify token field names (`access_token` or `accessToken`)
3. Check backend logs for errors

## Best Practices

1. **Always test with real API** before production deployment
2. **Use mock mode only** for UI development without backend
3. **Monitor logs** for automatic fallback warnings
4. **Update certificate pins** before they expire (production)
5. **Handle token expiry** gracefully in your UI
6. **Test offline scenarios** to ensure proper error messages

## Support

For issues or questions:
- Check logs for detailed error messages
- Verify environment configuration in `.env`
- Test API endpoints with Postman/curl
- Review `apps/mobile/lib/core/auth/auth_service.dart` for implementation details
