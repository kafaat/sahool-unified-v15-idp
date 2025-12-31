import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:dio/dio.dart';
import 'package:sahool_field_app/core/network/dio_error_handler.dart';
import 'package:sahool_field_app/core/network/api_result.dart';

/// Mock dependencies
class MockDioException extends Mock implements DioException {}
class MockResponse extends Mock implements Response {}
class MockRequestOptions extends Mock implements RequestOptions {}

void main() {
  setUpAll(() {
    registerFallbackValue(RequestOptions(path: ''));
  });

  group('DioErrorHandler', () {
    group('handle', () {
      test('should handle connection timeout error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.connectionTimeout,
          requestOptions: RequestOptions(path: '/test'),
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result, isA<Failure<String>>());
        expect(result.message, contains('انتهت مهلة الاتصال'));
      });

      test('should handle send timeout error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.sendTimeout,
          requestOptions: RequestOptions(path: '/test'),
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result, isA<Failure<String>>());
        expect(result.message, contains('انتهت مهلة إرسال البيانات'));
      });

      test('should handle receive timeout error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.receiveTimeout,
          requestOptions: RequestOptions(path: '/test'),
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result, isA<Failure<String>>());
        expect(result.message, contains('انتهت مهلة استقبال البيانات'));
      });

      test('should handle connection error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.connectionError,
          requestOptions: RequestOptions(path: '/test'),
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result, isA<Failure<String>>());
        expect(result.message, contains('لا يوجد اتصال بالإنترنت'));
      });

      test('should handle bad certificate error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badCertificate,
          requestOptions: RequestOptions(path: '/test'),
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result, isA<Failure<String>>());
        expect(result.message, contains('خطأ في شهادة الأمان'));
      });

      test('should handle cancel error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.cancel,
          requestOptions: RequestOptions(path: '/test'),
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result, isA<Failure<String>>());
        expect(result.message, contains('تم إلغاء الطلب'));
      });

      test('should handle 400 bad request error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badResponse,
          requestOptions: RequestOptions(path: '/test'),
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 400,
          ),
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result, isA<Failure<String>>());
        expect(result.statusCode, 400);
        expect(result.message, contains('طلب غير صحيح'));
      });

      test('should handle 401 unauthorized error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badResponse,
          requestOptions: RequestOptions(path: '/test'),
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 401,
          ),
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result.statusCode, 401);
        expect(result.message, contains('يرجى تسجيل الدخول مجدداً'));
      });

      test('should handle 403 forbidden error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badResponse,
          requestOptions: RequestOptions(path: '/test'),
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 403,
          ),
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result.statusCode, 403);
        expect(result.message, contains('غير مصرح لك'));
      });

      test('should handle 404 not found error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badResponse,
          requestOptions: RequestOptions(path: '/test'),
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 404,
          ),
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result.statusCode, 404);
        expect(result.message, contains('البيانات غير موجودة'));
      });

      test('should handle 413 payload too large error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badResponse,
          requestOptions: RequestOptions(path: '/test'),
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 413,
          ),
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result.statusCode, 413);
        expect(result.message, contains('حجم الملف كبير جداً'));
      });

      test('should handle 422 unprocessable entity error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badResponse,
          requestOptions: RequestOptions(path: '/test'),
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 422,
          ),
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result.statusCode, 422);
        expect(result.message, contains('بيانات غير صالحة'));
      });

      test('should handle 429 too many requests error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badResponse,
          requestOptions: RequestOptions(path: '/test'),
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 429,
          ),
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result.statusCode, 429);
        expect(result.message, contains('طلبات كثيرة'));
      });

      test('should handle 500 server error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badResponse,
          requestOptions: RequestOptions(path: '/test'),
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 500,
          ),
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result.statusCode, 500);
        expect(result.message, contains('خطأ في السيرفر'));
      });

      test('should handle unknown error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.unknown,
          requestOptions: RequestOptions(path: '/test'),
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result, isA<Failure<String>>());
        expect(result.message, contains('حدث خطأ غير متوقع'));
      });

      test('should detect socket exception in unknown error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.unknown,
          requestOptions: RequestOptions(path: '/test'),
          message: 'SocketException: Failed to connect',
        );

        // Act
        final result = DioErrorHandler.handle<String>(dioException);

        // Assert
        expect(result.message, contains('لا يوجد اتصال بالإنترنت'));
      });
    });

    group('isRetryable', () {
      test('should return true for connection timeout', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.connectionTimeout,
          requestOptions: RequestOptions(path: '/test'),
        );

        // Act
        final result = DioErrorHandler.isRetryable(dioException);

        // Assert
        expect(result, isTrue);
      });

      test('should return true for send timeout', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.sendTimeout,
          requestOptions: RequestOptions(path: '/test'),
        );

        // Act
        final result = DioErrorHandler.isRetryable(dioException);

        // Assert
        expect(result, isTrue);
      });

      test('should return true for receive timeout', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.receiveTimeout,
          requestOptions: RequestOptions(path: '/test'),
        );

        // Act
        final result = DioErrorHandler.isRetryable(dioException);

        // Assert
        expect(result, isTrue);
      });

      test('should return true for connection error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.connectionError,
          requestOptions: RequestOptions(path: '/test'),
        );

        // Act
        final result = DioErrorHandler.isRetryable(dioException);

        // Assert
        expect(result, isTrue);
      });

      test('should return true for 408 request timeout', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badResponse,
          requestOptions: RequestOptions(path: '/test'),
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 408,
          ),
        );

        // Act
        final result = DioErrorHandler.isRetryable(dioException);

        // Assert
        expect(result, isTrue);
      });

      test('should return true for 429 too many requests', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badResponse,
          requestOptions: RequestOptions(path: '/test'),
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 429,
          ),
        );

        // Act
        final result = DioErrorHandler.isRetryable(dioException);

        // Assert
        expect(result, isTrue);
      });

      test('should return true for 503 service unavailable', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badResponse,
          requestOptions: RequestOptions(path: '/test'),
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 503,
          ),
        );

        // Act
        final result = DioErrorHandler.isRetryable(dioException);

        // Assert
        expect(result, isTrue);
      });

      test('should return true for 504 gateway timeout', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badResponse,
          requestOptions: RequestOptions(path: '/test'),
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 504,
          ),
        );

        // Act
        final result = DioErrorHandler.isRetryable(dioException);

        // Assert
        expect(result, isTrue);
      });

      test('should return false for 400 bad request', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badResponse,
          requestOptions: RequestOptions(path: '/test'),
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 400,
          ),
        );

        // Act
        final result = DioErrorHandler.isRetryable(dioException);

        // Assert
        expect(result, isFalse);
      });

      test('should return false for 401 unauthorized', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badResponse,
          requestOptions: RequestOptions(path: '/test'),
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 401,
          ),
        );

        // Act
        final result = DioErrorHandler.isRetryable(dioException);

        // Assert
        expect(result, isFalse);
      });

      test('should return false for cancel error', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.cancel,
          requestOptions: RequestOptions(path: '/test'),
        );

        // Act
        final result = DioErrorHandler.isRetryable(dioException);

        // Assert
        expect(result, isFalse);
      });

      test('should return false for bad certificate', () {
        // Arrange
        final dioException = DioException(
          type: DioExceptionType.badCertificate,
          requestOptions: RequestOptions(path: '/test'),
        );

        // Act
        final result = DioErrorHandler.isRetryable(dioException);

        // Assert
        expect(result, isFalse);
      });
    });
  });
}
