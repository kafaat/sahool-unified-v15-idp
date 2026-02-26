import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:safe_device/safe_device.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:secure_application/secure_application.dart';
import '../utils/app_logger.dart';
import 'security_config.dart';

/// Device Security Service Provider
/// مزود خدمة أمان الجهاز
final deviceSecurityProvider = Provider<DeviceSecurityService>((ref) {
  return DeviceSecurityService();
});

/// Device Security Controller Provider (for state management)
final deviceSecurityControllerProvider = StateNotifierProvider<DeviceSecurityController, DeviceSecurityState>((ref) {
  final service = ref.watch(deviceSecurityProvider);
  return DeviceSecurityController(service);
});

/// Device Security State
class DeviceSecurityState {
  final bool isInitialized;
  final bool isSecure;
  final bool isRooted;
  final bool isJailbroken;
  final bool isEmulator;
  final bool isRealDevice;
  final bool hasMockLocation;
  final bool isOnExternalStorage;
  final bool isDevelopmentModeEnabled;
  final List<String> threats;
  final SecurityThreatLevel threatLevel;
  final DateTime? lastCheckTime;
  final Map<String, dynamic> deviceInfo;
  final String? errorMessage;

  const DeviceSecurityState({
    this.isInitialized = false,
    this.isSecure = true,
    this.isRooted = false,
    this.isJailbroken = false,
    this.isEmulator = false,
    this.isRealDevice = true,
    this.hasMockLocation = false,
    this.isOnExternalStorage = false,
    this.isDevelopmentModeEnabled = false,
    this.threats = const [],
    this.threatLevel = SecurityThreatLevel.none,
    this.lastCheckTime,
    this.deviceInfo = const {},
    this.errorMessage,
  });

  DeviceSecurityState copyWith({
    bool? isInitialized,
    bool? isSecure,
    bool? isRooted,
    bool? isJailbroken,
    bool? isEmulator,
    bool? isRealDevice,
    bool? hasMockLocation,
    bool? isOnExternalStorage,
    bool? isDevelopmentModeEnabled,
    List<String>? threats,
    SecurityThreatLevel? threatLevel,
    DateTime? lastCheckTime,
    Map<String, dynamic>? deviceInfo,
    String? errorMessage,
  }) {
    return DeviceSecurityState(
      isInitialized: isInitialized ?? this.isInitialized,
      isSecure: isSecure ?? this.isSecure,
      isRooted: isRooted ?? this.isRooted,
      isJailbroken: isJailbroken ?? this.isJailbroken,
      isEmulator: isEmulator ?? this.isEmulator,
      isRealDevice: isRealDevice ?? this.isRealDevice,
      hasMockLocation: hasMockLocation ?? this.hasMockLocation,
      isOnExternalStorage: isOnExternalStorage ?? this.isOnExternalStorage,
      isDevelopmentModeEnabled: isDevelopmentModeEnabled ?? this.isDevelopmentModeEnabled,
      threats: threats ?? this.threats,
      threatLevel: threatLevel ?? this.threatLevel,
      lastCheckTime: lastCheckTime ?? this.lastCheckTime,
      deviceInfo: deviceInfo ?? this.deviceInfo,
      errorMessage: errorMessage,
    );
  }

  /// Check if device is compromised (rooted/jailbroken)
  bool get isCompromised => isRooted || isJailbroken;

  /// Check if any threats were detected
  bool get hasThreats => threats.isNotEmpty;

  /// Get human-readable status
  String get statusMessage {
    if (!isInitialized) return 'Security check not performed';
    if (isSecure) return 'Device is secure';
    return 'Security issues detected: ${threats.join(", ")}';
  }

  /// Get Arabic status message
  String get statusMessageAr {
    if (!isInitialized) return 'لم يتم إجراء فحص الأمان';
    if (isSecure) return 'الجهاز آمن';
    return 'تم اكتشاف مشاكل أمنية: ${threats.join("، ")}';
  }
}

/// Security Threat Level
enum SecurityThreatLevel {
  none,       // No threats detected | لا توجد تهديدات
  low,        // Minor concerns (debug mode, emulator) | مخاوف بسيطة
  medium,     // Moderate threats (developer options) | تهديدات متوسطة
  high,       // Serious threats (root/jailbreak) | تهديدات خطيرة
  critical,   // Multiple serious threats | تهديدات حرجة متعددة
}

/// Device Security Controller
class DeviceSecurityController extends StateNotifier<DeviceSecurityState> {
  final DeviceSecurityService _service;

  DeviceSecurityController(this._service) : super(const DeviceSecurityState());

  /// Perform security check
  Future<void> checkSecurity({bool force = false}) async {
    // Skip if already checked recently (within 5 minutes) unless forced
    if (!force && state.isInitialized && state.lastCheckTime != null) {
      final elapsed = DateTime.now().difference(state.lastCheckTime!);
      if (elapsed.inMinutes < 5) return;
    }

    try {
      final result = await _service.performSecurityCheck();
      state = result;
    } catch (e) {
      state = state.copyWith(
        isInitialized: true,
        errorMessage: e.toString(),
      );
    }
  }

  /// Clear security state (for testing)
  void clearState() {
    state = const DeviceSecurityState();
  }
}

/// Device Security Service
/// خدمة أمان الجهاز
///
/// Provides comprehensive device security checks including:
/// - Root/Jailbreak detection using safe_device
/// - Emulator/Simulator detection
/// - Mock location detection
/// - Developer mode detection
/// - External storage detection
///
/// يوفر فحوصات أمنية شاملة للجهاز تشمل:
/// - كشف الروت/الجلبريك
/// - كشف المحاكيات
/// - كشف المواقع الوهمية
/// - كشف وضع المطور
/// - كشف التخزين الخارجي
class DeviceSecurityService {
  static final DeviceSecurityService _instance = DeviceSecurityService._internal();
  factory DeviceSecurityService() => _instance;
  DeviceSecurityService._internal();

  final DeviceInfoPlugin _deviceInfo = DeviceInfoPlugin();

  /// Perform comprehensive security check
  Future<DeviceSecurityState> performSecurityCheck() async {
    AppLogger.d('Starting device security check...', tag: 'DeviceSecurity');

    final threats = <String>[];
    Map<String, dynamic> deviceInfo = {};

    bool isJailbroken = false;
    bool isRooted = false;
    bool isEmulator = false;
    bool isRealDevice = true;
    bool hasMockLocation = false;
    bool isOnExternalStorage = false;
    bool isDevelopmentModeEnabled = false;

    try {
      // Platform-specific checks
      if (Platform.isAndroid) {
        deviceInfo = await _getAndroidInfo();

        // Check root status with timeout
        isRooted = await _checkWithTimeout(
          SafeDevice.isJailBroken,
          'Root check',
          defaultValue: false,
        );
        if (isRooted) {
          threats.add('Device is rooted');
          AppLogger.w('Root detected', tag: 'DeviceSecurity');
        }

        // Check emulator
        isEmulator = await _checkWithTimeout(
          SafeDevice.isRealDevice.then((v) => !v),
          'Emulator check',
          defaultValue: false,
        );
        isRealDevice = !isEmulator;
        if (isEmulator) {
          threats.add('Running on emulator');
          AppLogger.w('Emulator detected', tag: 'DeviceSecurity');
        }

        // Check mock location
        hasMockLocation = await _checkWithTimeout(
          SafeDevice.isMockLocation,
          'Mock location check',
          defaultValue: false,
        );
        if (hasMockLocation) {
          threats.add('Mock location detected');
          AppLogger.w('Mock location detected', tag: 'DeviceSecurity');
        }

        // Check external storage
        isOnExternalStorage = await _checkWithTimeout(
          SafeDevice.isOnExternalStorage,
          'External storage check',
          defaultValue: false,
        );
        if (isOnExternalStorage) {
          threats.add('App on external storage');
          AppLogger.w('External storage detected', tag: 'DeviceSecurity');
        }

        // Check developer mode
        isDevelopmentModeEnabled = await _checkWithTimeout(
          SafeDevice.isDevelopmentModeEnable,
          'Developer mode check',
          defaultValue: false,
        );
        if (isDevelopmentModeEnabled) {
          threats.add('Developer mode enabled');
          AppLogger.w('Developer mode detected', tag: 'DeviceSecurity');
        }

      } else if (Platform.isIOS) {
        deviceInfo = await _getIosInfo();

        // Check jailbreak
        isJailbroken = await _checkWithTimeout(
          SafeDevice.isJailBroken,
          'Jailbreak check',
          defaultValue: false,
        );
        if (isJailbroken) {
          threats.add('Device is jailbroken');
          AppLogger.w('Jailbreak detected', tag: 'DeviceSecurity');
        }

        // Check simulator
        isEmulator = await _checkWithTimeout(
          SafeDevice.isRealDevice.then((v) => !v),
          'Simulator check',
          defaultValue: false,
        );
        isRealDevice = !isEmulator;
        if (isEmulator) {
          threats.add('Running on simulator');
          AppLogger.w('Simulator detected', tag: 'DeviceSecurity');
        }
      }

      // Add debug mode check
      if (kDebugMode) {
        threats.add('Debug mode active');
      }

      // Calculate threat level
      final threatLevel = _calculateThreatLevel(
        isRooted: isRooted,
        isJailbroken: isJailbroken,
        isEmulator: isEmulator,
        hasMockLocation: hasMockLocation,
        isDevelopmentModeEnabled: isDevelopmentModeEnabled,
        isOnExternalStorage: isOnExternalStorage,
      );

      final isSecure = threats.isEmpty || (threats.length == 1 && kDebugMode);

      AppLogger.i('Security check complete', tag: 'DeviceSecurity', data: {
        'isSecure': isSecure,
        'threatLevel': threatLevel.name,
        'threatCount': threats.length,
      });

      return DeviceSecurityState(
        isInitialized: true,
        isSecure: isSecure,
        isRooted: isRooted,
        isJailbroken: isJailbroken,
        isEmulator: isEmulator,
        isRealDevice: isRealDevice,
        hasMockLocation: hasMockLocation,
        isOnExternalStorage: isOnExternalStorage,
        isDevelopmentModeEnabled: isDevelopmentModeEnabled,
        threats: threats,
        threatLevel: threatLevel,
        lastCheckTime: DateTime.now(),
        deviceInfo: deviceInfo,
      );

    } catch (e, stackTrace) {
      AppLogger.e('Security check failed', tag: 'DeviceSecurity', error: e, stackTrace: stackTrace);

      // Return insecure state on error - fail closed, not open
      return DeviceSecurityState(
        isInitialized: true,
        isSecure: false,
        threats: ['Security check failed: unable to verify device integrity'],
        threatLevel: ThreatLevel.medium,
        lastCheckTime: DateTime.now(),
        errorMessage: e.toString(),
        deviceInfo: deviceInfo,
      );
    }
  }

  /// Get Android device information
  Future<Map<String, dynamic>> _getAndroidInfo() async {
    try {
      final info = await _deviceInfo.androidInfo;
      return {
        'platform': 'Android',
        'manufacturer': info.manufacturer,
        'model': info.model,
        'device': info.device,
        'version': info.version.release,
        'sdkInt': info.version.sdkInt,
        'brand': info.brand,
        'isPhysicalDevice': info.isPhysicalDevice,
        'fingerprint': info.fingerprint,
      };
    } catch (e) {
      return {'platform': 'Android', 'error': e.toString()};
    }
  }

  /// Get iOS device information
  Future<Map<String, dynamic>> _getIosInfo() async {
    try {
      final info = await _deviceInfo.iosInfo;
      return {
        'platform': 'iOS',
        'model': info.model,
        'name': info.name,
        'systemName': info.systemName,
        'systemVersion': info.systemVersion,
        'isPhysicalDevice': info.isPhysicalDevice,
        'utsname': {
          'sysname': info.utsname.sysname,
          'nodename': info.utsname.nodename,
          'release': info.utsname.release,
          'version': info.utsname.version,
          'machine': info.utsname.machine,
        },
      };
    } catch (e) {
      return {'platform': 'iOS', 'error': e.toString()};
    }
  }

  /// Execute check with timeout to prevent hanging
  Future<bool> _checkWithTimeout(
    Future<bool> check,
    String checkName, {
    bool defaultValue = false,
    Duration timeout = const Duration(seconds: 5),
  }) async {
    try {
      return await check.timeout(
        timeout,
        onTimeout: () {
          AppLogger.w('$checkName timed out', tag: 'DeviceSecurity');
          return defaultValue;
        },
      );
    } catch (e) {
      AppLogger.w('$checkName failed: $e', tag: 'DeviceSecurity');
      return defaultValue;
    }
  }

  /// Calculate threat level based on detected issues
  SecurityThreatLevel _calculateThreatLevel({
    required bool isRooted,
    required bool isJailbroken,
    required bool isEmulator,
    required bool hasMockLocation,
    required bool isDevelopmentModeEnabled,
    required bool isOnExternalStorage,
  }) {
    int score = 0;

    // High severity (10 points each)
    if (isRooted) score += 10;
    if (isJailbroken) score += 10;

    // Medium severity (5 points each)
    if (hasMockLocation) score += 5;
    if (isDevelopmentModeEnabled && !kDebugMode) score += 5;

    // Low severity (2 points each)
    if (isEmulator) score += 2;
    if (isOnExternalStorage) score += 2;

    if (score >= 15) return SecurityThreatLevel.critical;
    if (score >= 10) return SecurityThreatLevel.high;
    if (score >= 5) return SecurityThreatLevel.medium;
    if (score > 0) return SecurityThreatLevel.low;
    return SecurityThreatLevel.none;
  }

  /// Check if app should be blocked based on security policy
  bool shouldBlockApp(DeviceSecurityState state, DeviceSecurityConfig config) {
    // Always allow in debug mode unless enforced
    if (kDebugMode && !config.enforceInDebug) {
      return false;
    }

    switch (config.policy) {
      case DeviceSecurityPolicy.disabled:
        return false;

      case DeviceSecurityPolicy.logOnly:
        return false;

      case DeviceSecurityPolicy.warnOnly:
        return false;

      case DeviceSecurityPolicy.blockRooted:
        return state.isCompromised;

      case DeviceSecurityPolicy.blockAll:
        return state.hasThreats && !state.threats.every((t) => t == 'Debug mode active');
    }
  }

  /// Get user-friendly threat message
  String getThreatMessage(SecurityThreatLevel level, {bool arabic = false}) {
    switch (level) {
      case SecurityThreatLevel.critical:
        return arabic
            ? 'تهديد أمني حرج - لا يمكن استخدام التطبيق'
            : 'Critical security threat - Cannot use app';
      case SecurityThreatLevel.high:
        return arabic
            ? 'تهديد أمني عالي - الجهاز غير آمن'
            : 'High security threat - Device is not secure';
      case SecurityThreatLevel.medium:
        return arabic
            ? 'تهديد أمني متوسط - يُنصح بالحذر'
            : 'Medium security threat - Proceed with caution';
      case SecurityThreatLevel.low:
        return arabic
            ? 'تحذير أمني بسيط'
            : 'Minor security warning';
      case SecurityThreatLevel.none:
        return arabic
            ? 'الجهاز آمن'
            : 'Device is secure';
    }
  }
}

/// Device Security Configuration
class DeviceSecurityConfig {
  final DeviceSecurityPolicy policy;
  final bool enforceInDebug;
  final bool allowEmulators;
  final bool logEvents;
  final Duration checkInterval;

  const DeviceSecurityConfig({
    this.policy = DeviceSecurityPolicy.warnOnly,
    this.enforceInDebug = false,
    this.allowEmulators = true,
    this.logEvents = true,
    this.checkInterval = const Duration(minutes: 5),
  });

  /// Production configuration - block rooted devices
  static const production = DeviceSecurityConfig(
    policy: DeviceSecurityPolicy.blockRooted,
    enforceInDebug: false,
    allowEmulators: false,
    logEvents: true,
    checkInterval: Duration(minutes: 5),
  );

  /// Staging configuration - warn but don't block
  static const staging = DeviceSecurityConfig(
    policy: DeviceSecurityPolicy.warnOnly,
    enforceInDebug: false,
    allowEmulators: true,
    logEvents: true,
    checkInterval: Duration(minutes: 5),
  );

  /// Development configuration - log only
  static const development = DeviceSecurityConfig(
    policy: DeviceSecurityPolicy.disabled,
    enforceInDebug: false,
    allowEmulators: true,
    logEvents: false,
    checkInterval: Duration(minutes: 30),
  );

  /// Get configuration for environment
  factory DeviceSecurityConfig.forEnvironment(String environment) {
    switch (environment.toLowerCase()) {
      case 'production':
      case 'prod':
        return DeviceSecurityConfig.production;
      case 'staging':
      case 'stage':
        return DeviceSecurityConfig.staging;
      default:
        return DeviceSecurityConfig.development;
    }
  }
}

/// Device Security Policy
enum DeviceSecurityPolicy {
  /// No security checks
  disabled,

  /// Log issues but take no action
  logOnly,

  /// Show warning but allow usage
  warnOnly,

  /// Block rooted/jailbroken devices
  blockRooted,

  /// Block all detected threats
  blockAll,
}

/// Screenshot Prevention Wrapper Widget
/// يستخدم secure_application لمنع لقطات الشاشة
///
/// Usage:
/// ```dart
/// ScreenshotPreventionWrapper(
///   enabled: true,
///   child: SensitiveScreen(),
/// )
/// ```
class ScreenshotPreventionWrapper extends StatefulWidget {
  final Widget child;
  final bool enabled;
  final bool blurOnBackground;
  final double blurSigma;
  final VoidCallback? onScreenshotAttempt;

  const ScreenshotPreventionWrapper({
    super.key,
    required this.child,
    this.enabled = true,
    this.blurOnBackground = true,
    this.blurSigma = 20.0,
    this.onScreenshotAttempt,
  });

  @override
  State<ScreenshotPreventionWrapper> createState() => _ScreenshotPreventionWrapperState();
}

class _ScreenshotPreventionWrapperState extends State<ScreenshotPreventionWrapper> {
  final SecureApplicationController _controller = SecureApplicationController(
    SecureApplicationState(
      secured: true,
      locked: false,
    ),
  );

  @override
  void initState() {
    super.initState();
    if (widget.enabled) {
      _enableScreenshotPrevention();
    }
  }

  @override
  void didUpdateWidget(ScreenshotPreventionWrapper oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.enabled != oldWidget.enabled) {
      if (widget.enabled) {
        _enableScreenshotPrevention();
      } else {
        _disableScreenshotPrevention();
      }
    }
  }

  void _enableScreenshotPrevention() {
    _controller.secure();
    AppLogger.d('Screenshot prevention enabled', tag: 'DeviceSecurity');
  }

  void _disableScreenshotPrevention() {
    _controller.open();
    AppLogger.d('Screenshot prevention disabled', tag: 'DeviceSecurity');
  }

  @override
  void dispose() {
    _disableScreenshotPrevention();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.enabled) {
      return widget.child;
    }

    return SecureApplication(
      nativeRemoveDelay: 800,
      onNeedUnlock: (controller) async {
        // Called when app comes back from background
        AppLogger.d('App returned from background', tag: 'DeviceSecurity');
        return SecureApplicationAuthenticationStatus.SUCCESS;
      },
      child: Builder(
        builder: (context) {
          // Access the controller from context
          SecureApplicationProvider.of(context)?.secure();

          return SecureGate(
            blurr: widget.blurSigma,
            opacity: 0.6,
            lockedBuilder: (context, controller) {
              // This is shown when app is in background
              return Container(
                color: const Color(0xFF2E7D32), // SAHOOL green
                child: const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.shield,
                        size: 80,
                        color: Colors.white,
                      ),
                      SizedBox(height: 24),
                      Text(
                        'SAHOOL',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          fontFamily: 'IBMPlexSansArabic',
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(
                        'Protected Content',
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.white70,
                          fontFamily: 'IBMPlexSansArabic',
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
            child: widget.child,
          );
        },
      ),
    );
  }
}

/// Security Shield Widget - Shows security status
class SecurityShieldWidget extends StatelessWidget {
  final SecurityThreatLevel threatLevel;
  final VoidCallback? onTap;
  final double size;

  const SecurityShieldWidget({
    super.key,
    required this.threatLevel,
    this.onTap,
    this.size = 48,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          color: _getBackgroundColor(),
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: _getBackgroundColor().withOpacity(0.3),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Icon(
          _getIcon(),
          color: Colors.white,
          size: size * 0.5,
        ),
      ),
    );
  }

  Color _getBackgroundColor() {
    switch (threatLevel) {
      case SecurityThreatLevel.none:
        return const Color(0xFF4CAF50); // Green
      case SecurityThreatLevel.low:
        return const Color(0xFFFFC107); // Amber
      case SecurityThreatLevel.medium:
        return const Color(0xFFFF9800); // Orange
      case SecurityThreatLevel.high:
        return const Color(0xFFF44336); // Red
      case SecurityThreatLevel.critical:
        return const Color(0xFF9C27B0); // Purple
    }
  }

  IconData _getIcon() {
    switch (threatLevel) {
      case SecurityThreatLevel.none:
        return Icons.verified_user;
      case SecurityThreatLevel.low:
      case SecurityThreatLevel.medium:
        return Icons.shield;
      case SecurityThreatLevel.high:
      case SecurityThreatLevel.critical:
        return Icons.gpp_bad;
    }
  }
}
