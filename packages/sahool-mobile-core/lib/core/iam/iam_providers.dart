/// SAHOOL IAM Providers
/// مزودات Riverpod لإدارة الهوية والوصول
///
/// Riverpod providers for Identity and Access Management:
/// - Session state management | إدارة حالة الجلسة
/// - Permission checking | فحص الصلاحيات
/// - Identity provider integration | تكامل مزودي الهوية
/// - Access control | التحكم في الوصول
///
/// These providers integrate all IAM components into the Flutter/Riverpod
/// state management system for reactive UI updates.
library;

import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/secure_storage_service.dart';
import '../utils/app_logger.dart';
import 'models/iam_models.dart';
import 'iam_service.dart';
import 'permission_manager.dart';
import 'identity_provider.dart';
import 'access_control.dart';

// =============================================================================
// Core IAM Providers
// مزودات IAM الأساسية
// =============================================================================

/// IAM Configuration provider
/// مزود إعدادات IAM
final iamConfigProvider = Provider<IAMConfig>((ref) {
  return const IAMConfig(
    accessTokenLifetimeMinutes: 15,
    refreshTokenLifetimeDays: 7,
    sessionTimeoutMinutes: 30,
    enableAuditLogging: true,
    maxConcurrentSessions: 5,
    enableOfflineTokens: true,
    offlineTokenLifetimeDays: 30,
  );
});

/// IAM Service provider
/// مزود خدمة IAM
final iamServiceProvider = Provider<IAMService>((ref) {
  final secureStorage = ref.watch(secureStorageProvider);
  final config = ref.watch(iamConfigProvider);

  return IAMService(
    secureStorage: secureStorage,
    config: config,
  );
});

/// IAM State Notifier
/// مدير حالة IAM
class IAMStateNotifier extends StateNotifier<IAMState> {
  final IAMService _iamService;
  final SecureStorageService _secureStorage;
  final Ref _ref;

  StreamSubscription<void>? _sessionSubscription;

  IAMStateNotifier({
    required IAMService iamService,
    required SecureStorageService secureStorage,
    required Ref ref,
  })  : _iamService = iamService,
        _secureStorage = secureStorage,
        _ref = ref,
        super(IAMState.initial) {
    _initialize();
  }

  /// Initialize IAM state
  Future<void> _initialize() async {
    AppLogger.i('Initializing IAM state', tag: 'IAM_PROVIDER');

    try {
      await _iamService.initialize();

      // Listen to session changes
      _iamService.addSessionListener(_onSessionChanged);

      state = state.copyWith(
        session: _iamService.currentSession,
        tenant: _iamService.currentTenant,
        isInitialized: true,
        isLoading: false,
      );

      AppLogger.i('IAM state initialized', tag: 'IAM_PROVIDER');
    } catch (e, stack) {
      AppLogger.e('Failed to initialize IAM state', tag: 'IAM_PROVIDER', error: e, stackTrace: stack);
      state = state.copyWith(
        isInitialized: true,
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  void _onSessionChanged(UserSession session) {
    state = state.copyWith(
      session: session,
      tenant: _iamService.currentTenant,
    );
  }

  @override
  void dispose() {
    _iamService.removeSessionListener(_onSessionChanged);
    _sessionSubscription?.cancel();
    super.dispose();
  }

  /// Login with credentials | تسجيل الدخول بالبيانات
  Future<AuthenticationResult> login({
    required String username,
    required String password,
    String? tenantId,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      // Get identity provider registry
      final registry = _ref.read(identityProviderRegistryProvider);
      final provider = registry.getProvider(IdentityProviderType.sahool);

      if (provider == null) {
        throw const IAMException(
          'SAHOOL identity provider not configured',
          'مزود هوية سهول غير مهيأ',
        );
      }

      final result = await provider.authenticate(parameters: {
        'username': username,
        'password': password,
        if (tenantId != null) 'tenant_id': tenantId,
      });

      if (result.success && result.user != null) {
        // Create session
        await _iamService.createSession(
          user: result.user!,
          accessToken: result.accessToken!,
          refreshToken: result.refreshToken ?? '',
          accessTokenExpiry: result.expiresAt!,
          refreshTokenExpiry: result.expiresAt!.add(const Duration(days: 7)),
          identityProvider: result.providerType.code,
        );

        // Create offline token if enabled
        if (_ref.read(iamConfigProvider).enableOfflineTokens) {
          await _iamService.createOfflineToken();
        }

        state = state.copyWith(
          session: _iamService.currentSession,
          tenant: _iamService.currentTenant,
          isLoading: false,
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: result.getLocalizedError(),
        );
      }

      return result;
    } catch (e, stack) {
      AppLogger.e('Login failed', tag: 'IAM_PROVIDER', error: e, stackTrace: stack);
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );

      return AuthenticationResult.failure(
        error: e.toString(),
        errorAr: 'فشل تسجيل الدخول',
        providerType: IdentityProviderType.sahool,
      );
    }
  }

  /// Login with identity provider | تسجيل الدخول بمزود هوية
  Future<AuthenticationResult> loginWithProvider(
    IdentityProviderType providerType, {
    Map<String, dynamic>? parameters,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final registry = _ref.read(identityProviderRegistryProvider);
      final provider = registry.getProvider(providerType);

      if (provider == null) {
        throw IAMException(
          'Identity provider not configured: ${providerType.code}',
          'مزود الهوية غير مهيأ: ${providerType.labelAr}',
        );
      }

      final result = await provider.authenticate(parameters: parameters);

      if (result.success && result.user != null) {
        await _iamService.createSession(
          user: result.user!,
          accessToken: result.accessToken!,
          refreshToken: result.refreshToken ?? '',
          accessTokenExpiry: result.expiresAt!,
          refreshTokenExpiry: result.expiresAt!.add(const Duration(days: 7)),
          identityProvider: providerType.code,
        );

        state = state.copyWith(
          session: _iamService.currentSession,
          tenant: _iamService.currentTenant,
          isLoading: false,
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: result.getLocalizedError(),
        );
      }

      return result;
    } catch (e) {
      AppLogger.e('Provider login failed', tag: 'IAM_PROVIDER', error: e);
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );

      return AuthenticationResult.failure(
        error: e.toString(),
        errorAr: 'فشل تسجيل الدخول',
        providerType: providerType,
      );
    }
  }

  /// Logout | تسجيل الخروج
  Future<void> logout({String? reason}) async {
    state = state.copyWith(isLoading: true);

    try {
      await _iamService.endSession(reason: reason);

      state = IAMState(
        session: UserSession.empty,
        isInitialized: true,
        isLoading: false,
      );

      AppLogger.i('Logout successful', tag: 'IAM_PROVIDER');
    } catch (e) {
      AppLogger.e('Logout error', tag: 'IAM_PROVIDER', error: e);
      // Force logout anyway
      state = IAMState(
        session: UserSession.empty,
        isInitialized: true,
        isLoading: false,
      );
    }
  }

  /// Refresh token | تحديث التوكن
  Future<bool> refreshToken() async {
    if (!_iamService.currentSession.canRefresh) {
      return false;
    }

    try {
      final registry = _ref.read(identityProviderRegistryProvider);
      final providerType = IdentityProviderType.fromCode(
        _iamService.currentSession.identityProvider ?? 'sahool',
      );
      final provider = registry.getProvider(providerType);

      if (provider == null) return false;

      final result = await provider.refreshToken(
        refreshToken: _iamService.refreshToken!,
      );

      if (result.success) {
        await _iamService.updateSessionTokens(
          accessToken: result.accessToken!,
          refreshToken: result.refreshToken ?? _iamService.refreshToken!,
          accessTokenExpiry: result.expiresAt!,
          refreshTokenExpiry: result.expiresAt!.add(const Duration(days: 7)),
        );

        state = state.copyWith(session: _iamService.currentSession);
        return true;
      }

      return false;
    } catch (e) {
      AppLogger.e('Token refresh failed', tag: 'IAM_PROVIDER', error: e);
      return false;
    }
  }

  /// Switch tenant | تبديل المستأجر
  Future<void> switchTenant(String tenantId) async {
    try {
      await _iamService.switchTenant(tenantId);
      state = state.copyWith(
        session: _iamService.currentSession,
        tenant: _iamService.currentTenant,
      );
    } catch (e) {
      AppLogger.e('Tenant switch failed', tag: 'IAM_PROVIDER', error: e);
      state = state.copyWith(error: e.toString());
    }
  }

  /// Load offline session | تحميل جلسة بدون اتصال
  Future<bool> loadOfflineSession() async {
    try {
      final success = await _iamService.loadOfflineSession();
      if (success) {
        state = state.copyWith(
          session: _iamService.currentSession,
          isLoading: false,
        );
      }
      return success;
    } catch (e) {
      AppLogger.e('Failed to load offline session', tag: 'IAM_PROVIDER', error: e);
      return false;
    }
  }

  /// Lock session | قفل الجلسة
  Future<void> lockSession() async {
    await _iamService.lockSession();
    state = state.copyWith(session: _iamService.currentSession);
  }

  /// Unlock session | فتح قفل الجلسة
  Future<void> unlockSession() async {
    await _iamService.unlockSession();
    state = state.copyWith(session: _iamService.currentSession);
  }

  /// Clear error | مسح الخطأ
  void clearError() {
    state = state.copyWith(error: null);
  }
}

/// IAM State provider
/// مزود حالة IAM
final iamStateProvider = StateNotifierProvider<IAMStateNotifier, IAMState>((ref) {
  return IAMStateNotifier(
    iamService: ref.watch(iamServiceProvider),
    secureStorage: ref.watch(secureStorageProvider),
    ref: ref,
  );
});

// =============================================================================
// Session Providers
// مزودات الجلسة
// =============================================================================

/// Current session provider | مزود الجلسة الحالية
final currentSessionProvider = Provider<UserSession>((ref) {
  return ref.watch(iamStateProvider).session;
});

/// Current user provider | مزود المستخدم الحالي
final currentUserProvider = Provider<UserIdentity?>((ref) {
  return ref.watch(iamStateProvider).user;
});

/// Is authenticated provider | مزود حالة المصادقة
final isAuthenticatedProvider = Provider<bool>((ref) {
  return ref.watch(iamStateProvider).isAuthenticated;
});

/// Current tenant provider | مزود المستأجر الحالي
final currentTenantProvider = Provider<Tenant?>((ref) {
  return ref.watch(iamStateProvider).tenant;
});

/// Access token provider | مزود توكن الوصول
final accessTokenProvider = Provider<String?>((ref) {
  return ref.watch(currentSessionProvider).accessToken;
});

/// Session status provider | مزود حالة الجلسة
final sessionStatusProvider = Provider<SessionStatus>((ref) {
  return ref.watch(currentSessionProvider).status;
});

/// Is session active provider | مزود نشاط الجلسة
final isSessionActiveProvider = Provider<bool>((ref) {
  final session = ref.watch(currentSessionProvider);
  return session.status == SessionStatus.authenticated &&
      !session.isAccessTokenExpired;
});

/// Needs token refresh provider | مزود الحاجة لتحديث التوكن
final needsTokenRefreshProvider = Provider<bool>((ref) {
  final service = ref.watch(iamServiceProvider);
  return service.needsTokenRefresh;
});

// =============================================================================
// Permission Providers
// مزودات الصلاحيات
// =============================================================================

/// Permission manager provider
/// مزود مدير الصلاحيات
final permissionManagerProvider = Provider<PermissionManager>((ref) {
  final user = ref.watch(currentUserProvider);
  return PermissionManager(user: user);
});

/// Can perform action provider | مزود القدرة على تنفيذ إجراء
final canProvider = Provider.family<bool, String>((ref, permission) {
  final manager = ref.watch(permissionManagerProvider);
  return manager.can(permission);
});

/// Can perform IAMPermission provider | مزود القدرة على تنفيذ صلاحية IAM
final canDoProvider = Provider.family<bool, IAMPermission>((ref, permission) {
  final manager = ref.watch(permissionManagerProvider);
  return manager.canDo(permission);
});

/// Has role provider | مزود وجود الدور
final hasRoleProvider = Provider.family<bool, IAMRole>((ref, role) {
  final manager = ref.watch(permissionManagerProvider);
  return manager.hasRole(role);
});

/// Has role at least provider | مزود الدور الأدنى
final hasRoleAtLeastProvider = Provider.family<bool, IAMRole>((ref, role) {
  final manager = ref.watch(permissionManagerProvider);
  return manager.hasRoleAtLeast(role);
});

/// Current role provider | مزود الدور الحالي
final currentRoleProvider = Provider<IAMRole>((ref) {
  final manager = ref.watch(permissionManagerProvider);
  return manager.currentRole;
});

/// Is admin provider | مزود كون المستخدم مسؤول
final isAdminProvider = Provider<bool>((ref) {
  final manager = ref.watch(permissionManagerProvider);
  return manager.isAdmin;
});

/// Is manager provider | مزود كون المستخدم مدير
final isManagerProvider = Provider<bool>((ref) {
  final manager = ref.watch(permissionManagerProvider);
  return manager.isManager;
});

/// Is supervisor provider | مزود كون المستخدم مشرف
final isSupervisorProvider = Provider<bool>((ref) {
  final manager = ref.watch(permissionManagerProvider);
  return manager.isSupervisor;
});

/// Effective permissions provider | مزود الصلاحيات الفعالة
final effectivePermissionsProvider = Provider<Set<String>>((ref) {
  final manager = ref.watch(permissionManagerProvider);
  return manager.effectivePermissions;
});

/// Granted permissions provider (as IAMPermission) | مزود الصلاحيات الممنوحة
final grantedPermissionsProvider = Provider<List<IAMPermission>>((ref) {
  final manager = ref.watch(permissionManagerProvider);
  return manager.grantedPermissions;
});

/// Permissions by category provider | مزود الصلاحيات حسب الفئة
final permissionsByCategoryProvider = Provider<Map<PermissionCategory, List<IAMPermission>>>((ref) {
  final manager = ref.watch(permissionManagerProvider);
  return manager.permissionsByCategory;
});

// =============================================================================
// Identity Provider Providers
// مزودات مزودي الهوية
// =============================================================================

/// Identity provider registry provider
/// مزود سجل مزودي الهوية
final identityProviderRegistryProvider = Provider<IdentityProviderRegistry>((ref) {
  final registry = IdentityProviderRegistry();

  // Register SAHOOL provider
  registry.register(SahoolIdentityProvider(
    apiBaseUrl: 'https://api.sahool.app',
    httpClient: (method, url, body, headers) async {
      // This would use the actual HTTP client
      // For now, return empty response
      return {};
    },
  ));

  // Social providers can be registered here when packages are added
  // registry.register(GoogleIdentityProvider(config: ...));
  // registry.register(AppleIdentityProvider(config: ...));

  registry.setDefaultProvider(IdentityProviderType.sahool);

  return registry;
});

/// Available identity providers provider
/// مزود مزودي الهوية المتاحين
final availableIdentityProvidersProvider = FutureProvider<List<IdentityProvider>>((ref) async {
  final registry = ref.watch(identityProviderRegistryProvider);
  return registry.getAvailableProviders();
});

// =============================================================================
// Access Control Providers
// مزودات التحكم في الوصول
// =============================================================================

/// Access control service provider
/// مزود خدمة التحكم في الوصول
final accessControlServiceProvider = Provider<AccessControlService>((ref) {
  final user = ref.watch(currentUserProvider);
  final permissionManager = ref.watch(permissionManagerProvider);

  return AccessControlService(
    user: user,
    permissionManager: permissionManager,
    onAudit: (entry) {
      if (kDebugMode) {
        AppLogger.d(
          'Access: ${entry.action.code} on ${entry.resourceType.code}:${entry.resourceId} - ${entry.allowed ? "ALLOWED" : "DENIED"}',
          tag: 'ACL_AUDIT',
        );
      }
    },
  );
});

/// Check resource access provider
/// مزود فحص الوصول للمورد
final checkResourceAccessProvider = Provider.family<AccessDecision, ResourceAccessRequest>((ref, request) {
  final service = ref.watch(accessControlServiceProvider);
  return service.checkResourceAccess(
    resourceType: request.resourceType,
    resourceId: request.resourceId,
    action: request.action,
    context: request.context,
  );
});

/// Resource access request for provider
/// طلب الوصول للمورد للمزود
@immutable
class ResourceAccessRequest {
  final ResourceType resourceType;
  final String resourceId;
  final AccessAction action;
  final Map<String, dynamic>? context;

  const ResourceAccessRequest({
    required this.resourceType,
    required this.resourceId,
    required this.action,
    this.context,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ResourceAccessRequest &&
          resourceType == other.resourceType &&
          resourceId == other.resourceId &&
          action == other.action;

  @override
  int get hashCode => Object.hash(resourceType, resourceId, action);
}

/// Can access resource provider
/// مزود القدرة على الوصول للمورد
final canAccessResourceProvider = Provider.family<bool, ResourceAccessRequest>((ref, request) {
  final decision = ref.watch(checkResourceAccessProvider(request));
  return decision.allowed;
});

/// Can read field provider
/// مزود القدرة على قراءة الحقل
final canReadFieldProvider = Provider.family<bool, FieldAccessRequest>((ref, request) {
  final service = ref.watch(accessControlServiceProvider);
  return service.canReadField(request.resourceType, request.fieldName);
});

/// Can write field provider
/// مزود القدرة على كتابة الحقل
final canWriteFieldProvider = Provider.family<bool, FieldAccessRequest>((ref, request) {
  final service = ref.watch(accessControlServiceProvider);
  return service.canWriteField(request.resourceType, request.fieldName);
});

/// Field access request
/// طلب الوصول للحقل
@immutable
class FieldAccessRequest {
  final ResourceType resourceType;
  final String fieldName;

  const FieldAccessRequest({
    required this.resourceType,
    required this.fieldName,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FieldAccessRequest &&
          resourceType == other.resourceType &&
          fieldName == other.fieldName;

  @override
  int get hashCode => Object.hash(resourceType, fieldName);
}

// =============================================================================
// Audit Providers
// مزودات التدقيق
// =============================================================================

/// IAM audit log provider
/// مزود سجل تدقيق IAM
final iamAuditLogProvider = Provider<List<IAMAuditEntry>>((ref) {
  final service = ref.watch(iamServiceProvider);
  return service.getAuditLog();
});

// =============================================================================
// Utility Extensions
// امتدادات مساعدة
// =============================================================================

/// Extension for easy permission checking on WidgetRef
/// امتداد لفحص الصلاحيات بسهولة على WidgetRef
extension IAMWidgetRefExtension on WidgetRef {
  /// Check if user can perform action | التحقق من قدرة المستخدم على تنفيذ إجراء
  bool can(String permission) => read(canProvider(permission));

  /// Check if user can perform IAMPermission | التحقق من قدرة المستخدم على تنفيذ صلاحية
  bool canDo(IAMPermission permission) => read(canDoProvider(permission));

  /// Check if user has role | التحقق من وجود الدور
  bool hasRole(IAMRole role) => read(hasRoleProvider(role));

  /// Check if user has minimum role | التحقق من الدور الأدنى
  bool hasRoleAtLeast(IAMRole role) => read(hasRoleAtLeastProvider(role));

  /// Get current user | الحصول على المستخدم الحالي
  UserIdentity? get currentUser => read(currentUserProvider);

  /// Get current session | الحصول على الجلسة الحالية
  UserSession get currentSession => read(currentSessionProvider);

  /// Check if authenticated | التحقق من المصادقة
  bool get isAuthenticated => read(isAuthenticatedProvider);

  /// Check if admin | التحقق من كون المستخدم مسؤول
  bool get isAdmin => read(isAdminProvider);

  /// Check if manager | التحقق من كون المستخدم مدير
  bool get isManager => read(isManagerProvider);

  /// Check if supervisor | التحقق من كون المستخدم مشرف
  bool get isSupervisor => read(isSupervisorProvider);

  /// Get permission manager | الحصول على مدير الصلاحيات
  PermissionManager get permissions => read(permissionManagerProvider);

  /// Get access control service | الحصول على خدمة التحكم في الوصول
  AccessControlService get accessControl => read(accessControlServiceProvider);
}

/// Extension for Ref
/// امتداد لـ Ref
extension IAMRefExtension on Ref {
  /// Check if user can perform action | التحقق من قدرة المستخدم على تنفيذ إجراء
  bool can(String permission) => read(canProvider(permission));

  /// Check if user can perform IAMPermission | التحقق من قدرة المستخدم على تنفيذ صلاحية
  bool canDo(IAMPermission permission) => read(canDoProvider(permission));

  /// Get current user | الحصول على المستخدم الحالي
  UserIdentity? get currentUser => read(currentUserProvider);

  /// Check if authenticated | التحقق من المصادقة
  bool get isAuthenticated => read(isAuthenticatedProvider);
}
