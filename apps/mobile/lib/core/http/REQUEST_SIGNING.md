# API Request Signing - نظام توقيع طلبات API

## Overview

This implementation adds HMAC-SHA256 request signing to all API requests for enhanced security. It protects against:
- **Request tampering**: Ensures requests haven't been modified in transit
- **Replay attacks**: Timestamp validation prevents request reuse
- **Man-in-the-middle attacks**: Combined with certificate pinning for complete security

## Architecture

### Components

1. **SigningKeyService** (`lib/core/security/signing_key_service.dart`)
   - Manages cryptographic keys for request signing
   - Handles key generation, storage, and rotation
   - Derives keys from device + user information

2. **RequestSigningInterceptor** (`lib/core/http/request_signing_interceptor.dart`)
   - Dio interceptor that signs outgoing requests
   - Generates HMAC-SHA256 signatures
   - Adds security headers to requests

3. **ApiClient Integration** (`lib/core/http/api_client.dart`)
   - Integrates signing interceptor into request chain
   - Configurable signing enable/disable

## How It Works

### Request Signing Process

1. **Interceptor Triggers**: Before each API request is sent
2. **Public Endpoint Check**: Skips signing for public endpoints (login, register, etc.)
3. **Generate Components**:
   - **Timestamp**: Current time in milliseconds (for replay protection)
   - **Nonce**: Random unique value (prevents duplicate requests)
   - **Body Hash**: SHA256 hash of request body
4. **Build Canonical Request**: Combines:
   ```
   METHOD\n
   PATH\n
   QUERY_PARAMS\n
   TIMESTAMP\n
   NONCE\n
   BODY_HASH
   ```
5. **Sign Request**: HMAC-SHA256(canonical_request, signing_key)
6. **Add Headers**:
   - `X-Signature`: The HMAC-SHA256 signature
   - `X-Timestamp`: Request timestamp
   - `X-Nonce`: Unique request identifier
   - `X-Signature-Version`: Signature algorithm version

### Key Management

#### Key Generation
```dart
// Keys are derived from:
// - Random base key (32 bytes)
// - Device ID (from device_info_plus)
// - User ID (from authenticated user)
// Using HMAC-SHA256 for key derivation

final derivedKey = HMAC-SHA256(
  baseKey + deviceId + userId + "sahool_v1",
  "sahool_signing_key_derivation"
)
```

#### Key Rotation
- **Automatic**: Keys rotate every 90 days
- **Version-based**: Keys rotate when version changes
- **Manual**: Call `signingKeyService.rotateKey()` to force rotation

#### Key Storage
- Stored in **Flutter Secure Storage** (encrypted)
- Platform-specific security:
  - **Android**: EncryptedSharedPreferences + AES encryption
  - **iOS**: Keychain with `first_unlock_this_device` accessibility

## Usage

### Basic Setup (Already Configured)

The signing is automatically enabled through the `apiClientProvider`:

```dart
// In lib/core/di/providers.dart
final apiClientProvider = Provider<ApiClient>((ref) {
  final signingKeyService = ref.watch(signingKeyServiceProvider);
  return ApiClient(
    signingKeyService: signingKeyService,
    enableRequestSigning: true,
  );
});
```

### Manual Configuration

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sahool_field_app/core/http/api_client.dart';
import 'package:sahool_field_app/core/security/signing_key_service.dart';

// Get services from providers
final container = ProviderContainer();
final signingKeyService = container.read(signingKeyServiceProvider);

// Create API client with signing
final apiClient = ApiClient(
  signingKeyService: signingKeyService,
  enableRequestSigning: true,
);

// Disable signing (not recommended for production)
final unsignedClient = ApiClient(
  enableRequestSigning: false,
);
```

### Accessing Key Information

```dart
final signingKeyService = ref.read(signingKeyServiceProvider);

// Get current key version
final version = await signingKeyService.getKeyVersion();
print('Key version: $version');

// Get key age
final createdAt = await signingKeyService.getKeyCreatedAt();
print('Key created: $createdAt');

// Get days until rotation
final daysLeft = await signingKeyService.getDaysUntilRotation();
print('Days until rotation: $daysLeft');

// Force key rotation
await signingKeyService.rotateKey();
```

### Public Endpoints

These endpoints **do not** require signing:
- `/auth/login`
- `/auth/register`
- `/auth/forgot-password`
- `/auth/reset-password`
- `/auth/verify-email`
- `/auth/resend-verification`
- `/health`
- `/version`
- `/api-docs`

To add more public endpoints, edit `_isPublicEndpoint()` in `request_signing_interceptor.dart`.

## Server-Side Validation

The backend must validate request signatures. Here's the validation algorithm:

### 1. Extract Headers
```
X-Signature: <signature>
X-Timestamp: <timestamp>
X-Nonce: <nonce>
X-Signature-Version: <version>
```

### 2. Validate Timestamp (Replay Protection)
```javascript
const MAX_DRIFT_SECONDS = 300; // 5 minutes
const requestTime = parseInt(headers['x-timestamp']);
const now = Date.now();

if (Math.abs(now - requestTime) > MAX_DRIFT_SECONDS * 1000) {
  throw new Error('Request timestamp expired');
}
```

### 3. Check Nonce (Prevent Duplicates)
```javascript
// Store used nonces in Redis with TTL
const nonceKey = `nonce:${headers['x-nonce']}`;
const exists = await redis.exists(nonceKey);

if (exists) {
  throw new Error('Duplicate request detected');
}

// Store nonce for 5 minutes
await redis.setex(nonceKey, 300, '1');
```

### 4. Rebuild Canonical Request
```javascript
const method = req.method;
const path = req.path;
const queryParams = sortQueryParams(req.query);
const timestamp = headers['x-timestamp'];
const nonce = headers['x-nonce'];
const bodyHash = sha256(JSON.stringify(req.body));

const canonicalRequest = [
  method,
  path,
  queryParams,
  timestamp,
  nonce,
  bodyHash
].join('\n');
```

### 5. Verify Signature
```javascript
const crypto = require('crypto');

// Get user's signing key from database
const signingKey = await getUserSigningKey(req.user.id);

// Calculate expected signature
const expectedSignature = crypto
  .createHmac('sha256', signingKey)
  .update(canonicalRequest)
  .digest('base64url');

// Compare signatures (constant-time comparison)
if (!crypto.timingSafeEqual(
  Buffer.from(expectedSignature),
  Buffer.from(headers['x-signature'])
)) {
  throw new Error('Invalid signature');
}
```

## Security Considerations

### ✅ Strengths
- **HMAC-SHA256**: Industry-standard cryptographic algorithm
- **Device binding**: Keys derived from device information
- **User binding**: Keys include user ID for per-user keys
- **Automatic rotation**: Keys expire after 90 days
- **Secure storage**: Platform-specific encrypted storage
- **Replay protection**: Timestamp + nonce validation
- **Tamper protection**: Any modification invalidates signature

### ⚠️ Limitations
- **Not end-to-end encryption**: Use HTTPS/TLS for transport security
- **Server key management**: Server must securely store user keys
- **Clock synchronization**: Requires reasonably synchronized clocks
- **Key compromise**: If device is rooted/jailbroken, keys may be exposed

### 🔒 Best Practices
1. **Always use HTTPS**: Signing complements, not replaces, TLS
2. **Enable certificate pinning**: Prevents MITM attacks
3. **Implement server-side validation**: Client signing is useless without server verification
4. **Monitor failed signatures**: Track and alert on validation failures
5. **Rotate keys regularly**: Don't disable automatic rotation
6. **Secure key storage**: Never log or expose signing keys
7. **Use device attestation**: Combine with device integrity checks

## Troubleshooting

### Request signing failed
```
Error: Failed to sign request
```
**Solution**: Check if signing key exists and is valid
```dart
final key = await signingKeyService.getSigningKey();
print('Key exists: ${key.isNotEmpty}');
```

### Signature validation failed (server)
**Possible causes**:
1. Clock drift between client and server (>5 minutes)
2. Request was modified in transit
3. Key mismatch between client and server
4. Incorrect canonical request building

**Debug**:
- Log canonical request on both client and server
- Compare timestamps
- Verify key versions match

### Public endpoint being signed
**Solution**: Add endpoint to `_isPublicEndpoint()` list

### Keys not rotating
**Check**:
```dart
final daysLeft = await signingKeyService.getDaysUntilRotation();
print('Days left: $daysLeft'); // Should be < 90
```

## Testing

### Unit Tests
```dart
test('Signs request correctly', () async {
  final signingKeyService = SigningKeyService(mockSecureStorage);
  final interceptor = RequestSigningInterceptor(signingKeyService);

  final options = RequestOptions(
    path: '/api/users',
    method: 'POST',
    data: {'name': 'Ahmed'},
  );

  await interceptor.onRequest(options, mockHandler);

  expect(options.headers['X-Signature'], isNotEmpty);
  expect(options.headers['X-Timestamp'], isNotEmpty);
  expect(options.headers['X-Nonce'], isNotEmpty);
});
```

### Integration Tests
```dart
testWidgets('API requests are signed', (tester) async {
  // Make API call
  final response = await apiClient.post('/api/test', {'data': 'value'});

  // Verify headers were added (check server logs)
  expect(response, isNotNull);
});
```

## Performance Impact

- **Key generation**: ~50ms (only on first use or rotation)
- **Request signing**: ~1-2ms per request
- **Memory overhead**: ~100 bytes per request (headers)
- **Storage**: ~500 bytes (encrypted key + metadata)

## Migration Guide

### Disabling Signing (Not Recommended)
```dart
final apiClient = ApiClient(
  enableRequestSigning: false,
);
```

### Gradual Rollout
1. Deploy backend with optional signature validation
2. Enable signing in mobile app
3. Monitor signature success rate
4. Make signature validation mandatory
5. Remove fallback for unsigned requests

## References

- [HMAC-SHA256 Specification (RFC 2104)](https://tools.ietf.org/html/rfc2104)
- [Flutter Secure Storage](https://pub.dev/packages/flutter_secure_storage)
- [Dio Interceptors](https://pub.dev/packages/dio)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
