/// SAHOOL Identity and Access Management (IAM) Module
/// وحدة إدارة الهوية والوصول لسهول
///
/// Comprehensive IAM system providing:
/// - User identity management | إدارة هوية المستخدم
/// - Access token handling | معالجة توكنات الوصول
/// - Permission checking | فحص الصلاحيات
/// - Multi-tenant support | دعم متعدد المستأجرين
/// - Session management | إدارة الجلسات
/// - OAuth 2.0 / OIDC support | دعم OAuth 2.0 / OIDC
/// - Social login (Google, Apple) | تسجيل الدخول الاجتماعي
/// - Access Control Lists (ACL) | قوائم التحكم في الوصول
/// - Resource-based permissions | صلاحيات قائمة على الموارد
/// - Field-level security | أمان على مستوى الحقل
/// - Audit logging | تسجيل التدقيق
/// - Bilingual support (Arabic/English) | دعم ثنائي اللغة
///
/// ## Quick Start
///
/// ```dart
/// // Import the IAM module
/// import 'package:sahool_field_app/core/iam/iam.dart';
///
/// // In a Riverpod widget, check authentication
/// class MyWidget extends ConsumerWidget {
///   @override
///   Widget build(BuildContext context, WidgetRef ref) {
///     final isAuth = ref.watch(isAuthenticatedProvider);
///     final user = ref.watch(currentUserProvider);
///
///     if (!isAuth) {
///       return LoginScreen();
///     }
///
///     return Text('Welcome ${user?.displayName}');
///   }
/// }
///
/// // Check permissions
/// if (ref.can('fieldops:field.create')) {
///   // Show create button
/// }
///
/// // Or using enum
/// if (ref.canDo(IAMPermission.fieldCreate)) {
///   // Show create button
/// }
///
/// // Check resource access
/// final canEdit = ref.watch(canAccessResourceProvider(
///   ResourceAccessRequest(
///     resourceType: ResourceType.field,
///     resourceId: 'field-123',
///     action: AccessAction.update,
///   ),
/// ));
/// ```
///
/// ## Features
///
/// ### Authentication
/// - Local username/password
/// - SAHOOL backend authentication
/// - OAuth 2.0 / OpenID Connect
/// - Google Sign-In (preparation)
/// - Apple Sign-In (preparation)
/// - MFA support
///
/// ### Authorization
/// - Role-Based Access Control (RBAC)
/// - Attribute-Based Access Control (ABAC)
/// - Resource-based permissions
/// - Field-level security
/// - Tenant isolation
///
/// ### Session Management
/// - Secure session storage
/// - Token refresh
/// - Session locking
/// - Offline capability tokens
///
/// ### Audit
/// - Access logging
/// - Permission checks logging
/// - Session events logging

library;

// Models
export 'models/iam_models.dart';

// Core Services
export 'iam_service.dart';
export 'permission_manager.dart';
export 'identity_provider.dart';
export 'access_control.dart';

// Riverpod Providers
export 'iam_providers.dart';
