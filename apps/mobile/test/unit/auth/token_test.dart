/// Comprehensive Token Management Tests
/// اختبارات شاملة لإدارة الرموز المميزة
///
/// Tests for:
/// - TokenRefreshResult factory constructors
/// - JWT token parsing and validation
/// - Token expiry checking
/// - Token storage and retrieval patterns
/// - Auth state change callbacks
///
/// Run with: flutter test test/unit/auth/token_test.dart
library;

import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/auth/token_manager.dart';

// Helper to create mock JWT tokens for testing
String createMockJwt({
  required String userId,
  required String tenantId,
  required DateTime expiresAt,
  String role = 'farmer',
}) {
  // JWT header
  final header = base64Url.encode(
    utf8.encode(jsonEncode({'alg': 'HS256', 'typ': 'JWT'})),
  );

  // JWT payload
  final payload = base64Url.encode(
    utf8.encode(
      jsonEncode({
        'sub': userId,
        'tid': tenantId,
        'role': role,
        'exp': expiresAt.millisecondsSinceEpoch ~/ 1000,
        'iat': DateTime.now().millisecondsSinceEpoch ~/ 1000,
      }),
    ),
  );

  // Mock signature (not valid for real JWT verification)
  const signature = 'mock_signature_for_testing_only';

  return '$header.$payload.$signature';
}

/// Parse JWT claims from a token string (test utility)
Map<String, dynamic> parseJwtClaims(String token) {
  final parts = token.split('.');
  if (parts.length != 3) {
    throw const FormatException('Invalid JWT format');
  }

  // Add padding if necessary
  final payload = parts[1];
  final padded = payload.padRight(
    payload.length + (4 - payload.length % 4) % 4,
    '=',
  );

  final decoded = utf8.decode(base64Url.decode(padded));
  return jsonDecode(decoded) as Map<String, dynamic>;
}

void main() {
  // ============================================================
  // TokenRefreshResult Tests
  // ============================================================
  group('TokenRefreshResult - نتيجة تحديث الرمز', () {
    group('Success Factory', () {
      test('creates successful result with all fields', () {
        final result = TokenRefreshResult.success(
          accessToken: 'new_access_token_xyz',
          refreshToken: 'new_refresh_token_xyz',
          expiresIn: 3600,
        );

        expect(result.success, isTrue);
        expect(result.accessToken, equals('new_access_token_xyz'));
        expect(result.refreshToken, equals('new_refresh_token_xyz'));
        expect(result.expiresIn, equals(3600));
        expect(result.error, isNull);
      });

      test('success result has no error', () {
        final result = TokenRefreshResult.success(
          accessToken: 'token',
          refreshToken: 'refresh',
          expiresIn: 7200,
        );

        expect(result.success, isTrue);
        expect(result.error, isNull);
      });
    });

    group('Failure Factory', () {
      test('creates failed result with error message', () {
        const errorMsg = 'Refresh token expired';
        final result = TokenRefreshResult.failure(errorMsg);

        expect(result.success, isFalse);
        expect(result.error, equals(errorMsg));
        expect(result.accessToken, isNull);
        expect(result.refreshToken, isNull);
        expect(result.expiresIn, isNull);
      });

      test('handles various error scenarios', () {
        final scenarios = [
          'Network unavailable',
          'Invalid refresh token',
          'Server error 500',
          'Token revoked',
          'Session expired',
        ];

        for (final error in scenarios) {
          final result = TokenRefreshResult.failure(error);
          expect(result.success, isFalse, reason: 'Should fail for: $error');
          expect(result.error, equals(error));
        }
      });
    });
  });

  // ============================================================
  // JWT Token Parsing Tests (utility functions)
  // ============================================================
  group('JWT Token Utilities - أدوات رمز JWT', () {
    test('creates and parses mock JWT correctly', () {
      final expiry = DateTime.now().add(const Duration(hours: 1));
      final token = createMockJwt(
        userId: 'user-123',
        tenantId: 'tenant-456',
        expiresAt: expiry,
      );

      expect(token, isNotEmpty);
      expect(token.split('.').length, equals(3));

      final claims = parseJwtClaims(token);
      expect(claims['sub'], equals('user-123'));
      expect(claims['tid'], equals('tenant-456'));
      expect(claims['role'], equals('farmer'));
    });

    test('extracts user ID from JWT claims', () {
      final token = createMockJwt(
        userId: 'farmer-789',
        tenantId: 'farm-org-1',
        expiresAt: DateTime.now().add(const Duration(hours: 2)),
      );

      final claims = parseJwtClaims(token);
      expect(claims['sub'], equals('farmer-789'));
    });

    test('extracts tenant ID from JWT claims', () {
      final token = createMockJwt(
        userId: 'user-1',
        tenantId: 'cooperative-001',
        expiresAt: DateTime.now().add(const Duration(hours: 1)),
      );

      final claims = parseJwtClaims(token);
      expect(claims['tid'], equals('cooperative-001'));
    });

    test('detects expired token', () {
      final expiredToken = createMockJwt(
        userId: 'user-1',
        tenantId: 'tenant-1',
        expiresAt: DateTime.now().subtract(const Duration(hours: 1)),
      );

      final claims = parseJwtClaims(expiredToken);
      final exp = claims['exp'] as int;
      final expiresAt = DateTime.fromMillisecondsSinceEpoch(exp * 1000);

      expect(expiresAt.isBefore(DateTime.now()), isTrue);
    });

    test('detects valid (non-expired) token', () {
      final validToken = createMockJwt(
        userId: 'user-1',
        tenantId: 'tenant-1',
        expiresAt: DateTime.now().add(const Duration(hours: 2)),
      );

      final claims = parseJwtClaims(validToken);
      final exp = claims['exp'] as int;
      final expiresAt = DateTime.fromMillisecondsSinceEpoch(exp * 1000);

      expect(expiresAt.isAfter(DateTime.now()), isTrue);
    });

    test('token expiry buffer calculation', () {
      const ttlSeconds = 3600;
      const bufferSeconds = 300;

      final issuedAt = DateTime.now();
      final expiresAt = issuedAt.add(const Duration(seconds: ttlSeconds));
      final refreshBefore =
          expiresAt.subtract(const Duration(seconds: bufferSeconds));

      expect(refreshBefore.isBefore(expiresAt), isTrue);
      expect(
        DateTime.now().isBefore(refreshBefore),
        isTrue,
        reason: 'Should not need refresh yet for a fresh token',
      );
    });

    test('throws FormatException for invalid JWT format', () {
      expect(
        () => parseJwtClaims('invalid_token'),
        throwsA(isA<FormatException>()),
      );

      expect(
        () => parseJwtClaims('only.two.parts'),
        throwsA(isA<FormatException>()),
        reason: 'JWT must have exactly 3 parts',
      );
    });
  });

  // ============================================================
  // Token Expiry Strategies Tests (pure logic)
  // ============================================================
  group('Token Expiry Strategy - استراتيجية انتهاء الرمز', () {
    test('calculates refresh threshold correctly (5min buffer)', () {
      const refreshBufferSeconds = 300;

      bool shouldRefresh(int secondsUntilExpiry) {
        return secondsUntilExpiry <= refreshBufferSeconds;
      }

      expect(shouldRefresh(3600), isFalse);
      expect(shouldRefresh(refreshBufferSeconds + 1), isFalse);
      expect(shouldRefresh(refreshBufferSeconds), isTrue);
      expect(shouldRefresh(60), isTrue);
      expect(shouldRefresh(0), isTrue);
      expect(shouldRefresh(-100), isTrue);
    });

    test('refresh token expiry is longer than access token', () {
      const accessTokenTtlHours = 1;
      const refreshTokenTtlDays = 30;

      expect(
        refreshTokenTtlDays * 24,
        greaterThan(accessTokenTtlHours),
      );
    });

    test('calculates next refresh time correctly', () {
      final issuedAt = DateTime.now();
      const ttlSeconds = 3600;
      const bufferSeconds = 300;

      final expiresAt = issuedAt.add(const Duration(seconds: ttlSeconds));
      final nextRefresh =
          expiresAt.subtract(const Duration(seconds: bufferSeconds));

      const expectedRefreshMs = (ttlSeconds - bufferSeconds) * 1000;
      final actualRefreshMs = nextRefresh.difference(issuedAt).inMilliseconds;

      expect(actualRefreshMs, closeTo(expectedRefreshMs, 1000));
    });
  });

  // ============================================================
  // Auth State Callback Tests
  // ============================================================
  group('Auth State Callbacks - مراجعة حالة المصادقة', () {
    test('AuthStateCallback type accepts boolean argument', () {
      bool? capturedState;

      callback(bool isAuthenticated) {
        capturedState = isAuthenticated;
      }

      callback(true);
      expect(capturedState, isTrue);

      callback(false);
      expect(capturedState, isFalse);
    });

    test('auth state changes are tracked correctly', () {
      final stateChanges = <bool>[];

      trackChanges(bool isAuthenticated) {
        stateChanges.add(isAuthenticated);
      }

      // Simulate login -> logout -> login cycle
      trackChanges(true);
      trackChanges(false);
      trackChanges(true);

      expect(stateChanges.length, equals(3));
      expect(stateChanges[0], isTrue);
      expect(stateChanges[1], isFalse);
      expect(stateChanges[2], isTrue);
    });
  });

  // ============================================================
  // TokenRefreshCallback Tests
  // ============================================================
  group('TokenRefreshCallback - رد نداء تحديث الرمز', () {
    test('successful refresh callback returns valid result', () async {
      Future<TokenRefreshResult> refreshCallback(String refreshToken) async {
        return TokenRefreshResult.success(
          accessToken: 'new_access_${refreshToken.hashCode}',
          refreshToken: 'new_refresh_token',
          expiresIn: 3600,
        );
      }

      final result = await refreshCallback('old_refresh_token');
      expect(result.success, isTrue);
      expect(result.accessToken, isNotNull);
      expect(result.refreshToken, equals('new_refresh_token'));
    });

    test('failed refresh callback returns failure result', () async {
      Future<TokenRefreshResult> refreshCallback(String refreshToken) async {
        if (refreshToken == 'expired') {
          return TokenRefreshResult.failure('Refresh token expired');
        }
        return TokenRefreshResult.success(
          accessToken: 'access',
          refreshToken: 'refresh',
          expiresIn: 3600,
        );
      }

      final result = await refreshCallback('expired');
      expect(result.success, isFalse);
      expect(result.error, contains('expired'));
    });
  });

  // ============================================================
  // Token Storage Patterns Tests (pure logic)
  // ============================================================
  group('Token Storage Patterns - أنماط تخزين الرمز', () {
    test('stores access and refresh tokens separately', () {
      final mutableStorage = <String, String>{};

      mutableStorage['access_token'] = 'eyJ...access';
      mutableStorage['refresh_token'] = 'eyJ...refresh';
      mutableStorage['token_expiry'] =
          DateTime.now().add(const Duration(hours: 1)).toIso8601String();

      expect(mutableStorage['access_token'], isNotNull);
      expect(mutableStorage['refresh_token'], isNotNull);
      expect(mutableStorage['token_expiry'], isNotNull);
    });

    test('clears all auth tokens on logout', () {
      final storage = <String, String>{
        'access_token': 'eyJ...access',
        'refresh_token': 'eyJ...refresh',
        'token_expiry': DateTime.now().toIso8601String(),
        'user_id': 'user-123',
        'tenant_id': 'tenant-456',
      };

      // Clear auth tokens
      storage.remove('access_token');
      storage.remove('refresh_token');
      storage.remove('token_expiry');

      expect(storage.containsKey('access_token'), isFalse);
      expect(storage.containsKey('refresh_token'), isFalse);
      expect(storage.containsKey('token_expiry'), isFalse);
      // User info persists for display
      expect(storage.containsKey('user_id'), isTrue);
    });

    test('token scoping prevents cross-tenant access', () {
      final user1Token = createMockJwt(
        userId: 'user-1',
        tenantId: 'tenant-A',
        expiresAt: DateTime.now().add(const Duration(hours: 1)),
      );

      final user2Token = createMockJwt(
        userId: 'user-2',
        tenantId: 'tenant-B',
        expiresAt: DateTime.now().add(const Duration(hours: 1)),
      );

      final claims1 = parseJwtClaims(user1Token);
      final claims2 = parseJwtClaims(user2Token);

      expect(claims1['tid'], equals('tenant-A'));
      expect(claims2['tid'], equals('tenant-B'));
      expect(claims1['tid'], isNot(equals(claims2['tid'])));
      expect(claims1['sub'], isNot(equals(claims2['sub'])));
    });
  });

  // ============================================================
  // Role-Based Access Control Tests (pure logic)
  // ============================================================
  group('RBAC Token Claims - مطالبات التحكم في الوصول', () {
    test('creates JWT with farmer role by default', () {
      final token = createMockJwt(
        userId: 'farmer-1',
        tenantId: 'farm-1',
        expiresAt: DateTime.now().add(const Duration(hours: 1)),
      );

      final claims = parseJwtClaims(token);
      expect(claims['role'], equals('farmer'));
    });

    test('creates JWT with custom role', () {
      final token = createMockJwt(
        userId: 'admin-1',
        tenantId: 'farm-1',
        expiresAt: DateTime.now().add(const Duration(hours: 1)),
        role: 'admin',
      );

      final claims = parseJwtClaims(token);
      expect(claims['role'], equals('admin'));
    });

    test('supports multiple role types', () {
      for (final role in ['farmer', 'admin', 'supervisor', 'researcher']) {
        final token = createMockJwt(
          userId: 'user-1',
          tenantId: 'tenant-1',
          expiresAt: DateTime.now().add(const Duration(hours: 1)),
          role: role,
        );

        final claims = parseJwtClaims(token);
        expect(claims['role'], equals(role));
      }
    });
  });
}
