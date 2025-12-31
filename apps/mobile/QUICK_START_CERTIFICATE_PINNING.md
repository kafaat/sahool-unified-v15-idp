# Certificate Pinning - Quick Start Guide

## 🎯 What Was Done

Certificate pinning has been enabled in the main mobile app at `/apps/mobile/`. It's automatically configured based on build mode:

- **Debug builds**: Certificate pinning DISABLED (for local development)
- **Release builds**: Certificate pinning ENABLED (for production security)

## 📁 Files Created

```
/apps/mobile/lib/core/security/
├── certificate_pinning_service.dart    # Core pinning service
├── certificate_config.dart             # Pin configurations (⚠️ NEEDS UPDATE)
├── security_config.dart                # Security settings
├── certificate_pinning_example.dart    # Usage examples
├── CERTIFICATE_PINNING_GUIDE.md        # Complete guide
└── README.md                           # Module overview
```

## ⚡ How It Works

### Development (Debug Mode)
```bash
flutter run
# Output: ⚠️ Certificate pinning is disabled
# No configuration needed - works with localhost
```

### Production (Release Mode)
```bash
flutter build apk --release
# Output: 🔒 SSL Certificate Pinning enabled
#         Environment: production
#         Strict mode: true
```

## ⚠️ CRITICAL: Before Production Deployment

**You MUST replace placeholder certificate fingerprints!**

### Step 1: Get Your Certificate Fingerprints

```bash
# For production API
openssl s_client -connect api.sahool.app:443 < /dev/null 2>/dev/null | \
  openssl x509 -fingerprint -sha256 -noout -in /dev/stdin
```

### Step 2: Update Configuration

Edit `/apps/mobile/lib/core/security/certificate_config.dart`:

**BEFORE:**
```dart
value: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
```

**AFTER:**
```dart
value: 'a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890',
```

### Step 3: Build and Test

```bash
# Build for production
flutter build apk --release

# Install and test
adb install build/app/outputs/flutter-apk/app-release.apk
adb logcat | grep "Certificate"

# Expected output:
# ✅ Certificate pin matched for host: api.sahool.app
```

## 🔧 Configuration Files

### Main Configuration File
```
/apps/mobile/lib/core/security/certificate_config.dart
```

**Update these sections:**
- `getProductionPins()` - Production certificate fingerprints
- `getStagingPins()` - Staging certificate fingerprints

**Example:**
```dart
static Map<String, List<CertificatePin>> getProductionPins() {
  return {
    'api.sahool.app': [
      // Primary certificate
      CertificatePin(
        type: PinType.sha256,
        value: 'YOUR_ACTUAL_FINGERPRINT_HERE',  // ⚠️ REPLACE THIS
        expiryDate: DateTime(2026, 12, 31),
        description: 'Primary production certificate',
      ),
      // Backup for rotation
      CertificatePin(
        type: PinType.sha256,
        value: 'YOUR_BACKUP_FINGERPRINT_HERE',  // ⚠️ REPLACE THIS
        expiryDate: DateTime(2027, 6, 30),
        description: 'Backup production certificate',
      ),
    ],
  };
}
```

## 📝 Pre-Deployment Checklist

- [ ] Get certificate fingerprints for all domains
- [ ] Update `certificate_config.dart` with real values
- [ ] Add backup pins (minimum 2 per domain)
- [ ] Test in staging environment
- [ ] Build in release mode (`--release` flag)
- [ ] Verify certificate pinning is enabled in logs
- [ ] Test API connectivity
- [ ] Monitor for errors after deployment

## 🧪 Testing

### Check if Pinning is Enabled
```bash
adb logcat | grep "Certificate"
```

**Debug build:**
```
⚠️ Certificate pinning is disabled
```

**Release build:**
```
🔒 SSL Certificate Pinning enabled
   Environment: production
   Strict mode: true
   Debug bypass: false
   Configured domains: [api.sahool.app, ws.sahool.app, *.sahool.io]
```

### Successful Connection
```
✅ Certificate pin matched for host: api.sahool.app
```

### Failed Validation
```
❌ Certificate validation failed for host: api.sahool.app
   Certificate fingerprint: abc123...
```

## 📚 Documentation

### Quick Reference
- **This file** - Quick start guide
- `/lib/core/security/README.md` - Module overview

### Detailed Guides
- `/lib/core/security/CERTIFICATE_PINNING_GUIDE.md` - Complete setup guide
- `/apps/mobile/CERTIFICATE_PINNING_IMPLEMENTATION.md` - Implementation details
- `/apps/mobile/CERTIFICATE_PINNING_CODE_CHANGES.md` - All code changes

### Examples
- `/lib/core/security/certificate_pinning_example.dart` - 8 usage examples

## 🔍 Troubleshooting

### App Can't Connect in Production
**Problem:** Network errors in release build, works in debug

**Solution:**
1. Check fingerprints match actual server certificates
2. Use the helper function to get actual fingerprint:
   ```dart
   final fp = await getCertificateFingerprintFromUrl('https://api.sahool.app');
   print('Server fingerprint: $fp');
   ```
3. Update `certificate_config.dart` with correct value
4. Rebuild app

### Pinning Not Enabled
**Problem:** Logs show "Certificate pinning is disabled" in production

**Solution:**
1. Ensure building with `--release` flag
2. Check you're using `flutter build apk --release` (not `flutter run`)
3. Verify app is installed from release build

### Certificate Mismatch
**Problem:** "Certificate validation failed"

**Solution:**
1. Get current fingerprint from server
2. Compare with configured values
3. Update configuration if needed

## 🚀 Quick Commands

```bash
# Development (pinning disabled)
flutter run

# Get certificate fingerprint
openssl s_client -connect api.sahool.app:443 < /dev/null 2>/dev/null | \
  openssl x509 -fingerprint -sha256 -noout

# Build for production
flutter build apk --release

# Install and check logs
adb install build/app/outputs/flutter-apk/app-release.apk
adb logcat | grep "Certificate"
```

## 💡 Key Points

1. **Automatic Configuration** - No code changes needed in app logic
2. **Zero Impact on Development** - Disabled in debug mode
3. **Production Security** - Automatically enabled in release builds
4. **Must Update Fingerprints** - Replace placeholders before production!
5. **Always Have Backups** - Include 2+ pins per domain for rotation

## 📞 Next Steps

1. **Get fingerprints** from your actual servers
2. **Update** `certificate_config.dart`
3. **Test** in staging environment
4. **Deploy** to production
5. **Monitor** logs for any issues

## 🔐 Security Warning

⚠️ **CRITICAL**: The app will work in debug mode but MUST have correct fingerprints configured before production deployment!

**Current Status:** ⚠️ Placeholder fingerprints - UPDATE REQUIRED

---

**Need Help?** See `/lib/core/security/CERTIFICATE_PINNING_GUIDE.md` for complete documentation.
