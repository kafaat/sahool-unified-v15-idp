import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../auth/biometric_service.dart';
import '../auth/secure_storage_service.dart';
import '../utils/app_logger.dart';

/// Session Manager Provider
final sessionManagerProvider = Provider<SessionManager>((ref) {
  final secureStorage = ref.watch(secureStorageProvider);
  final biometricService = ref.watch(biometricServiceProvider);
  return SessionManager(
    secureStorage: secureStorage,
    biometricService: biometricService,
  );
});

/// Session State Provider (StateNotifier)
final sessionStateProvider = StateNotifierProvider<SessionStateNotifier, SessionState>((ref) {
  final manager = ref.watch(sessionManagerProvider);
  return SessionStateNotifier(manager);
});

/// Session State
class SessionState {
  /// Whether user is authenticated
  final bool isAuthenticated;

  /// Whether session is locked (requires re-auth)
  final bool isLocked;

  /// When session was last active
  final DateTime? lastActivityTime;

  /// Time until session expires (null if not authenticated)
  final Duration? timeUntilExpiry;

  /// Whether biometric re-auth is required after background
  final bool requiresBiometricReauth;

  /// Time app was last in background
  final DateTime? backgroundedAt;

  /// Session ID for tracking
  final String? sessionId;

  /// Error message if any
  final String? errorMessage;

  const SessionState({
    this.isAuthenticated = false,
    this.isLocked = false,
    this.lastActivityTime,
    this.timeUntilExpiry,
    this.requiresBiometricReauth = false,
    this.backgroundedAt,
    this.sessionId,
    this.errorMessage,
  });

  SessionState copyWith({
    bool? isAuthenticated,
    bool? isLocked,
    DateTime? lastActivityTime,
    Duration? timeUntilExpiry,
    bool? requiresBiometricReauth,
    DateTime? backgroundedAt,
    String? sessionId,
    String? errorMessage,
  }) {
    return SessionState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      isLocked: isLocked ?? this.isLocked,
      lastActivityTime: lastActivityTime ?? this.lastActivityTime,
      timeUntilExpiry: timeUntilExpiry ?? this.timeUntilExpiry,
      requiresBiometricReauth: requiresBiometricReauth ?? this.requiresBiometricReauth,
      backgroundedAt: backgroundedAt ?? this.backgroundedAt,
      sessionId: sessionId ?? this.sessionId,
      errorMessage: errorMessage,
    );
  }

  /// Check if session is valid (authenticated and not locked)
  bool get isValid => isAuthenticated && !isLocked;

  /// Check if session has expired
  bool get hasExpired {
    if (!isAuthenticated) return false;
    if (lastActivityTime == null) return false;
    return timeUntilExpiry != null && timeUntilExpiry!.isNegative;
  }
}

/// Session State Notifier
class SessionStateNotifier extends StateNotifier<SessionState> {
  final SessionManager _manager;
  Timer? _expiryTimer;
  Timer? _warningTimer;

  /// Callback when session expires
  VoidCallback? onSessionExpired;

  /// Callback when session is about to expire (1 minute warning)
  VoidCallback? onSessionExpiring;

  /// Callback when biometric re-auth is required
  VoidCallback? onBiometricReauthRequired;

  SessionStateNotifier(this._manager) : super(const SessionState()) {
    _initialize();
  }

  Future<void> _initialize() async {
    // Check if there's an existing session
    final hasSession = await _manager.hasActiveSession();
    if (hasSession) {
      final expiryTime = await _manager.getSessionExpiryTime();
      if (expiryTime != null && expiryTime.isAfter(DateTime.now())) {
        state = state.copyWith(
          isAuthenticated: true,
          lastActivityTime: DateTime.now(),
          timeUntilExpiry: expiryTime.difference(DateTime.now()),
          sessionId: await _manager.getSessionId(),
        );
        _startExpiryTimer();
      } else {
        // Session expired
        await _manager.clearSession();
      }
    }
  }

  /// Start a new session
  Future<void> startSession({
    required String sessionId,
    Duration timeout = const Duration(minutes: 15),
  }) async {
    await _manager.startSession(sessionId: sessionId, timeout: timeout);

    state = state.copyWith(
      isAuthenticated: true,
      isLocked: false,
      lastActivityTime: DateTime.now(),
      timeUntilExpiry: timeout,
      sessionId: sessionId,
      requiresBiometricReauth: false,
    );

    _startExpiryTimer();
    AppLogger.i('Session started', tag: 'SessionManager', data: {
      'sessionId': sessionId.substring(0, 8),
      'timeout': timeout.inMinutes,
    });
  }

  /// End current session
  Future<void> endSession() async {
    _cancelTimers();
    await _manager.clearSession();

    state = const SessionState();
    AppLogger.i('Session ended', tag: 'SessionManager');
  }

  /// Lock the session (requires re-auth)
  void lockSession({String? reason}) {
    if (!state.isAuthenticated) return;

    state = state.copyWith(
      isLocked: true,
      errorMessage: reason,
    );

    AppLogger.i('Session locked', tag: 'SessionManager', data: {'reason': reason});
  }

  /// Unlock session after successful re-auth
  Future<void> unlockSession() async {
    if (!state.isAuthenticated) return;

    state = state.copyWith(
      isLocked: false,
      requiresBiometricReauth: false,
      lastActivityTime: DateTime.now(),
      errorMessage: null,
    );

    await _manager.recordActivity();
    _resetExpiryTimer();

    AppLogger.i('Session unlocked', tag: 'SessionManager');
  }

  /// Record user activity (resets idle timer)
  Future<void> recordActivity() async {
    if (!state.isAuthenticated || state.isLocked) return;

    final timeout = state.timeUntilExpiry ?? const Duration(minutes: 15);
    state = state.copyWith(
      lastActivityTime: DateTime.now(),
      timeUntilExpiry: timeout,
    );

    await _manager.recordActivity();
    _resetExpiryTimer();
  }

  /// Handle app going to background
  void onAppBackgrounded() {
    if (!state.isAuthenticated) return;

    state = state.copyWith(
      backgroundedAt: DateTime.now(),
    );

    AppLogger.d('App backgrounded', tag: 'SessionManager');
  }

  /// Handle app coming to foreground
  Future<void> onAppResumed() async {
    if (!state.isAuthenticated || state.backgroundedAt == null) return;

    final backgroundDuration = DateTime.now().difference(state.backgroundedAt!);
    final config = _manager.config;

    AppLogger.d('App resumed', tag: 'SessionManager', data: {
      'backgroundDuration': backgroundDuration.inSeconds,
    });

    // Check if session expired while in background
    if (backgroundDuration > config.sessionTimeout) {
      AppLogger.w('Session expired while in background', tag: 'SessionManager');
      await endSession();
      onSessionExpired?.call();
      return;
    }

    // Check if biometric re-auth is required
    if (config.requireBiometricAfterBackground &&
        backgroundDuration >= config.backgroundLockThreshold) {
      state = state.copyWith(
        isLocked: true,
        requiresBiometricReauth: true,
        errorMessage: 'Re-authentication required',
      );
      onBiometricReauthRequired?.call();
      AppLogger.i('Biometric re-auth required after background', tag: 'SessionManager');
    }

    state = state.copyWith(backgroundedAt: null);
  }

  /// Attempt biometric re-authentication
  Future<bool> attemptBiometricReauth() async {
    if (!state.requiresBiometricReauth) return true;

    try {
      final success = await _manager.biometricService.authenticate(
        reason: 'Verify your identity to continue',
      );

      if (success) {
        await unlockSession();
        return true;
      }
    } catch (e) {
      AppLogger.e('Biometric re-auth failed', tag: 'SessionManager', error: e);
    }

    return false;
  }

  void _startExpiryTimer() {
    _cancelTimers();

    final timeout = state.timeUntilExpiry;
    if (timeout == null) return;

    // Warning 1 minute before expiry
    final warningTime = timeout - const Duration(minutes: 1);
    if (warningTime.isNegative) {
      // Less than 1 minute left, warn immediately
      onSessionExpiring?.call();
    } else {
      _warningTimer = Timer(warningTime, () {
        onSessionExpiring?.call();
        AppLogger.w('Session expiring soon', tag: 'SessionManager');
      });
    }

    // Expiry timer
    _expiryTimer = Timer(timeout, () {
      _handleSessionExpired();
    });
  }

  void _resetExpiryTimer() {
    _startExpiryTimer();
  }

  void _cancelTimers() {
    _expiryTimer?.cancel();
    _warningTimer?.cancel();
    _expiryTimer = null;
    _warningTimer = null;
  }

  Future<void> _handleSessionExpired() async {
    AppLogger.w('Session expired due to inactivity', tag: 'SessionManager');
    await endSession();
    onSessionExpired?.call();
  }

  @override
  void dispose() {
    _cancelTimers();
    super.dispose();
  }
}

/// Session Manager Configuration
class SessionConfig {
  /// Session timeout duration (idle logout)
  final Duration sessionTimeout;

  /// How long in background before requiring re-auth
  final Duration backgroundLockThreshold;

  /// Whether to require biometric after background
  final bool requireBiometricAfterBackground;

  /// Whether to show session expiry warning
  final bool showExpiryWarning;

  /// How long before expiry to show warning
  final Duration expiryWarningThreshold;

  /// Whether to extend session on activity
  final bool extendOnActivity;

  const SessionConfig({
    this.sessionTimeout = const Duration(minutes: 15),
    this.backgroundLockThreshold = const Duration(minutes: 1),
    this.requireBiometricAfterBackground = true,
    this.showExpiryWarning = true,
    this.expiryWarningThreshold = const Duration(minutes: 1),
    this.extendOnActivity = true,
  });

  /// Production configuration - stricter timeouts
  static const production = SessionConfig(
    sessionTimeout: Duration(minutes: 15),
    backgroundLockThreshold: Duration(seconds: 30),
    requireBiometricAfterBackground: true,
    showExpiryWarning: true,
    expiryWarningThreshold: Duration(minutes: 1),
    extendOnActivity: true,
  );

  /// Staging configuration - more lenient for testing
  static const staging = SessionConfig(
    sessionTimeout: Duration(minutes: 30),
    backgroundLockThreshold: Duration(minutes: 2),
    requireBiometricAfterBackground: true,
    showExpiryWarning: true,
    expiryWarningThreshold: Duration(minutes: 2),
    extendOnActivity: true,
  );

  /// Development configuration - very lenient
  static const development = SessionConfig(
    sessionTimeout: Duration(hours: 2),
    backgroundLockThreshold: Duration(minutes: 5),
    requireBiometricAfterBackground: false,
    showExpiryWarning: false,
    expiryWarningThreshold: Duration(minutes: 5),
    extendOnActivity: true,
  );

  /// Get config for environment
  factory SessionConfig.forEnvironment(String environment) {
    switch (environment.toLowerCase()) {
      case 'production':
      case 'prod':
        return SessionConfig.production;
      case 'staging':
      case 'stage':
        return SessionConfig.staging;
      default:
        return SessionConfig.development;
    }
  }
}

/// Session Manager
/// مدير الجلسات
///
/// Manages user session lifecycle including:
/// - Session timeout (idle logout)
/// - Biometric re-authentication after background
/// - Session persistence
/// - Activity tracking
///
/// يدير دورة حياة جلسة المستخدم بما في ذلك:
/// - مهلة الجلسة (تسجيل الخروج عند الخمول)
/// - إعادة المصادقة البيومترية بعد الخلفية
/// - استمرارية الجلسة
/// - تتبع النشاط
class SessionManager {
  final SecureStorageService secureStorage;
  final BiometricService biometricService;
  final SessionConfig config;

  // Storage keys
  static const _keySessionId = 'session_id';
  static const _keySessionStart = 'session_start';
  static const _keySessionExpiry = 'session_expiry';
  static const _keyLastActivity = 'last_activity';

  SessionManager({
    required this.secureStorage,
    required this.biometricService,
    this.config = const SessionConfig(),
  });

  /// Check if there's an active session
  Future<bool> hasActiveSession() async {
    final sessionId = await secureStorage.read(_keySessionId);
    if (sessionId == null) return false;

    final expiryStr = await secureStorage.read(_keySessionExpiry);
    if (expiryStr == null) return false;

    try {
      final expiry = DateTime.parse(expiryStr);
      return expiry.isAfter(DateTime.now());
    } catch (e) {
      return false;
    }
  }

  /// Get current session ID
  Future<String?> getSessionId() async {
    return secureStorage.read(_keySessionId);
  }

  /// Get session expiry time
  Future<DateTime?> getSessionExpiryTime() async {
    final expiryStr = await secureStorage.read(_keySessionExpiry);
    if (expiryStr == null) return null;

    try {
      return DateTime.parse(expiryStr);
    } catch (e) {
      return null;
    }
  }

  /// Get last activity time
  Future<DateTime?> getLastActivityTime() async {
    final activityStr = await secureStorage.read(_keyLastActivity);
    if (activityStr == null) return null;

    try {
      return DateTime.parse(activityStr);
    } catch (e) {
      return null;
    }
  }

  /// Start a new session
  Future<void> startSession({
    required String sessionId,
    Duration? timeout,
  }) async {
    final now = DateTime.now();
    final expiry = now.add(timeout ?? config.sessionTimeout);

    await Future.wait([
      secureStorage.write(_keySessionId, sessionId),
      secureStorage.write(_keySessionStart, now.toIso8601String()),
      secureStorage.write(_keySessionExpiry, expiry.toIso8601String()),
      secureStorage.write(_keyLastActivity, now.toIso8601String()),
    ]);

    AppLogger.d('Session persisted', tag: 'SessionManager', data: {
      'expiry': expiry.toIso8601String(),
    });
  }

  /// Record user activity (extends session if configured)
  Future<void> recordActivity() async {
    final now = DateTime.now();
    await secureStorage.write(_keyLastActivity, now.toIso8601String());

    if (config.extendOnActivity) {
      final expiry = now.add(config.sessionTimeout);
      await secureStorage.write(_keySessionExpiry, expiry.toIso8601String());
    }
  }

  /// Clear the current session
  Future<void> clearSession() async {
    await Future.wait([
      secureStorage.delete(_keySessionId),
      secureStorage.delete(_keySessionStart),
      secureStorage.delete(_keySessionExpiry),
      secureStorage.delete(_keyLastActivity),
    ]);

    AppLogger.d('Session cleared', tag: 'SessionManager');
  }

  /// Extend session by specified duration
  Future<void> extendSession(Duration extension) async {
    final currentExpiry = await getSessionExpiryTime();
    if (currentExpiry == null) return;

    final newExpiry = currentExpiry.add(extension);
    await secureStorage.write(_keySessionExpiry, newExpiry.toIso8601String());

    AppLogger.d('Session extended', tag: 'SessionManager', data: {
      'newExpiry': newExpiry.toIso8601String(),
    });
  }
}

/// Session Lifecycle Observer Widget
/// Wraps app content to observe lifecycle events and manage session
class SessionLifecycleObserver extends StatefulWidget {
  final Widget child;
  final WidgetRef ref;
  final VoidCallback? onSessionExpired;
  final VoidCallback? onBiometricRequired;

  const SessionLifecycleObserver({
    super.key,
    required this.child,
    required this.ref,
    this.onSessionExpired,
    this.onBiometricRequired,
  });

  @override
  State<SessionLifecycleObserver> createState() => _SessionLifecycleObserverState();
}

class _SessionLifecycleObserverState extends State<SessionLifecycleObserver>
    with WidgetsBindingObserver {

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);

    // Set up callbacks
    final notifier = widget.ref.read(sessionStateProvider.notifier);
    notifier.onSessionExpired = widget.onSessionExpired;
    notifier.onBiometricReauthRequired = widget.onBiometricRequired;
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    final notifier = widget.ref.read(sessionStateProvider.notifier);

    switch (state) {
      case AppLifecycleState.paused:
      case AppLifecycleState.inactive:
        notifier.onAppBackgrounded();
        break;
      case AppLifecycleState.resumed:
        notifier.onAppResumed();
        break;
      case AppLifecycleState.detached:
      case AppLifecycleState.hidden:
        // App is being terminated or hidden
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      behavior: HitTestBehavior.translucent,
      onTap: _recordActivity,
      onPanDown: (_) => _recordActivity(),
      child: widget.child,
    );
  }

  void _recordActivity() {
    widget.ref.read(sessionStateProvider.notifier).recordActivity();
  }
}

/// Session Lock Screen
/// Shows when session is locked and requires re-authentication
class SessionLockScreen extends StatelessWidget {
  final VoidCallback onUnlockAttempt;
  final VoidCallback? onLogout;
  final String? message;
  final bool showLogoutOption;

  const SessionLockScreen({
    super.key,
    required this.onUnlockAttempt,
    this.onLogout,
    this.message,
    this.showLogoutOption = true,
  });

  @override
  Widget build(BuildContext context) {
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return Scaffold(
      backgroundColor: const Color(0xFF2E7D32),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Lock icon
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.lock_outline,
                  size: 64,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 32),

              // Title
              Text(
                isArabic ? 'الجلسة مقفلة' : 'Session Locked',
                style: const TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                  fontFamily: 'IBMPlexSansArabic',
                ),
              ),
              const SizedBox(height: 16),

              // Message
              Text(
                message ?? (isArabic
                    ? 'يرجى التحقق من هويتك للمتابعة'
                    : 'Please verify your identity to continue'),
                style: const TextStyle(
                  fontSize: 16,
                  color: Colors.white70,
                  fontFamily: 'IBMPlexSansArabic',
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),

              // Unlock button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: onUnlockAttempt,
                  icon: const Icon(Icons.fingerprint),
                  label: Text(
                    isArabic ? 'فتح القفل بالبصمة' : 'Unlock with Biometric',
                    style: const TextStyle(
                      fontSize: 16,
                      fontFamily: 'IBMPlexSansArabic',
                    ),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: const Color(0xFF2E7D32),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),

              if (showLogoutOption && onLogout != null) ...[
                const SizedBox(height: 16),
                TextButton(
                  onPressed: onLogout,
                  child: Text(
                    isArabic ? 'تسجيل الخروج' : 'Logout',
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 16,
                      fontFamily: 'IBMPlexSansArabic',
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

/// Session Expiry Warning Dialog
class SessionExpiryWarningDialog extends StatelessWidget {
  final VoidCallback onExtend;
  final VoidCallback onLogout;
  final Duration timeRemaining;

  const SessionExpiryWarningDialog({
    super.key,
    required this.onExtend,
    required this.onLogout,
    this.timeRemaining = const Duration(minutes: 1),
  });

  @override
  Widget build(BuildContext context) {
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';
    final seconds = timeRemaining.inSeconds;

    return AlertDialog(
      title: Row(
        children: [
          const Icon(Icons.timer, color: Colors.orange),
          const SizedBox(width: 8),
          Text(
            isArabic ? 'الجلسة ستنتهي' : 'Session Expiring',
            style: const TextStyle(fontFamily: 'IBMPlexSansArabic'),
          ),
        ],
      ),
      content: Text(
        isArabic
            ? 'ستنتهي جلستك خلال $seconds ثانية. هل تريد تمديد الجلسة؟'
            : 'Your session will expire in $seconds seconds. Would you like to extend it?',
        style: const TextStyle(fontFamily: 'IBMPlexSansArabic'),
      ),
      actions: [
        TextButton(
          onPressed: onLogout,
          child: Text(
            isArabic ? 'تسجيل الخروج' : 'Logout',
            style: const TextStyle(fontFamily: 'IBMPlexSansArabic'),
          ),
        ),
        ElevatedButton(
          onPressed: onExtend,
          child: Text(
            isArabic ? 'تمديد الجلسة' : 'Extend Session',
            style: const TextStyle(fontFamily: 'IBMPlexSansArabic'),
          ),
        ),
      ],
    );
  }
}
