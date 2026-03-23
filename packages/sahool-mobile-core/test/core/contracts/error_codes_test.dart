/// Error Codes Unit Tests - اختبارات رموز الأخطاء
///
/// Tests that error codes are properly defined with bilingual messages,
/// correct HTTP status codes, and retryable flags.
///
/// Run with: flutter test test/core/contracts/error_codes_test.dart
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_mobile_core/core/contracts/error_codes.dart';

void main() {
  // ===========================================================================
  // ErrorCodes constants
  // ===========================================================================

  group('ErrorCodes - constant values', () {
    test('network error codes are defined', () {
      expect(ErrorCodes.networkError, 'NETWORK_ERROR');
      expect(ErrorCodes.timeout, 'TIMEOUT');
      expect(ErrorCodes.circuitOpen, 'CIRCUIT_OPEN');
      expect(ErrorCodes.invalidResponse, 'INVALID_RESPONSE');
    });

    test('authentication error codes are defined', () {
      expect(ErrorCodes.unauthorized, 'UNAUTHORIZED');
      expect(ErrorCodes.tokenExpired, 'TOKEN_EXPIRED');
      expect(ErrorCodes.tokenInvalid, 'TOKEN_INVALID');
      expect(ErrorCodes.sessionExpired, 'SESSION_EXPIRED');
      expect(ErrorCodes.forbidden, 'FORBIDDEN');
      expect(ErrorCodes.insufficientPermissions, 'INSUFFICIENT_PERMISSIONS');
    });

    test('client error codes are defined', () {
      expect(ErrorCodes.badRequest, 'BAD_REQUEST');
      expect(ErrorCodes.validationError, 'VALIDATION_ERROR');
      expect(ErrorCodes.notFound, 'NOT_FOUND');
      expect(ErrorCodes.conflict, 'CONFLICT');
      expect(ErrorCodes.rateLimited, 'RATE_LIMITED');
    });

    test('server error codes are defined', () {
      expect(ErrorCodes.serverError, 'SERVER_ERROR');
      expect(ErrorCodes.badGateway, 'BAD_GATEWAY');
      expect(ErrorCodes.serviceUnavailable, 'SERVICE_UNAVAILABLE');
      expect(ErrorCodes.gatewayTimeout, 'GATEWAY_TIMEOUT');
    });

    test('offline/sync error codes are defined', () {
      expect(ErrorCodes.offline, 'OFFLINE');
      expect(ErrorCodes.syncFailed, 'SYNC_FAILED');
      expect(ErrorCodes.syncConflict, 'SYNC_CONFLICT');
    });

    test('security error codes are defined', () {
      expect(ErrorCodes.certificateError, 'CERTIFICATE_ERROR');
    });

    test('unknown error code is defined', () {
      expect(ErrorCodes.unknown, 'UNKNOWN');
    });

    test('vision service E-codes are defined', () {
      expect(ErrorCodes.visionInvalidFormat, 'E1001');
      expect(ErrorCodes.visionFileTooLarge, 'E1002');
      expect(ErrorCodes.visionInvalidDimensions, 'E1003');
      expect(ErrorCodes.visionUnsupportedType, 'E1004');
      expect(ErrorCodes.visionEmptyImage, 'E1005');
      expect(ErrorCodes.visionCorruptFile, 'E1006');
      expect(ErrorCodes.visionModelNotFound, 'E2001');
      expect(ErrorCodes.visionModelLoadFailed, 'E2002');
      expect(ErrorCodes.visionInferenceFailed, 'E2003');
      expect(ErrorCodes.visionModelIncompatible, 'E2004');
      expect(ErrorCodes.visionWarmupFailed, 'E2005');
      expect(ErrorCodes.visionImageDecode, 'E3001');
      expect(ErrorCodes.visionBatchFailed, 'E3003');
      expect(ErrorCodes.visionGpuOom, 'E4001');
      expect(ErrorCodes.visionMaxConcurrent, 'E4004');
      expect(ErrorCodes.visionDbError, 'E5001');
      expect(ErrorCodes.visionCacheError, 'E5002');
      expect(ErrorCodes.visionRateExceeded, 'E6001');
      expect(ErrorCodes.visionQuotaExceeded, 'E6002');
      expect(ErrorCodes.visionInferenceTimeout, 'E7001');
      expect(ErrorCodes.visionRequestTimeout, 'E7002');
    });
  });

  // ===========================================================================
  // ErrorMessage model
  // ===========================================================================

  group('ErrorMessage', () {
    test('has all required fields', () {
      const msg = ErrorMessage(
        code: 'TEST',
        httpStatus: 400,
        en: 'Test error',
        ar: 'خطأ تجريبي',
        retryable: false,
      );
      expect(msg.code, 'TEST');
      expect(msg.httpStatus, 400);
      expect(msg.en, 'Test error');
      expect(msg.ar, 'خطأ تجريبي');
      expect(msg.retryable, isFalse);
    });
  });

  // ===========================================================================
  // errorMessages map
  // ===========================================================================

  group('errorMessages map', () {
    test('contains all standard error codes', () {
      final expectedCodes = [
        'NETWORK_ERROR',
        'TIMEOUT',
        'CIRCUIT_OPEN',
        'INVALID_RESPONSE',
        'UNAUTHORIZED',
        'TOKEN_EXPIRED',
        'TOKEN_INVALID',
        'SESSION_EXPIRED',
        'FORBIDDEN',
        'INSUFFICIENT_PERMISSIONS',
        'BAD_REQUEST',
        'VALIDATION_ERROR',
        'NOT_FOUND',
        'CONFLICT',
        'RATE_LIMITED',
        'SERVER_ERROR',
        'BAD_GATEWAY',
        'SERVICE_UNAVAILABLE',
        'GATEWAY_TIMEOUT',
        'OFFLINE',
        'SYNC_FAILED',
        'SYNC_CONFLICT',
        'CERTIFICATE_ERROR',
        'UNKNOWN',
      ];
      for (final code in expectedCodes) {
        expect(errorMessages.containsKey(code), isTrue, reason: 'Missing entry for $code');
      }
    });

    test('every entry has non-empty English message', () {
      for (final entry in errorMessages.entries) {
        expect(entry.value.en, isNotEmpty, reason: '${entry.key} has empty English message');
      }
    });

    test('every entry has non-empty Arabic message', () {
      for (final entry in errorMessages.entries) {
        expect(entry.value.ar, isNotEmpty, reason: '${entry.key} has empty Arabic message');
      }
    });

    test('every entry code matches its map key', () {
      for (final entry in errorMessages.entries) {
        expect(
          entry.value.code,
          entry.key,
          reason: 'Map key ${entry.key} does not match code ${entry.value.code}',
        );
      }
    });

    test('HTTP status codes are valid', () {
      for (final entry in errorMessages.entries) {
        final status = entry.value.httpStatus;
        // 0 is used for client-side / offline errors
        expect(
          status == 0 || (status >= 200 && status < 600),
          isTrue,
          reason: '${entry.key} has invalid httpStatus: $status',
        );
      }
    });

    test('retryable errors have expected codes', () {
      final expectedRetryable = {
        'NETWORK_ERROR',
        'TIMEOUT',
        'CIRCUIT_OPEN',
        'RATE_LIMITED',
        'SERVER_ERROR',
        'BAD_GATEWAY',
        'SERVICE_UNAVAILABLE',
        'GATEWAY_TIMEOUT',
        'OFFLINE',
        'SYNC_FAILED',
      };
      for (final code in expectedRetryable) {
        expect(
          errorMessages[code]?.retryable,
          isTrue,
          reason: '$code should be retryable',
        );
      }
    });

    test('non-retryable errors include auth and client errors', () {
      final expectedNonRetryable = [
        'UNAUTHORIZED',
        'TOKEN_EXPIRED',
        'TOKEN_INVALID',
        'FORBIDDEN',
        'BAD_REQUEST',
        'NOT_FOUND',
        'UNKNOWN',
      ];
      for (final code in expectedNonRetryable) {
        expect(
          errorMessages[code]?.retryable,
          isFalse,
          reason: '$code should not be retryable',
        );
      }
    });

    test('HTTP status mapping for auth errors is 401', () {
      expect(errorMessages['UNAUTHORIZED']!.httpStatus, 401);
      expect(errorMessages['TOKEN_EXPIRED']!.httpStatus, 401);
      expect(errorMessages['TOKEN_INVALID']!.httpStatus, 401);
      expect(errorMessages['SESSION_EXPIRED']!.httpStatus, 401);
    });

    test('HTTP status mapping for forbidden is 403', () {
      expect(errorMessages['FORBIDDEN']!.httpStatus, 403);
      expect(errorMessages['INSUFFICIENT_PERMISSIONS']!.httpStatus, 403);
    });
  });

  // ===========================================================================
  // getErrorMessage helper
  // ===========================================================================

  group('getErrorMessage', () {
    test('returns correct message for known code', () {
      final msg = getErrorMessage('UNAUTHORIZED');
      expect(msg.code, 'UNAUTHORIZED');
      expect(msg.httpStatus, 401);
    });

    test('returns UNKNOWN for unrecognized code', () {
      final msg = getErrorMessage('NONEXISTENT_CODE');
      expect(msg.code, 'UNKNOWN');
    });
  });

  // ===========================================================================
  // getLocalizedError helper
  // ===========================================================================

  group('getLocalizedError', () {
    test('returns Arabic message by default', () {
      final msg = getLocalizedError('NETWORK_ERROR');
      expect(msg, contains('الشبكة'));
    });

    test('returns English message when locale is en', () {
      final msg = getLocalizedError('NETWORK_ERROR', locale: 'en');
      expect(msg, contains('Network'));
    });

    test('falls back to UNKNOWN for bad code', () {
      final msg = getLocalizedError('FAKE_CODE');
      // Should return the UNKNOWN error message
      expect(msg, isNotEmpty);
    });
  });

  // ===========================================================================
  // httpStatusToErrorCode helper
  // ===========================================================================

  group('httpStatusToErrorCode', () {
    test('maps 401 to unauthorized', () {
      expect(httpStatusToErrorCode(401), ErrorCodes.unauthorized);
    });

    test('maps 403 to forbidden', () {
      expect(httpStatusToErrorCode(403), ErrorCodes.forbidden);
    });

    test('maps 404 to notFound', () {
      expect(httpStatusToErrorCode(404), ErrorCodes.notFound);
    });

    test('maps 409 to conflict', () {
      expect(httpStatusToErrorCode(409), ErrorCodes.conflict);
    });

    test('maps 429 to rateLimited', () {
      expect(httpStatusToErrorCode(429), ErrorCodes.rateLimited);
    });

    test('maps 400 to badRequest', () {
      expect(httpStatusToErrorCode(400), ErrorCodes.badRequest);
    });

    test('maps 502 to invalidResponse', () {
      expect(httpStatusToErrorCode(502), ErrorCodes.invalidResponse);
    });

    test('maps 503 to serviceUnavailable', () {
      expect(httpStatusToErrorCode(503), ErrorCodes.serviceUnavailable);
    });

    test('maps 504 to gatewayTimeout', () {
      expect(httpStatusToErrorCode(504), ErrorCodes.gatewayTimeout);
    });

    test('maps generic 5xx to serverError', () {
      expect(httpStatusToErrorCode(500), ErrorCodes.serverError);
      expect(httpStatusToErrorCode(501), ErrorCodes.serverError);
      expect(httpStatusToErrorCode(599), ErrorCodes.serverError);
    });

    test('maps unknown status to unknown', () {
      expect(httpStatusToErrorCode(200), ErrorCodes.unknown);
      expect(httpStatusToErrorCode(301), ErrorCodes.unknown);
      expect(httpStatusToErrorCode(418), ErrorCodes.unknown);
    });
  });

  // ===========================================================================
  // isRetryable helper
  // ===========================================================================

  group('isRetryable', () {
    test('network and server errors are retryable', () {
      expect(isRetryable('NETWORK_ERROR'), isTrue);
      expect(isRetryable('TIMEOUT'), isTrue);
      expect(isRetryable('SERVER_ERROR'), isTrue);
      expect(isRetryable('SERVICE_UNAVAILABLE'), isTrue);
    });

    test('auth and client errors are not retryable', () {
      expect(isRetryable('UNAUTHORIZED'), isFalse);
      expect(isRetryable('FORBIDDEN'), isFalse);
      expect(isRetryable('NOT_FOUND'), isFalse);
      expect(isRetryable('BAD_REQUEST'), isFalse);
    });

    test('unknown codes fall back to UNKNOWN (not retryable)', () {
      expect(isRetryable('DOES_NOT_EXIST'), isFalse);
    });
  });
}
