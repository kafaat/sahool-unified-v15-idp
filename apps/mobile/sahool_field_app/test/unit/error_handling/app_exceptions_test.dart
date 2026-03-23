/// Comprehensive App Exceptions Tests - SAHOOL Mobile
/// اختبارات شاملة لنظام الأخطاء - تطبيق سهول للجوال
///
/// Tests cover:
/// - ErrorType and ErrorSeverity enums
/// - AppException base class (bilingual messages, copyWith, toString)
/// - NetworkException factory methods
/// - ServerException factory methods
/// - AuthException factory methods
/// - ValidationException factory methods
/// - NotFoundException factory methods
/// - RateLimitException, SecurityException, StorageException, SyncException
/// - fromDioException converter
/// - Extension methods
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/error_handling/app_exceptions.dart';

void main() {
  group('ErrorType enum', () {
    test('should have all expected values', () {
      expect(ErrorType.values.length, 12);
      expect(ErrorType.values, contains(ErrorType.network));
      expect(ErrorType.values, contains(ErrorType.server));
      expect(ErrorType.values, contains(ErrorType.client));
      expect(ErrorType.values, contains(ErrorType.auth));
      expect(ErrorType.values, contains(ErrorType.validation));
      expect(ErrorType.values, contains(ErrorType.storage));
      expect(ErrorType.values, contains(ErrorType.timeout));
      expect(ErrorType.values, contains(ErrorType.notFound));
      expect(ErrorType.values, contains(ErrorType.rateLimit));
      expect(ErrorType.values, contains(ErrorType.security));
      expect(ErrorType.values, contains(ErrorType.sync));
      expect(ErrorType.values, contains(ErrorType.unknown));
    });
  });

  group('ErrorSeverity enum', () {
    test('should have all expected values', () {
      expect(ErrorSeverity.values.length, 4);
      expect(ErrorSeverity.values, contains(ErrorSeverity.info));
      expect(ErrorSeverity.values, contains(ErrorSeverity.warning));
      expect(ErrorSeverity.values, contains(ErrorSeverity.error));
      expect(ErrorSeverity.values, contains(ErrorSeverity.critical));
    });
  });

  group('AppException', () {
    test('should create with required fields', () {
      const exc = AppException(
        message: 'Something failed',
        messageAr: 'فشل شيء ما',
      );
      expect(exc.message, 'Something failed');
      expect(exc.messageAr, 'فشل شيء ما');
      expect(exc.type, ErrorType.unknown);
      expect(exc.severity, ErrorSeverity.error);
      expect(exc.isRetryable, false);
      expect(exc.code, isNull);
      expect(exc.statusCode, isNull);
      expect(exc.context, isNull);
    });

    test('should create with all fields', () {
      const exc = AppException(
        message: 'Test error',
        messageAr: 'خطأ اختبار',
        type: ErrorType.network,
        severity: ErrorSeverity.critical,
        code: 'E001',
        statusCode: 500,
        isRetryable: true,
        recoverySuggestion: 'Try again',
        recoverySuggestionAr: 'حاول مرة أخرى',
      );
      expect(exc.type, ErrorType.network);
      expect(exc.severity, ErrorSeverity.critical);
      expect(exc.code, 'E001');
      expect(exc.statusCode, 500);
      expect(exc.isRetryable, true);
      expect(exc.recoverySuggestion, 'Try again');
      expect(exc.recoverySuggestionAr, 'حاول مرة أخرى');
    });

    test('getUserMessage returns Arabic by default', () {
      const exc = AppException(
        message: 'English message',
        messageAr: 'رسالة عربية',
      );
      expect(exc.getUserMessage(), 'رسالة عربية');
      expect(exc.getUserMessage(isArabic: true), 'رسالة عربية');
      expect(exc.getUserMessage(isArabic: false), 'English message');
    });

    test('getRecoverySuggestion returns locale-specific', () {
      const exc = AppException(
        message: 'Error',
        messageAr: 'خطأ',
        recoverySuggestion: 'Try again',
        recoverySuggestionAr: 'حاول مرة أخرى',
      );
      expect(exc.getRecoverySuggestion(isArabic: true), 'حاول مرة أخرى');
      expect(exc.getRecoverySuggestion(isArabic: false), 'Try again');
    });

    test('getRecoverySuggestion returns null when not set', () {
      const exc = AppException(
        message: 'Error',
        messageAr: 'خطأ',
      );
      expect(exc.getRecoverySuggestion(), isNull);
    });

    test('toString includes code and message', () {
      const exc = AppException(
        message: 'Test error',
        messageAr: 'خطأ',
        code: 'E001',
      );
      expect(exc.toString(), 'AppException[E001]: Test error');
    });

    test('toString handles null code', () {
      const exc = AppException(
        message: 'Test error',
        messageAr: 'خطأ',
      );
      expect(exc.toString(), 'AppException[null]: Test error');
    });

    test('copyWith creates new instance with updated fields', () {
      const original = AppException(
        message: 'Original',
        messageAr: 'أصلي',
        code: 'E001',
        statusCode: 400,
      );
      final copy = original.copyWith(
        message: 'Updated',
        statusCode: 500,
      );
      expect(copy.message, 'Updated');
      expect(copy.messageAr, 'أصلي');
      expect(copy.code, 'E001');
      expect(copy.statusCode, 500);
    });

    test('copyWith preserves fields when not specified', () {
      const original = AppException(
        message: 'Original',
        messageAr: 'أصلي',
        type: ErrorType.network,
        severity: ErrorSeverity.critical,
        isRetryable: true,
      );
      final copy = original.copyWith();
      expect(copy.message, original.message);
      expect(copy.messageAr, original.messageAr);
      expect(copy.type, original.type);
      expect(copy.severity, original.severity);
      expect(copy.isRetryable, original.isRetryable);
    });

    test('implements Exception interface', () {
      const exc = AppException(message: 'test', messageAr: 'اختبار');
      expect(exc, isA<Exception>());
    });
  });

  group('NetworkException', () {
    test('default values', () {
      const exc = NetworkException();
      expect(exc.message, 'Network error occurred');
      expect(exc.messageAr, 'حدث خطأ في الشبكة');
      expect(exc.type, ErrorType.network);
      expect(exc.isRetryable, true);
      expect(exc.code, 'NETWORK_ERROR');
    });

    test('noConnection factory', () {
      final exc = NetworkException.noConnection();
      expect(exc.code, 'NO_CONNECTION');
      expect(exc.message, 'No internet connection');
      expect(exc.messageAr, 'لا يوجد اتصال بالإنترنت');
      expect(exc.isRetryable, true);
      expect(exc.recoverySuggestion, isNotNull);
      expect(exc.recoverySuggestionAr, isNotNull);
    });

    test('timeout factory', () {
      final exc = NetworkException.timeout();
      expect(exc.code, 'TIMEOUT');
      expect(exc.message, 'Connection timed out');
      expect(exc.messageAr, 'انتهت مهلة الاتصال');
      expect(exc.isRetryable, true);
    });

    test('dnsFailure factory', () {
      final exc = NetworkException.dnsFailure();
      expect(exc.code, 'DNS_FAILURE');
      expect(exc.message, contains('resolve'));
      expect(exc.isRetryable, true);
    });

    test('preserves originalError', () {
      final originalError = Exception('network down');
      final exc = NetworkException.noConnection(originalError: originalError);
      expect(exc.originalError, originalError);
    });
  });

  group('ServerException', () {
    test('default values', () {
      const exc = ServerException();
      expect(exc.type, ErrorType.server);
      expect(exc.isRetryable, true);
      expect(exc.code, 'SERVER_ERROR');
    });

    test('internalError factory', () {
      final exc = ServerException.internalError(statusCode: 500);
      expect(exc.code, 'INTERNAL_ERROR');
      expect(exc.statusCode, 500);
    });

    test('unavailable factory', () {
      final exc = ServerException.unavailable();
      expect(exc.code, 'SERVICE_UNAVAILABLE');
      expect(exc.statusCode, 503);
      expect(exc.isRetryable, true);
    });

    test('gatewayTimeout factory', () {
      final exc = ServerException.gatewayTimeout();
      expect(exc.code, 'GATEWAY_TIMEOUT');
      expect(exc.statusCode, 504);
      expect(exc.isRetryable, true);
    });
  });

  group('AuthException', () {
    test('default values', () {
      const exc = AuthException();
      expect(exc.type, ErrorType.auth);
      expect(exc.isRetryable, false);
      expect(exc.code, 'AUTH_ERROR');
    });

    test('invalidCredentials factory', () {
      final exc = AuthException.invalidCredentials();
      expect(exc.code, 'INVALID_CREDENTIALS');
      expect(exc.statusCode, 401);
      expect(exc.messageAr, contains('كلمة المرور'));
    });

    test('sessionExpired factory', () {
      final exc = AuthException.sessionExpired();
      expect(exc.code, 'SESSION_EXPIRED');
      expect(exc.statusCode, 401);
      expect(exc.messageAr, contains('انتهت'));
    });

    test('unauthorized factory', () {
      final exc = AuthException.unauthorized();
      expect(exc.code, 'UNAUTHORIZED');
      expect(exc.statusCode, 403);
    });

    test('tokenRefreshFailed factory', () {
      final exc = AuthException.tokenRefreshFailed();
      expect(exc.code, 'TOKEN_REFRESH_FAILED');
      expect(exc.recoverySuggestion, isNotNull);
    });

    test('biometricFailed factory with custom reason', () {
      final exc = AuthException.biometricFailed(reason: 'Sensor not available');
      expect(exc.code, 'BIOMETRIC_FAILED');
      expect(exc.message, 'Sensor not available');
    });

    test('biometricFailed factory without reason', () {
      final exc = AuthException.biometricFailed();
      expect(exc.message, 'Biometric authentication failed');
      expect(exc.messageAr, 'فشل التحقق بالبصمة');
    });
  });

  group('ValidationException', () {
    test('default values', () {
      const exc = ValidationException();
      expect(exc.type, ErrorType.validation);
      expect(exc.severity, ErrorSeverity.warning);
      expect(exc.isRetryable, false);
      expect(exc.statusCode, 400);
    });

    test('requiredField factory', () {
      final exc = ValidationException.requiredField('email', 'البريد الإلكتروني');
      expect(exc.code, 'REQUIRED_FIELD');
      expect(exc.message, contains('email'));
      expect(exc.messageAr, contains('البريد الإلكتروني'));
      expect(exc.fieldErrors, isNotNull);
      expect(exc.fieldErrors!['email'], 'This field is required');
      expect(exc.fieldErrorsAr, isNotNull);
    });

    test('invalidFormat factory', () {
      final exc = ValidationException.invalidFormat('phone', 'رقم الهاتف');
      expect(exc.code, 'INVALID_FORMAT');
      expect(exc.message, contains('phone'));
      expect(exc.fieldErrors!['phone'], 'Invalid format');
    });

    test('outOfRange with min and max', () {
      final exc = ValidationException.outOfRange('age', 'العمر', min: 18, max: 120);
      expect(exc.code, 'OUT_OF_RANGE');
      expect(exc.message, contains('between 18 and 120'));
      expect(exc.messageAr, contains('بين 18 و 120'));
    });

    test('outOfRange with min only', () {
      final exc = ValidationException.outOfRange('age', 'العمر', min: 0);
      expect(exc.message, contains('at least 0'));
      expect(exc.messageAr, contains('على الأقل 0'));
    });

    test('outOfRange with max only', () {
      final exc = ValidationException.outOfRange('count', 'العدد', max: 100);
      expect(exc.message, contains('at most 100'));
      expect(exc.messageAr, contains('على الأكثر 100'));
    });
  });

  group('NotFoundException', () {
    test('default values', () {
      const exc = NotFoundException();
      expect(exc.type, ErrorType.notFound);
      expect(exc.statusCode, 404);
      expect(exc.isRetryable, false);
    });

    test('field factory', () {
      final exc = NotFoundException.field('F001');
      expect(exc.code, 'FIELD_NOT_FOUND');
      expect(exc.context, isNotNull);
      expect(exc.context!['fieldId'], 'F001');
      expect(exc.messageAr, 'الحقل غير موجود');
    });

    test('task factory', () {
      final exc = NotFoundException.task('T001');
      expect(exc.code, 'TASK_NOT_FOUND');
      expect(exc.context!['taskId'], 'T001');
      expect(exc.messageAr, 'المهمة غير موجودة');
    });

    test('user factory', () {
      final exc = NotFoundException.user('U001');
      expect(exc.code, 'USER_NOT_FOUND');
      expect(exc.context!['userId'], 'U001');
      expect(exc.messageAr, 'المستخدم غير موجود');
    });
  });

  group('RateLimitException (AppException)', () {
    test('default values', () {
      const exc = RateLimitException();
      expect(exc.type, ErrorType.rateLimit);
      expect(exc.statusCode, 429);
      expect(exc.isRetryable, true);
      expect(exc.severity, ErrorSeverity.warning);
      expect(exc.messageAr, 'طلبات كثيرة جدًا');
    });

    test('with retryAfter', () {
      final retryTime = DateTime(2026, 3, 14, 12, 0);
      final exc = RateLimitException(retryAfter: retryTime);
      expect(exc.retryAfter, retryTime);
    });
  });

  group('SecurityException', () {
    test('default values', () {
      const exc = SecurityException();
      expect(exc.type, ErrorType.security);
      expect(exc.severity, ErrorSeverity.critical);
      expect(exc.isRetryable, false);
    });

    test('certificatePinningFailed factory', () {
      final exc = SecurityException.certificatePinningFailed();
      expect(exc.code, 'CERT_PINNING_FAILED');
      expect(exc.message, contains('SSL'));
      expect(exc.recoverySuggestion, isNotNull);
    });

    test('requestTampered factory', () {
      final exc = SecurityException.requestTampered();
      expect(exc.code, 'REQUEST_TAMPERED');
      expect(exc.message, contains('integrity'));
    });
  });

  group('StorageException', () {
    test('default values', () {
      const exc = StorageException();
      expect(exc.type, ErrorType.storage);
      expect(exc.isRetryable, false);
    });

    test('database factory', () {
      final exc = StorageException.database(details: 'Table not found');
      expect(exc.code, 'DATABASE_ERROR');
      expect(exc.message, 'Table not found');
    });

    test('database factory without details', () {
      final exc = StorageException.database();
      expect(exc.message, 'Database operation failed');
    });

    test('encryption factory', () {
      final exc = StorageException.encryption();
      expect(exc.code, 'ENCRYPTION_ERROR');
      expect(exc.messageAr, contains('تشفير'));
    });

    test('full factory', () {
      final exc = StorageException.full();
      expect(exc.code, 'STORAGE_FULL');
      expect(exc.recoverySuggestion, isNotNull);
      expect(exc.recoverySuggestionAr, isNotNull);
    });
  });

  group('SyncException', () {
    test('default values', () {
      const exc = SyncException();
      expect(exc.type, ErrorType.sync);
      expect(exc.isRetryable, true);
      expect(exc.severity, ErrorSeverity.warning);
    });

    test('conflict factory', () {
      final exc = SyncException.conflict(
        entityType: 'field',
        entityId: 'F001',
      );
      expect(exc.code, 'SYNC_CONFLICT');
      expect(exc.context!['entityType'], 'field');
      expect(exc.context!['entityId'], 'F001');
    });

    test('conflict factory without optional params', () {
      final exc = SyncException.conflict();
      expect(exc.code, 'SYNC_CONFLICT');
      expect(exc.context, isNotNull);
    });

    test('offline factory', () {
      final exc = SyncException.offline();
      expect(exc.code, 'OFFLINE');
      expect(exc.messageAr, contains('غير متصل'));
    });
  });

  group('ExceptionExtension', () {
    test('AppException returns itself', () {
      const original = AppException(message: 'test', messageAr: 'اختبار');
      final result = original.toAppException();
      expect(identical(result, original), true);
    });

    test('generic error converts to AppException', () {
      const error = FormatException('bad format');
      final result = error.toAppException();
      expect(result, isA<AppException>());
      expect(result.type, ErrorType.unknown);
      expect(result.code, 'UNEXPECTED_ERROR');
    });

    test('string converts to AppException', () {
      final result = 'some error'.toAppException();
      expect(result, isA<AppException>());
      expect(result.originalError, 'some error');
    });
  });
}
