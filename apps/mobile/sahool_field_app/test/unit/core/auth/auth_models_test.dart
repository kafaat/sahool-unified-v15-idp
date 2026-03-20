import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/auth/auth_service.dart';
import 'package:sahool_field_app/core/auth/permission_service.dart';

void main() {
  group('User', () {
    test('should create user with required fields', () {
      const user = User(
        id: 'user_001',
        email: 'test@sahool.app',
        name: 'مستخدم تجريبي',
        role: 'farmer',
        tenantId: 'tenant_001',
      );

      expect(user.id, 'user_001');
      expect(user.email, 'test@sahool.app');
      expect(user.name, 'مستخدم تجريبي');
      expect(user.role, 'farmer');
      expect(user.status, 'active');
      expect(user.tenantId, 'tenant_001');
      expect(user.phone, isNull);
      expect(user.avatarUrl, isNull);
      expect(user.emailVerified, false);
      expect(user.phoneVerified, false);
    });

    test('should create user with optional fields', () {
      const user = User(
        id: 'user_002',
        email: 'admin@sahool.app',
        name: 'Admin',
        role: 'admin',
        status: 'active',
        tenantId: 'tenant_001',
        phone: '+967771234567',
        firstName: 'Admin',
        lastName: 'User',
        nameAr: 'مسؤول',
        avatarUrl: 'https://avatar.example.com/001.png',
        emailVerified: true,
        phoneVerified: true,
      );

      expect(user.phone, '+967771234567');
      expect(user.avatarUrl, 'https://avatar.example.com/001.png');
      expect(user.firstName, 'Admin');
      expect(user.lastName, 'User');
      expect(user.nameAr, 'مسؤول');
      expect(user.emailVerified, true);
      expect(user.phoneVerified, true);
    });

    test('should serialize to JSON', () {
      const user = User(
        id: 'user_001',
        email: 'test@sahool.app',
        name: 'مستخدم',
        role: 'farmer',
        status: 'active',
        tenantId: 'tenant_001',
        phone: '+967771234567',
        firstName: 'Test',
        lastName: 'User',
      );

      final json = user.toJson();

      expect(json['id'], 'user_001');
      expect(json['email'], 'test@sahool.app');
      expect(json['name'], 'مستخدم');
      expect(json['role'], 'farmer');
      expect(json['status'], 'active');
      expect(json['tenant_id'], 'tenant_001');
      expect(json['phone'], '+967771234567');
      expect(json['first_name'], 'Test');
      expect(json['last_name'], 'User');
      expect(json['avatar_url'], isNull);
      expect(json['email_verified'], false);
      expect(json['phone_verified'], false);
    });

    test('should deserialize from JSON', () {
      final json = {
        'id': 'user_003',
        'email': 'farmer@sahool.app',
        'name': 'مزارع',
        'role': 'farmer',
        'status': 'active',
        'tenant_id': 'tenant_002',
        'first_name': 'أحمد',
        'last_name': 'محمد',
        'name_ar': 'أحمد محمد',
        'phone': null,
        'avatar_url': null,
        'email_verified': true,
        'phone_verified': false,
      };

      final user = User.fromJson(json);

      expect(user.id, 'user_003');
      expect(user.email, 'farmer@sahool.app');
      expect(user.name, 'مزارع');
      expect(user.role, 'farmer');
      expect(user.status, 'active');
      expect(user.tenantId, 'tenant_002');
      expect(user.firstName, 'أحمد');
      expect(user.lastName, 'محمد');
      expect(user.nameAr, 'أحمد محمد');
      expect(user.emailVerified, true);
      expect(user.phoneVerified, false);
    });

    test('should handle uppercase role from backend', () {
      final json = {
        'id': 'user_004',
        'email': 'admin@sahool.app',
        'name': 'Admin',
        'role': 'FARMER',
        'status': 'ACTIVE',
        'tenant_id': 'tenant_001',
      };

      final user = User.fromJson(json);

      expect(user.role, 'farmer');
      expect(user.status, 'active');
    });

    test('should build name from firstName/lastName when name is absent', () {
      final json = {
        'id': 'user_005',
        'email': 'test@sahool.app',
        'first_name': 'أحمد',
        'last_name': 'العلي',
        'role': 'farmer',
        'tenant_id': 'tenant_001',
      };

      final user = User.fromJson(json);

      expect(user.name, 'أحمد العلي');
    });

    test('should round-trip through JSON', () {
      const original = User(
        id: 'user_rt',
        email: 'rt@sahool.app',
        name: 'Round Trip',
        role: 'admin',
        status: 'active',
        tenantId: 'tenant_rt',
        phone: '+967771111111',
        firstName: 'Round',
        lastName: 'Trip',
        nameAr: 'رحلة ذهاب وإياب',
        avatarUrl: 'https://example.com/avatar.png',
        emailVerified: true,
        phoneVerified: true,
      );

      final json = original.toJson();
      final restored = User.fromJson(json);

      expect(restored.id, original.id);
      expect(restored.email, original.email);
      expect(restored.name, original.name);
      expect(restored.role, original.role);
      expect(restored.status, original.status);
      expect(restored.tenantId, original.tenantId);
      expect(restored.phone, original.phone);
      expect(restored.firstName, original.firstName);
      expect(restored.lastName, original.lastName);
      expect(restored.nameAr, original.nameAr);
      expect(restored.avatarUrl, original.avatarUrl);
      expect(restored.emailVerified, original.emailVerified);
      expect(restored.phoneVerified, original.phoneVerified);
    });
  });

  group('UserStatus', () {
    test('should parse from string', () {
      expect(UserStatus.fromString('active'), UserStatus.active);
      expect(UserStatus.fromString('ACTIVE'), UserStatus.active);
      expect(UserStatus.fromString('suspended'), UserStatus.suspended);
      expect(UserStatus.fromString('INACTIVE'), UserStatus.inactive);
      expect(UserStatus.fromString('pending'), UserStatus.pending);
    });

    test('should default to pending for unknown values', () {
      expect(UserStatus.fromString('unknown'), UserStatus.pending);
    });

    test('canLogin should only be true for active', () {
      expect(UserStatus.active.canLogin, true);
      expect(UserStatus.inactive.canLogin, false);
      expect(UserStatus.suspended.canLogin, false);
      expect(UserStatus.pending.canLogin, false);
    });
  });

  group('UserRole', () {
    test('should parse from string case-insensitively', () {
      expect(UserRole.fromString('farmer'), UserRole.farmer);
      expect(UserRole.fromString('FARMER'), UserRole.farmer);
      expect(UserRole.fromString('Farmer'), UserRole.farmer);
      expect(UserRole.fromString('admin'), UserRole.admin);
      expect(UserRole.fromString('ADMIN'), UserRole.admin);
      expect(UserRole.fromString('viewer'), UserRole.viewer);
      expect(UserRole.fromString('VIEWER'), UserRole.viewer);
      expect(UserRole.fromString('worker'), UserRole.worker);
      expect(UserRole.fromString('WORKER'), UserRole.worker);
      expect(UserRole.fromString('manager'), UserRole.manager);
      expect(UserRole.fromString('MANAGER'), UserRole.manager);
    });

    test('should default to viewer for unknown values', () {
      expect(UserRole.fromString('unknown'), UserRole.viewer);
    });

    test('farmer role should have correct Arabic label', () {
      expect(UserRole.farmer.arabicLabel, 'مزارع');
    });
  });

  group('UserProfile', () {
    test('should deserialize from JSON', () {
      final json = {
        'id': 'profile_001',
        'tenant_id': 'tenant_001',
        'user_id': 'user_001',
        'national_id': '1234567890',
        'date_of_birth': '1990-05-15T00:00:00.000Z',
        'address': '123 Farm Road',
        'city': 'Riyadh',
        'region': 'Central',
        'country': 'SA',
        'avatar_url': 'https://example.com/avatar.png',
      };

      final profile = UserProfile.fromJson(json);

      expect(profile.id, 'profile_001');
      expect(profile.userId, 'user_001');
      expect(profile.nationalId, '1234567890');
      expect(profile.city, 'Riyadh');
      expect(profile.country, 'SA');
    });

    test('should serialize to JSON', () {
      const profile = UserProfile(
        id: 'profile_001',
        tenantId: 'tenant_001',
        userId: 'user_001',
        city: 'Sana\'a',
        country: 'YE',
      );

      final json = profile.toJson();

      expect(json['user_id'], 'user_001');
      expect(json['city'], 'Sana\'a');
      expect(json['country'], 'YE');
      expect(json['national_id'], isNull);
    });
  });

  group('TokenPair', () {
    test('should create token pair', () {
      const pair = TokenPair(
        accessToken: 'access_123',
        refreshToken: 'refresh_456',
        expiresIn: 3600,
      );

      expect(pair.accessToken, 'access_123');
      expect(pair.refreshToken, 'refresh_456');
      expect(pair.expiresIn, 3600);
    });
  });

  group('AuthException', () {
    test('should create with message', () {
      final ex = AuthException('Login failed');
      expect(ex.message, 'Login failed');
      expect(ex.code, isNull);
      expect(ex.toString(), 'Login failed');
    });

    test('should create with message and code', () {
      final ex = AuthException('Token expired', code: 'SESSION_EXPIRED');
      expect(ex.message, 'Token expired');
      expect(ex.code, 'SESSION_EXPIRED');
    });

    test('should support Arabic messages', () {
      final ex = AuthException('انتهت صلاحية الجلسة', code: 'SESSION_EXPIRED');
      expect(ex.message, 'انتهت صلاحية الجلسة');
      expect(ex.toString(), 'انتهت صلاحية الجلسة');
    });
  });

  group('SessionInfo', () {
    test('should have correct defaults', () {
      const session = SessionInfo();

      expect(session.tokenExpiresAt, isNull);
      expect(session.lastActivity, isNull);
      expect(session.sessionStartedAt, isNull);
      expect(session.isBiometricSession, false);
    });

    test('isExpiringSoon should return true when token near expiry', () {
      final session = SessionInfo(
        tokenExpiresAt: DateTime.now().add(const Duration(minutes: 3)),
      );

      // With 5-minute buffer, 3 minutes left = expiring soon
      expect(session.isExpiringSoon(const Duration(minutes: 5)), true);
    });

    test('isExpiringSoon should return false when token has time left', () {
      final session = SessionInfo(
        tokenExpiresAt: DateTime.now().add(const Duration(hours: 1)),
      );

      expect(session.isExpiringSoon(const Duration(minutes: 5)), false);
    });

    test('isExpiringSoon should return true when no expiry set', () {
      const session = SessionInfo();
      expect(session.isExpiringSoon(const Duration(minutes: 5)), true);
    });

    test('isIdleTooLong should return true when idle exceeds max', () {
      final session = SessionInfo(
        lastActivity: DateTime.now().subtract(const Duration(minutes: 40)),
      );

      expect(session.isIdleTooLong(const Duration(minutes: 30)), true);
    });

    test('isIdleTooLong should return false when recently active', () {
      final session = SessionInfo(
        lastActivity: DateTime.now().subtract(const Duration(minutes: 5)),
      );

      expect(session.isIdleTooLong(const Duration(minutes: 30)), false);
    });

    test('isIdleTooLong should return false when no activity recorded', () {
      const session = SessionInfo();
      expect(session.isIdleTooLong(const Duration(minutes: 30)), false);
    });

    test('copyWith should update specified fields', () {
      final original = SessionInfo(
        tokenExpiresAt: DateTime(2026, 1, 1),
        lastActivity: DateTime(2026, 1, 1, 10, 0),
        sessionStartedAt: DateTime(2026, 1, 1, 9, 0),
        isBiometricSession: false,
      );

      final updated = original.copyWith(
        isBiometricSession: true,
        lastActivity: DateTime(2026, 1, 1, 11, 0),
      );

      expect(updated.isBiometricSession, true);
      expect(updated.lastActivity, DateTime(2026, 1, 1, 11, 0));
      // Unchanged fields
      expect(updated.tokenExpiresAt, original.tokenExpiresAt);
      expect(updated.sessionStartedAt, original.sessionStartedAt);
    });
  });

  group('AuthState', () {
    test('should have correct defaults', () {
      const state = AuthState();

      expect(state.status, AuthStatus.initial);
      expect(state.user, isNull);
      expect(state.accessToken, isNull);
      expect(state.error, isNull);
      expect(state.isAuthenticated, false);
      expect(state.isLoading, false);
      expect(state.isSessionExpired, false);
    });

    test('isAuthenticated should return true when authenticated', () {
      const state = AuthState(status: AuthStatus.authenticated);
      expect(state.isAuthenticated, true);
    });

    test('isLoading should return true when loading', () {
      const state = AuthState(status: AuthStatus.loading);
      expect(state.isLoading, true);
    });

    test('isSessionExpired should return true when expired', () {
      const state = AuthState(status: AuthStatus.sessionExpired);
      expect(state.isSessionExpired, true);
    });

    test('copyWith should update fields', () {
      const original = AuthState();

      final updated = original.copyWith(
        status: AuthStatus.authenticated,
        user: const User(
          id: 'u1',
          email: 'test@test.com',
          name: 'Test',
          role: 'farmer',
          tenantId: 't1',
        ),
        accessToken: 'token_123',
      );

      expect(updated.status, AuthStatus.authenticated);
      expect(updated.user?.id, 'u1');
      expect(updated.accessToken, 'token_123');
    });

    test('copyWith clearToken should set token to null', () {
      const state = AuthState(
        status: AuthStatus.authenticated,
        accessToken: 'some_token',
      );

      final cleared = state.copyWith(clearToken: true);
      expect(cleared.accessToken, isNull);
    });

    test('copyWith clearUser should set user to null', () {
      const state = AuthState(
        status: AuthStatus.authenticated,
        user: User(
          id: 'u1',
          email: 'e',
          name: 'n',
          role: 'r',
          tenantId: 't',
        ),
      );

      final cleared = state.copyWith(clearUser: true);
      expect(cleared.user, isNull);
    });
  });

  group('BiometricResult (from biometric_service)', () {
    // Import happens through auth_service re-exports or direct import
    // Testing the BiometricResult factory constructors
  });
}
