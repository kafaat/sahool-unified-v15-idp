import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/auth/auth_service.dart';

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
      expect(user.tenantId, 'tenant_001');
      expect(user.phone, isNull);
      expect(user.avatarUrl, isNull);
    });

    test('should create user with optional fields', () {
      const user = User(
        id: 'user_002',
        email: 'admin@sahool.app',
        name: 'Admin',
        role: 'admin',
        tenantId: 'tenant_001',
        phone: '+967771234567',
        avatarUrl: 'https://avatar.example.com/001.png',
      );

      expect(user.phone, '+967771234567');
      expect(user.avatarUrl, 'https://avatar.example.com/001.png');
    });

    test('should serialize to JSON', () {
      const user = User(
        id: 'user_001',
        email: 'test@sahool.app',
        name: 'مستخدم',
        role: 'farmer',
        tenantId: 'tenant_001',
        phone: '+967771234567',
      );

      final json = user.toJson();

      expect(json['id'], 'user_001');
      expect(json['email'], 'test@sahool.app');
      expect(json['name'], 'مستخدم');
      expect(json['role'], 'farmer');
      expect(json['tenant_id'], 'tenant_001');
      expect(json['phone'], '+967771234567');
      expect(json['avatar_url'], isNull);
    });

    test('should deserialize from JSON', () {
      final json = {
        'id': 'user_003',
        'email': 'farmer@sahool.app',
        'name': 'مزارع',
        'role': 'farmer',
        'tenant_id': 'tenant_002',
        'phone': null,
        'avatar_url': null,
      };

      final user = User.fromJson(json);

      expect(user.id, 'user_003');
      expect(user.email, 'farmer@sahool.app');
      expect(user.name, 'مزارع');
      expect(user.role, 'farmer');
      expect(user.tenantId, 'tenant_002');
    });

    test('should round-trip through JSON', () {
      const original = User(
        id: 'user_rt',
        email: 'rt@sahool.app',
        name: 'Round Trip',
        role: 'admin',
        tenantId: 'tenant_rt',
        phone: '+967771111111',
        avatarUrl: 'https://example.com/avatar.png',
      );

      final json = original.toJson();
      final restored = User.fromJson(json);

      expect(restored.id, original.id);
      expect(restored.email, original.email);
      expect(restored.name, original.name);
      expect(restored.role, original.role);
      expect(restored.tenantId, original.tenantId);
      expect(restored.phone, original.phone);
      expect(restored.avatarUrl, original.avatarUrl);
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
