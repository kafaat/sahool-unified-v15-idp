# Certificate Pinning Replacement Guide | دليل استبدال شهادات التثبيت

## Overview | نظرة عامة

This document provides step-by-step instructions for replacing placeholder certificate pins with actual production certificates. Certificate pinning is **CRITICAL** for production security.

هذا المستند يوفر تعليمات خطوة بخطوة لاستبدال شهادات التثبيت الوهمية بشهادات الإنتاج الحقيقية.

---

## Current Status | الحالة الحالية

| Platform | Status | Location |
|----------|--------|----------|
| **Android (Dart)** | ⚠️ Placeholder values | `lib/core/security/certificate_pinning_service.dart` |
| **iOS (Info.plist)** | ⚠️ Placeholder values | `ios/Runner/Info.plist` |

**Total Placeholders to Replace**: ~22 (18 Android + 4 iOS)

---

## Step 1: Get Production Certificate Fingerprints

### For Android (SHA256 Fingerprint)

```bash
# Production API
openssl s_client -connect api.sahool.app:443 -servername api.sahool.app < /dev/null 2>/dev/null | \
  openssl x509 -noout -fingerprint -sha256 | cut -d= -f2 | tr -d ':' | tr 'A-F' 'a-f'

# Production WebSocket
openssl s_client -connect ws.sahool.app:443 -servername ws.sahool.app < /dev/null 2>/dev/null | \
  openssl x509 -noout -fingerprint -sha256 | cut -d= -f2 | tr -d ':' | tr 'A-F' 'a-f'

# Staging API
openssl s_client -connect api-staging.sahool.app:443 -servername api-staging.sahool.app < /dev/null 2>/dev/null | \
  openssl x509 -noout -fingerprint -sha256 | cut -d= -f2 | tr -d ':' | tr 'A-F' 'a-f'
```

**Expected Output Format**: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### For iOS (SPKI Base64 Hash)

```bash
# Production API
openssl s_client -connect api.sahool.app:443 -servername api.sahool.app < /dev/null 2>/dev/null | \
  openssl x509 -pubkey -noout | \
  openssl pkey -pubin -outform der | \
  openssl dgst -sha256 -binary | \
  openssl enc -base64

# Production WebSocket
openssl s_client -connect ws.sahool.app:443 -servername ws.sahool.app < /dev/null 2>/dev/null | \
  openssl x509 -pubkey -noout | \
  openssl pkey -pubin -outform der | \
  openssl dgst -sha256 -binary | \
  openssl enc -base64

# Staging API
openssl s_client -connect api-staging.sahool.app:443 -servername api-staging.sahool.app < /dev/null 2>/dev/null | \
  openssl x509 -pubkey -noout | \
  openssl pkey -pubin -outform der | \
  openssl dgst -sha256 -binary | \
  openssl enc -base64
```

**Expected Output Format**: `AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=`

---

## Step 2: Replace Android Certificate Pins

Edit `lib/core/security/certificate_pinning_service.dart`:

```dart
// Replace placeholder values:
static Map<String, List<CertificatePin>> _getDefaultPins() {
  return {
    'api.sahool.app': [
      CertificatePin(
        type: PinType.sha256,
        value: 'YOUR_ACTUAL_SHA256_HERE',  // <-- Replace
        expiryDate: DateTime(2027, 1, 1),
        description: 'Production API - Primary',
      ),
      CertificatePin(
        type: PinType.sha256,
        value: 'YOUR_BACKUP_SHA256_HERE',  // <-- Replace
        expiryDate: DateTime(2028, 1, 1),
        description: 'Production API - Backup',
      ),
    ],
    // ... repeat for all domains
  };
}
```

### Placeholder Pattern to Search:
```
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae
```

---

## Step 3: Replace iOS Certificate Pins

Edit `ios/Runner/Info.plist`:

```xml
<key>NSPinnedDomains</key>
<dict>
    <key>api.sahool.app</key>
    <dict>
        <key>NSPinnedLeafIdentities</key>
        <array>
            <dict>
                <key>SPKI-SHA256-BASE64</key>
                <string>YOUR_ACTUAL_SPKI_BASE64_HERE</string>  <!-- Replace -->
            </dict>
        </array>
    </dict>
</dict>
```

### Placeholder Pattern to Search:
```
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC=
```

---

## Step 4: Verification

### Android Verification
```dart
// In main.dart or startup code
if (kReleaseMode) {
  final service = CertificatePinningService();
  // Will throw exception if placeholders are still present
}
```

### iOS Verification
```bash
# Build app and test against production server
flutter build ios --release
```

### Test Certificate Pinning
```bash
# Should succeed with valid certificate
curl -v https://api.sahool.app/health

# Use Charles Proxy or mitmproxy to test pinning rejection
# App should reject the proxied certificate
```

---

## Step 5: Certificate Rotation Schedule

| Domain | Current Expiry | Action Required |
|--------|----------------|-----------------|
| api.sahool.app | TBD | Update before expiry |
| ws.sahool.app | TBD | Update before expiry |
| api-staging.sahool.app | TBD | Update before expiry |

### Rotation Process
1. **30 days before expiry**: Add new certificate as backup pin
2. **14 days before expiry**: Deploy app update with new primary pin
3. **7 days before expiry**: Verify new certificate is active
4. **After expiry**: Remove old pin from configuration

---

## Security Checklist

- [ ] All placeholder values replaced with actual certificates
- [ ] At least 2 pins per domain (primary + backup)
- [ ] Expiry dates set correctly
- [ ] Tested in staging environment
- [ ] Tested certificate rejection (via proxy)
- [ ] iOS and Android pins synchronized
- [ ] Monitoring/alerting configured for expiry
- [ ] Documentation updated with actual expiry dates

---

## Troubleshooting

### Error: "Placeholder certificate detected"
- **Cause**: Placeholder values still in production build
- **Fix**: Replace all placeholder fingerprints with actual values

### Error: "Certificate pinning failed"
- **Cause**: Certificate changed without updating pins
- **Fix**: Generate new fingerprint and update configuration

### Error: iOS build fails with "Invalid SPKI"
- **Cause**: Malformed Base64 SPKI hash
- **Fix**: Regenerate using OpenSSL command above

---

## Contact

For certificate management issues, contact:
- **DevOps Team**: devops@sahool.app
- **Security Team**: security@sahool.app

---

*Last Updated: 2026-02-04*
