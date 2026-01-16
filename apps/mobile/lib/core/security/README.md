# SAHOOL Mobile App Security Module

This directory contains security-related implementations for the SAHOOL mobile application.

## Contents

### Core Files

- **`certificate_pinning_service.dart`** - Main service that handles SSL certificate pinning and validation
- **`certificate_config.dart`** - Certificate pin configurations for different environments
- **`security_config.dart`** - Security configuration that controls when features are enabled

### Documentation

- **`CERTIFICATE_PINNING_GUIDE.md`** - Complete guide on certificate pinning setup and maintenance
- **`certificate_pinning_example.dart`** - Code examples showing how to use certificate pinning

## Quick Start

### For Development

Certificate pinning is automatically disabled in debug mode, so you can develop with local servers without any configuration.

### For Production

1. **Get your certificate fingerprints**:

   ```bash
   openssl s_client -connect api.sahool.app:443 < /dev/null 2>/dev/null | \
     openssl x509 -fingerprint -sha256 -noout -in /dev/stdin
   ```

2. **Update `certificate_config.dart`** with actual fingerprints (replace placeholders)

3. **Build for production**:
   ```bash
   flutter build apk --release
   ```

Certificate pinning will be automatically enabled for release builds.

## How It Works

The security system automatically configures itself based on the build mode:

- **Debug builds** (`flutter run`): Certificate pinning disabled
- **Release builds** (`flutter build apk --release`): Certificate pinning enabled and enforced

This is handled by `SecurityConfig.fromBuildMode()` which returns:

- `SecurityConfig.development` in debug mode (pinning OFF)
- `SecurityConfig.production` in release mode (pinning ON, strict)

## Integration

The certificate pinning is integrated into the `ApiClient` class in `/lib/core/http/api_client.dart`.

When you create an `ApiClient` instance, it automatically:

1. Detects the build mode (debug/release)
2. Loads the appropriate security configuration
3. Configures certificate pinning if needed
4. Logs the security status

Example initialization:

```dart
// In your providers or main app setup
final apiClient = ApiClient(); // Automatically configured!
```

## Security Features

Current features:

- ✅ SSL Certificate Pinning (SHA-256 fingerprints)
- ✅ Multiple pin support (for certificate rotation)
- ✅ Pin expiry tracking
- ✅ Environment-based configuration
- ✅ Automatic debug mode bypass
- ✅ Wildcard domain support

## Before Deploying to Production

**CRITICAL CHECKLIST**:

- [ ] Replace ALL placeholder fingerprints in `certificate_config.dart`
- [ ] Verify fingerprints match your actual server certificates
- [ ] Add at least 2 pins per domain (primary + backup)
- [ ] Set correct expiry dates
- [ ] Test in staging environment first
- [ ] Review `CERTIFICATE_PINNING_GUIDE.md` for detailed instructions

## Files Overview

```
lib/core/security/
├── README.md                          # This file
├── CERTIFICATE_PINNING_GUIDE.md       # Detailed setup guide
├── certificate_pinning_service.dart    # Core pinning service
├── certificate_config.dart             # Pin configurations
├── certificate_pinning_example.dart    # Usage examples
└── security_config.dart                # Security settings
```

## Support

For questions or issues:

1. Read the `CERTIFICATE_PINNING_GUIDE.md` for detailed documentation
2. Check the examples in `certificate_pinning_example.dart`
3. Review the troubleshooting section in the guide
4. Contact the development team

## Security Notice

⚠️ **IMPORTANT**: Never commit real production certificate fingerprints to public repositories!

For production deployments:

- Use environment variables or CI/CD secrets
- Keep certificate configurations private
- Rotate certificates regularly
- Monitor for expiring pins

## Related Files

- `/lib/core/http/api_client.dart` - API client with integrated certificate pinning
- `/lib/core/config/env_config.dart` - Environment configuration
- `/pubspec.yaml` - Includes `crypto` dependency for SHA-256 hashing
