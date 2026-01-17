# SAHOOL Security Module

## نظام الأمان في تطبيق SAHOOL الميداني

This directory contains all security-related implementations for the SAHOOL Field App.

---

## 📁 File Structure

```
security/
├── README.md                           # This file - Overview of security module
├── CERTIFICATE_PINNING_GUIDE.md       # Complete guide for certificate pinning
├── security_config.dart                # Security configuration and levels
├── security_utils.dart                 # Security utility functions
├── certificate_pinning_service.dart    # Core certificate pinning implementation
├── certificate_config.dart             # Certificate pin configurations
├── certificate_tools.dart              # Development tools for certificates
├── certificate_monitor.dart            # Certificate monitoring widgets
└── certificate_pinning_example.dart    # Integration examples
```

---

## 🔒 Security Features

### 1. **Certificate Pinning** ✅ NEW

- SSL/TLS certificate validation
- SHA-256 fingerprint pinning
- Public key pinning support
- Multiple pins per domain (rotation)
- Pin expiry tracking
- Debug mode bypass
- Automatic validation

**Status**: Implemented
**Files**: `certificate_pinning_service.dart`, `certificate_config.dart`

### 2. **Security Configuration**

- Multiple security levels (Low, Medium, High, Maximum)
- Environment-based configuration
- Biometric authentication settings
- Session management
- Network security policies

**Status**: Implemented
**Files**: `security_config.dart`

### 3. **Security Utilities**

- Token validation
- Encryption helpers
- Secure storage integration
- Data sanitization

**Status**: Implemented
**Files**: `security_utils.dart`

---

## 🚀 Quick Start

### Enable Certificate Pinning

1. **Update `pubspec.yaml`** (Already done):

   ```yaml
   dependencies:
     dio_certificate_pinning: ^1.0.0
   ```

2. **Get actual certificate fingerprints**:

   ```dart
   // In debug mode
   import 'core/security/certificate_tools.dart';

   final info = await getCertificateInfo('https://api.sahool.app');
   printCertificateConfigCode(info);
   ```

3. **Update certificate configuration**:
   Edit `certificate_config.dart` and replace placeholder fingerprints.

4. **Enable in your app**:

   ```dart
   import 'core/security/security_config.dart';

   final apiClient = ApiClient(
     securityConfig: SecurityConfig(level: SecurityLevel.high),
   );
   ```

That's it! Certificate pinning is now active.

---

## 📚 Documentation

### Certificate Pinning

**Complete Guide**: See [CERTIFICATE_PINNING_GUIDE.md](CERTIFICATE_PINNING_GUIDE.md)

**Quick Reference**:

- **Extract certificates**: Use `certificate_tools.dart`
- **Configure pins**: Edit `certificate_config.dart`
- **Monitor status**: Use `CertificateMonitorWidget`
- **Integration examples**: See `certificate_pinning_example.dart`

### Security Levels

| Level       | Description       | Use Case       | Certificate Pinning      |
| ----------- | ----------------- | -------------- | ------------------------ |
| **Low**     | Minimal security  | Development    | ❌ Disabled              |
| **Medium**  | Standard security | Testing        | ❌ Disabled              |
| **High**    | Enhanced security | Production     | ✅ Enabled (with bypass) |
| **Maximum** | Maximum security  | Sensitive data | ✅ Strict mode           |

**Configure security level**:

```dart
final securityConfig = SecurityConfig(level: SecurityLevel.high);
```

**Available settings per level**:

- Token refresh intervals
- Session timeouts
- Biometric requirements
- Network policies
- Certificate pinning
- Data encryption
- And more...

See `security_config.dart` for all available options.

---

## 🛠️ Development Tools

### Extract Certificate Fingerprints

```dart
import 'core/security/certificate_tools.dart';

// Single certificate
final info = await getCertificateInfo('https://api.sahool.app');
print(info);

// Multiple certificates
final urls = ['https://api.sahool.app', 'https://api-staging.sahool.app'];
final results = await getCertificateInfoBatch(urls);
generateBulkConfiguration(results);
```

### Monitor Certificate Status (Debug)

```dart
import 'core/security/certificate_monitor.dart';

// In your debug screen
CertificateMonitorWidget(
  pinningService: apiClient.certificatePinningService,
)
```

### Validate Configuration

```dart
import 'core/security/certificate_config.dart';

final pins = CertificateConfig.getProductionPins();
final issues = CertificateRotationHelper.validatePinConfiguration(pins);

if (issues.isNotEmpty) {
  print('⚠️ Configuration issues:');
  for (final issue in issues) {
    print('  - $issue');
  }
}
```

---

## 🔄 Certificate Rotation

### Why Multiple Pins?

Having 2+ pins per domain allows smooth certificate rotation without downtime:

1. **Deploy new certificate** to server (both old and new valid)
2. **App validates** against either pin
3. **Release app update** with both pins
4. **Users update** gradually
5. **Remove old pin** after adoption
6. **Remove old certificate** from server

### Rotation Process

```dart
// Step 1: Add new pin (keep old one)
'api.sahool.app': [
  // Existing pin
  CertificatePin(
    type: PinType.sha256,
    value: 'old_fingerprint',
    expiryDate: DateTime(2026, 6, 30),
  ),
  // New pin for rotation
  CertificatePin(
    type: PinType.sha256,
    value: 'new_fingerprint',
    expiryDate: DateTime(2027, 6, 30),
  ),
],

// Step 2: Release app with both pins
// Step 3: Wait 2-4 weeks for adoption
// Step 4: Remove old pin from config
// Step 5: Remove old certificate from server
```

### Monitor Expiring Pins

```dart
final expiringPins = apiClient.getExpiringPins(daysThreshold: 30);
if (expiringPins.isNotEmpty) {
  print('⚠️ Certificates expiring soon:');
  for (final pin in expiringPins) {
    print('  ${pin.domain}: ${pin.daysUntilExpiry} days');
  }
}
```

---

## 📋 Checklist for Production

### Before Deployment

- [ ] Replace placeholder fingerprints with actual values
- [ ] Configure pins for all production domains
- [ ] Add backup pins for rotation
- [ ] Set appropriate expiry dates
- [ ] Validate configuration (no issues)
- [ ] Test in release mode
- [ ] Document certificate details
- [ ] Set up monitoring alerts

### Certificate Configuration

- [ ] Production API: `api.sahool.app`
- [ ] Production WebSocket: `ws.sahool.app`
- [ ] Staging API: `api-staging.sahool.app`
- [ ] Staging WebSocket: `ws-staging.sahool.app`
- [ ] Wildcard domains: `*.sahool.io`

### Validation

```dart
// Run this before deployment
final pins = CertificateConfig.getProductionPins();
final issues = CertificateRotationHelper.validatePinConfiguration(pins);
assert(issues.isEmpty, 'Fix configuration issues before deployment!');
```

---

## 🧪 Testing

### Test Certificate Pinning

```dart
import 'core/security/certificate_pinning_example.dart';

// Complete test suite
await testCertificatePinning(apiClient);
```

### Verify Against Expected Fingerprint

```dart
import 'core/security/certificate_tools.dart';

final matches = await verifyCertificateFingerprint(
  url: 'https://api.sahool.app',
  expectedFingerprint: 'your_fingerprint_here',
);
```

### Test Different Security Levels

```dart
// Test with different levels
final levels = [
  SecurityLevel.low,
  SecurityLevel.medium,
  SecurityLevel.high,
  SecurityLevel.maximum,
];

for (final level in levels) {
  final config = SecurityConfig(level: level);
  print('Level: ${level.nameAr}');
  print('  Pinning: ${config.enableCertificatePinning}');
  print('  Strict: ${config.strictCertificatePinning}');
}
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "Certificate validation failed"**

```
Cause: Fingerprint mismatch
Fix: Extract actual fingerprint and update config
```

**2. "No certificate pins configured"**

```
Cause: Domain not in configuration
Fix: Add domain to certificate_config.dart
```

**3. "All pins expired"**

```
Cause: Pins past expiry date
Fix: Update with current certificate fingerprints
```

**4. Works in debug, fails in release**

```
Cause: Debug bypass enabled, release enforces pinning
Fix: This is expected - update pins to match actual certificates
```

### Debug Mode

Enable detailed logging in debug mode:

```dart
// Certificate info will be printed to console
if (kDebugMode) {
  print('Certificate details...');
}
```

### Get Help

1. Check [CERTIFICATE_PINNING_GUIDE.md](CERTIFICATE_PINNING_GUIDE.md)
2. Review `certificate_pinning_example.dart`
3. Use debugging tools in `certificate_tools.dart`
4. Contact security team

---

## 📊 Monitoring

### Production Monitoring

Set up periodic checks for certificate health:

```dart
// Check daily
Timer.periodic(Duration(days: 1), (_) async {
  final expiringPins = apiClient.getExpiringPins(daysThreshold: 30);

  if (expiringPins.isNotEmpty) {
    // Send alert to monitoring system
    // Notify admins
    // Log to analytics
  }
});
```

### Metrics to Track

- Pins expiring soon (< 30 days)
- Configuration validation errors
- Certificate validation failures
- Pin rotation schedule adherence

---

## 🔐 Security Best Practices

1. **Always use HTTPS** in production
2. **Enable certificate pinning** for high security
3. **Maintain 2+ pins** per domain for rotation
4. **Set expiry dates** and monitor them
5. **Test thoroughly** before deployment
6. **Document changes** to certificates
7. **Use environment-specific** configurations
8. **Regular audits** of security settings
9. **Monitor expiring** certificates
10. **Have rotation plan** in place

---

## 📖 Additional Resources

- [OWASP Certificate Pinning](https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning)
- [Flutter Security Best Practices](https://docs.flutter.dev/security)
- [Dio Package Documentation](https://pub.dev/packages/dio)
- [OpenSSL Documentation](https://www.openssl.org/docs/)

---

## 🤝 Contributing

When adding new security features:

1. Update this README
2. Add comprehensive documentation
3. Include usage examples
4. Write tests
5. Update security_config.dart if needed
6. Document breaking changes

---

## 📝 Changelog

### Version 1.0.0 (2025-01-01)

- ✅ Added SSL certificate pinning
- ✅ SHA-256 fingerprint support
- ✅ Public key pinning support
- ✅ Certificate rotation helpers
- ✅ Monitoring and debugging tools
- ✅ Comprehensive documentation
- ✅ Integration examples

### Previous Versions

- Security configuration system
- Security levels implementation
- Biometric authentication
- Session management

---

## 📧 Contact

For security-related questions or issues:

- Security Team: [security@sahool.app]
- Documentation: See CERTIFICATE_PINNING_GUIDE.md
- Code Examples: See certificate_pinning_example.dart

---

**Last Updated**: 2025-01-01
**Version**: 1.0.0
**Status**: Production Ready
