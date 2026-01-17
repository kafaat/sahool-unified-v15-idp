# SSL Certificate Pinning Implementation Guide

## دليل تطبيق تثبيت شهادات SSL

This guide explains how to use and configure SSL certificate pinning in the SAHOOL Field App.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Getting Certificate Fingerprints](#getting-certificate-fingerprints)
4. [Configuration](#configuration)
5. [Certificate Rotation](#certificate-rotation)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## Overview

SSL Certificate Pinning is a security mechanism that ensures your app only trusts specific SSL certificates, preventing man-in-the-middle attacks even if a Certificate Authority is compromised.

### Features

- ✅ SHA-256 fingerprint pinning
- ✅ Public key pinning support
- ✅ Multiple pins per domain (for rotation)
- ✅ Pin expiry tracking
- ✅ Debug mode bypass
- ✅ Automatic validation
- ✅ Wildcard domain support
- ✅ Certificate rotation helpers

### Security Levels

Certificate pinning is enabled based on security level:

- **Low/Medium**: Disabled (development friendly)
- **High**: Enabled with debug bypass allowed
- **Maximum**: Strict mode, no bypasses

---

## Quick Start

### 1. Install Dependencies

The required dependency is already added to `pubspec.yaml`:

```yaml
dependencies:
  dio_certificate_pinning: ^1.0.0
```

Run:

```bash
flutter pub get
```

### 2. Basic Usage

The certificate pinning is automatically configured when you create an `ApiClient` with a security config:

```dart
import 'package:sahool_field_app/core/http/api_client.dart';
import 'package:sahool_field_app/core/security/security_config.dart';

// Enable certificate pinning with high security
final apiClient = ApiClient(
  securityConfig: SecurityConfig(level: SecurityLevel.high),
);
```

That's it! Certificate pinning is now active.

---

## Getting Certificate Fingerprints

**IMPORTANT**: Replace placeholder fingerprints in `certificate_config.dart` with actual values!

### Method 1: Using the Built-in Helper (Recommended)

Add this debug code to your app:

```dart
import 'package:sahool_field_app/core/security/certificate_tools.dart';
import 'package:flutter/foundation.dart';

void _debugExtractCertificates() async {
  if (!kDebugMode) return;

  // Single certificate
  final info = await getCertificateInfo('https://api.sahool.app');
  if (info != null) {
    print(info);
    printCertificateConfigCode(info);
  }

  // Multiple certificates
  final urls = [
    'https://api.sahool.app',
    'https://api-staging.sahool.app',
    'https://ws.sahool.app',
  ];
  final results = await getCertificateInfoBatch(urls);
  generateBulkConfiguration(results);
}
```

Run this in your app, and it will print the configuration code you can copy directly into `certificate_config.dart`.

### Method 2: Using OpenSSL Command Line

```bash
# Get certificate fingerprint
openssl s_client -connect api.sahool.app:443 < /dev/null 2>/dev/null | \
  openssl x509 -fingerprint -sha256 -noout -in /dev/stdin

# Or get full certificate info
openssl s_client -connect api.sahool.app:443 -showcerts < /dev/null 2>/dev/null | \
  openssl x509 -text -noout
```

### Method 3: Using Browser

1. Navigate to `https://api.sahool.app` in Chrome/Firefox
2. Click the lock icon 🔒 in address bar
3. Click "Certificate" → "Details"
4. Find "SHA-256 Fingerprint"
5. Copy the fingerprint

### Method 4: Using Online Tools

```bash
# Using curl and openssl
curl --insecure -v https://api.sahool.app 2>&1 | \
  awk 'BEGIN { cert=0 } /BEGIN CERT/{ cert=1 } /END CERT/{ cert=0 } { if (cert) print }' | \
  openssl x509 -fingerprint -sha256 -noout
```

---

## Configuration

### Update Certificate Configuration

Edit `/lib/core/security/certificate_config.dart`:

```dart
static Map<String, List<CertificatePin>> getProductionPins() {
  return {
    'api.sahool.app': [
      // Primary certificate
      CertificatePin(
        type: PinType.sha256,
        value: 'YOUR_ACTUAL_SHA256_FINGERPRINT_HERE',
        expiryDate: DateTime(2026, 12, 31),
        description: 'Primary production certificate',
      ),
      // Backup certificate for rotation
      CertificatePin(
        type: PinType.sha256,
        value: 'YOUR_BACKUP_SHA256_FINGERPRINT_HERE',
        expiryDate: DateTime(2027, 6, 30),
        description: 'Backup production certificate',
      ),
    ],
  };
}
```

### Add Custom Pins at Runtime

```dart
final apiClient = ApiClient(
  securityConfig: SecurityConfig(level: SecurityLevel.high),
);

// Add/update pins for a domain
apiClient.updateCertificatePins('api.sahool.app', [
  CertificatePin(
    type: PinType.sha256,
    value: 'new_fingerprint_here',
    expiryDate: DateTime(2027, 1, 1),
  ),
]);
```

### Wildcard Domains

Support multiple subdomains with a single wildcard:

```dart
'*.sahool.io': [
  CertificatePin(
    type: PinType.sha256,
    value: 'fingerprint_for_wildcard_cert',
    expiryDate: DateTime(2026, 12, 31),
  ),
],
```

This will match: `api.sahool.io`, `cdn.sahool.io`, `static.sahool.io`, etc.

---

## Certificate Rotation

### Why Multiple Pins?

Having 2+ pins per domain allows you to rotate certificates without app downtime:

1. Deploy new certificate to server (both old and new certs valid)
2. App validates against either pin (old or new)
3. Release app update with only new pin
4. Remove old certificate from server

### Rotation Steps

1. **Before Certificate Expires**: Generate new certificate
2. **Install Both Certificates**: On your server
3. **Add New Pin to App**:
   ```dart
   'api.sahool.app': [
     // Keep old pin
     CertificatePin(
       type: PinType.sha256,
       value: 'old_fingerprint',
       expiryDate: DateTime(2026, 6, 30),
     ),
     // Add new pin
     CertificatePin(
       type: PinType.sha256,
       value: 'new_fingerprint',
       expiryDate: DateTime(2027, 6, 30),
     ),
   ],
   ```
4. **Release App Update**
5. **Wait for User Adoption** (2-4 weeks)
6. **Remove Old Pin** from app config
7. **Remove Old Certificate** from server

### Monitor Expiring Pins

```dart
final expiringPins = apiClient.getExpiringPins(daysThreshold: 60);
if (expiringPins.isNotEmpty) {
  print('⚠️ Certificates expiring soon:');
  for (final pin in expiringPins) {
    print('  ${pin.domain}: ${pin.daysUntilExpiry} days left');
  }
}
```

### Validation Helper

```dart
import 'package:sahool_field_app/core/security/certificate_config.dart';

final pins = CertificateConfig.getProductionPins();
final issues = CertificateRotationHelper.validatePinConfiguration(pins);

if (issues.isNotEmpty) {
  print('⚠️ Configuration Issues:');
  for (final issue in issues) {
    print('  - $issue');
  }
}
```

---

## Testing

### Test in Debug Mode

By default, certificate pinning is bypassed in debug mode for development:

```dart
// Debug mode - pinning bypassed (if allowPinningDebugBypass = true)
flutter run --debug

// Release mode - pinning enforced
flutter run --release
```

### Force Enable in Debug

```dart
final apiClient = ApiClient(
  securityConfig: SecurityConfig(level: SecurityLevel.maximum), // No bypass
);
```

### Test Certificate Validation

```dart
if (kDebugMode) {
  // Verify actual certificate matches expected
  await verifyCertificateFingerprint(
    url: 'https://api.sahool.app',
    expectedFingerprint: 'your_fingerprint_here',
  );
}
```

### Test Different Scenarios

1. **Valid Certificate**: Should connect successfully
2. **Wrong Certificate**: Should fail with certificate error
3. **Expired Pin**: Should fail or fallback (depending on config)
4. **No Pins Configured**: Behavior depends on `enforceStrict` setting

---

## Troubleshooting

### Issue: "Certificate validation failed"

**Cause**: Certificate fingerprint doesn't match configured pins.

**Solutions**:

1. Extract actual fingerprint and update config
2. Check if certificate was recently rotated
3. Verify domain name matches exactly
4. Check if using wildcard cert incorrectly

### Issue: "No certificate pins configured"

**Cause**: Domain not in configuration.

**Solutions**:

1. Add domain to `certificate_config.dart`
2. Check for typos in domain name
3. Use wildcard if appropriate

### Issue: "All pins expired"

**Cause**: All configured pins have passed their expiry date.

**Solutions**:

1. Update certificate configuration with new pins
2. Check actual certificate on server
3. Implement monitoring for expiring pins

### Issue: App works in debug but fails in release

**Cause**: Debug bypass is enabled, release enforces pinning.

**Solutions**:

1. This is expected behavior for security
2. Update pins to match actual certificates
3. Temporarily use Medium security level if needed

### Issue: Certificate works in browser but not in app

**Cause**: Certificate chain or pinning mismatch.

**Solutions**:

1. Verify you're pinning the correct certificate in chain
2. Check if intermediate certificates are involved
3. Use `getCertificateInfo()` tool to inspect

### Debug Certificate Issues

Add this to see detailed certificate info:

```dart
import 'package:sahool_field_app/core/security/certificate_config.dart';

void debugCertificateConfig() {
  final pins = CertificateConfig.getProductionPins();
  final status = CertificateRotationHelper.getConfigurationStatus(pins);
  print(status);
}
```

---

## Best Practices

1. **Always Have 2+ Pins Per Domain**: For safe rotation
2. **Set Expiry Dates**: Track certificate lifetimes
3. **Monitor Expiring Pins**: Check monthly
4. **Test Before Release**: Verify pins in staging first
5. **Document Rotation Dates**: Keep a schedule
6. **Backup Pins**: Keep old pins during transition
7. **Use Environment-Specific Configs**: Different pins for prod/staging
8. **Regular Audits**: Review pins quarterly

---

## Security Levels Summary

| Level   | Pinning | Strict | Debug Bypass | Use Case      |
| ------- | ------- | ------ | ------------ | ------------- |
| Low     | ❌      | ❌     | ✅           | Development   |
| Medium  | ❌      | ❌     | ✅           | Testing       |
| High    | ✅      | ❌     | ✅           | Production    |
| Maximum | ✅      | ✅     | ❌           | High Security |

---

## Additional Resources

- [OWASP Certificate Pinning](https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning)
- [Flutter Security Best Practices](https://docs.flutter.dev/security)
- [Dio Documentation](https://pub.dev/packages/dio)

---

## Support

For issues or questions about certificate pinning:

1. Check this guide first
2. Review `/lib/core/security/certificate_tools.dart` for debugging
3. Contact the security team
4. Check server certificate configuration

---

**Last Updated**: 2025-01-01
**Version**: 1.0.0
