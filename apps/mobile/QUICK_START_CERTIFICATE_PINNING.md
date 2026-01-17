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

### ⚠️ WARNING: PLACEHOLDER VALUES IN USE

The app currently uses **PLACEHOLDER** certificate pins (AAAA..., BBBB..., CCCC..., etc.) that are **NOT SECURE** for production use. You MUST replace these before deploying.

### Step 1: Generate Real Certificate Pins

**Use the automated script (RECOMMENDED):**

```bash
cd /apps/mobile

# For production API
./scripts/generate_cert_pins.sh api.sahool.app

# For production API (alternate domain)
./scripts/generate_cert_pins.sh api.sahool.io

# For WebSocket
./scripts/generate_cert_pins.sh ws.sahool.app

# For staging
./scripts/generate_cert_pins.sh api-staging.sahool.app
./scripts/generate_cert_pins.sh ws-staging.sahool.app
```

The script will:

- Generate both Android (SHA256) and iOS (SPKI) pins
- Save a summary file with all the pins
- Show you exactly where to paste each pin
- Provide certificate information and expiry dates

**Manual method (alternative):**

```bash
# For Android - SHA256 certificate fingerprint
openssl s_client -connect api.sahool.app:443 < /dev/null 2>/dev/null | \
  openssl x509 -fingerprint -sha256 -noout | cut -d= -f2 | tr -d ':'

# For iOS - SPKI public key hash
openssl s_client -connect api.sahool.app:443 < /dev/null 2>/dev/null | \
  openssl x509 -pubkey -noout | \
  openssl pkey -pubin -outform der | \
  openssl dgst -sha256 -binary | \
  openssl enc -base64
```

### Step 2: Update All Configuration Files

You need to update pins in **THREE** places:

#### 2.1 Android Configuration

Edit `/apps/mobile/android/app/src/main/res/xml/network_security_config.xml`:

**Find the TODO comments and replace:**

```xml
<!-- TODO: Replace AAAA... with actual SHA256 fingerprint -->
<pin digest="sha256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
```

**With your generated pin:**

```xml
<pin digest="sha256">YOUR_ACTUAL_SHA256_FINGERPRINT_HERE</pin>
```

#### 2.2 iOS Configuration

Edit `/apps/mobile/ios/Runner/Info.plist`:

**Find the TODO comments and replace:**

```xml
<!-- TODO: Replace AAAA... with actual SPKI hash from production certificate -->
<key>SPKI-SHA256-BASE64</key>
<string>AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</string>
```

**With your generated SPKI hash:**

```xml
<key>SPKI-SHA256-BASE64</key>
<string>YOUR_ACTUAL_SPKI_HASH_HERE</string>
```

#### 2.3 Dart Configuration

Edit `/apps/mobile/lib/core/security/certificate_config.dart`:

**Find the TODO comments and replace:**

```dart
// TODO: CRITICAL - Replace with actual production certificate fingerprint
value: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', // PLACEHOLDER
```

**With your generated fingerprint:**

```dart
value: 'your_actual_sha256_fingerprint_in_lowercase',
```

### Step 3: Verify All Placeholders Are Replaced

**Search for remaining placeholders:**

```bash
cd /apps/mobile

# Search for placeholder patterns
grep -r "AAAA" ios/Runner/Info.plist android/app/src/main/res/xml/network_security_config.xml
grep -r "PLACEHOLDER - MUST REPLACE" lib/core/security/
```

If any placeholders are found, replace them before deploying!

### Step 4: Build and Test

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

### Generate Certificate Pins

- [ ] Run `./scripts/generate_cert_pins.sh` for all domains
- [ ] Save the generated summary files for reference
- [ ] Get certificate fingerprints for all domains:
  - [ ] api.sahool.app
  - [ ] api.sahool.io
  - [ ] ws.sahool.app
  - [ ] api-staging.sahool.app
  - [ ] ws-staging.sahool.app

### Update Configuration Files

- [ ] Update Android `network_security_config.xml` with SHA256 pins
- [ ] Update iOS `Info.plist` with SPKI hashes
- [ ] Update Dart `certificate_config.dart` with SHA256 pins
- [ ] Add backup pins (minimum 2 per domain)
- [ ] Verify ALL placeholder values are replaced (search for AAAA, BBBB, CCCC, etc.)

### Testing

- [ ] Test in staging environment first
- [ ] Build in release mode (`--release` flag)
- [ ] Verify certificate pinning is enabled in logs
- [ ] Test API connectivity for all domains
- [ ] Test certificate rotation with backup pins
- [ ] Verify error handling when pins don't match

### Monitoring

- [ ] Set up alerts for certificate expiry (30 days before)
- [ ] Document certificate rotation procedures
- [ ] Monitor for errors after deployment
- [ ] Test on both Android and iOS platforms

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
# Generate certificate pins (RECOMMENDED)
cd /apps/mobile
./scripts/generate_cert_pins.sh api.sahool.app

# Development (pinning disabled)
flutter run

# Get certificate fingerprint (manual method)
openssl s_client -connect api.sahool.app:443 < /dev/null 2>/dev/null | \
  openssl x509 -fingerprint -sha256 -noout

# Verify placeholders are replaced
grep -r "AAAA" ios/Runner/Info.plist android/app/src/main/res/xml/network_security_config.xml
grep -r "PLACEHOLDER - MUST REPLACE" lib/core/security/

# Build for production
flutter build apk --release

# Install and check logs
adb install build/app/outputs/flutter-apk/app-release.apk
adb logcat | grep "Certificate"
```

## 🔧 Certificate Pin Generation Script

The automated script at `/apps/mobile/scripts/generate_cert_pins.sh` makes it easy to generate certificate pins for both Android and iOS platforms.

### Features

- Generates both Android SHA256 fingerprints and iOS SPKI hashes
- Shows certificate information (subject, issuer, validity dates)
- Provides ready-to-paste configuration snippets
- Saves a summary file for reference
- Validates SSL connection and certificate

### Usage

```bash
cd /apps/mobile

# Basic usage
./scripts/generate_cert_pins.sh <domain>

# With custom port
./scripts/generate_cert_pins.sh <domain> <port>

# Examples
./scripts/generate_cert_pins.sh api.sahool.app
./scripts/generate_cert_pins.sh api.sahool.app 443
./scripts/generate_cert_pins.sh api-staging.sahool.app
```

### Output

The script generates:

1. **Console output** with formatted pins for each platform
2. **Summary file** (`cert_pins_<domain>_<timestamp>.txt`) with all the information

### What to do with the output

1. **For Android**: Copy the SHA256 fingerprint to `network_security_config.xml`
2. **For iOS**: Copy the SPKI hash to `Info.plist`
3. **For Dart**: Copy the SHA256 fingerprint (lowercase) to `certificate_config.dart`

### Requirements

- OpenSSL must be installed
- Network access to the certificate server
- Valid SSL certificate on the server

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

⚠️ **CRITICAL SECURITY WARNING** ⚠️

### Current Status: PLACEHOLDER VALUES IN USE

The mobile app currently contains **PLACEHOLDER** certificate pins that are **NOT SECURE** for production use:

- **Android**: `network_security_config.xml` contains AAAA..., BBBB..., CCCC... placeholders
- **iOS**: `Info.plist` contains AAAA..., BBBB..., CCCC... placeholders
- **Dart**: `certificate_config.dart` contains example SHA256 hashes

### Why This Matters

Without real certificate pins:

- Certificate pinning will **NOT WORK** in production
- The app is **VULNERABLE** to man-in-the-middle attacks
- Security benefits of certificate pinning are **LOST**

### Required Actions Before Production

1. **Generate real certificate pins** using `./scripts/generate_cert_pins.sh`
2. **Replace ALL placeholders** in:
   - `/apps/mobile/android/app/src/main/res/xml/network_security_config.xml`
   - `/apps/mobile/ios/Runner/Info.plist`
   - `/apps/mobile/lib/core/security/certificate_config.dart`
3. **Verify** no placeholders remain (use grep commands above)
4. **Test thoroughly** in staging before production
5. **Add backup pins** for certificate rotation

### How to Verify Placeholders Are Replaced

```bash
cd /apps/mobile

# This should return NO results:
grep -r "AAAA" ios/Runner/Info.plist android/app/src/main/res/xml/network_security_config.xml
grep -r "PLACEHOLDER - MUST REPLACE" lib/core/security/

# If any results are found, you MUST replace those values before deploying!
```

### Deployment Blockers

**DO NOT DEPLOY TO PRODUCTION IF:**

- Any placeholder values (AAAA..., BBBB..., etc.) remain in configuration files
- Grep commands above return any results
- You haven't tested with real certificate pins in staging
- You don't have backup pins configured for rotation

---

**Need Help?** See `/lib/core/security/CERTIFICATE_PINNING_GUIDE.md` for complete documentation.

**Quick Start:** Run `./scripts/generate_cert_pins.sh api.sahool.app` to get started.
