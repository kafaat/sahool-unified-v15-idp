/// User Context - سياق المستخدم الحالي
/// يُستخدم للحصول على معرف المستخدم في العمليات المختلفة
class UserContext {
  String? _currentUserId;

  String get currentUserId => _currentUserId ?? 'anonymous';

  bool get isAuthenticated => _currentUserId != null;

  void setUser(String userId) {
    _currentUserId = userId;
  }

  void clearUser() {
    _currentUserId = null;
  }
}
