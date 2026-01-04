# iOS Certificate Pinning Implementation Summary

## Overview

This document summarizes the iOS certificate pinning implementation added to the SAHOOL Field App mobile application. The implementation provides protection against man-in-the-middle (MITM) attacks and compromised Certificate Authorities (CAs) by validating server certificates against known public key hashes.

**Date Implemented:** 2026-01-03
**Platform:** iOS 14.0+
**Implementation Type:** SPKI (Subject Public Key Info) Pinning

---

## What Was Implemented

### 1. Dual-Layer Certificate Pinning

The iOS implementation uses a **two-layer approach** for maximum security:

#### Layer 1: System-Level (Info.plist)
- **File:** `ios/Runner/Info.plist`
- **Technology:** NSAppTransportSecurity with NSPinnedDomains
- **Enforcement:** iOS system level (cannot be bypassed)
- **Use Case:** Compliance and OS-level protection

#### Layer 2: Application-Level (Swift)
- **File:** `ios/Runner/CertificatePinning.swift`
- **Technology:** URLSession delegate with ServerTrust validation
- **Enforcement:** Application level (flexible, configurable)
- **Use Case:** Runtime configuration and detailed logging

### 2. Protected Domains

Certificate pinning is configured for the following domains:

| Domain | Purpose | Environment |
|--------|---------|-------------|
| `api.sahool.io` | Main Production API | Production |
| `api.sahool.app` | Alternative Production API | Production |
| `api-staging.sahool.app` | Staging API | Staging |
| `ws.sahool.app` | Production WebSocket | Production |
| `ws-staging.sahool.app` | Staging WebSocket | Staging |

### 3. Development Exceptions

The following domains are excluded from pinning to support development:

- `localhost` - iOS Simulator
- `10.0.2.2` - Android Emulator (when testing on same machine)

---

## Files Created/Modified

### Created Files

1. **`ios/Runner/CertificatePinning.swift`** (New)
   - Main certificate pinning implementation
   - URLSession delegate for certificate validation
   - SPKI hash extraction and validation
   - Pin expiry tracking and warnings
   - Debug logging and monitoring
   - ~400 lines of Swift code

2. **`ios/get_spki_hash.sh`** (New)
   - Utility script to extract SPKI hashes
   - Generates code snippets for easy integration
   - Provides certificate information
   - Creates audit trail with reports
   - ~150 lines of Bash script

3. **`CERTIFICATE_ROTATION_IOS.md`** (New)
   - Comprehensive iOS certificate rotation guide
   - Step-by-step rotation procedures
   - Troubleshooting guide
   - Emergency procedures
   - Best practices
   - ~500 lines of documentation

4. **`ios/README_CERTIFICATE_PINNING.md`** (New)
   - Quick reference guide for developers
   - Common tasks and commands
   - Testing checklist
   - Troubleshooting tips
   - ~200 lines of documentation

### Modified Files

1. **`ios/Runner/Info.plist`** (Updated)
   - Added NSAppTransportSecurity configuration
   - Added NSPinnedDomains for all protected domains
   - Added SPKI pin placeholders
   - Added localhost exceptions for development

2. **`ios/Runner/AppDelegate.swift`** (Updated)
   - Added certificate pinning initialization
   - Added DEBUG/RELEASE mode configuration
   - Added expiry warnings on app start
   - Added logging for monitoring

3. **`lib/core/security/certificate_pinning_service.dart`** (Updated)
   - Added comprehensive iOS implementation documentation
   - Added platform-specific implementation notes
   - Added SPKI hash extraction instructions
   - Updated checklist to include iOS items

---

## Technical Implementation Details

### SPKI Pinning vs Certificate Pinning

**Why SPKI Pinning?**

The implementation uses SPKI (Subject Public Key Info) pinning instead of certificate pinning:

| Aspect | Certificate Pinning | SPKI Pinning (Used) |
|--------|-------------------|-------------------|
| What's pinned | Entire certificate | Public key only |
| Certificate renewal | Breaks app | Works seamlessly |
| Rotation complexity | High | Low |
| Apple recommendation | Not recommended | Recommended |
| Expiry handling | App update required | Transparent |

**SPKI Hash Format:**
```
Base64-encoded SHA256 hash of the public key
Example: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
```

### Security Flow

```
┌─────────────────────────────────────────────────────┐
│ iOS App Makes HTTPS Request                        │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ iOS System Checks Info.plist NSPinnedDomains       │
│ (System-Level Validation)                           │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │ Pins Match?   │
         └───────┬───────┘
                 │
        ┌────────┴────────┐
        │ YES             │ NO
        │                 │
        ▼                 ▼
┌─────────────┐   ┌─────────────────┐
│ Continue    │   │ Block Request   │
└──────┬──────┘   └─────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│ URLSession Delegate Performs Additional Validation │
│ (Application-Level Validation)                      │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │ Pins Match?   │
         │ Not Expired?  │
         └───────┬───────┘
                 │
        ┌────────┴────────┐
        │ YES             │ NO
        │                 │
        ▼                 ▼
┌─────────────┐   ┌─────────────────┐
│ Allow       │   │ Block Request   │
│ Request     │   │ Log Error       │
└─────────────┘   └─────────────────┘
```

### Debug vs Release Behavior

**DEBUG Mode:**
```swift
CertificatePinningManager.shared.configure(
    enforceStrict: false,
    allowDebugBypass: true
)
```
- Pinning configured but bypassed
- Allows testing with localhost
- Logs warnings but doesn't block
- Useful for development

**RELEASE Mode:**
```swift
CertificatePinningManager.shared.configure(
    enforceStrict: true,
    allowDebugBypass: false
)
```
- Pinning strictly enforced
- Blocks invalid certificates
- No bypass allowed
- Production-ready

---

## How to Use

### For Developers

#### 1. Extract SPKI Hash

```bash
cd ios
./get_spki_hash.sh api.sahool.io
```

This outputs:
```
=================================
  SPKI Hash (for iOS Pinning)
=================================

SPKI-SHA256-BASE64:
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=

=================================
  Code Snippets
=================================

1. For Info.plist:

<dict>
    <key>SPKI-SHA256-BASE64</key>
    <string>AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</string>
</dict>

2. For CertificatePinning.swift:

certificatePins["api.sahool.io"] = [
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
]
```

#### 2. Update Info.plist

Copy the SPKI hash to `ios/Runner/Info.plist`:

```xml
<key>api.sahool.io</key>
<dict>
    <key>NSIncludesSubdomains</key>
    <true/>
    <key>NSPinnedLeafIdentities</key>
    <array>
        <dict>
            <key>SPKI-SHA256-BASE64</key>
            <string>YOUR_ACTUAL_SPKI_HASH_HERE</string>
        </dict>
    </array>
</dict>
```

#### 3. Update CertificatePinning.swift

Add the pin in `ios/Runner/CertificatePinning.swift`:

```swift
private func configureDefaultPins() {
    certificatePins["api.sahool.io"] = [
        "YOUR_ACTUAL_SPKI_HASH_HERE"
    ]
    pinExpiry["api.sahool.io"] = Date(timeIntervalSince1970: 1735689600)
}
```

#### 4. Test

```bash
flutter run
# Check console for:
# ✅ Certificate pin matched for host: api.sahool.io
```

### For DevOps/Operations

#### Certificate Rotation Process

**Timeline for certificate expiring on December 31, 2026:**

| Days Before | Action |
|------------|--------|
| 90 days | Obtain new certificate, get SPKI hash, update staging |
| 60 days | Submit app update to App Store |
| 30 days | Release app to production |
| 7 days | Install new certificate on server (alongside old) |
| 0 days (expiry) | Remove old certificate from server |
| +30 days | Remove old pin from code (optional cleanup) |

See `CERTIFICATE_ROTATION_IOS.md` for detailed procedures.

---

## Current Status

### ⚠️ Action Required Before Production

The current implementation uses **placeholder SPKI hashes**. Before deploying to production:

1. **Extract actual SPKI hashes** for each domain:
   ```bash
   cd ios
   ./get_spki_hash.sh api.sahool.io
   ./get_spki_hash.sh api.sahool.app
   ./get_spki_hash.sh api-staging.sahool.app
   ./get_spki_hash.sh ws.sahool.app
   ./get_spki_hash.sh ws-staging.sahool.app
   ```

2. **Update Info.plist** with actual hashes (replace placeholders)

3. **Update CertificatePinning.swift** with actual hashes (replace placeholders)

4. **Set correct expiry dates** based on certificate validity

5. **Test thoroughly** in staging environment

6. **Deploy to production** after validation

### Placeholder Locations

**In `ios/Runner/Info.plist`:**
```xml
<!-- Lines 67, 72, 86, 91, 105, 119, 133 -->
<string>AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</string>
<string>BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</string>
<string>EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE=</string>
<string>CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC=</string>
<string>FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF=</string>
```

**In `ios/Runner/CertificatePinning.swift`:**
```swift
// Lines 61-99
"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
"BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
"EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE="
"CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC="
"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF="
```

---

## Testing & Validation

### Pre-Production Checklist

- [ ] Extract SPKI hashes for all domains
- [ ] Replace placeholders in Info.plist
- [ ] Replace placeholders in CertificatePinning.swift
- [ ] Set correct expiry dates
- [ ] Test in iOS Simulator
- [ ] Test on physical iOS device
- [ ] Test valid certificates (should succeed)
- [ ] Test invalid certificates (should fail)
- [ ] Verify DEBUG mode bypass works
- [ ] Verify RELEASE mode enforces pinning
- [ ] Check console logs for warnings
- [ ] Build RELEASE version and test
- [ ] Test localhost works in development
- [ ] Test API requests succeed
- [ ] Test WebSocket connections work
- [ ] Document actual SPKI hashes securely
- [ ] Create certificate rotation schedule

### Manual Testing

```bash
# 1. Test in DEBUG mode (should bypass pinning)
flutter run

# 2. Test in RELEASE mode (should enforce pinning)
flutter build ios --release

# 3. Check logs for certificate validation
# Look for:
# ✅ Certificate pin matched for host: api.sahool.io
# OR
# ❌ Certificate validation failed for host: api.sahool.io
```

### Automated Testing

Consider adding integration tests:

```swift
// ios/RunnerTests/CertificatePinningTests.swift
func testValidCertificate() async throws {
    let url = URL(string: "https://api.sahool.io/healthz")!
    let (_, response) = try await URLSession.withCertificatePinning().data(from: url)
    XCTAssertEqual((response as? HTTPURLResponse)?.statusCode, 200)
}
```

---

## Monitoring & Maintenance

### Certificate Expiry Monitoring

The app automatically logs expiring certificates on startup:

```
⚠️ WARNING: Some certificate pins will expire soon:
   - api.sahool.io: 2026-12-31 00:00:00 +0000 (30 days)
```

### Recommended Monitoring

1. **Set up certificate expiry alerts** (90, 60, 30 days before expiry)
2. **Monitor API connection failures** in production
3. **Track app version adoption** before removing old pins
4. **Document all certificate rotations** for audit trail

### Maintenance Tasks

| Task | Frequency | Action |
|------|-----------|--------|
| Check expiring pins | Monthly | Review expiry dates in code |
| Test certificate rotation | Quarterly | Practice in staging |
| Update documentation | As needed | Keep procedures current |
| Audit pin configuration | Quarterly | Verify pins match server |
| Review security logs | Weekly | Check for validation failures |

---

## Security Considerations

### ✅ What This Protects Against

1. **Compromised Certificate Authorities**
   - Even if a CA is compromised, pinned apps won't trust rogue certificates

2. **Man-in-the-Middle Attacks**
   - Attackers cannot intercept traffic even with a valid-looking certificate

3. **DNS Hijacking**
   - Even if DNS is hijacked, certificate validation will fail

4. **Rogue WiFi Access Points**
   - Public WiFi attacks are ineffective due to pinning

### ⚠️ What This Doesn't Protect Against

1. **Compromised Private Keys**
   - If server private key is stolen, pinning won't help

2. **Jailbroken Devices**
   - Pinning can be bypassed on jailbroken devices

3. **Code Injection**
   - Malicious code injected into app can bypass pinning

4. **Reverse Engineering**
   - Determined attackers can extract pins from app binary

### Best Practices

1. **Always pin multiple certificates** (current + backup)
2. **Monitor certificate expiry** (set up automated alerts)
3. **Test thoroughly** in staging before production
4. **Document rotation procedures** for the team
5. **Keep pins secure** (don't commit to public repos if sensitive)
6. **Update regularly** (before certificates expire)
7. **Plan for emergencies** (have rollback procedures)

---

## Troubleshooting

### Common Issues

#### Issue 1: All API requests failing

**Symptoms:**
```
❌ Certificate validation failed for host: api.sahool.io
```

**Solution:**
```bash
# Verify server certificate
./ios/get_spki_hash.sh api.sahool.io

# Compare with configured hash
# Update if different
```

#### Issue 2: Works in DEBUG, fails in RELEASE

**Cause:** Debug bypass enabled (expected)

**Solution:** This is normal. In DEBUG mode, pinning is bypassed for development.

#### Issue 3: Localhost not working

**Solution:** Check Info.plist has localhost exception:
```xml
<key>NSExceptionDomains</key>
<dict>
    <key>localhost</key>
    <dict>
        <key>NSExceptionAllowsInsecureHTTPLoads</key>
        <true/>
    </dict>
</dict>
```

---

## Related Documentation

1. **`CERTIFICATE_ROTATION_IOS.md`** - Detailed rotation guide
2. **`ios/README_CERTIFICATE_PINNING.md`** - Quick reference
3. **`lib/core/security/certificate_pinning_service.dart`** - Android implementation
4. **Apple Documentation:**
   - [App Transport Security](https://developer.apple.com/documentation/security/preventing_insecure_network_connections)
   - [Certificate Pinning](https://developer.apple.com/news/?id=g9ejcf8y)

---

## Next Steps

### Immediate (Before Production Deploy)

1. [ ] Extract actual SPKI hashes using `get_spki_hash.sh`
2. [ ] Update Info.plist with actual hashes
3. [ ] Update CertificatePinning.swift with actual hashes
4. [ ] Set correct expiry dates
5. [ ] Test thoroughly in staging
6. [ ] Document actual hashes securely

### Short-term (Within 1 Month)

1. [ ] Set up certificate expiry monitoring
2. [ ] Create certificate rotation schedule
3. [ ] Document emergency procedures
4. [ ] Train team on rotation process
5. [ ] Set up automated alerts

### Long-term (Ongoing)

1. [ ] Monitor certificate expiry dates
2. [ ] Perform quarterly rotation tests
3. [ ] Keep documentation updated
4. [ ] Review and update pins as needed
5. [ ] Audit security logs regularly

---

## Summary

The iOS certificate pinning implementation provides robust protection against MITM attacks and compromised CAs. The dual-layer approach (system-level + application-level) ensures comprehensive security while maintaining flexibility for development and debugging.

**Key Features:**
- ✅ SPKI pinning (recommended by Apple)
- ✅ Two-layer protection (Info.plist + Swift)
- ✅ Debug bypass for development
- ✅ Expiry tracking and warnings
- ✅ Comprehensive logging
- ✅ Easy-to-use utility scripts
- ✅ Detailed documentation

**Before Production:**
- ⚠️ Replace all placeholder SPKI hashes
- ⚠️ Set correct expiry dates
- ⚠️ Test thoroughly
- ⚠️ Document certificate rotation plan

---

**Implementation Date:** 2026-01-03
**Version:** 1.0
**Status:** Ready for production (after replacing placeholders)
**Maintained By:** SAHOOL Mobile Team
