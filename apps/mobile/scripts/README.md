# Mobile App Scripts

This directory contains utility scripts for the mobile app.

## Available Scripts

### generate_cert_pins.sh

**Purpose:** Generate SSL certificate pins for both Android and iOS platforms.

**Usage:**

```bash
./generate_cert_pins.sh <domain> [port]
```

**Examples:**

```bash
# Generate pins for production API
./generate_cert_pins.sh api.sahool.app

# Generate pins with custom port
./generate_cert_pins.sh api.sahool.app 443

# Generate pins for staging
./generate_cert_pins.sh api-staging.sahool.app
```

**What it does:**

1. Fetches the SSL certificate from the specified domain
2. Generates SHA256 fingerprint for Android (full certificate hash)
3. Generates SPKI hash for iOS (public key hash)
4. Displays certificate information (subject, issuer, validity dates)
5. Provides ready-to-paste configuration snippets for:
   - Android `network_security_config.xml`
   - iOS `Info.plist`
   - Dart `certificate_config.dart`
6. Saves a summary file for reference

**Output:**

- Console output with formatted pins
- Summary file: `cert_pins_<domain>_<timestamp>.txt`

**Requirements:**

- OpenSSL must be installed
- Network access to the certificate server
- Valid SSL certificate on the server

**Platform-Specific Notes:**

- **Android**: Uses SHA256 of full certificate
- **iOS**: Uses SHA256 of SPKI (Subject Public Key Info - public key only)
- **Dart**: Uses SHA256 of full certificate (same as Android)

---

### generate_code.sh

**Purpose:** Generate code from Dart templates.

**Usage:**

```bash
./generate_code.sh
```

---

### generate_code.ps1

**Purpose:** Generate code from Dart templates (PowerShell version for Windows).

**Usage:**

```powershell
.\generate_code.ps1
```

---

### build_release.sh

**Purpose:** Build release versions of the mobile app.

**Usage:**

```bash
./build_release.sh
```

---

### generate_icons.py

**Purpose:** Generate app icons for different platforms.

**Usage:**

```bash
python generate_icons.py
```

---

## Certificate Pinning Workflow

To set up certificate pinning for production:

1. **Generate certificate pins for all domains:**

   ```bash
   ./generate_cert_pins.sh api.sahool.app
   ./generate_cert_pins.sh api.sahool.io
   ./generate_cert_pins.sh ws.sahool.app
   ./generate_cert_pins.sh api-staging.sahool.app
   ./generate_cert_pins.sh ws-staging.sahool.app
   ```

2. **Update configuration files:**
   - Android: `/apps/mobile/android/app/src/main/res/xml/network_security_config.xml`
   - iOS: `/apps/mobile/ios/Runner/Info.plist`
   - Dart: `/apps/mobile/lib/core/security/certificate_config.dart`

3. **Verify placeholders are replaced:**

   ```bash
   cd /apps/mobile
   grep -r "AAAA" ios/Runner/Info.plist android/app/src/main/res/xml/network_security_config.xml
   grep -r "PLACEHOLDER - MUST REPLACE" lib/core/security/
   ```

4. **Test in staging before production**

See `/apps/mobile/QUICK_START_CERTIFICATE_PINNING.md` for complete documentation.

---

## Contributing

When adding new scripts:

1. Make them executable: `chmod +x script_name.sh`
2. Add documentation to this README
3. Include usage examples
4. Test on multiple platforms if applicable
