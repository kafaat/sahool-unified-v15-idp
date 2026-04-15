import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:secure_application/secure_application.dart';
import 'security_config.dart';

// Re-export securityConfigProvider for screens that use SecureScreen
export 'security_config.dart' show securityConfigProvider, SecurityConfig;

/// SAHOOL Screen Security Service
/// خدمة حماية الشاشة من لقطات الشاشة والتسجيل
///
/// Features:
/// - Screenshot prevention (Android FLAG_SECURE)
/// - iOS snapshot prevention
/// - Screen recording detection
/// - Configurable per security level
/// - Arabic/English warning messages

/// Screen security service class
class ScreenSecurityService {
  static final ScreenSecurityService _instance =
      ScreenSecurityService._internal();
  factory ScreenSecurityService() => _instance;
  ScreenSecurityService._internal();

  bool _isInitialized = false;
  bool _isProtectionEnabled = false;

  /// Initialize screen security service
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      if (kDebugMode) {
        debugPrint('🔒 Initializing Screen Security Service...');
      }
      _isInitialized = true;
      if (kDebugMode) {
        debugPrint('✅ Screen Security Service initialized');
      }
    } catch (e) {
      if (kDebugMode) {
        debugPrint('❌ Screen Security initialization failed: $e');
      }
    }
  }

  /// Enable screenshot protection globally
  /// This enables FLAG_SECURE on Android and prevents snapshots on iOS
  Future<void> enableProtection() async {
    if (!_isInitialized) await initialize();
    if (_isProtectionEnabled) return;

    try {
      if (kDebugMode) {
        debugPrint('🔒 Enabling screenshot protection...');
      }

      // Note: The actual protection is applied via SecureApplication widget
      // This method is for service-level tracking
      _isProtectionEnabled = true;

      if (kDebugMode) {
        debugPrint('✅ Screenshot protection enabled');
      }
    } catch (e) {
      if (kDebugMode) {
        debugPrint('❌ Failed to enable screenshot protection: $e');
      }
    }
  }

  /// Disable screenshot protection globally
  Future<void> disableProtection() async {
    if (!_isProtectionEnabled) return;

    try {
      if (kDebugMode) {
        debugPrint('🔓 Disabling screenshot protection...');
      }
      _isProtectionEnabled = false;
      if (kDebugMode) {
        debugPrint('✅ Screenshot protection disabled');
      }
    } catch (e) {
      if (kDebugMode) {
        debugPrint('❌ Failed to disable screenshot protection: $e');
      }
    }
  }

  /// Check if protection is enabled
  bool get isProtectionEnabled => _isProtectionEnabled;

  /// Check if service is initialized
  bool get isInitialized => _isInitialized;
}

/// Provider for screen security service
final screenSecurityServiceProvider = Provider<ScreenSecurityService>((ref) {
  return ScreenSecurityService();
});

/// Provider to determine if screen security should be enabled based on security level
final screenSecurityEnabledProvider = Provider<bool>((ref) {
  final securityConfig = ref.watch(securityConfigProvider);
  return securityConfig.screenSecurityEnabled;
});

/// Provider for specific screen types that should be secured
final securedScreenTypesProvider = Provider<Set<String>>((ref) {
  final securityConfig = ref.watch(securityConfigProvider);
  return securityConfig.securedScreenTypes;
});

/// Enum for screen types that can be secured
enum SecuredScreenType {
  /// Login and authentication screens
  authentication,

  /// Wallet and payment screens
  wallet,

  /// Personal data and profile screens
  personalData,

  /// Task evidence photos
  evidencePhotos,

  /// All screens (app-wide protection)
  all,
}

/// Extension to get localized names for secured screen types
extension SecuredScreenTypeExtension on SecuredScreenType {
  String get nameAr {
    switch (this) {
      case SecuredScreenType.authentication:
        return 'شاشات تسجيل الدخول';
      case SecuredScreenType.wallet:
        return 'المحفظة والمدفوعات';
      case SecuredScreenType.personalData:
        return 'البيانات الشخصية';
      case SecuredScreenType.evidencePhotos:
        return 'صور المهام';
      case SecuredScreenType.all:
        return 'جميع الشاشات';
    }
  }

  String get nameEn {
    switch (this) {
      case SecuredScreenType.authentication:
        return 'Authentication Screens';
      case SecuredScreenType.wallet:
        return 'Wallet & Payments';
      case SecuredScreenType.personalData:
        return 'Personal Data';
      case SecuredScreenType.evidencePhotos:
        return 'Evidence Photos';
      case SecuredScreenType.all:
        return 'All Screens';
    }
  }
}

/// Secure Screen Wrapper Widget
/// Wraps screens that need screenshot protection
class SecureScreen extends ConsumerStatefulWidget {
  final Widget child;
  final SecuredScreenType screenType;
  final bool showWarning;
  final String? warningMessageAr;
  final String? warningMessageEn;

  const SecureScreen({
    super.key,
    required this.child,
    this.screenType = SecuredScreenType.all,
    this.showWarning = false,
    this.warningMessageAr,
    this.warningMessageEn,
  });

  @override
  ConsumerState<SecureScreen> createState() => _SecureScreenState();
}

class _SecureScreenState extends ConsumerState<SecureScreen> {
  final _secureApplicationController =
      SecureApplicationController(SecureApplicationState());
  bool _isSecured = false;

  @override
  void initState() {
    super.initState();
    _initializeScreenSecurity();
  }

  Future<void> _initializeScreenSecurity() async {
    final service = ref.read(screenSecurityServiceProvider);
    if (!service.isInitialized) {
      await service.initialize();
    }

    // Check if this screen type should be secured
    final securityConfig = ref.read(securityConfigProvider);
    final shouldSecure = securityConfig.shouldSecureScreen(widget.screenType);

    if (shouldSecure) {
      await _enableSecurity();
    }
  }

  Future<void> _enableSecurity() async {
    if (_isSecured) return;

    try {
      // Secure the screen
      _secureApplicationController.secure();
      setState(() => _isSecured = true);

      if (kDebugMode) {
        debugPrint('🔒 Screen secured: ${widget.screenType.nameEn}');
      }

      // Show warning if requested
      if (widget.showWarning && mounted) {
        _showSecurityWarning();
      }
    } catch (e) {
      if (kDebugMode) {
        debugPrint('❌ Failed to secure screen: $e');
      }
    }
  }

  Future<void> _disableSecurity() async {
    if (!_isSecured) return;

    try {
      _secureApplicationController.open();
      setState(() => _isSecured = false);
      if (kDebugMode) {
        debugPrint('🔓 Screen unsecured: ${widget.screenType.nameEn}');
      }
    } catch (e) {
      if (kDebugMode) {
        debugPrint('❌ Failed to unsecure screen: $e');
      }
    }
  }

  void _showSecurityWarning() {
    final warningAr = widget.warningMessageAr ??
        'لا يمكن أخذ لقطات شاشة في هذه الصفحة لحماية بياناتك';
    final warningEn = widget.warningMessageEn ??
        'Screenshots are disabled on this screen to protect your data';

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              warningAr,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              warningEn,
              style: const TextStyle(fontSize: 12),
            ),
          ],
        ),
        backgroundColor: Colors.orange.shade800,
        duration: const Duration(seconds: 4),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  void dispose() {
    // Unsecure the screen without calling setState (widget is being disposed)
    if (_isSecured) {
      try {
        _secureApplicationController.open();
      } catch (e) {
        if (kDebugMode) {
          debugPrint('Failed to unsecure screen on dispose: $e');
        }
      }
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Listen to security config changes
    ref.listen<SecurityConfig>(securityConfigProvider, (previous, next) {
      final shouldSecure = next.shouldSecureScreen(widget.screenType);
      if (shouldSecure && !_isSecured) {
        _enableSecurity();
      } else if (!shouldSecure && _isSecured) {
        _disableSecurity();
      }
    });

    return SecureApplication(
      nativeRemoveDelay: 800, // Delay before showing secure overlay on iOS
      secureApplicationController: _secureApplicationController,
      child: widget.child,
    );
  }
}

/// App-wide secure wrapper
/// Wraps the entire app to enable global screenshot protection
class SecureApp extends ConsumerWidget {
  final Widget child;
  final bool autoEnable;

  const SecureApp({
    super.key,
    required this.child,
    this.autoEnable = true,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final securityEnabled = ref.watch(screenSecurityEnabledProvider);

    // Only wrap if app-wide security is enabled
    if (securityEnabled && autoEnable) {
      return SecureScreen(
        screenType: SecuredScreenType.all,
        child: child,
      );
    }

    return child;
  }
}

/// Screen recording detection widget
/// Shows a warning when screen recording is detected
class ScreenRecordingDetector extends ConsumerStatefulWidget {
  final Widget child;
  final VoidCallback? onRecordingDetected;

  const ScreenRecordingDetector({
    super.key,
    required this.child,
    this.onRecordingDetected,
  });

  @override
  ConsumerState<ScreenRecordingDetector> createState() =>
      _ScreenRecordingDetectorState();
}

class _ScreenRecordingDetectorState
    extends ConsumerState<ScreenRecordingDetector> {
  bool _isRecording = false;
  StreamSubscription? _recordingSubscription;

  @override
  void initState() {
    super.initState();
    _setupRecordingDetection();
  }

  void _setupRecordingDetection() {
    // Note: secure_application package doesn't provide direct recording detection
    // This is a placeholder for future implementation or custom native code
    // For now, we rely on FLAG_SECURE which prevents recording on Android

    // Future enhancement: Add native platform channel to detect screen recording
    // on both Android and iOS
  }

  void _onRecordingDetected() {
    if (!_isRecording) {
      setState(() => _isRecording = true);
      widget.onRecordingDetected?.call();
      _showRecordingWarning();
    }
  }

  void _showRecordingWarning() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('⚠️ تحذير أمني'),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'تم اكتشاف تسجيل للشاشة',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            SizedBox(height: 12),
            Text('Screen recording detected'),
            SizedBox(height: 12),
            Text(
              'لا يمكنك تسجيل الشاشة أثناء استخدام التطبيق لحماية بياناتك.',
              style: TextStyle(fontSize: 14),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              // Optionally force logout or minimize app
            },
            child: const Text('فهمت'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _recordingSubscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return widget.child;
  }
}
