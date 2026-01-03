# iOS Certificate Pinning - Quick Reference

## Overview

The iOS app implements certificate pinning using SPKI (Subject Public Key Info) hashes to protect against man-in-the-middle attacks and compromised Certificate Authorities.

## Quick Start

### 1. Extract SPKI Hash

```bash
cd ios
./get_spki_hash.sh api.sahool.io
```

This will output the SPKI hash and code snippets for easy integration.

### 2. Update Info.plist

Add or update the SPKI hash in `Runner/Info.plist`:

```xml
<key>NSPinnedDomains</key>
<dict>
    <key>api.sahool.io</key>
    <dict>
        <key>NSIncludesSubdomains</key>
        <true/>
        <key>NSPinnedLeafIdentities</key>
        <array>
            <dict>
                <key>SPKI-SHA256-BASE64</key>
                <string>YOUR_SPKI_HASH_HERE</string>
            </dict>
        </array>
    </dict>
</dict>
```

### 3. Update CertificatePinning.swift

Add or update pins in `Runner/CertificatePinning.swift`:

```swift
private func configureDefaultPins() {
    certificatePins["api.sahool.io"] = [
        "YOUR_SPKI_HASH_HERE"
    ]
    pinExpiry["api.sahool.io"] = Date(timeIntervalSince1970: 1735689600)
}
```

### 4. Test

```bash
# Build and run in simulator
flutter run

# Check console for:
# ✅ Certificate pin matched for host: api.sahool.io
```

## Files Structure

```
ios/
├── Runner/
│   ├── Info.plist                    # System-level pinning (NSPinnedDomains)
│   ├── CertificatePinning.swift      # Application-level pinning (URLSession)
│   └── AppDelegate.swift             # Initialization
├── get_spki_hash.sh                  # Utility script to extract SPKI hashes
└── README_CERTIFICATE_PINNING.md     # This file
```

## Implementation Details

### Two-Layer Protection

1. **System-Level (Info.plist)**
   - Enforced by iOS before app code runs
   - Cannot be bypassed programmatically
   - Uses `NSAppTransportSecurity` > `NSPinnedDomains`

2. **Application-Level (Swift)**
   - Uses `URLSession` delegate
   - More flexible and configurable
   - Provides detailed logging
   - Can bypass in DEBUG mode for development

### Pinned Domains

Current domains with certificate pinning:

- ✅ `api.sahool.io` - Production API
- ✅ `api.sahool.app` - Production API (alternative)
- ✅ `api-staging.sahool.app` - Staging API
- ✅ `ws.sahool.app` - Production WebSocket
- ✅ `ws-staging.sahool.app` - Staging WebSocket

### Debug vs Release

**DEBUG Mode:**
- Certificate pinning configured but bypassed
- Allows testing with localhost/development servers
- Logs: "⚠️ Certificate pinning bypassed in DEBUG mode"

**RELEASE Mode:**
- Certificate pinning strictly enforced
- Blocks connections with invalid certificates
- Logs: "✅ Certificate pin matched" or "❌ Certificate validation failed"

## Common Tasks

### Add New Domain

1. Extract SPKI hash:
   ```bash
   ./get_spki_hash.sh newdomain.sahool.io
   ```

2. Add to `Info.plist`:
   ```xml
   <key>newdomain.sahool.io</key>
   <dict>
       <key>NSIncludesSubdomains</key>
       <true/>
       <key>NSPinnedLeafIdentities</key>
       <array>
           <dict>
               <key>SPKI-SHA256-BASE64</key>
               <string>YOUR_HASH</string>
           </dict>
       </array>
   </dict>
   ```

3. Add to `CertificatePinning.swift`:
   ```swift
   certificatePins["newdomain.sahool.io"] = ["YOUR_HASH"]
   pinExpiry["newdomain.sahool.io"] = Date(timeIntervalSince1970: 1735689600)
   ```

### Update Existing Pins

See detailed guide in: `../CERTIFICATE_ROTATION_IOS.md`

**Quick steps:**

1. Get new SPKI hash
2. Add new hash alongside old hash (don't remove old yet!)
3. Test thoroughly
4. Deploy app update
5. Wait for user adoption (80%+)
6. Remove old hash

### Remove Domain

1. Remove from `Info.plist` NSPinnedDomains
2. Remove from `CertificatePinning.swift`
3. Test to ensure app still works

### Check Expiring Pins

The app automatically logs expiring pins on startup:

```
⚠️ WARNING: Some certificate pins will expire soon:
   - api.sahool.io: 2026-12-31 00:00:00 +0000
```

## Troubleshooting

### Issue: All API requests failing

**Symptoms:**
```
❌ Certificate validation failed for host: api.sahool.io
```

**Solution:**
```bash
# 1. Check if server certificate changed
./get_spki_hash.sh api.sahool.io

# 2. Compare with configured hash in CertificatePinning.swift

# 3. If different, update the hash
```

### Issue: Works in DEBUG, fails in RELEASE

**Cause:** Debug bypass enabled (expected behavior)

**Solution:** To test pinning in DEBUG mode, modify `AppDelegate.swift`:

```swift
#if DEBUG
CertificatePinningManager.shared.configure(
    enforceStrict: true,    // Changed from false
    allowDebugBypass: false // Changed from true
)
#endif
```

### Issue: Localhost not working

**Solution:** Check `Info.plist` has localhost exception:

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

## Testing Checklist

Before deploying to production:

- [ ] Extract SPKI hashes for all domains
- [ ] Update Info.plist with correct hashes
- [ ] Update CertificatePinning.swift with correct hashes
- [ ] Set correct expiry dates
- [ ] Test in iOS Simulator
- [ ] Test on physical iOS device
- [ ] Test with valid certificates (should succeed)
- [ ] Test with invalid certificates (should fail)
- [ ] Test localhost works in development
- [ ] Check console logs for certificate warnings
- [ ] Build in RELEASE mode and test
- [ ] Verify pins match between Info.plist and Swift code

## Security Checklist

- [ ] All production domains use HTTPS
- [ ] At least 2 pins per domain (current + backup)
- [ ] Expiry dates set correctly
- [ ] Debug bypass disabled in RELEASE builds
- [ ] No hardcoded API keys or secrets
- [ ] Localhost exceptions only for development
- [ ] Certificate rotation plan documented

## Useful Commands

```bash
# Extract SPKI hash
./get_spki_hash.sh api.sahool.io

# Test SSL connection
openssl s_client -connect api.sahool.io:443 -servername api.sahool.io

# View certificate details
openssl s_client -connect api.sahool.io:443 -servername api.sahool.io < /dev/null 2>/dev/null | openssl x509 -noout -text

# Check certificate expiry
openssl s_client -connect api.sahool.io:443 -servername api.sahool.io < /dev/null 2>/dev/null | openssl x509 -noout -dates

# Clean Xcode build
cd ios
xcodebuild clean
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# Build release
flutter build ios --release
```

## Additional Resources

- **Detailed Guide:** `../CERTIFICATE_ROTATION_IOS.md`
- **Android Implementation:** `../lib/core/security/certificate_pinning_service.dart`
- **Apple Documentation:** [App Transport Security](https://developer.apple.com/documentation/security/preventing_insecure_network_connections)

## Support

For issues:

1. Check troubleshooting section above
2. Review console logs in Xcode
3. Test with `./get_spki_hash.sh` to verify server certificate
4. Contact mobile team if issues persist

---

**Last Updated:** 2026-01-03
**iOS Version:** 14.0+
**Flutter Version:** 3.x+
