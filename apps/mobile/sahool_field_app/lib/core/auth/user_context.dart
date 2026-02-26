import 'package:flutter/foundation.dart';
import '../utils/app_logger.dart';

/// User Context - سياق المستخدم الحالي
/// يُستخدم للحصول على معرف المستخدم في العمليات المختلفة
///
/// This class maintains the current user's context and provides
/// a way to track authentication state across the application.
class UserContext extends ChangeNotifier {
  String? _currentUserId;
  String? _currentTenantId;
  String? _currentRole;
  DateTime? _sessionStartTime;

  /// Get current user ID, returns 'anonymous' if not authenticated
  String get currentUserId => _currentUserId ?? 'anonymous';

  /// Get current tenant ID
  String? get currentTenantId => _currentTenantId;

  /// Get current user role
  String? get currentRole => _currentRole;

  /// Get session start time
  DateTime? get sessionStartTime => _sessionStartTime;

  /// Check if user is authenticated
  bool get isAuthenticated =>
      _currentUserId != null && _currentUserId!.isNotEmpty;

  /// Get session duration
  Duration? get sessionDuration {
    if (_sessionStartTime == null) return null;
    return DateTime.now().difference(_sessionStartTime!);
  }

  /// Set user context
  void setUser(String userId, {String? tenantId, String? role}) {
    if (userId.isEmpty) {
      AppLogger.w('Attempted to set empty user ID', tag: 'USER_CONTEXT');
      return;
    }

    final wasAuthenticated = isAuthenticated;
    final previousUserId = _currentUserId;

    _currentUserId = userId;
    _currentTenantId = tenantId;
    _currentRole = role;

    // Only set session start if this is a new session
    if (!wasAuthenticated || previousUserId != userId) {
      _sessionStartTime = DateTime.now();
    }

    AppLogger.i(
      'User context set',
      tag: 'USER_CONTEXT',
      data: {'userId': userId, 'tenantId': tenantId, 'role': role},
    );

    notifyListeners();
  }

  /// Update tenant ID without changing user
  void setTenantId(String tenantId) {
    if (tenantId.isEmpty) {
      AppLogger.w('Attempted to set empty tenant ID', tag: 'USER_CONTEXT');
      return;
    }

    _currentTenantId = tenantId;
    AppLogger.d('Tenant ID updated',
        tag: 'USER_CONTEXT', data: {'tenantId': tenantId});
    notifyListeners();
  }

  /// Update role without changing user
  void setRole(String role) {
    _currentRole = role;
    AppLogger.d('Role updated', tag: 'USER_CONTEXT', data: {'role': role});
    notifyListeners();
  }

  /// Clear user context (logout)
  void clearUser() {
    final wasAuthenticated = isAuthenticated;

    _currentUserId = null;
    _currentTenantId = null;
    _currentRole = null;
    _sessionStartTime = null;

    if (wasAuthenticated) {
      AppLogger.i('User context cleared', tag: 'USER_CONTEXT');
      notifyListeners();
    }
  }

  /// Create a snapshot of current context (for passing to isolates, etc.)
  UserContextSnapshot get snapshot => UserContextSnapshot(
        userId: _currentUserId,
        tenantId: _currentTenantId,
        role: _currentRole,
        sessionStartTime: _sessionStartTime,
      );

  @override
  String toString() {
    return 'UserContext(userId: $currentUserId, tenantId: $currentTenantId, role: $currentRole, authenticated: $isAuthenticated)';
  }
}

/// Immutable snapshot of user context
/// Can be safely passed to isolates or stored
class UserContextSnapshot {
  final String? userId;
  final String? tenantId;
  final String? role;
  final DateTime? sessionStartTime;

  const UserContextSnapshot({
    this.userId,
    this.tenantId,
    this.role,
    this.sessionStartTime,
  });

  bool get isAuthenticated => userId != null && userId!.isNotEmpty;

  String get currentUserId => userId ?? 'anonymous';

  Map<String, dynamic> toJson() => {
        'userId': userId,
        'tenantId': tenantId,
        'role': role,
        'sessionStartTime': sessionStartTime?.toIso8601String(),
      };

  factory UserContextSnapshot.fromJson(Map<String, dynamic> json) {
    return UserContextSnapshot(
      userId: json['userId'] as String?,
      tenantId: json['tenantId'] as String?,
      role: json['role'] as String?,
      sessionStartTime: json['sessionStartTime'] != null
          ? DateTime.tryParse(json['sessionStartTime'] as String)
          : null,
    );
  }
}
