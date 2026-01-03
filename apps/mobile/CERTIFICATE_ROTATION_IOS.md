# iOS Certificate Pinning & Rotation Guide

## Overview

This document provides comprehensive guidance for managing SSL/TLS certificate pinning on iOS in the SAHOOL Field App. iOS certificate pinning is implemented using SPKI (Subject Public Key Info) pinning, which provides better resilience during certificate rotation compared to certificate pinning.

## Table of Contents

- [How iOS Certificate Pinning Works](#how-ios-certificate-pinning-works)
- [Implementation Architecture](#implementation-architecture)
- [Getting SPKI Hashes](#getting-spki-hashes)
- [Updating Certificate Pins](#updating-certificate-pins)
- [Certificate Rotation Process](#certificate-rotation-process)
- [Testing & Validation](#testing--validation)
- [Troubleshooting](#troubleshooting)
- [Emergency Procedures](#emergency-procedures)

---

## How iOS Certificate Pinning Works

### SPKI Pinning vs Certificate Pinning

**SPKI (Subject Public Key Info) Pinning** (Recommended for iOS):
- Pins the **public key** of the certificate
- Public key remains the same when certificate is renewed
- More resilient to certificate rotation
- Recommended by Apple for production apps
- Less likely to break app during routine certificate renewal

**Certificate Pinning**:
- Pins the **entire certificate**
- Certificate changes completely when renewed
- Requires app update when certificate is renewed
- Higher risk of app breakage

### Two-Layer Implementation

The iOS certificate pinning is implemented at two levels:

1. **System-Level (Info.plist)**
   - Location: `ios/Runner/Info.plist`
   - Uses `NSAppTransportSecurity` with `NSPinnedDomains`
   - Enforced by iOS system before app code runs
   - Cannot be bypassed programmatically
   - Good for compliance requirements

2. **Application-Level (Swift)**
   - Location: `ios/Runner/CertificatePinning.swift`
   - Uses `URLSession` delegate
   - More flexible and configurable
   - Allows runtime pin updates
   - Provides detailed logging
   - Can be bypassed in DEBUG mode for development

---

## Implementation Architecture

### Files Involved

```
apps/mobile/
├── ios/
│   └── Runner/
│       ├── Info.plist                    # System-level pinning
│       ├── CertificatePinning.swift      # Application-level pinning
│       └── AppDelegate.swift             # Initialization
└── lib/core/security/
    └── certificate_pinning_service.dart  # Android pinning (reference)
```

### Domains Configured

Current domains with certificate pinning:

- `api.sahool.io` - Production API
- `api.sahool.app` - Production API (alternative)
- `api-staging.sahool.app` - Staging API
- `ws.sahool.app` - Production WebSocket
- `ws-staging.sahool.app` - Staging WebSocket

---

## Getting SPKI Hashes

### Method 1: OpenSSL Command (Recommended)

```bash
# Get SPKI hash for a domain
openssl s_client -connect api.sahool.io:443 -servername api.sahool.io < /dev/null 2>/dev/null | \
openssl x509 -pubkey -noout | \
openssl pkey -pubin -outform der | \
openssl dgst -sha256 -binary | \
openssl enc -base64

# Output example:
# AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
```

### Method 2: Using a Script

Create a script `get_spki_hash.sh`:

```bash
#!/bin/bash

DOMAIN=$1
PORT=${2:-443}

if [ -z "$DOMAIN" ]; then
    echo "Usage: $0 <domain> [port]"
    echo "Example: $0 api.sahool.io 443"
    exit 1
fi

echo "Getting SPKI hash for $DOMAIN:$PORT..."

SPKI_HASH=$(openssl s_client -connect $DOMAIN:$PORT -servername $DOMAIN < /dev/null 2>/dev/null | \
openssl x509 -pubkey -noout | \
openssl pkey -pubin -outform der | \
openssl dgst -sha256 -binary | \
openssl enc -base64)

if [ -n "$SPKI_HASH" ]; then
    echo ""
    echo "✅ SPKI Hash for $DOMAIN:"
    echo "$SPKI_HASH"
    echo ""
    echo "Add this to Info.plist and CertificatePinning.swift"
else
    echo "❌ Failed to get SPKI hash"
    exit 1
fi
```

Usage:
```bash
chmod +x get_spki_hash.sh
./get_spki_hash.sh api.sahool.io
```

### Method 3: Using Swift (In-App)

Add this to your iOS app for debugging:

```swift
// In CertificatePinning.swift, add this utility method
static func printCertificateInfo(forURL urlString: String) {
    guard let url = URL(string: urlString) else { return }

    let task = URLSession.shared.dataTask(with: url) { _, response, _ in
        // Certificate info will be logged by URLSession delegate
    }
    task.resume()
}
```

### Method 4: Browser (Less Accurate)

⚠️ **Not recommended** - Browser may cache or modify certificates

1. Visit domain in Safari/Chrome
2. Click lock icon → Certificate → Details
3. Export certificate
4. Run openssl command on exported file

---

## Updating Certificate Pins

### Step 1: Get New SPKI Hashes

```bash
# Production API
./get_spki_hash.sh api.sahool.io

# Staging API
./get_spki_hash.sh api-staging.sahool.app

# WebSocket
./get_spki_hash.sh ws.sahool.app
```

### Step 2: Update Info.plist

Location: `ios/Runner/Info.plist`

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
                <!-- NEW SPKI hash -->
                <key>SPKI-SHA256-BASE64</key>
                <string>YOUR_NEW_SPKI_HASH_HERE</string>
            </dict>
            <dict>
                <!-- OLD SPKI hash (keep for backward compatibility) -->
                <key>SPKI-SHA256-BASE64</key>
                <string>YOUR_OLD_SPKI_HASH_HERE</string>
            </dict>
        </array>
    </dict>
</dict>
```

### Step 3: Update CertificatePinning.swift

Location: `ios/Runner/CertificatePinning.swift`

```swift
private func configureDefaultPins() {
    // Production API domain: api.sahool.io
    certificatePins["api.sahool.io"] = [
        "YOUR_NEW_SPKI_HASH_HERE", // New certificate
        "YOUR_OLD_SPKI_HASH_HERE"  // Old certificate (backup)
    ]
    pinExpiry["api.sahool.io"] = Date(timeIntervalSince1970: 1735689600) // 2026-12-31

    // Add other domains...
}
```

### Step 4: Test in Staging

1. Update staging pins first
2. Build and test in staging environment
3. Verify connections work
4. Check certificate validation logs

### Step 5: Deploy to Production

1. Submit app update to App Store
2. Wait for approval
3. Release to users
4. Monitor for connection issues

---

## Certificate Rotation Process

### Proactive Rotation (Recommended)

**Timeline for certificate expiring on December 31, 2026:**

#### 90 Days Before Expiry (October 1, 2026)

1. **Obtain new certificate** from CA
2. **Get SPKI hash** of new certificate
3. **Add new pin** to app alongside old pin
4. **Update staging** environment
5. **Test thoroughly** in staging

#### 60 Days Before Expiry (November 1, 2026)

1. **Submit app update** to App Store with new pins
2. **Include release notes** about improved security
3. Wait for Apple approval

#### 30 Days Before Expiry (December 1, 2026)

1. **Release app** to production
2. **Monitor adoption** rate
3. Wait for sufficient user adoption (e.g., 80%+)

#### 7 Days Before Expiry (December 24, 2026)

1. **Install new certificate** on server
2. Server now has both old and new certificates
3. Old app versions still work (pinned to old cert)
4. New app versions work (pinned to both certs)

#### On Expiry Date (December 31, 2026)

1. **Remove old certificate** from server
2. Only new certificate remains
3. Old app versions stop working (force update)
4. Monitor for connection issues

#### 30 Days After Rotation (January 30, 2027)

1. **Remove old pin** from codebase
2. Only new pin remains
3. Submit another app update (optional cleanup)

### Emergency Rotation (Compromise)

If a certificate is compromised and needs immediate rotation:

#### Immediate Actions (Within 1 Hour)

1. **Revoke compromised certificate**
2. **Generate new certificate**
3. **Get SPKI hash** of new certificate
4. **Install new certificate** on server
5. **Disable old certificate** immediately

#### Same Day

1. **Update app code** with new pins (keep old as backup)
2. **Submit emergency update** to App Store
   - Request expedited review
   - Explain security issue in review notes
3. **Communicate to users** via:
   - Push notification
   - Email
   - In-app message
   - Social media

#### Week 1

1. **Monitor adoption**
2. **Send reminder notifications**
3. **Provide support** for users with issues

#### Week 2

1. **Force update** if adoption is low
2. **Block old app versions** via API version check

---

## Testing & Validation

### Local Testing

#### 1. Test Valid Certificate

```swift
// In your app, enable debug logging
#if DEBUG
print("Testing certificate pinning for api.sahool.io...")
#endif

// Make a request
let url = URL(string: "https://api.sahool.io/healthz")!
let task = URLSession.withCertificatePinning().dataTask(with: url) { data, response, error in
    if let error = error {
        print("❌ Request failed: \(error)")
    } else {
        print("✅ Request succeeded")
    }
}
task.resume()
```

#### 2. Test Invalid Certificate

Temporarily add a wrong SPKI hash to test rejection:

```swift
certificatePins["api.sahool.io"] = [
    "WRONGWRONGWRONGWRONGWRONGWRONGWRONGWRONGWRONG=" // Invalid hash
]
```

Expected result: Connection should fail with certificate validation error.

### Integration Testing

Create integration tests:

```swift
// CertificatePinningTests.swift
import XCTest

class CertificatePinningTests: XCTestCase {

    func testValidCertificate() async throws {
        let url = URL(string: "https://api.sahool.io/healthz")!
        let (_, response) = try await URLSession.withCertificatePinning().data(from: url)

        XCTAssertNotNil(response)
        XCTAssertEqual((response as? HTTPURLResponse)?.statusCode, 200)
    }

    func testInvalidCertificate() async {
        // Test with invalid pins
        CertificatePinningManager.shared.addPins(
            forDomain: "badhost.example.com",
            pins: ["INVALIDINVALIDINVALIDINVALIDINVALIDINVALI="]
        )

        let url = URL(string: "https://badhost.example.com")!

        do {
            let _ = try await URLSession.withCertificatePinning().data(from: url)
            XCTFail("Should have failed with invalid certificate")
        } catch {
            // Expected to fail
            XCTAssertNotNil(error)
        }
    }
}
```

### Manual Testing Checklist

- [ ] App starts successfully
- [ ] API requests succeed in DEBUG mode
- [ ] API requests succeed in RELEASE mode
- [ ] Correct pins allow connections
- [ ] Incorrect pins block connections
- [ ] Localhost works in development
- [ ] Staging environment works
- [ ] Production environment works
- [ ] Certificate expiry warnings appear
- [ ] App handles certificate validation failure gracefully

---

## Troubleshooting

### Issue 1: All API Requests Failing

**Symptoms:**
- All network requests fail
- Error: "The certificate for this server is invalid"
- Console shows: "❌ Certificate validation failed"

**Causes:**
1. Wrong SPKI hash configured
2. Server certificate changed
3. Man-in-the-middle attack (legitimate)

**Solutions:**

```bash
# 1. Verify current server certificate
openssl s_client -connect api.sahool.io:443 -servername api.sahool.io < /dev/null 2>/dev/null | \
openssl x509 -pubkey -noout | \
openssl pkey -pubin -outform der | \
openssl dgst -sha256 -binary | \
openssl enc -base64

# 2. Compare with configured pins in CertificatePinning.swift

# 3. If different, update pins and redeploy
```

### Issue 2: App Works in DEBUG but Fails in RELEASE

**Cause:** Debug bypass is enabled

**Solution:** Check AppDelegate.swift:

```swift
#if DEBUG
CertificatePinningManager.shared.configure(
    enforceStrict: false,
    allowDebugBypass: true  // This bypasses pinning in DEBUG
)
#endif
```

This is expected behavior. Test with `allowDebugBypass: false` to verify pins.

### Issue 3: Localhost Not Working

**Cause:** NSExceptionDomains not configured

**Solution:** Check Info.plist:

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

### Issue 4: Certificate Expiry Warnings

**Symptoms:**
- Console shows: "⚠️ Certificate pins expired for host: api.sahool.io"

**Solution:**

1. Update pins before expiry (see [Certificate Rotation](#certificate-rotation-process))
2. Check expiry dates:

```swift
// In app
let expiringPins = CertificatePinningManager.shared.getExpiringPins(daysThreshold: 30)
for (domain, expiryDate) in expiringPins {
    print("⚠️ \(domain) expires on \(expiryDate)")
}
```

### Issue 5: App Store Rejection

**Cause:** Apple flagged NSAllowsArbitraryLoads or security issues

**Solutions:**

1. **Remove NSAllowsArbitraryLoads** or set to `false`
2. **Ensure all domains use HTTPS**
3. **Document exceptions** in App Store review notes:
   ```
   NSExceptionDomains is used for:
   - localhost: Development/testing only
   - 10.0.2.2: Android emulator compatibility
   These exceptions are not used in production.
   ```

---

## Emergency Procedures

### Scenario 1: Certificate Compromised

**Immediate Actions (Within 1 Hour):**

1. **Revoke certificate** via CA portal
2. **Generate new certificate**
3. **Get new SPKI hash**
4. **Install on server**
5. **Update app** with new pins
6. **Submit expedited review** to Apple

**Communication Template:**

```
Subject: Critical Security Update Required

Dear SAHOOL Field App User,

We have identified a security issue that requires you to update your app immediately.

Action Required:
1. Update SAHOOL Field App to version X.X.X
2. Update is available now on the App Store

What's changed:
- Enhanced security certificates
- Improved data protection

Thank you for your prompt attention.
```

### Scenario 2: Pins Expire Before App Update Released

**If pins expire before users update:**

**Option 1: Emergency Server Configuration**

Keep old certificate active alongside new:

```nginx
# nginx configuration
ssl_certificate /path/to/new/cert.pem;
ssl_certificate /path/to/old/cert.pem;  # Keep old cert temporarily
```

**Option 2: API Version Check**

Implement forced update:

```swift
// Server response
{
  "min_app_version": "2.0.0",
  "update_required": true,
  "update_url": "https://apps.apple.com/app/sahool/id..."
}
```

**Option 3: Dynamic Pin Updates (Advanced)**

Consider implementing remote pin configuration:
- Store pins in secure remote config
- Download pins on app start
- Validate pins using signature verification
- ⚠️ This adds complexity but prevents app updates for pin changes

---

## Best Practices

### 1. Always Pin Multiple Certificates

```swift
certificatePins["api.sahool.io"] = [
    "CURRENT_CERT_HASH",  // Current production certificate
    "BACKUP_CERT_HASH",   // Backup for rotation
    "FUTURE_CERT_HASH"    // Next certificate (optional)
]
```

### 2. Monitor Certificate Expiry

Set up automated monitoring:

```bash
# Cron job to check certificate expiry
0 0 * * * /usr/local/bin/check_cert_expiry.sh api.sahool.io 30
```

### 3. Test Before Production

Always test in staging:

```swift
// Staging configuration
certificatePins["api-staging.sahool.app"] = [
    "STAGING_CERT_HASH"
]

// Test rotation process in staging first
```

### 4. Document Everything

Maintain a certificate inventory:

| Domain | Current Hash | Expiry Date | Backup Hash | Status |
|--------|-------------|-------------|-------------|---------|
| api.sahool.io | ABC...123 | 2026-12-31 | DEF...456 | Active |
| api-staging.sahool.app | GHI...789 | 2026-06-30 | - | Active |

### 5. Plan Rotation Early

Start planning 90 days before expiry:
- Day 90: Get new certificate
- Day 60: Submit app update
- Day 30: Release update
- Day 7: Install new cert on server
- Day 0: Remove old cert

---

## Additional Resources

### Apple Documentation

- [App Transport Security](https://developer.apple.com/documentation/security/preventing_insecure_network_connections)
- [Certificate, Key, and Trust Services](https://developer.apple.com/documentation/security/certificate_key_and_trust_services)
- [URLSession Authentication](https://developer.apple.com/documentation/foundation/url_loading_system/handling_an_authentication_challenge)

### Tools

- [SSL Labs](https://www.ssllabs.com/ssltest/) - Test server SSL configuration
- [Certificate Transparency](https://crt.sh/) - Monitor certificate issuance
- [OpenSSL](https://www.openssl.org/) - Certificate management

### Internal Documentation

- `ios/Runner/CertificatePinning.swift` - Implementation details
- `lib/core/security/certificate_pinning_service.dart` - Android implementation
- `CERTIFICATE_PINNING_IMPLEMENTATION.md` - Overall architecture

---

## Support

For issues or questions:

1. Check troubleshooting section above
2. Review console logs for detailed error messages
3. Contact DevOps team for server-side issues
4. Contact mobile team for app-side issues

---

**Last Updated:** 2026-01-03
**Document Version:** 1.0
**Maintained By:** SAHOOL Mobile Team
