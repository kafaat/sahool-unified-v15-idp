/// SAHOOL Security Module
/// وحدة الأمان لتطبيق سهول
///
/// This module provides comprehensive security features for the SAHOOL mobile app:
///
/// ## Features
///
/// ### SSL/TLS Certificate Pinning
/// - Multiple pinning strategies (SHA256, SPKI)
/// - Certificate rotation support
/// - Expiry monitoring
/// - See: [SslPinningManager], [SslPin]
///
/// ### Device Security
/// - Root/Jailbreak detection using safe_device
/// - Emulator/Simulator detection
/// - Mock location detection
/// - Developer mode detection
/// - See: [DeviceSecurityService], [DeviceSecurityState]
///
/// ### Session Management
/// - Idle timeout with configurable duration
/// - Biometric re-authentication after background
/// - Session persistence
/// - Expiry warnings
/// - See: [SessionManager], [SessionStateNotifier]
///
/// ### Secure Input
/// - Clipboard clearing after paste
/// - Secure password field with visibility toggle
/// - Secure PIN input
/// - OTP input with auto-clear
/// - See: [SecureTextField], [SecurePinField], [SecureOtpField]
///
/// ### Screenshot Prevention
/// - Using secure_application package
/// - Blur on background
/// - Configurable per-screen
/// - See: [ScreenshotPreventionWrapper]
///
/// ## Usage
///
/// ```dart
/// import 'package:sahool_mobile_core/core/security/security.dart';
///
/// // Get security config
/// final config = SecurityConfig.production;
///
/// // Check device security
/// final deviceSecurity = DeviceSecurityService();
/// final state = await deviceSecurity.performSecurityCheck();
/// if (state.isCompromised) {
///   // Handle rooted/jailbroken device
/// }
///
/// // Use secure text field
/// SecureTextField(
///   isPassword: true,
///   clearClipboardAfterPaste: true,
///   onChanged: (value) => print('Password: $value'),
/// )
///
/// // Wrap sensitive screen with screenshot prevention
/// ScreenshotPreventionWrapper(
///   enabled: true,
///   child: SensitiveScreen(),
/// )
/// ```
///
/// ## Configuration
///
/// Use [SecurityConfig] to configure security features:
/// - [SecurityConfig.production] - Full security for production
/// - [SecurityConfig.staging] - Balanced security for staging
/// - [SecurityConfig.development] - Minimal security for development
///
/// ## Arabic Support
///
/// All security messages support Arabic localization:
/// - Error messages
/// - Warning dialogs
/// - Status messages
///
library;

// Core configuration
export 'security_config.dart';

// SSL/TLS Certificate Pinning
export 'ssl_pinning.dart';
export 'certificate_config.dart';
export 'certificate_pinning_service.dart';

// Device Security (Root/Jailbreak Detection)
export 'device_security.dart';
export 'device_integrity_service.dart' hide SecurityThreatLevel;
export 'device_security_screen.dart';

// Session Management
export 'session_manager.dart';

// Secure Input
export 'secure_input.dart';

// Request Signing
export 'signing_key_service.dart';
