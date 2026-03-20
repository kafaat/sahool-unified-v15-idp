/// SAHOOL IAM Models
/// نماذج إدارة الهوية والوصول
///
/// Core data models for Identity and Access Management system.
/// Contains user identity, session, and audit models with bilingual support.

import 'package:flutter/foundation.dart';

// =============================================================================
// User Identity Model
// نموذج هوية المستخدم
// =============================================================================

/// Complete user identity with all attributes
/// الهوية الكاملة للمستخدم مع جميع الخصائص
///
/// NOTE: This model has field name differences from the backend User model
/// (Prisma schema). When possible, prefer using `User` from `auth_service.dart`
/// for data synced from the backend. Field mapping:
///   - displayName → name (backend)
///   - displayNameAr → nameAr (backend)
///   - username → not in backend User model
///   - tenantIds → single tenantId in backend
@immutable
class UserIdentity {
  /// Unique user identifier | المعرف الفريد للمستخدم
  final String id;

  /// Username for login | اسم المستخدم لتسجيل الدخول
  final String username;

  /// User's email address | البريد الإلكتروني
  final String? email;

  /// User's phone number | رقم الهاتف
  final String? phone;

  /// Display name | الاسم المعروض
  final String displayName;

  /// Display name in Arabic | الاسم بالعربية
  final String? displayNameAr;

  /// Profile picture URL | رابط صورة الملف الشخصي
  final String? avatarUrl;

  /// User's role | دور المستخدم
  final String role;

  /// Current tenant ID | معرف المستأجر الحالي
  final String tenantId;

  /// All tenant IDs user has access to | المستأجرون المتاحون
  final List<String> tenantIds;

  /// User's permissions | صلاحيات المستخدم
  final Set<String> permissions;

  /// Custom attributes | خصائص مخصصة
  final Map<String, dynamic> attributes;

  /// Whether email is verified | هل البريد الإلكتروني مُتحقق منه
  final bool emailVerified;

  /// Whether phone is verified | هل رقم الهاتف مُتحقق منه
  final bool phoneVerified;

  /// Account status (matches Prisma UserStatus: active, inactive, suspended, pending)
  /// حالة الحساب
  final String status;

  /// Whether account is active | هل الحساب نشط
  final bool isActive;

  /// Whether MFA is enabled | هل المصادقة الثنائية مفعلة
  final bool mfaEnabled;

  /// Preferred language (ar/en) | اللغة المفضلة
  final String preferredLanguage;

  /// Created timestamp | تاريخ الإنشاء
  final DateTime createdAt;

  /// Last updated timestamp | تاريخ آخر تحديث
  final DateTime? updatedAt;

  /// Last login timestamp | تاريخ آخر تسجيل دخول
  final DateTime? lastLoginAt;

  const UserIdentity({
    required this.id,
    required this.username,
    this.email,
    this.phone,
    required this.displayName,
    this.displayNameAr,
    this.avatarUrl,
    required this.role,
    required this.tenantId,
    this.tenantIds = const [],
    this.permissions = const {},
    this.attributes = const {},
    this.emailVerified = false,
    this.phoneVerified = false,
    this.status = 'active',
    this.isActive = true,
    this.mfaEnabled = false,
    this.preferredLanguage = 'ar',
    required this.createdAt,
    this.updatedAt,
    this.lastLoginAt,
  });

  /// Get localized display name
  String getDisplayName({String locale = 'ar'}) {
    if (locale == 'ar' && displayNameAr != null) {
      return displayNameAr!;
    }
    return displayName;
  }

  /// Check if user is admin
  bool get isAdmin => role == 'admin' || role == 'super_admin';

  /// Check if user is super admin
  bool get isSuperAdmin => role == 'super_admin';

  /// Copy with modifications
  UserIdentity copyWith({
    String? id,
    String? username,
    String? email,
    String? phone,
    String? displayName,
    String? displayNameAr,
    String? avatarUrl,
    String? role,
    String? tenantId,
    List<String>? tenantIds,
    Set<String>? permissions,
    Map<String, dynamic>? attributes,
    bool? emailVerified,
    bool? phoneVerified,
    String? status,
    bool? isActive,
    bool? mfaEnabled,
    String? preferredLanguage,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? lastLoginAt,
  }) {
    return UserIdentity(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      displayName: displayName ?? this.displayName,
      displayNameAr: displayNameAr ?? this.displayNameAr,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      role: role ?? this.role,
      tenantId: tenantId ?? this.tenantId,
      tenantIds: tenantIds ?? this.tenantIds,
      permissions: permissions ?? this.permissions,
      attributes: attributes ?? this.attributes,
      emailVerified: emailVerified ?? this.emailVerified,
      phoneVerified: phoneVerified ?? this.phoneVerified,
      status: status ?? this.status,
      isActive: isActive ?? this.isActive,
      mfaEnabled: mfaEnabled ?? this.mfaEnabled,
      preferredLanguage: preferredLanguage ?? this.preferredLanguage,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      lastLoginAt: lastLoginAt ?? this.lastLoginAt,
    );
  }

  /// Create from JSON
  factory UserIdentity.fromJson(Map<String, dynamic> json) {
    return UserIdentity(
      id: json['id'] as String,
      username: json['username'] as String,
      email: json['email'] as String?,
      phone: json['phone'] as String?,
      displayName: json['display_name'] as String? ?? json['name'] as String? ?? '',
      displayNameAr: json['display_name_ar'] as String?,
      avatarUrl: json['avatar_url'] as String?,
      role: json['role'] as String? ?? 'viewer',
      tenantId: json['tenant_id'] as String? ?? '',
      tenantIds: (json['tenant_ids'] as List<dynamic>?)?.whereType<String>().toList() ?? [],
      permissions: (json['permissions'] as List<dynamic>?)?.whereType<String>().toSet() ?? {},
      attributes: (json['attributes'] as Map<String, dynamic>?) ?? {},
      emailVerified: json['email_verified'] as bool? ?? false,
      phoneVerified: json['phone_verified'] as bool? ?? false,
      status: (json['status'] as String? ?? 'active').toLowerCase(),
      isActive: json['is_active'] as bool? ?? ((json['status'] as String? ?? 'active').toLowerCase() == 'active'),
      mfaEnabled: json['mfa_enabled'] as bool? ?? false,
      preferredLanguage: json['preferred_language'] as String? ?? 'ar',
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
      lastLoginAt: json['last_login_at'] != null
          ? DateTime.parse(json['last_login_at'] as String)
          : null,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'phone': phone,
      'display_name': displayName,
      'display_name_ar': displayNameAr,
      'avatar_url': avatarUrl,
      'role': role,
      'tenant_id': tenantId,
      'tenant_ids': tenantIds,
      'permissions': permissions.toList(),
      'attributes': attributes,
      'email_verified': emailVerified,
      'phone_verified': phoneVerified,
      'status': status,
      'is_active': isActive,
      'mfa_enabled': mfaEnabled,
      'preferred_language': preferredLanguage,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'last_login_at': lastLoginAt?.toIso8601String(),
    };
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is UserIdentity && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;
}

// =============================================================================
// Session Model
// نموذج الجلسة
// =============================================================================

/// Authentication session state
/// حالة جلسة المصادقة
enum SessionStatus {
  /// Not authenticated | غير مصادق
  unauthenticated,

  /// Authenticated and active | مصادق ونشط
  authenticated,

  /// Token expired, needs refresh | انتهت صلاحية التوكن، يحتاج تحديث
  expired,

  /// Session locked (e.g., for sensitive operations) | الجلسة مقفلة
  locked,

  /// Session terminated | الجلسة منتهية
  terminated,
}

/// User session information
/// معلومات جلسة المستخدم
@immutable
class UserSession {
  /// Session ID | معرف الجلسة
  final String sessionId;

  /// User identity | هوية المستخدم
  final UserIdentity? user;

  /// Access token | توكن الوصول
  final String? accessToken;

  /// Refresh token | توكن التحديث
  final String? refreshToken;

  /// Access token expiry | تاريخ انتهاء توكن الوصول
  final DateTime? accessTokenExpiry;

  /// Refresh token expiry | تاريخ انتهاء توكن التحديث
  final DateTime? refreshTokenExpiry;

  /// Session status | حالة الجلسة
  final SessionStatus status;

  /// Session started at | بداية الجلسة
  final DateTime startedAt;

  /// Last activity timestamp | آخر نشاط
  final DateTime? lastActivityAt;

  /// Device information | معلومات الجهاز
  final DeviceInfo? deviceInfo;

  /// IP address (for audit) | عنوان IP
  final String? ipAddress;

  /// Identity provider used | مزود الهوية المستخدم
  final String? identityProvider;

  /// Whether this is an offline session | هل هذه جلسة بدون اتصال
  final bool isOffline;

  const UserSession({
    required this.sessionId,
    this.user,
    this.accessToken,
    this.refreshToken,
    this.accessTokenExpiry,
    this.refreshTokenExpiry,
    this.status = SessionStatus.unauthenticated,
    required this.startedAt,
    this.lastActivityAt,
    this.deviceInfo,
    this.ipAddress,
    this.identityProvider,
    this.isOffline = false,
  });

  /// Check if session is authenticated
  bool get isAuthenticated => status == SessionStatus.authenticated && user != null;

  /// Check if access token is expired
  bool get isAccessTokenExpired {
    if (accessTokenExpiry == null) return true;
    return DateTime.now().isAfter(accessTokenExpiry!);
  }

  /// Check if refresh token is expired
  bool get isRefreshTokenExpired {
    if (refreshTokenExpiry == null) return true;
    return DateTime.now().isAfter(refreshTokenExpiry!);
  }

  /// Check if session can be refreshed
  bool get canRefresh => !isRefreshTokenExpired && refreshToken != null;

  /// Get time until access token expires
  Duration? get timeUntilExpiry {
    if (accessTokenExpiry == null) return null;
    return accessTokenExpiry!.difference(DateTime.now());
  }

  /// Empty/initial session
  static UserSession get empty => UserSession(
        sessionId: '',
        startedAt: DateTime.now(),
        status: SessionStatus.unauthenticated,
      );

  /// Copy with modifications
  UserSession copyWith({
    String? sessionId,
    UserIdentity? user,
    String? accessToken,
    String? refreshToken,
    DateTime? accessTokenExpiry,
    DateTime? refreshTokenExpiry,
    SessionStatus? status,
    DateTime? startedAt,
    DateTime? lastActivityAt,
    DeviceInfo? deviceInfo,
    String? ipAddress,
    String? identityProvider,
    bool? isOffline,
  }) {
    return UserSession(
      sessionId: sessionId ?? this.sessionId,
      user: user ?? this.user,
      accessToken: accessToken ?? this.accessToken,
      refreshToken: refreshToken ?? this.refreshToken,
      accessTokenExpiry: accessTokenExpiry ?? this.accessTokenExpiry,
      refreshTokenExpiry: refreshTokenExpiry ?? this.refreshTokenExpiry,
      status: status ?? this.status,
      startedAt: startedAt ?? this.startedAt,
      lastActivityAt: lastActivityAt ?? this.lastActivityAt,
      deviceInfo: deviceInfo ?? this.deviceInfo,
      ipAddress: ipAddress ?? this.ipAddress,
      identityProvider: identityProvider ?? this.identityProvider,
      isOffline: isOffline ?? this.isOffline,
    );
  }

  /// Create from JSON
  factory UserSession.fromJson(Map<String, dynamic> json) {
    return UserSession(
      sessionId: json['session_id'] as String? ?? '',
      user: json['user'] != null
          ? UserIdentity.fromJson(json['user'] as Map<String, dynamic>)
          : null,
      accessToken: json['access_token'] as String?,
      refreshToken: json['refresh_token'] as String?,
      accessTokenExpiry: json['access_token_expiry'] != null
          ? DateTime.parse(json['access_token_expiry'] as String)
          : null,
      refreshTokenExpiry: json['refresh_token_expiry'] != null
          ? DateTime.parse(json['refresh_token_expiry'] as String)
          : null,
      status: SessionStatus.values.firstWhere(
        (s) => s.name == json['status'],
        orElse: () => SessionStatus.unauthenticated,
      ),
      startedAt: json['started_at'] != null
          ? DateTime.parse(json['started_at'] as String)
          : DateTime.now(),
      lastActivityAt: json['last_activity_at'] != null
          ? DateTime.parse(json['last_activity_at'] as String)
          : null,
      deviceInfo: json['device_info'] != null
          ? DeviceInfo.fromJson(json['device_info'] as Map<String, dynamic>)
          : null,
      ipAddress: json['ip_address'] as String?,
      identityProvider: json['identity_provider'] as String?,
      isOffline: json['is_offline'] as bool? ?? false,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'session_id': sessionId,
      'user': user?.toJson(),
      'access_token': accessToken,
      'refresh_token': refreshToken,
      'access_token_expiry': accessTokenExpiry?.toIso8601String(),
      'refresh_token_expiry': refreshTokenExpiry?.toIso8601String(),
      'status': status.name,
      'started_at': startedAt.toIso8601String(),
      'last_activity_at': lastActivityAt?.toIso8601String(),
      'device_info': deviceInfo?.toJson(),
      'ip_address': ipAddress,
      'identity_provider': identityProvider,
      'is_offline': isOffline,
    };
  }
}

// =============================================================================
// Device Info Model
// نموذج معلومات الجهاز
// =============================================================================

/// Device information for session tracking
/// معلومات الجهاز لتتبع الجلسات
@immutable
class DeviceInfo {
  /// Device unique identifier | المعرف الفريد للجهاز
  final String deviceId;

  /// Device name | اسم الجهاز
  final String? deviceName;

  /// Device model | موديل الجهاز
  final String? model;

  /// Operating system | نظام التشغيل
  final String? os;

  /// OS version | إصدار نظام التشغيل
  final String? osVersion;

  /// App version | إصدار التطبيق
  final String? appVersion;

  /// Platform (android/ios) | المنصة
  final String platform;

  /// Is physical device (not emulator) | هل جهاز حقيقي
  final bool isPhysicalDevice;

  const DeviceInfo({
    required this.deviceId,
    this.deviceName,
    this.model,
    this.os,
    this.osVersion,
    this.appVersion,
    required this.platform,
    this.isPhysicalDevice = true,
  });

  factory DeviceInfo.fromJson(Map<String, dynamic> json) {
    return DeviceInfo(
      deviceId: json['device_id'] as String,
      deviceName: json['device_name'] as String?,
      model: json['model'] as String?,
      os: json['os'] as String?,
      osVersion: json['os_version'] as String?,
      appVersion: json['app_version'] as String?,
      platform: json['platform'] as String? ?? 'unknown',
      isPhysicalDevice: json['is_physical_device'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'device_id': deviceId,
      'device_name': deviceName,
      'model': model,
      'os': os,
      'os_version': osVersion,
      'app_version': appVersion,
      'platform': platform,
      'is_physical_device': isPhysicalDevice,
    };
  }
}

// =============================================================================
// Audit Log Entry
// سجل التدقيق
// =============================================================================

/// Access audit log entry
/// سجل تدقيق الوصول
@immutable
class IAMAuditEntry {
  /// Unique entry ID | معرف فريد للسجل
  final String id;

  /// User ID | معرف المستخدم
  final String userId;

  /// Tenant ID | معرف المستأجر
  final String tenantId;

  /// Action performed | الإجراء المنفذ
  final IAMAuditAction action;

  /// Resource type accessed | نوع المورد
  final String? resourceType;

  /// Resource ID accessed | معرف المورد
  final String? resourceId;

  /// Permission checked | الصلاحية المُتحقق منها
  final String? permission;

  /// Whether access was granted | هل تم منح الوصول
  final bool granted;

  /// Reason for denial (if applicable) | سبب الرفض
  final String? denialReason;

  /// Additional details | تفاصيل إضافية
  final Map<String, dynamic>? details;

  /// IP address | عنوان IP
  final String? ipAddress;

  /// Device ID | معرف الجهاز
  final String? deviceId;

  /// Timestamp | الطابع الزمني
  final DateTime timestamp;

  const IAMAuditEntry({
    required this.id,
    required this.userId,
    required this.tenantId,
    required this.action,
    this.resourceType,
    this.resourceId,
    this.permission,
    required this.granted,
    this.denialReason,
    this.details,
    this.ipAddress,
    this.deviceId,
    required this.timestamp,
  });

  factory IAMAuditEntry.fromJson(Map<String, dynamic> json) {
    return IAMAuditEntry(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      tenantId: json['tenant_id'] as String,
      action: IAMAuditAction.values.firstWhere(
        (a) => a.name == json['action'],
        orElse: () => IAMAuditAction.accessCheck,
      ),
      resourceType: json['resource_type'] as String?,
      resourceId: json['resource_id'] as String?,
      permission: json['permission'] as String?,
      granted: json['granted'] as bool? ?? false,
      denialReason: json['denial_reason'] as String?,
      details: json['details'] as Map<String, dynamic>?,
      ipAddress: json['ip_address'] as String?,
      deviceId: json['device_id'] as String?,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'tenant_id': tenantId,
      'action': action.name,
      'resource_type': resourceType,
      'resource_id': resourceId,
      'permission': permission,
      'granted': granted,
      'denial_reason': denialReason,
      'details': details,
      'ip_address': ipAddress,
      'device_id': deviceId,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}

/// IAM audit actions
/// إجراءات تدقيق IAM
enum IAMAuditAction {
  /// Login attempt | محاولة تسجيل الدخول
  login,

  /// Logout | تسجيل الخروج
  logout,

  /// Token refresh | تحديث التوكن
  tokenRefresh,

  /// Permission check | فحص الصلاحية
  accessCheck,

  /// Resource access | الوصول للمورد
  resourceAccess,

  /// Role change | تغيير الدور
  roleChange,

  /// Tenant switch | تبديل المستأجر
  tenantSwitch,

  /// Session created | إنشاء جلسة
  sessionCreated,

  /// Session expired | انتهاء الجلسة
  sessionExpired,

  /// Session terminated | إنهاء الجلسة
  sessionTerminated,

  /// MFA enabled | تفعيل المصادقة الثنائية
  mfaEnabled,

  /// MFA disabled | تعطيل المصادقة الثنائية
  mfaDisabled,

  /// MFA verified | التحقق من المصادقة الثنائية
  mfaVerified,

  /// Password changed | تغيير كلمة المرور
  passwordChanged,

  /// Account locked | قفل الحساب
  accountLocked,

  /// Account unlocked | فتح قفل الحساب
  accountUnlocked,
}

// =============================================================================
// Tenant Model
// نموذج المستأجر
// =============================================================================

/// Tenant information
/// معلومات المستأجر
@immutable
class Tenant {
  /// Tenant ID | معرف المستأجر
  final String id;

  /// Tenant name | اسم المستأجر
  final String name;

  /// Tenant name in Arabic | اسم المستأجر بالعربية
  final String? nameAr;

  /// Tenant slug/code | رمز المستأجر
  final String slug;

  /// Logo URL | رابط الشعار
  final String? logoUrl;

  /// Subscription plan | خطة الاشتراك
  final String plan;

  /// Whether tenant is active | هل المستأجر نشط
  final bool isActive;

  /// Tenant settings | إعدادات المستأجر
  final Map<String, dynamic> settings;

  /// Created timestamp | تاريخ الإنشاء
  final DateTime createdAt;

  const Tenant({
    required this.id,
    required this.name,
    this.nameAr,
    required this.slug,
    this.logoUrl,
    this.plan = 'starter',
    this.isActive = true,
    this.settings = const {},
    required this.createdAt,
  });

  /// Get localized name
  String getName({String locale = 'ar'}) {
    if (locale == 'ar' && nameAr != null) {
      return nameAr!;
    }
    return name;
  }

  factory Tenant.fromJson(Map<String, dynamic> json) {
    return Tenant(
      id: json['id'] as String,
      name: json['name'] as String,
      nameAr: json['name_ar'] as String?,
      slug: json['slug'] as String,
      logoUrl: json['logo_url'] as String?,
      plan: json['plan'] as String? ?? 'starter',
      isActive: json['is_active'] as bool? ?? true,
      settings: (json['settings'] as Map<String, dynamic>?) ?? {},
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'name_ar': nameAr,
      'slug': slug,
      'logo_url': logoUrl,
      'plan': plan,
      'is_active': isActive,
      'settings': settings,
      'created_at': createdAt.toIso8601String(),
    };
  }
}
