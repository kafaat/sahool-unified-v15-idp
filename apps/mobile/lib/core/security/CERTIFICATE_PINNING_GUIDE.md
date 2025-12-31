# Certificate Pinning Implementation Guide

## Overview

This mobile app implements SSL certificate pinning for enhanced security. Certificate pinning helps prevent man-in-the-middle attacks by validating that the server's SSL certificate matches a known fingerprint.

## How It Works

1. **Development Mode**: Certificate pinning is DISABLED by default to allow testing with local servers
2. **Staging Mode**: Certificate pinning is ENABLED but not strict (allows bypass in debug mode)
3. **Production Mode**: Certificate pinning is ENABLED and STRICT (no bypass allowed)

The security configuration is automatically selected based on the build mode:
- Debug builds → Development config (pinning disabled)
- Release builds → Production config (pinning enabled and strict)

## Configuration Files

### 1. `certificate_pinning_service.dart`
Core service that handles certificate validation and pinning logic.

### 2. `certificate_config.dart`
Contains the actual certificate fingerprints for all domains (production, staging, development).

**IMPORTANT**: You MUST replace the placeholder fingerprints with actual values before deploying to production!

### 3. `security_config.dart`
Controls when certificate pinning is enabled based on environment.

## Getting Certificate Fingerprints

Before deploying to production, you need to obtain the actual SHA-256 fingerprints of your SSL certificates.

### Method 1: Using OpenSSL (Recommended)

```bash
# For production API
openssl s_client -connect api.sahool.app:443 < /dev/null 2>/dev/null | \
  openssl x509 -fingerprint -sha256 -noout -in /dev/stdin

# For staging API
openssl s_client -connect api-staging.sahool.app:443 < /dev/null 2>/dev/null | \
  openssl x509 -fingerprint -sha256 -noout -in /dev/stdin

# For WebSocket server
openssl s_client -connect ws.sahool.app:443 < /dev/null 2>/dev/null | \
  openssl x509 -fingerprint -sha256 -noout -in /dev/stdin
```

### Method 2: Using the App (Debug Mode)

Add this code to your app during development:

```dart
import 'package:sahool_field_app/core/security/certificate_pinning_service.dart';

void checkCertificateFingerprint() async {
  final fingerprint = await getCertificateFingerprintFromUrl('https://api.sahool.app');
  print('Production API Fingerprint: $fingerprint');

  final stagingFingerprint = await getCertificateFingerprintFromUrl('https://api-staging.sahool.app');
  print('Staging API Fingerprint: $stagingFingerprint');
}
```

### Method 3: Using Browser

1. Navigate to your API URL in Chrome/Firefox
2. Click the lock icon in the address bar
3. Click "Certificate" or "Certificate (Valid)"
4. Go to "Details" tab
5. Look for "SHA-256 Fingerprint" or "Thumbprint"
6. Copy the value

## Updating Certificate Pins

### Step 1: Get the Fingerprints

Use one of the methods above to get your certificate fingerprints.

### Step 2: Update `certificate_config.dart`

Replace the placeholder values:

```dart
static Map<String, List<CertificatePin>> getProductionPins() {
  return {
    'api.sahool.app': [
      CertificatePin(
        type: PinType.sha256,
        value: 'YOUR_ACTUAL_FINGERPRINT_HERE',  // Replace this!
        expiryDate: DateTime(2026, 12, 31),
        description: 'Primary production certificate',
      ),
      // Always keep a backup pin for rotation
      CertificatePin(
        type: PinType.sha256,
        value: 'YOUR_BACKUP_FINGERPRINT_HERE',  // Replace this!
        expiryDate: DateTime(2027, 6, 30),
        description: 'Backup production certificate',
      ),
    ],
  };
}
```

### Step 3: Verify Configuration

Build the app and check the console logs:

```
🔒 SSL Certificate Pinning enabled
   Environment: production
   Strict mode: true
   Debug bypass: false
   Configured domains: [api.sahool.app, ws.sahool.app, *.sahool.io]
```

## Certificate Rotation

When rotating SSL certificates:

1. **Get new certificate fingerprint** using one of the methods above
2. **Add new fingerprint** to the configuration BEFORE deploying
3. **Keep old fingerprint** in the list during transition
4. **Deploy app update** with both old and new fingerprints
5. **Update server certificate**
6. **Remove old fingerprint** after transition period (e.g., 30 days)

Example:

```dart
'api.sahool.app': [
  // Old certificate (to be removed after rotation)
  CertificatePin(
    type: PinType.sha256,
    value: 'old_fingerprint_here',
    expiryDate: DateTime(2025, 12, 31),
    description: 'Old certificate - remove after rotation',
  ),
  // New certificate
  CertificatePin(
    type: PinType.sha256,
    value: 'new_fingerprint_here',
    expiryDate: DateTime(2027, 12, 31),
    description: 'New certificate',
  ),
],
```

## Production Deployment Checklist

Before deploying to production:

- [ ] Replace ALL placeholder fingerprints with actual values
- [ ] Verify fingerprints match your production servers
- [ ] Add backup pins for certificate rotation
- [ ] Set appropriate expiry dates
- [ ] Test in staging environment first
- [ ] Verify app can connect to production API
- [ ] Monitor for certificate validation errors

## Testing

### Development Testing

Certificate pinning is disabled in debug mode by default, so you can test with local servers.

### Staging Testing

1. Build in release mode with staging environment:
   ```bash
   flutter build apk --dart-define=ENV=staging
   ```

2. Install and test:
   ```bash
   adb install build/app/outputs/flutter-apk/app-release.apk
   adb logcat | grep "Certificate"
   ```

3. Verify logs show certificate pinning is working

### Production Testing

1. Build production release:
   ```bash
   flutter build apk --dart-define=ENV=production --release
   ```

2. Test on a real device (not emulator)

3. Verify app connects successfully and logs show:
   ```
   ✅ Certificate pin matched for host: api.sahool.app
   ```

## Troubleshooting

### App Cannot Connect in Production

**Symptom**: App shows network errors in production but works in development

**Possible Causes**:
1. Certificate fingerprints don't match actual server certificates
2. Certificate has expired
3. Using wrong environment configuration

**Solution**:
1. Get current certificate fingerprint from server
2. Update `certificate_config.dart` with correct value
3. Rebuild and redeploy app

### Certificate Validation Failed

**Symptom**: Logs show "Certificate validation failed for host: api.sahool.app"

**Solution**:
1. Check that the fingerprint in the logs matches your configuration
2. Verify the domain name matches exactly
3. Ensure certificate hasn't expired

### Certificate Pinning Bypassed in Production

**Symptom**: Logs show "Certificate pinning bypassed in debug mode" in production

**Solution**:
1. Ensure you're building with `--release` flag
2. Check that `SecurityConfig.fromBuildMode()` returns production config
3. Verify `kReleaseMode` is true in production builds

## Security Best Practices

1. **Always use at least 2 pins** per domain for safe rotation
2. **Monitor expiry dates** - plan rotation 30+ days before expiry
3. **Never commit real fingerprints** to public repositories (use environment variables or secure CI/CD)
4. **Test thoroughly** in staging before production deployment
5. **Have a rollback plan** in case of certificate issues
6. **Monitor production logs** for certificate validation errors

## Environment Variables

You can override certificate pinning behavior using environment variables:

```bash
# Disable certificate pinning (for development only!)
flutter run --dart-define=DISABLE_CERT_PINNING=true

# Force production security config
flutter build apk --dart-define=ENV=production --release
```

## Support

For questions or issues with certificate pinning:
1. Check logs for specific error messages
2. Verify certificate fingerprints match
3. Review this guide's troubleshooting section
4. Contact the security team for assistance

## References

- [OWASP Certificate Pinning Guide](https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning)
- [Dio SSL Pinning Documentation](https://pub.dev/packages/dio#https-certificate-verification)
- [Flutter Security Best Practices](https://flutter.dev/docs/deployment/security)
