import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/auth/secure_storage_service.dart';
import 'package:sahool_field_app/core/security/security_audit_service.dart';

class MockSecureStorageService extends Mock implements SecureStorageService {}

void main() {
  group('SecurityEvent', () {
    test('should serialize to JSON', () {
      final event = SecurityEvent(
        id: 'sec_123',
        timestamp: DateTime(2026, 1, 1, 12, 0),
        category: SecurityEventCategory.biometric,
        severity: SecuritySeverity.info,
        action: 'biometric_success',
        success: true,
        details: 'Test detail',
        metadata: {'type': 'fingerprint'},
      );

      final json = event.toJson();

      expect(json['id'], 'sec_123');
      expect(json['category'], 'biometric');
      expect(json['severity'], 'info');
      expect(json['action'], 'biometric_success');
      expect(json['success'], true);
      expect(json['details'], 'Test detail');
      expect((json['metadata'] as Map<String, dynamic>)['type'], 'fingerprint');
    });

    test('should deserialize from JSON', () {
      final json = {
        'id': 'sec_456',
        'timestamp': '2026-01-01T12:00:00.000',
        'category': 'tokenRefresh',
        'severity': 'warning',
        'action': 'token_refresh_failure',
        'success': false,
        'errorCode': 'NETWORK_ERROR',
      };

      final event = SecurityEvent.fromJson(json);

      expect(event.id, 'sec_456');
      expect(event.category, SecurityEventCategory.tokenRefresh);
      expect(event.severity, SecuritySeverity.warning);
      expect(event.action, 'token_refresh_failure');
      expect(event.success, false);
      expect(event.errorCode, 'NETWORK_ERROR');
    });

    test('should handle unknown category gracefully', () {
      final json = {
        'id': 'sec_789',
        'timestamp': '2026-01-01T12:00:00.000',
        'category': 'unknown_category',
        'severity': 'info',
        'action': 'test',
        'success': true,
      };

      final event = SecurityEvent.fromJson(json);
      // Should default to session
      expect(event.category, SecurityEventCategory.session);
    });

    test('should omit null fields in JSON', () {
      final event = SecurityEvent(
        id: 'sec_100',
        timestamp: DateTime(2026, 1, 1),
        category: SecurityEventCategory.biometric,
        severity: SecuritySeverity.info,
        action: 'test',
        success: true,
      );

      final json = event.toJson();

      expect(json.containsKey('details'), false);
      expect(json.containsKey('errorCode'), false);
      expect(json.containsKey('metadata'), false);
    });

    test('should round-trip through JSON', () {
      final original = SecurityEvent(
        id: 'sec_rt',
        timestamp: DateTime(2026, 2, 15, 10, 30),
        category: SecurityEventCategory.certificatePinning,
        severity: SecuritySeverity.critical,
        action: 'pin_validation_failed',
        success: false,
        errorCode: 'PIN_MISMATCH',
        details: 'Certificate pin does not match',
        metadata: {'domain': 'api.sahool.app'},
      );

      final json = original.toJson();
      final restored = SecurityEvent.fromJson(json);

      expect(restored.id, original.id);
      expect(restored.category, original.category);
      expect(restored.severity, original.severity);
      expect(restored.action, original.action);
      expect(restored.success, original.success);
      expect(restored.errorCode, original.errorCode);
      expect(restored.details, original.details);
    });
  });

  group('SecurityAuditSummary', () {
    test('should compute biometric success rate', () {
      const summary = SecurityAuditSummary(
        biometricAttempts: 10,
        biometricSuccesses: 8,
      );

      expect(summary.biometricSuccessRate, 0.8);
    });

    test('should compute token refresh success rate', () {
      const summary = SecurityAuditSummary(
        tokenRefreshAttempts: 20,
        tokenRefreshSuccesses: 19,
      );

      expect(summary.tokenRefreshSuccessRate, 0.95);
    });

    test('should handle zero attempts gracefully', () {
      const summary = SecurityAuditSummary();

      expect(summary.biometricSuccessRate, 0.0);
      expect(summary.tokenRefreshSuccessRate, 0.0);
    });

    test('should have correct default values', () {
      const summary = SecurityAuditSummary();

      expect(summary.totalEvents, 0);
      expect(summary.biometricAttempts, 0);
      expect(summary.biometricLockouts, 0);
      expect(summary.criticalEvents, 0);
      expect(summary.lastEventTime, isNull);
    });

    test('should compute 100% success rate', () {
      const summary = SecurityAuditSummary(
        biometricAttempts: 5,
        biometricSuccesses: 5,
        tokenRefreshAttempts: 10,
        tokenRefreshSuccesses: 10,
      );

      expect(summary.biometricSuccessRate, 1.0);
      expect(summary.tokenRefreshSuccessRate, 1.0);
    });
  });

  group('SecurityAuditService', () {
    late MockSecureStorageService mockStorage;
    late SecurityAuditService service;

    setUp(() {
      mockStorage = MockSecureStorageService();
      service = SecurityAuditService(secureStorage: mockStorage);
    });

    test('logBiometricAttempt should record success event', () async {
      await service.logBiometricAttempt(
        success: true,
        biometricType: 'fingerprint',
      );

      final events = service.getRecentEvents();
      expect(events.length, 1);
      expect(events[0].category, SecurityEventCategory.biometric);
      expect(events[0].success, true);
      expect(events[0].action, 'biometric_success');
      expect(events[0].severity, SecuritySeverity.info);
    });

    test('logBiometricAttempt should record failure event', () async {
      await service.logBiometricAttempt(
        success: false,
        errorCode: 'FAILED',
        remainingAttempts: 3,
      );

      final events = service.getRecentEvents();
      expect(events.length, 1);
      expect(events[0].success, false);
      expect(events[0].action, 'biometric_failure');
      expect(events[0].severity, SecuritySeverity.warning);
      expect(events[0].errorCode, 'FAILED');
    });

    test('logBiometricAttempt lockout should be critical severity', () async {
      await service.logBiometricAttempt(
        success: false,
        errorCode: 'LOCKED_OUT',
      );

      final events = service.getRecentEvents();
      expect(events[0].severity, SecuritySeverity.critical);
    });

    test('logBiometricLockout should record critical event', () async {
      await service.logBiometricLockout(
        lockoutDuration: const Duration(minutes: 30),
        failedAttempts: 5,
      );

      final events = service.getRecentEvents();
      expect(events.length, 1);
      expect(events[0].action, 'biometric_lockout');
      expect(events[0].severity, SecuritySeverity.critical);
      expect(events[0].metadata?['failedAttempts'], 5);
      expect(events[0].metadata?['lockoutDurationMinutes'], 30);
    });

    test('logTokenRefresh should record success', () async {
      await service.logTokenRefresh(success: true);

      final events = service.getRecentEvents();
      expect(events.length, 1);
      expect(events[0].action, 'token_refresh_success');
      expect(events[0].success, true);
    });

    test('logTokenRefresh should record failure with retry info', () async {
      await service.logTokenRefresh(
        success: false,
        errorCode: 'NETWORK_ERROR',
        retryAttempt: 2,
        backoffDelay: const Duration(seconds: 4),
      );

      final events = service.getRecentEvents();
      expect(events[0].action, 'token_refresh_failure');
      expect(events[0].metadata?['retryAttempt'], 2);
      expect(events[0].metadata?['backoffDelayMs'], 4000);
    });

    test('logSessionEvent should record login', () async {
      await service.logSessionEvent(
        action: 'login',
        success: true,
      );

      final events = service.getRecentEvents();
      expect(events[0].category, SecurityEventCategory.session);
      expect(events[0].action, 'login');
      expect(events[0].severity, SecuritySeverity.info);
    });

    test('logSessionEvent should record expired as warning', () async {
      await service.logSessionEvent(
        action: 'session_expired',
        success: false,
        reason: 'Token expired',
      );

      final events = service.getRecentEvents();
      expect(events[0].severity, SecuritySeverity.warning);
      expect(events[0].details, 'Token expired');
    });

    test('logDeviceIntegrityCheck should record critical on failure', () async {
      await service.logDeviceIntegrityCheck(
        passed: false,
        threats: ['root_detected', 'emulator'],
      );

      final events = service.getRecentEvents();
      expect(events[0].severity, SecuritySeverity.critical);
      expect(events[0].success, false);
      expect(events[0].metadata?['threats'], ['root_detected', 'emulator']);
    });

    test('logCertificatePinning should record success', () async {
      await service.logCertificatePinning(
        success: true,
        domain: 'api.sahool.app',
      );

      final events = service.getRecentEvents();
      expect(events[0].category, SecurityEventCategory.certificatePinning);
      expect(events[0].success, true);
      expect(events[0].metadata?['domain'], 'api.sahool.app');
    });

    test('getRecentEvents should return events sorted newest first', () async {
      // Log events with time gaps
      await service.logBiometricAttempt(success: true);
      await service.logTokenRefresh(success: true);
      await service.logSessionEvent(action: 'login', success: true);

      final events = service.getRecentEvents();
      expect(events.length, 3);
      // Last logged should be first (most recent)
      expect(events[0].category, SecurityEventCategory.session);
    });

    test('getRecentEvents should respect limit', () async {
      for (int i = 0; i < 10; i++) {
        await service.logBiometricAttempt(success: true);
      }

      final events = service.getRecentEvents(limit: 3);
      expect(events.length, 3);
    });

    test('getEventsByCategory should filter correctly', () async {
      await service.logBiometricAttempt(success: true);
      await service.logTokenRefresh(success: true);
      await service.logBiometricAttempt(success: false, errorCode: 'FAILED');

      final biometricEvents =
          service.getEventsByCategory(SecurityEventCategory.biometric);
      expect(biometricEvents.length, 2);

      final tokenEvents =
          service.getEventsByCategory(SecurityEventCategory.tokenRefresh);
      expect(tokenEvents.length, 1);
    });

    test('getCriticalEvents should only return critical severity', () async {
      await service.logBiometricAttempt(success: true); // info
      await service.logBiometricLockout(
        lockoutDuration: const Duration(minutes: 30),
        failedAttempts: 5,
      ); // critical
      await service.logDeviceIntegrityCheck(
        passed: false,
        threats: ['root'],
      ); // critical

      final criticalEvents = service.getCriticalEvents();
      expect(criticalEvents.length, 2);
    });

    test('getSummary should compute correct statistics', () async {
      // Biometric events
      await service.logBiometricAttempt(success: true);
      await service.logBiometricAttempt(success: true);
      await service.logBiometricAttempt(success: false, errorCode: 'FAILED');
      await service.logBiometricLockout(
        lockoutDuration: const Duration(minutes: 30),
        failedAttempts: 5,
      );

      // Token refresh events
      await service.logTokenRefresh(success: true);
      await service.logTokenRefresh(success: false, errorCode: 'NETWORK');

      // Session events
      await service.logSessionEvent(action: 'login', success: true);
      await service.logSessionEvent(action: 'session_expired', success: false);

      final summary = service.getSummary();

      expect(summary.totalEvents, 8);
      expect(summary.biometricAttempts, 3);
      expect(summary.biometricSuccesses, 2);
      expect(summary.biometricFailures, 1);
      expect(summary.biometricLockouts, 1);
      expect(summary.tokenRefreshAttempts, 2);
      expect(summary.tokenRefreshSuccesses, 1);
      expect(summary.tokenRefreshFailures, 1);
      expect(summary.sessionLogins, 1);
      expect(summary.sessionExpiries, 1);
      expect(summary.criticalEvents, 1); // biometric lockout
      expect(summary.lastEventTime, isNotNull);
    });

    test('getSummary should return empty for no events', () {
      final summary = service.getSummary();
      expect(summary.totalEvents, 0);
    });

    test('exportForSync should return all events as JSON list', () async {
      await service.logBiometricAttempt(success: true);
      await service.logTokenRefresh(success: true);

      final exported = await service.exportForSync();

      expect(exported.length, 2);
      expect(exported[0], isA<Map<String, dynamic>>());
      expect(exported[0]['success'], true);
    });
  });
}
