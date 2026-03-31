/// SAHOOL IAM Service
/// خدمة إدارة الهوية والوصول الرئيسية
///
/// Core Identity and Access Management service providing:
/// - User identity management | إدارة هوية المستخدم
/// - Access token handling | معالجة توكنات الوصول
/// - Permission checking | فحص الصلاحيات
/// - Multi-tenant support | دعم متعدد المستأجرين
/// - Session management | إدارة الجلسات
///
/// This is the central coordination point for all IAM operations.
library;

import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';

import '../auth/secure_storage_service.dart';
import '../utils/app_logger.dart';
import 'models/iam_models.dart';

// =============================================================================
// IAM Configuration
// إعدادات IAM
// =============================================================================

/// IAM Service configuration
class IAMConfig {
  /// Access token lifetime in minutes | عمر توكن الوصول بالدقائق
  final int accessTokenLifetimeMinutes;

  /// Refresh token lifetime in days | عمر توكن التحديث بالأيام
  final int refreshTokenLifetimeDays;

  /// Session timeout in minutes | مهلة الجلسة بالدقائق
  final int sessionTimeoutMinutes;

  /// Enable audit logging | تفعيل تسجيل التدقيق
  final bool enableAuditLogging;

  /// Max concurrent sessions per user | الحد الأقصى للجلسات المتزامنة
  final int maxConcurrentSessions;

  /// Enable offline capability tokens | تفعيل توكنات العمل بدون اتصال
  final bool enableOfflineTokens;

  /// Offline token lifetime in days | عمر توكن العمل بدون اتصال
  final int offlineTokenLifetimeDays;

  const IAMConfig({
    this.accessTokenLifetimeMinutes = 15,
    this.refreshTokenLifetimeDays = 7,
    this.sessionTimeoutMinutes = 30,
    this.enableAuditLogging = true,
    this.maxConcurrentSessions = 5,
    this.enableOfflineTokens = true,
    this.offlineTokenLifetimeDays = 30,
  });
}

// =============================================================================
// IAM Service
// خدمة IAM
// =============================================================================

/// Main IAM Service - Central coordination for identity and access
/// خدمة IAM الرئيسية - التنسيق المركزي للهوية والوصول
class IAMService {
  final SecureStorageService _secureStorage;
  final IAMConfig config;

  /// Current session | الجلسة الحالية
  UserSession _currentSession = UserSession.empty;

  /// Current tenant | المستأجر الحالي
  Tenant? _currentTenant;

  /// Audit log buffer | مخزن سجل التدقيق
  final List<IAMAuditEntry> _auditBuffer = [];
  static const int _maxAuditBufferSize = 100;

  /// Session listeners | مستمعي الجلسة
  final List<void Function(UserSession)> _sessionListeners = [];

  /// UUID generator
  final _uuid = const Uuid();

  IAMService({
    required SecureStorageService secureStorage,
    this.config = const IAMConfig(),
  }) : _secureStorage = secureStorage;

  // ===========================================================================
  // Session Management | إدارة الجلسات
  // ===========================================================================

  /// Get current session | الحصول على الجلسة الحالية
  UserSession get currentSession => _currentSession;

  /// Get current user | الحصول على المستخدم الحالي
  UserIdentity? get currentUser => _currentSession.user;

  /// Get current tenant | الحصول على المستأجر الحالي
  Tenant? get currentTenant => _currentTenant;

  /// Check if user is authenticated | التحقق من المصادقة
  bool get isAuthenticated => _currentSession.isAuthenticated;

  /// Check if session is active | التحقق من نشاط الجلسة
  bool get isSessionActive =>
      _currentSession.status == SessionStatus.authenticated &&
      !_currentSession.isAccessTokenExpired;

  /// Initialize IAM service - loads stored session
  /// تهيئة خدمة IAM - تحميل الجلسة المخزنة
  Future<void> initialize() async {
    AppLogger.i('Initializing IAM Service', tag: 'IAM');

    try {
      // Try to restore session from secure storage
      final sessionData = await _secureStorage.read('iam_session');
      if (sessionData != null) {
        final json = jsonDecode(sessionData) as Map<String, dynamic>;
        _currentSession = UserSession.fromJson(json);

        // Check if session is still valid
        if (_currentSession.isAuthenticated && !_currentSession.isRefreshTokenExpired) {
          AppLogger.i('Restored valid session for user: ${_currentSession.user?.id}', tag: 'IAM');

          // Load tenant
          await _loadCurrentTenant();

          // Refresh token if access token expired
          if (_currentSession.isAccessTokenExpired && _currentSession.canRefresh) {
            AppLogger.i('Access token expired, refreshing...', tag: 'IAM');
            // Token refresh would be handled by the auth service
          }
        } else {
          AppLogger.w('Stored session expired, clearing', tag: 'IAM');
          await _clearSession();
        }
      }

      _logAudit(IAMAuditAction.sessionCreated, granted: true);
    } catch (e, stack) {
      AppLogger.e('Failed to initialize IAM', tag: 'IAM', error: e, stackTrace: stack);
      await _clearSession();
    }
  }

  /// Create new session after successful authentication
  /// إنشاء جلسة جديدة بعد المصادقة الناجحة
  Future<UserSession> createSession({
    required UserIdentity user,
    required String accessToken,
    required String refreshToken,
    required DateTime accessTokenExpiry,
    required DateTime refreshTokenExpiry,
    String? identityProvider,
    DeviceInfo? deviceInfo,
    String? ipAddress,
  }) async {
    AppLogger.i('Creating new session for user: ${user.id}', tag: 'IAM');

    final sessionId = _uuid.v4();
    final now = DateTime.now();

    _currentSession = UserSession(
      sessionId: sessionId,
      user: user,
      accessToken: accessToken,
      refreshToken: refreshToken,
      accessTokenExpiry: accessTokenExpiry,
      refreshTokenExpiry: refreshTokenExpiry,
      status: SessionStatus.authenticated,
      startedAt: now,
      lastActivityAt: now,
      deviceInfo: deviceInfo,
      ipAddress: ipAddress,
      identityProvider: identityProvider ?? 'local',
    );

    // Save session to secure storage
    await _persistSession();

    // Load tenant
    await _loadCurrentTenant();

    // Notify listeners
    _notifySessionListeners();

    // Log audit
    _logAudit(
      IAMAuditAction.login,
      granted: true,
      details: {
        'identity_provider': identityProvider,
        'device_id': deviceInfo?.deviceId,
      },
    );

    AppLogger.i('Session created successfully', tag: 'IAM');
    return _currentSession;
  }

  /// Update session tokens (after refresh)
  /// تحديث توكنات الجلسة (بعد التحديث)
  Future<void> updateSessionTokens({
    required String accessToken,
    required String refreshToken,
    required DateTime accessTokenExpiry,
    required DateTime refreshTokenExpiry,
  }) async {
    if (!isAuthenticated) {
      throw const IAMException(
        'Cannot update tokens: No active session',
        'لا يمكن تحديث التوكنات: لا توجد جلسة نشطة',
      );
    }

    _currentSession = _currentSession.copyWith(
      accessToken: accessToken,
      refreshToken: refreshToken,
      accessTokenExpiry: accessTokenExpiry,
      refreshTokenExpiry: refreshTokenExpiry,
      lastActivityAt: DateTime.now(),
    );

    await _persistSession();
    _notifySessionListeners();

    _logAudit(IAMAuditAction.tokenRefresh, granted: true);
    AppLogger.i('Session tokens updated', tag: 'IAM');
  }

  /// Update last activity timestamp
  /// تحديث طابع آخر نشاط
  void updateActivity() {
    if (isAuthenticated) {
      _currentSession = _currentSession.copyWith(
        lastActivityAt: DateTime.now(),
      );
    }
  }

  /// Lock session (e.g., for sensitive operations)
  /// قفل الجلسة (مثلاً للعمليات الحساسة)
  Future<void> lockSession() async {
    if (isAuthenticated) {
      _currentSession = _currentSession.copyWith(
        status: SessionStatus.locked,
      );
      await _persistSession();
      _notifySessionListeners();

      AppLogger.i('Session locked', tag: 'IAM');
    }
  }

  /// Unlock session after re-authentication
  /// فتح قفل الجلسة بعد إعادة المصادقة
  Future<void> unlockSession() async {
    if (_currentSession.status == SessionStatus.locked) {
      _currentSession = _currentSession.copyWith(
        status: SessionStatus.authenticated,
        lastActivityAt: DateTime.now(),
      );
      await _persistSession();
      _notifySessionListeners();

      AppLogger.i('Session unlocked', tag: 'IAM');
    }
  }

  /// End session (logout)
  /// إنهاء الجلسة (تسجيل الخروج)
  Future<void> endSession({String? reason}) async {
    AppLogger.i('Ending session${reason != null ? ': $reason' : ''}', tag: 'IAM');

    _logAudit(
      IAMAuditAction.logout,
      granted: true,
      details: {'reason': reason},
    );

    await _clearSession();
    _notifySessionListeners();
  }

  /// Terminate session forcefully
  /// إنهاء الجلسة بالقوة
  Future<void> terminateSession({required String reason}) async {
    AppLogger.w('Session terminated: $reason', tag: 'IAM');

    _logAudit(
      IAMAuditAction.sessionTerminated,
      granted: true,
      details: {'reason': reason},
    );

    _currentSession = _currentSession.copyWith(
      status: SessionStatus.terminated,
    );

    await _clearSession();
    _notifySessionListeners();
  }

  /// Add session listener
  void addSessionListener(void Function(UserSession) listener) {
    _sessionListeners.add(listener);
  }

  /// Remove session listener
  void removeSessionListener(void Function(UserSession) listener) {
    _sessionListeners.remove(listener);
  }

  // ===========================================================================
  // Multi-Tenant Support | دعم متعدد المستأجرين
  // ===========================================================================

  /// Get available tenants for current user
  /// الحصول على المستأجرين المتاحين للمستخدم الحالي
  List<String> get availableTenants => currentUser?.tenantIds ?? [];

  /// Switch to a different tenant
  /// التبديل إلى مستأجر مختلف
  Future<void> switchTenant(String tenantId) async {
    if (currentUser == null) {
      throw const IAMException(
        'Cannot switch tenant: Not authenticated',
        'لا يمكن تبديل المستأجر: غير مصادق',
      );
    }

    if (!availableTenants.contains(tenantId)) {
      throw const IAMException(
        'Cannot switch tenant: Access denied',
        'لا يمكن تبديل المستأجر: الوصول مرفوض',
      );
    }

    final oldTenantId = currentUser!.tenantId;

    // Update user's current tenant
    final updatedUser = currentUser!.copyWith(tenantId: tenantId);
    _currentSession = _currentSession.copyWith(user: updatedUser);

    // Update stored tenant
    await _secureStorage.setTenantId(tenantId);

    // Load new tenant info
    await _loadCurrentTenant();

    await _persistSession();
    _notifySessionListeners();

    _logAudit(
      IAMAuditAction.tenantSwitch,
      granted: true,
      details: {
        'from_tenant': oldTenantId,
        'to_tenant': tenantId,
      },
    );

    AppLogger.i('Switched to tenant: $tenantId', tag: 'IAM');
  }

  /// Check if user has access to tenant
  /// التحقق من وصول المستخدم للمستأجر
  bool hasAccessToTenant(String tenantId) {
    if (currentUser == null) return false;
    if (currentUser!.isSuperAdmin) return true;
    return availableTenants.contains(tenantId);
  }

  // ===========================================================================
  // Token Access | الوصول للتوكنات
  // ===========================================================================

  /// Get current access token
  /// الحصول على توكن الوصول الحالي
  String? get accessToken => _currentSession.accessToken;

  /// Get current refresh token
  /// الحصول على توكن التحديث الحالي
  String? get refreshToken => _currentSession.refreshToken;

  /// Check if access token needs refresh
  /// التحقق مما إذا كان توكن الوصول يحتاج تحديث
  bool get needsTokenRefresh {
    if (!isAuthenticated) return false;

    final expiry = _currentSession.accessTokenExpiry;
    if (expiry == null) return true;

    // Refresh if less than 5 minutes until expiry
    return expiry.difference(DateTime.now()).inMinutes < 5;
  }

  // ===========================================================================
  // Offline Support | دعم العمل بدون اتصال
  // ===========================================================================

  /// Create offline capability token
  /// إنشاء توكن قدرات العمل بدون اتصال
  Future<Map<String, dynamic>> createOfflineToken() async {
    if (!isAuthenticated) {
      throw const IAMException(
        'Cannot create offline token: Not authenticated',
        'لا يمكن إنشاء توكن بدون اتصال: غير مصادق',
      );
    }

    if (!config.enableOfflineTokens) {
      throw const IAMException(
        'Offline tokens are disabled',
        'توكنات العمل بدون اتصال معطلة',
      );
    }

    final now = DateTime.now();
    final expiry = now.add(Duration(days: config.offlineTokenLifetimeDays));

    final offlineToken = {
      'user_id': currentUser!.id,
      'tenant_id': currentUser!.tenantId,
      'role': currentUser!.role,
      'permissions': currentUser!.permissions.toList(),
      'issued_at': now.toIso8601String(),
      'expires_at': expiry.toIso8601String(),
    };

    // Store offline token
    await _secureStorage.write(
      'iam_offline_token',
      jsonEncode(offlineToken),
    );

    AppLogger.i('Created offline token', tag: 'IAM');
    return offlineToken;
  }

  /// Load offline session
  /// تحميل جلسة العمل بدون اتصال
  Future<bool> loadOfflineSession() async {
    try {
      final tokenData = await _secureStorage.read('iam_offline_token');
      if (tokenData == null) return false;

      final token = jsonDecode(tokenData) as Map<String, dynamic>;
      final expiry = DateTime.tryParse(token['expires_at'] as String) ?? DateTime.now();

      if (DateTime.now().isAfter(expiry)) {
        AppLogger.w('Offline token expired', tag: 'IAM');
        await _secureStorage.delete('iam_offline_token');
        return false;
      }

      // Create minimal offline session
      _currentSession = UserSession(
        sessionId: 'offline-${_uuid.v4()}',
        user: UserIdentity(
          id: token['user_id'] as String,
          username: 'offline_user',
          displayName: 'Offline User',
          role: token['role'] as String,
          tenantId: token['tenant_id'] as String,
          permissions: (token['permissions'] as List<dynamic>).cast<String>().toSet(),
          createdAt: DateTime.now(),
        ),
        status: SessionStatus.authenticated,
        startedAt: DateTime.now(),
        isOffline: true,
      );

      _notifySessionListeners();
      AppLogger.i('Loaded offline session', tag: 'IAM');
      return true;
    } catch (e) {
      AppLogger.e('Failed to load offline session', tag: 'IAM', error: e);
      return false;
    }
  }

  // ===========================================================================
  // Audit Logging | تسجيل التدقيق
  // ===========================================================================

  /// Get audit log entries
  /// الحصول على سجلات التدقيق
  List<IAMAuditEntry> getAuditLog() => List.unmodifiable(_auditBuffer);

  /// Clear audit log
  void clearAuditLog() => _auditBuffer.clear();

  /// Export audit log
  List<Map<String, dynamic>> exportAuditLog() {
    return _auditBuffer.map((e) => e.toJson()).toList();
  }

  // ===========================================================================
  // Private Methods | الدوال الخاصة
  // ===========================================================================

  Future<void> _persistSession() async {
    try {
      await _secureStorage.write(
        'iam_session',
        jsonEncode(_currentSession.toJson()),
      );
    } catch (e) {
      AppLogger.e('Failed to persist session', tag: 'IAM', error: e);
    }
  }

  Future<void> _clearSession() async {
    _currentSession = UserSession.empty;
    _currentTenant = null;

    try {
      await _secureStorage.delete('iam_session');
      await _secureStorage.deleteTokens();
    } catch (e) {
      AppLogger.e('Failed to clear session storage', tag: 'IAM', error: e);
    }
  }

  void _notifySessionListeners() {
    for (final listener in _sessionListeners) {
      try {
        listener(_currentSession);
      } catch (e) {
        AppLogger.e('Session listener error', tag: 'IAM', error: e);
      }
    }
  }

  Future<void> _loadCurrentTenant() async {
    if (currentUser == null) return;

    try {
      // In a real implementation, this would fetch from API or cache
      // For now, create a basic tenant object
      _currentTenant = Tenant(
        id: currentUser!.tenantId,
        name: 'SAHOOL Tenant',
        nameAr: 'مستأجر سهول',
        slug: currentUser!.tenantId,
        createdAt: DateTime.now(),
      );
    } catch (e) {
      AppLogger.e('Failed to load tenant', tag: 'IAM', error: e);
    }
  }

  void _logAudit(
    IAMAuditAction action, {
    required bool granted,
    String? resourceType,
    String? resourceId,
    String? permission,
    String? denialReason,
    Map<String, dynamic>? details,
  }) {
    if (!config.enableAuditLogging) return;

    final entry = IAMAuditEntry(
      id: _uuid.v4(),
      userId: currentUser?.id ?? 'anonymous',
      tenantId: currentUser?.tenantId ?? '',
      action: action,
      resourceType: resourceType,
      resourceId: resourceId,
      permission: permission,
      granted: granted,
      denialReason: denialReason,
      details: details,
      ipAddress: _currentSession.ipAddress,
      deviceId: _currentSession.deviceInfo?.deviceId,
      timestamp: DateTime.now(),
    );

    _auditBuffer.add(entry);

    // Trim buffer if needed
    if (_auditBuffer.length > _maxAuditBufferSize) {
      _auditBuffer.removeAt(0);
    }

    // Log to app logger as well
    if (kDebugMode) {
      AppLogger.d(
        'IAM Audit: ${action.name} - ${granted ? "GRANTED" : "DENIED"}',
        tag: 'IAM_AUDIT',
        data: details,
      );
    }
  }
}

// =============================================================================
// IAM Exception
// استثناء IAM
// =============================================================================

/// IAM-specific exception with bilingual support
class IAMException implements Exception {
  /// Error message in English
  final String message;

  /// Error message in Arabic
  final String messageAr;

  /// Error code
  final String? code;

  const IAMException(this.message, this.messageAr, {this.code});

  /// Get localized message
  String getLocalizedMessage({String locale = 'ar'}) {
    return locale == 'ar' ? messageAr : message;
  }

  @override
  String toString() => 'IAMException: $message | $messageAr';
}

// =============================================================================
// IAM State for Riverpod
// حالة IAM لـ Riverpod
// =============================================================================

/// IAM state for state management
@immutable
class IAMState {
  final UserSession session;
  final Tenant? tenant;
  final bool isInitialized;
  final bool isLoading;
  final String? error;

  const IAMState({
    required this.session,
    this.tenant,
    this.isInitialized = false,
    this.isLoading = false,
    this.error,
  });

  bool get isAuthenticated => session.isAuthenticated;

  UserIdentity? get user => session.user;

  IAMState copyWith({
    UserSession? session,
    Tenant? tenant,
    bool? isInitialized,
    bool? isLoading,
    String? error,
  }) {
    return IAMState(
      session: session ?? this.session,
      tenant: tenant ?? this.tenant,
      isInitialized: isInitialized ?? this.isInitialized,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }

  static IAMState get initial => IAMState(
        session: UserSession.empty,
        isInitialized: false,
        isLoading: true,
      );
}
