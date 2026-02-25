import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:sahool_field_app/core/error_handling/app_exceptions.dart';
import 'package:sahool_field_app/core/error_handling/error_handler.dart';

void main() {
  group('AppException', () {
    test('should create with required fields', () {
      final exception = AppException(
        message: 'Test error',
        messageAr: 'خطأ تجريبي',
      );

      expect(exception.message, 'Test error');
      expect(exception.messageAr, 'خطأ تجريبي');
      expect(exception.type, ErrorType.unknown);
      expect(exception.isRetryable, false);
    });

    test('should return correct user message based on locale', () {
      final exception = AppException(
        message: 'Test error',
        messageAr: 'خطأ تجريبي',
      );

      expect(exception.getUserMessage(isArabic: true), 'خطأ تجريبي');
      expect(exception.getUserMessage(isArabic: false), 'Test error');
    });

    test('should support copyWith', () {
      final original = AppException(
        message: 'Original',
        messageAr: 'أصلي',
        code: 'ORIG',
      );

      final copy = original.copyWith(
        message: 'Modified',
        code: 'MOD',
      );

      expect(copy.message, 'Modified');
      expect(copy.messageAr, 'أصلي'); // Unchanged
      expect(copy.code, 'MOD');
    });
  });

  group('NetworkException', () {
    test('should create no connection exception', () {
      final exception = NetworkException.noConnection();

      expect(exception.code, 'NO_CONNECTION');
      expect(exception.type, ErrorType.network);
      expect(exception.isRetryable, true);
      expect(exception.messageAr, contains('اتصال'));
    });

    test('should create timeout exception', () {
      final exception = NetworkException.timeout();

      expect(exception.code, 'TIMEOUT');
      expect(exception.type, ErrorType.network);
      expect(exception.isRetryable, true);
      expect(exception.messageAr, contains('مهلة'));
    });
  });

  group('ServerException', () {
    test('should create internal error exception', () {
      final exception = ServerException.internalError(statusCode: 500);

      expect(exception.code, 'INTERNAL_ERROR');
      expect(exception.statusCode, 500);
      expect(exception.type, ErrorType.server);
      expect(exception.isRetryable, true);
    });

    test('should create unavailable exception', () {
      final exception = ServerException.unavailable();

      expect(exception.code, 'SERVICE_UNAVAILABLE');
      expect(exception.statusCode, 503);
      expect(exception.isRetryable, true);
    });
  });

  group('AuthException', () {
    test('should create invalid credentials exception', () {
      final exception = AuthException.invalidCredentials();

      expect(exception.code, 'INVALID_CREDENTIALS');
      expect(exception.statusCode, 401);
      expect(exception.type, ErrorType.auth);
      expect(exception.isRetryable, false);
    });

    test('should create session expired exception', () {
      final exception = AuthException.sessionExpired();

      expect(exception.code, 'SESSION_EXPIRED');
      expect(exception.messageAr, contains('انتهت'));
    });

    test('should create unauthorized exception', () {
      final exception = AuthException.unauthorized();

      expect(exception.code, 'UNAUTHORIZED');
      expect(exception.statusCode, 403);
    });
  });

  group('ValidationException', () {
    test('should create required field exception', () {
      final exception =
          ValidationException.requiredField('email', 'البريد الإلكتروني');

      expect(exception.code, 'REQUIRED_FIELD');
      expect(exception.message, contains('email'));
      expect(exception.messageAr, contains('البريد الإلكتروني'));
      expect(exception.type, ErrorType.validation);
    });

    test('should create invalid format exception', () {
      final exception =
          ValidationException.invalidFormat('phone', 'رقم الهاتف');

      expect(exception.code, 'INVALID_FORMAT');
      expect(exception.message, contains('phone'));
      expect(exception.messageAr, contains('رقم الهاتف'));
    });

    test('should support field errors', () {
      final exception = ValidationException(
        message: 'Validation error',
        messageAr: 'خطأ في البيانات',
        fieldErrors: {'email': 'Invalid email'},
        fieldErrorsAr: {'البريد': 'بريد غير صالح'},
      );

      expect(exception.fieldErrors?['email'], 'Invalid email');
      expect(exception.fieldErrorsAr?['البريد'], 'بريد غير صالح');
    });
  });

  group('NotFoundException', () {
    test('should create field not found exception', () {
      final exception = NotFoundException.field('field_123');

      expect(exception.code, 'FIELD_NOT_FOUND');
      expect(exception.context?['fieldId'], 'field_123');
      expect(exception.type, ErrorType.notFound);
    });

    test('should create task not found exception', () {
      final exception = NotFoundException.task('task_456');

      expect(exception.code, 'TASK_NOT_FOUND');
      expect(exception.context?['taskId'], 'task_456');
    });
  });

  group('SyncException', () {
    test('should create offline exception', () {
      final exception = SyncException.offline();

      expect(exception.code, 'OFFLINE');
      expect(exception.type, ErrorType.sync);
      expect(exception.isRetryable, true);
    });

    test('should create conflict exception with context', () {
      final exception = SyncException.conflict(
        entityType: 'field',
        entityId: 'field_123',
      );

      expect(exception.code, 'SYNC_CONFLICT');
      expect(exception.context?['entityType'], 'field');
      expect(exception.context?['entityId'], 'field_123');
    });
  });

  group('RateLimitException', () {
    test('should create with retry after', () {
      final retryAfter = DateTime.now().add(const Duration(minutes: 5));
      final exception = RateLimitException(retryAfter: retryAfter);

      expect(exception.code, 'RATE_LIMITED');
      expect(exception.statusCode, 429);
      expect(exception.retryAfter, retryAfter);
      expect(exception.isRetryable, true);
    });
  });

  group('SecurityException', () {
    test('should create certificate pinning failed exception', () {
      final exception = SecurityException.certificatePinningFailed();

      expect(exception.code, 'CERT_PINNING_FAILED');
      expect(exception.type, ErrorType.security);
      expect(exception.isRetryable, false);
      expect(exception.severity, ErrorSeverity.critical);
    });
  });

  group('fromDioException', () {
    test('should convert connection timeout to NetworkException', () {
      final dioException = DioException(
        type: DioExceptionType.connectionTimeout,
        requestOptions: RequestOptions(path: '/test'),
      );

      final appException = fromDioException(dioException);

      expect(appException, isA<NetworkException>());
      expect(appException.code, 'TIMEOUT');
      expect(appException.isRetryable, true);
    });

    test('should convert connection error to NetworkException', () {
      final dioException = DioException(
        type: DioExceptionType.connectionError,
        requestOptions: RequestOptions(path: '/test'),
      );

      final appException = fromDioException(dioException);

      expect(appException, isA<NetworkException>());
      expect(appException.code, 'NO_CONNECTION');
    });

    test('should convert bad certificate to SecurityException', () {
      final dioException = DioException(
        type: DioExceptionType.badCertificate,
        requestOptions: RequestOptions(path: '/test'),
      );

      final appException = fromDioException(dioException);

      expect(appException, isA<SecurityException>());
      expect(appException.code, 'CERT_PINNING_FAILED');
    });

    test('should convert 401 response to AuthException', () {
      final dioException = DioException(
        type: DioExceptionType.badResponse,
        requestOptions: RequestOptions(path: '/test'),
        response: Response(
          requestOptions: RequestOptions(path: '/test'),
          statusCode: 401,
        ),
      );

      final appException = fromDioException(dioException);

      expect(appException, isA<AuthException>());
    });

    test('should convert 404 response to NotFoundException', () {
      final dioException = DioException(
        type: DioExceptionType.badResponse,
        requestOptions: RequestOptions(path: '/test'),
        response: Response(
          requestOptions: RequestOptions(path: '/test'),
          statusCode: 404,
        ),
      );

      final appException = fromDioException(dioException);

      expect(appException, isA<NotFoundException>());
    });

    test('should convert 429 response to RateLimitException', () {
      final dioException = DioException(
        type: DioExceptionType.badResponse,
        requestOptions: RequestOptions(path: '/test'),
        response: Response(
          requestOptions: RequestOptions(path: '/test'),
          statusCode: 429,
        ),
      );

      final appException = fromDioException(dioException);

      expect(appException, isA<RateLimitException>());
    });

    test('should convert 500 response to ServerException', () {
      final dioException = DioException(
        type: DioExceptionType.badResponse,
        requestOptions: RequestOptions(path: '/test'),
        response: Response(
          requestOptions: RequestOptions(path: '/test'),
          statusCode: 500,
        ),
      );

      final appException = fromDioException(dioException);

      expect(appException, isA<ServerException>());
    });
  });

  group('ExceptionExtension', () {
    test('should convert any exception to AppException', () {
      final error = Exception('Some error');
      final appException = error.toAppException();

      expect(appException, isA<AppException>());
      expect(appException.type, ErrorType.unknown);
    });

    test('should return same AppException if already an AppException', () {
      final original = NetworkException.noConnection();
      final result = original.toAppException();

      expect(result, same(original));
    });
  });

  group('Result', () {
    test('Success should hold value', () {
      final result = Success<int>(42);

      expect(result.isSuccess, true);
      expect(result.isFailure, false);
      expect(result.valueOrNull, 42);
      expect(result.getOrThrow(), 42);
      expect(result.errorOrNull, isNull);
    });

    test('Failure should hold error', () {
      final error = NetworkException.noConnection();
      final result = Failure<int>(error);

      expect(result.isSuccess, false);
      expect(result.isFailure, true);
      expect(result.valueOrNull, isNull);
      expect(result.errorOrNull, error);
    });

    test('getOrElse should return default on failure', () {
      final result = Failure<int>(NetworkException.noConnection());

      expect(result.getOrElse(0), 0);
    });

    test('when should call appropriate callback', () {
      final successResult = Success<int>(42);
      final failureResult = Failure<int>(NetworkException.noConnection());

      final successValue = successResult.when(
        success: (v) => 'Success: $v',
        failure: (e) => 'Failure: ${e.code}',
      );

      final failureValue = failureResult.when(
        success: (v) => 'Success: $v',
        failure: (e) => 'Failure: ${e.code}',
      );

      expect(successValue, 'Success: 42');
      expect(failureValue, 'Failure: NO_CONNECTION');
    });

    test('map should transform success value', () {
      final result = Success<int>(21);
      final mapped = result.map((v) => v * 2);

      expect(mapped.valueOrNull, 42);
    });

    test('map should preserve failure', () {
      final error = NetworkException.noConnection();
      final result = Failure<int>(error);
      final mapped = result.map((v) => v * 2);

      expect(mapped.errorOrNull, error);
    });
  });

  group('getRecoveryStrategy', () {
    test('should return retry for network errors', () {
      final exception = NetworkException.noConnection();
      final strategy = getRecoveryStrategy(exception);

      expect(strategy, RecoveryStrategy.retry);
    });

    test('should return reAuthenticate for session expired', () {
      final exception = AuthException.sessionExpired();
      final strategy = getRecoveryStrategy(exception);

      expect(strategy, RecoveryStrategy.reAuthenticate);
    });

    test('should return useCache for sync errors', () {
      final exception = SyncException.offline();
      final strategy = getRecoveryStrategy(exception);

      expect(strategy, RecoveryStrategy.useCache);
    });

    test('should return manualRetry for validation errors', () {
      final exception = ValidationException.requiredField('name', 'الاسم');
      final strategy = getRecoveryStrategy(exception);

      expect(strategy, RecoveryStrategy.manualRetry);
    });

    test('should return navigateFallback for not found errors', () {
      final exception = NotFoundException.field('field_123');
      final strategy = getRecoveryStrategy(exception);

      expect(strategy, RecoveryStrategy.navigateFallback);
    });
  });
}
