import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/auth/auth_service.dart';

void main() {
  // ===========================================================================
  // AuthStatus enum
  // ===========================================================================
  group('AuthStatus', () {
    test('has all expected values', () {
      expect(AuthStatus.values, hasLength(5));
      expect(
        AuthStatus.values,
        containsAll([
          AuthStatus.initial,
          AuthStatus.authenticated,
          AuthStatus.unauthenticated,
          AuthStatus.loading,
          AuthStatus.sessionExpired,
        ]),
      );
    });
  });

  // ===========================================================================
  // AuthState - default values
  // ===========================================================================
  group('AuthState default values', () {
    test('should have initial status by default', () {
      const state = AuthState();
      expect(state.status, AuthStatus.initial);
    });

    test('should have null user by default', () {
      const state = AuthState();
      expect(state.user, isNull);
    });

    test('should have null accessToken by default', () {
      const state = AuthState();
      expect(state.accessToken, isNull);
    });

    test('should have null error by default', () {
      const state = AuthState();
      expect(state.error, isNull);
    });

    test('should not be authenticated by default', () {
      const state = AuthState();
      expect(state.isAuthenticated, isFalse);
    });

    test('should not be loading by default', () {
      const state = AuthState();
      expect(state.isLoading, isFalse);
    });

    test('should not be session expired by default', () {
      const state = AuthState();
      expect(state.isSessionExpired, isFalse);
    });
  });

  // ===========================================================================
  // AuthState - copyWith
  // ===========================================================================
  group('AuthState.copyWith', () {
    test('should update status', () {
      const original = AuthState();
      final updated = original.copyWith(status: AuthStatus.loading);
      expect(updated.status, AuthStatus.loading);
    });

    test('should update user', () {
      const original = AuthState();
      final updated = original.copyWith(
        user: const User(
          id: 'user_001',
          email: 'farmer@sahool.app',
          name: 'Ahmed',
          role: 'farmer',
          tenantId: 'tenant_001',
        ),
      );
      expect(updated.user, isNotNull);
      expect(updated.user!.id, 'user_001');
    });

    test('should update accessToken', () {
      const original = AuthState();
      final updated = original.copyWith(accessToken: 'jwt_token_abc');
      expect(updated.accessToken, 'jwt_token_abc');
    });

    test('should update error', () {
      const original = AuthState();
      final updated = original.copyWith(error: 'Login failed');
      expect(updated.error, 'Login failed');
    });

    test('should clear error when passing null explicitly', () {
      const state = AuthState(error: 'Some error');
      // copyWith sets error to the provided value (null clears it)
      final updated = state.copyWith();
      // When error param is not provided, copyWith passes null for error
      // Based on source: error: error (the parameter, which defaults to null)
      expect(updated.error, isNull);
    });

    test('should preserve unchanged fields', () {
      const user = User(
        id: 'u1',
        email: 'test@sahool.app',
        name: 'Test',
        role: 'farmer',
        tenantId: 't1',
      );
      const original = AuthState(
        status: AuthStatus.authenticated,
        user: user,
        accessToken: 'token_123',
      );

      final updated = original.copyWith(error: 'network error');

      expect(updated.status, AuthStatus.authenticated);
      expect(updated.user?.id, 'u1');
      expect(updated.accessToken, 'token_123');
      expect(updated.error, 'network error');
    });

    test('clearToken should set accessToken to null', () {
      const state = AuthState(
        status: AuthStatus.authenticated,
        accessToken: 'some_token_value',
      );

      final cleared = state.copyWith(clearToken: true);
      expect(cleared.accessToken, isNull);
    });

    test('clearToken should set accessToken to null even when new token provided', () {
      const state = AuthState(accessToken: 'old_token');

      // When clearToken is true, the token is set to null regardless
      final cleared = state.copyWith(
        clearToken: true,
        accessToken: 'new_token',
      );
      expect(cleared.accessToken, isNull);
    });

    test('clearUser should set user to null', () {
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

    test('should update multiple fields at once', () {
      const original = AuthState();
      final updated = original.copyWith(
        status: AuthStatus.authenticated,
        user: const User(
          id: 'u2',
          email: 'admin@sahool.app',
          name: 'Admin',
          role: 'admin',
          tenantId: 'tenant_002',
        ),
        accessToken: 'jwt_xyz',
      );

      expect(updated.status, AuthStatus.authenticated);
      expect(updated.user!.email, 'admin@sahool.app');
      expect(updated.accessToken, 'jwt_xyz');
      expect(updated.error, isNull);
    });
  });

  // ===========================================================================
  // AuthState - isAuthenticated
  // ===========================================================================
  group('AuthState.isAuthenticated', () {
    test('returns true only when status is authenticated', () {
      const state = AuthState(status: AuthStatus.authenticated);
      expect(state.isAuthenticated, isTrue);
    });

    test('returns false for initial status', () {
      const state = AuthState(status: AuthStatus.initial);
      expect(state.isAuthenticated, isFalse);
    });

    test('returns false for unauthenticated status', () {
      const state = AuthState(status: AuthStatus.unauthenticated);
      expect(state.isAuthenticated, isFalse);
    });

    test('returns false for loading status', () {
      const state = AuthState(status: AuthStatus.loading);
      expect(state.isAuthenticated, isFalse);
    });

    test('returns false for sessionExpired status', () {
      const state = AuthState(status: AuthStatus.sessionExpired);
      expect(state.isAuthenticated, isFalse);
    });
  });

  // ===========================================================================
  // AuthState - isLoading
  // ===========================================================================
  group('AuthState.isLoading', () {
    test('returns true only when status is loading', () {
      const state = AuthState(status: AuthStatus.loading);
      expect(state.isLoading, isTrue);
    });

    test('returns false for authenticated status', () {
      const state = AuthState(status: AuthStatus.authenticated);
      expect(state.isLoading, isFalse);
    });

    test('returns false for initial status', () {
      const state = AuthState(status: AuthStatus.initial);
      expect(state.isLoading, isFalse);
    });

    test('returns false for unauthenticated status', () {
      const state = AuthState(status: AuthStatus.unauthenticated);
      expect(state.isLoading, isFalse);
    });

    test('returns false for sessionExpired status', () {
      const state = AuthState(status: AuthStatus.sessionExpired);
      expect(state.isLoading, isFalse);
    });
  });

  // ===========================================================================
  // AuthState - isSessionExpired
  // ===========================================================================
  group('AuthState.isSessionExpired', () {
    test('returns true only when status is sessionExpired', () {
      const state = AuthState(status: AuthStatus.sessionExpired);
      expect(state.isSessionExpired, isTrue);
    });

    test('returns false for authenticated status', () {
      const state = AuthState(status: AuthStatus.authenticated);
      expect(state.isSessionExpired, isFalse);
    });

    test('returns false for initial status', () {
      const state = AuthState(status: AuthStatus.initial);
      expect(state.isSessionExpired, isFalse);
    });
  });

  // ===========================================================================
  // User construction
  // ===========================================================================
  group('User', () {
    test('should construct with all required fields', () {
      const user = User(
        id: 'user_001',
        email: 'farmer@sahool.app',
        name: 'Ahmed Al-Rashid',
        role: 'farmer',
        tenantId: 'tenant_001',
      );

      expect(user.id, 'user_001');
      expect(user.email, 'farmer@sahool.app');
      expect(user.name, 'Ahmed Al-Rashid');
      expect(user.role, 'farmer');
      expect(user.tenantId, 'tenant_001');
    });

    test('should have null optional fields when not provided', () {
      const user = User(
        id: 'user_001',
        email: 'test@sahool.app',
        name: 'Test',
        role: 'viewer',
        tenantId: 'tenant_001',
      );

      expect(user.phone, isNull);
      expect(user.avatarUrl, isNull);
    });

    test('should construct with all optional fields', () {
      const user = User(
        id: 'user_002',
        email: 'admin@sahool.app',
        name: 'Admin User',
        role: 'admin',
        tenantId: 'tenant_001',
        phone: '+967771234567',
        avatarUrl: 'https://cdn.sahool.app/avatars/002.png',
      );

      expect(user.phone, '+967771234567');
      expect(user.avatarUrl, 'https://cdn.sahool.app/avatars/002.png');
    });

    test('should support Arabic names', () {
      const user = User(
        id: 'user_003',
        email: 'ahmed@sahool.app',
        name: 'أحمد الرشيد',
        role: 'farmer',
        tenantId: 'tenant_001',
      );

      expect(user.name, 'أحمد الرشيد');
    });

    test('should serialize to JSON and back (round-trip)', () {
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

    test('fromJson should default name to email when name is null', () {
      final json = {
        'id': 'user_004',
        'email': 'noname@sahool.app',
        'name': null,
        'role': 'farmer',
        'tenant_id': 'tenant_001',
      };

      final user = User.fromJson(json);
      expect(user.name, 'noname@sahool.app');
    });

    test('fromJson should default role to viewer when role is null', () {
      final json = {
        'id': 'user_005',
        'email': 'norole@sahool.app',
        'name': 'No Role',
        'tenant_id': 'tenant_001',
      };

      final user = User.fromJson(json);
      expect(user.role, 'viewer');
    });
  });
}
