/// User Context - سياق المستخدم الحالي
/// يُستخدم للحصول على معرف المستخدم والمستأجر في العمليات المختلفة
/// Used to access current user ID and tenant ID across operations
class UserContext {
  String? _currentUserId;

  /// معرف المستأجر الحالي - Tenant ID from JWT 'tid' claim
  static String? _currentTenantId;

  String get currentUserId => _currentUserId ?? 'anonymous';

  bool get isAuthenticated => _currentUserId != null;

  /// معرف المستأجر الحالي
  /// Current tenant ID, returns null if not set
  static String? get currentTenantId => _currentTenantId;

  /// هل يوجد سياق مستأجر؟
  /// Whether a tenant context is available
  static bool get hasTenantContext => _currentTenantId != null;

  void setUser(String userId) {
    _currentUserId = userId;
  }

  /// تعيين معرف المستأجر
  /// Set tenant ID (typically from login response or JWT decode)
  static void setTenantId(String tenantId) {
    _currentTenantId = tenantId;
  }

  void clearUser() {
    _currentUserId = null;
  }

  /// مسح سياق المستخدم والمستأجر بالكامل (عند تسجيل الخروج)
  /// Clear both user and tenant context (on logout)
  static void clear() {
    _currentTenantId = null;
  }
}
