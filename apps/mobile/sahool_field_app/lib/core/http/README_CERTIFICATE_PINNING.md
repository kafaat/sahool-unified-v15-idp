# SSL Certificate Pinning Implementation

## Overview

This implementation protects the SAHOOL Field App from Man-in-the-Middle (MITM) attacks by validating SSL certificates against known certificate fingerprints.

## Features

- **Public Key Pinning**: Uses SHA-256 fingerprints of public keys
- **Multiple Certificates**: Supports backup certificates for smooth rotation
- **Development Bypass**: Automatically disabled in debug mode for local testing
- **Detailed Logging**: Comprehensive logs for debugging SSL issues
- **Fallback Support**: Multiple pinned certificates prevent app breakage during cert rotation

## Security Benefits

1. **Prevents MITM Attacks**: Even if a CA is compromised, attackers cannot intercept traffic
2. **Defense in Depth**: Adds an extra layer beyond standard SSL/TLS
3. **Protection Against Rogue CAs**: App only trusts specific certificates
4. **Certificate Rotation Support**: Multiple pinned certs allow smooth updates

## Configuration Status

⚠️ **IMPORTANT**: Before deploying to production, you must update the certificate fingerprints!

### Current Status
- Status: 🔴 **PLACEHOLDER CERTIFICATES IN USE**
- Action Required: Extract and configure actual certificate fingerprints
- File to Update: `lib/core/http/certificate_pinning.dart`

## How to Extract Certificate Fingerprints

### Option 1: Using OpenSSL (Recommended)

```bash
# For the primary production server (api.sahool.io)
openssl s_client -servername api.sahool.io -connect api.sahool.io:443 </dev/null 2>/dev/null | \
  openssl x509 -pubkey -noout | \
  openssl pkey -pubin -outform der | \
  openssl dgst -sha256 -binary | \
  openssl enc -base64

# For backup/staging server
openssl s_client -servername api-staging.sahool.io -connect api-staging.sahool.io:443 </dev/null 2>/dev/null | \
  openssl x509 -pubkey -noout | \
  openssl pkey -pubin -outform der | \
  openssl dgst -sha256 -binary | \
  openssl enc -base64
```

### Option 2: Using Browser

1. Navigate to `https://api.sahool.io` in Chrome/Firefox
2. Click the padlock icon → Certificate → Details
3. Export the certificate as PEM
4. Run:
   ```bash
   openssl x509 -in certificate.pem -pubkey -noout | \
     openssl pkey -pubin -outform der | \
     openssl dgst -sha256 -binary | \
     openssl enc -base64
   ```

### Option 3: Using Online Tools

⚠️ **Not Recommended for Production**: Only use for testing

- Visit: https://www.ssllabs.com/ssltest/analyze.html?d=api.sahool.io
- Look for "Pin SHA256" in the certificate details

## Updating Certificate Fingerprints

1. Extract fingerprints using one of the methods above
2. Open `lib/core/http/certificate_pinning.dart`
3. Update the `_pinnedCertificates` list:

```dart
static const List<String> _pinnedCertificates = [
  // Primary production certificate
  'sha256/YOUR_ACTUAL_FINGERPRINT_HERE=',

  // Backup certificate for rotation
  'sha256/YOUR_BACKUP_FINGERPRINT_HERE=',
];
```

4. Remove placeholder values
5. Test thoroughly before deployment

## Testing Certificate Pinning

### In Development Mode

Certificate pinning is **disabled by default** in debug mode to allow local testing.

To enable pinning in debug mode:
```bash
flutter run --dart-define=ENABLE_CERT_PINNING=true
```

### Testing Programmatically

```dart
// In your app initialization or settings screen
if (kDebugMode) {
  final apiClient = ApiClient();
  final testResult = await CertificatePinning.testPinning(
    apiClient._dio,
    'https://api.sahool.io/healthz',
  );

  if (testResult) {
    print('✅ Certificate pinning is working correctly');
  } else {
    print('❌ Certificate pinning validation failed');
  }
}
```

## Development Bypass Hosts

The following hosts automatically bypass certificate pinning (even in release mode if needed):

- `localhost`
- `127.0.0.1`
- `10.0.2.2` (Android Emulator)
- `192.168.*` (Local network)

To modify this list, update `_devBypassHosts` in `certificate_pinning.dart`.

## Certificate Rotation Strategy

1. **Before Certificate Expires**:
   - Extract fingerprint of new certificate
   - Add new fingerprint to `_pinnedCertificates` array (keep old one)
   - Release app update with both fingerprints

2. **After App Update Deployment**:
   - Wait for majority of users to update (check analytics)
   - Install new certificate on server
   - Both old and new apps continue working

3. **After Grace Period**:
   - Release new app version with only new fingerprint
   - Remove old certificate from server

## Production Checklist

Before deploying to production:

- [ ] Extract actual certificate fingerprints from production server
- [ ] Update `_pinnedCertificates` in `certificate_pinning.dart`
- [ ] Remove all PLACEHOLDER values
- [ ] Add backup certificate fingerprint for rotation
- [ ] Test in staging environment
- [ ] Verify certificate expiry dates
- [ ] Set up certificate expiry monitoring
- [ ] Document certificate rotation procedure
- [ ] Test certificate pinning with production API
- [ ] Verify error logging works correctly

## Troubleshooting

### Issue: "Certificate pinning validation FAILED"

**Cause**: The server's certificate doesn't match any pinned fingerprints.

**Solutions**:
1. Verify you extracted the fingerprint correctly
2. Ensure you're connecting to the correct server (not staging/dev)
3. Check if certificate was recently rotated
4. Verify fingerprint format includes `sha256/` prefix

### Issue: App works in debug but not release

**Cause**: Certificate pinning is enabled in release mode.

**Solutions**:
1. Ensure certificate fingerprints are correctly configured
2. Check app is connecting to correct API endpoint
3. Review logs for specific validation errors
4. Test with `--dart-define=ENABLE_CERT_PINNING=true` in debug mode

### Issue: Cannot connect to local development server

**Cause**: Development bypass might not be working.

**Solutions**:
1. Verify your local IP is in `_devBypassHosts`
2. Add custom bypass logic if needed
3. Ensure `kDebugMode` is true
4. Check `isPinningEnabled` returns false in dev

## Security Considerations

1. **Multiple Pins**: Always maintain at least 2 pinned certificates
2. **Backup Pin**: Include a backup certificate before primary expires
3. **Monitoring**: Set up alerts for certificate expiry (90 days before)
4. **Rotation Plan**: Document and test rotation procedure regularly
5. **Incident Response**: Have plan for emergency certificate updates
6. **Code Review**: Changes to pinning logic should have security review

## Related Files

- `lib/core/http/certificate_pinning.dart` - Main implementation
- `lib/core/http/api_client.dart` - Integration point
- `lib/core/config/api_config.dart` - API endpoint configuration

## References

- [OWASP Certificate Pinning](https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning)
- [RFC 7469: Public Key Pinning](https://tools.ietf.org/html/rfc7469)
- [Flutter Security Best Practices](https://flutter.dev/docs/deployment/security)

## Support

For questions or issues with certificate pinning:
1. Check this README for common solutions
2. Review logs with `tag: 'SSL'`
3. Test in debug mode with `ENABLE_CERT_PINNING=true`
4. Contact security team for production issues

---

**Last Updated**: 2025-12-30
**Version**: 1.0.0
**Status**: Initial Implementation - Requires Configuration
