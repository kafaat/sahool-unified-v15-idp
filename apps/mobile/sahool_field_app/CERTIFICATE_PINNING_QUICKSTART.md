# Certificate Pinning Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### Step 1: Extract Certificate Fingerprint

```bash
cd /home/user/sahool-unified-v15-idp/apps/mobile/sahool_field_app
./scripts/extract_cert_fingerprint.sh api.sahool.io
```

**Expected Output**:
```
SHA-256 Public Key Fingerprint:
sha256/YLh1dUR9y6Kja30RrAn7JKnbQG/uEtLMkBgFF2Fuihg=
```

### Step 2: Update Configuration

Open: `lib/core/http/certificate_pinning.dart`

Find and replace:
```dart
static const List<String> _pinnedCertificates = [
  'sha256/PLACEHOLDER_PRIMARY_CERT_FINGERPRINT=',  // ← Replace this
  'sha256/PLACEHOLDER_BACKUP_CERT_FINGERPRINT=',   // ← Replace this
];
```

With your actual fingerprints:
```dart
static const List<String> _pinnedCertificates = [
  'sha256/YLh1dUR9y6Kja30RrAn7JKnbQG/uEtLMkBgFF2Fuihg=',
  'sha256/C5+lpZ7tcVwmwQIMcRtPbsQtWLABXhQzejna0wHFr8M=',
];
```

### Step 3: Test

```bash
# Test with pinning enabled
flutter run --dart-define=ENABLE_CERT_PINNING=true

# Run integration tests
flutter test integration_test/certificate_pinning_test.dart
```

---

## 📋 Common Commands

### Extract Certificate
```bash
./scripts/extract_cert_fingerprint.sh api.sahool.io
```

### Test in Development
```bash
# Default: Pinning disabled
flutter run

# With pinning enabled
flutter run --dart-define=ENABLE_CERT_PINNING=true
```

### Build for Production
```bash
# Release build (pinning auto-enabled)
flutter build apk --release
```

### Run Tests
```bash
# Unit tests
flutter test test/unit/core/certificate_pinning_test.dart

# Integration tests
flutter test integration_test/certificate_pinning_test.dart
```

---

## 🔍 Verify Configuration

```bash
# Check if placeholders are still in use
grep "PLACEHOLDER" lib/core/http/certificate_pinning.dart
```

**Expected**: No output (no matches found)

---

## 🐛 Quick Troubleshooting

### Problem: "Certificate validation FAILED"

1. Re-extract certificate:
   ```bash
   ./scripts/extract_cert_fingerprint.sh api.sahool.io
   ```

2. Compare with configured fingerprint in `certificate_pinning.dart`

3. Update if different

### Problem: "Cannot connect in production"

1. Check you're using production URL:
   ```dart
   // In api_config.dart
   static const String productionBaseUrl = 'https://api.sahool.io';
   ```

2. Verify certificate is for the correct domain

3. Check logs:
   ```bash
   flutter run --release
   # Look for [SSL] tagged logs
   ```

### Problem: "Works in debug, fails in release"

- This is normal if placeholders are still in use
- Update with real certificates from production

---

## 📍 File Locations

| Purpose | File Path |
|---------|-----------|
| Main Implementation | `lib/core/http/certificate_pinning.dart` |
| API Client | `lib/core/http/api_client.dart` |
| Extraction Script | `scripts/extract_cert_fingerprint.sh` |
| Documentation | `lib/core/http/README_CERTIFICATE_PINNING.md` |
| Full Summary | `CERTIFICATE_PINNING_IMPLEMENTATION.md` |

---

## ⚡ One-Line Setup

```bash
# Extract, copy, and open file in one go (macOS/Linux)
./scripts/extract_cert_fingerprint.sh api.sahool.io && \
code lib/core/http/certificate_pinning.dart
```

---

## 🎯 Production Checklist

Before deploying:

- [ ] Extracted production certificate fingerprint
- [ ] Updated `_pinnedCertificates` array
- [ ] Removed all PLACEHOLDER values
- [ ] Added backup certificate
- [ ] Tested with `--dart-define=ENABLE_CERT_PINNING=true`
- [ ] Ran integration tests successfully
- [ ] Verified certificate expiry date (6+ months)
- [ ] Tested release build on real device

---

## 💡 Pro Tips

1. **Always maintain 2 certificates**: Primary + Backup
2. **Update before expiry**: Start rotation 90 days before expiry
3. **Test in staging first**: Use staging certificate to test rotation
4. **Monitor logs**: Watch for `[SSL]` tag in production
5. **Document rotation**: Keep record of when certificates were updated

---

## 🆘 Need Help?

1. Read full docs: `lib/core/http/README_CERTIFICATE_PINNING.md`
2. Check implementation summary: `CERTIFICATE_PINNING_IMPLEMENTATION.md`
3. Review integration tests: `integration_test/certificate_pinning_test.dart`
4. Check logs for `[SSL]` tag

---

**Last Updated**: 2025-12-30
