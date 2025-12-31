import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/network/api_result.dart';

void main() {
  group('ApiResult', () {
    group('Success', () {
      test('should create Success with data', () {
        // Arrange & Act
        const result = Success<String>('test data');

        // Assert
        expect(result.data, 'test data');
        expect(result.isSuccess, isTrue);
        expect(result.isFailure, isFalse);
      });

      test('should return data from dataOrNull', () {
        // Arrange
        const result = Success<int>(42);

        // Act
        final data = result.dataOrNull;

        // Assert
        expect(data, 42);
      });

      test('should return null from errorOrNull', () {
        // Arrange
        const result = Success<String>('test');

        // Act
        final error = result.errorOrNull;

        // Assert
        expect(error, isNull);
      });

      test('should support equality comparison', () {
        // Arrange
        const result1 = Success<String>('test');
        const result2 = Success<String>('test');
        const result3 = Success<String>('other');

        // Assert
        expect(result1, equals(result2));
        expect(result1, isNot(equals(result3)));
      });

      test('should have correct hashCode', () {
        // Arrange
        const result1 = Success<String>('test');
        const result2 = Success<String>('test');

        // Assert
        expect(result1.hashCode, equals(result2.hashCode));
      });

      test('should have string representation', () {
        // Arrange
        const result = Success<String>('test data');

        // Act
        final str = result.toString();

        // Assert
        expect(str, contains('Success'));
        expect(str, contains('test data'));
      });
    });

    group('Failure', () {
      test('should create Failure with message', () {
        // Arrange & Act
        const result = Failure<String>('Error occurred');

        // Assert
        expect(result.message, 'Error occurred');
        expect(result.isSuccess, isFalse);
        expect(result.isFailure, isTrue);
      });

      test('should create Failure with status code', () {
        // Arrange & Act
        const result = Failure<String>('Not found', statusCode: 404);

        // Assert
        expect(result.message, 'Not found');
        expect(result.statusCode, 404);
      });

      test('should create Failure with original error', () {
        // Arrange
        final originalError = Exception('Original error');

        // Act
        final result = Failure<String>('Wrapped error', originalError: originalError);

        // Assert
        expect(result.message, 'Wrapped error');
        expect(result.originalError, originalError);
      });

      test('should return null from dataOrNull', () {
        // Arrange
        const result = Failure<int>('Error');

        // Act
        final data = result.dataOrNull;

        // Assert
        expect(data, isNull);
      });

      test('should return error from errorOrNull', () {
        // Arrange
        const result = Failure<String>('Test error');

        // Act
        final error = result.errorOrNull;

        // Assert
        expect(error, 'Test error');
      });

      test('should support equality comparison', () {
        // Arrange
        const result1 = Failure<String>('error', statusCode: 404);
        const result2 = Failure<String>('error', statusCode: 404);
        const result3 = Failure<String>('error', statusCode: 500);

        // Assert
        expect(result1, equals(result2));
        expect(result1, isNot(equals(result3)));
      });

      test('should have correct hashCode', () {
        // Arrange
        const result1 = Failure<String>('error', statusCode: 404);
        const result2 = Failure<String>('error', statusCode: 404);

        // Assert
        expect(result1.hashCode, equals(result2.hashCode));
      });

      test('should have string representation', () {
        // Arrange
        const result = Failure<String>('Test error', statusCode: 500);

        // Act
        final str = result.toString();

        // Assert
        expect(str, contains('Failure'));
        expect(str, contains('Test error'));
        expect(str, contains('500'));
      });
    });

    group('when', () {
      test('should call success callback for Success', () {
        // Arrange
        const result = Success<int>(42);
        String? calledWith;

        // Act
        final output = result.when(
          success: (data) {
            calledWith = 'success: $data';
            return calledWith!;
          },
          failure: (message, statusCode) => 'failure: $message',
        );

        // Assert
        expect(calledWith, 'success: 42');
        expect(output, 'success: 42');
      });

      test('should call failure callback for Failure', () {
        // Arrange
        const result = Failure<int>('Error occurred', statusCode: 500);
        String? calledWith;

        // Act
        final output = result.when(
          success: (data) => 'success: $data',
          failure: (message, statusCode) {
            calledWith = 'failure: $message ($statusCode)';
            return calledWith!;
          },
        );

        // Assert
        expect(calledWith, 'failure: Error occurred (500)');
        expect(output, 'failure: Error occurred (500)');
      });
    });

    group('map', () {
      test('should transform data for Success', () {
        // Arrange
        const result = Success<int>(42);

        // Act
        final mapped = result.map((data) => data * 2);

        // Assert
        expect(mapped, isA<Success<int>>());
        expect(mapped.dataOrNull, 84);
      });

      test('should preserve error for Failure', () {
        // Arrange
        const result = Failure<int>('Error', statusCode: 500);

        // Act
        final mapped = result.map((data) => data * 2);

        // Assert
        expect(mapped, isA<Failure<int>>());
        expect(mapped.errorOrNull, 'Error');
        expect((mapped as Failure).statusCode, 500);
      });

      test('should allow type transformation', () {
        // Arrange
        const result = Success<int>(42);

        // Act
        final mapped = result.map((data) => data.toString());

        // Assert
        expect(mapped, isA<Success<String>>());
        expect(mapped.dataOrNull, '42');
      });
    });

    group('FailureExtension', () {
      test('should return network error type when status code is null', () {
        // Arrange
        const failure = Failure<String>('Network error');

        // Act
        final errorType = failure.errorType;

        // Assert
        expect(errorType, ApiErrorType.network);
      });

      test('should return unauthorized error type for 401', () {
        // Arrange
        const failure = Failure<String>('Unauthorized', statusCode: 401);

        // Act
        final errorType = failure.errorType;

        // Assert
        expect(errorType, ApiErrorType.unauthorized);
      });

      test('should return notFound error type for 404', () {
        // Arrange
        const failure = Failure<String>('Not found', statusCode: 404);

        // Act
        final errorType = failure.errorType;

        // Assert
        expect(errorType, ApiErrorType.notFound);
      });

      test('should return badRequest error type for 400', () {
        // Arrange
        const failure = Failure<String>('Bad request', statusCode: 400);

        // Act
        final errorType = failure.errorType;

        // Assert
        expect(errorType, ApiErrorType.badRequest);
      });

      test('should return server error type for 500', () {
        // Arrange
        const failure = Failure<String>('Server error', statusCode: 500);

        // Act
        final errorType = failure.errorType;

        // Assert
        expect(errorType, ApiErrorType.server);
      });

      test('should return server error type for 503', () {
        // Arrange
        const failure = Failure<String>('Service unavailable', statusCode: 503);

        // Act
        final errorType = failure.errorType;

        // Assert
        expect(errorType, ApiErrorType.server);
      });

      test('should return unknown error type for other status codes', () {
        // Arrange
        const failure = Failure<String>('Unknown error', statusCode: 418);

        // Act
        final errorType = failure.errorType;

        // Assert
        expect(errorType, ApiErrorType.unknown);
      });
    });

    group('Complex scenarios', () {
      test('should handle nested transformations', () {
        // Arrange
        const result = Success<int>(10);

        // Act
        final mapped = result
            .map((x) => x * 2)  // 20
            .map((x) => x + 5)  // 25
            .map((x) => x.toString()); // "25"

        // Assert
        expect(mapped.dataOrNull, '25');
      });

      test('should preserve failure through multiple maps', () {
        // Arrange
        const result = Failure<int>('Initial error', statusCode: 500);

        // Act
        final mapped = result
            .map((x) => x * 2)
            .map((x) => x + 5)
            .map((x) => x.toString());

        // Assert
        expect(mapped.isFailure, isTrue);
        expect(mapped.errorOrNull, 'Initial error');
      });

      test('should work with complex data types', () {
        // Arrange
        final userData = {'name': 'Ahmed', 'age': 30};
        final result = Success<Map<String, dynamic>>(userData);

        // Act
        final mapped = result.map((user) => user['name'] as String);

        // Assert
        expect(mapped.dataOrNull, 'Ahmed');
      });

      test('should handle list transformations', () {
        // Arrange
        const numbers = [1, 2, 3, 4, 5];
        const result = Success<List<int>>(numbers);

        // Act
        final mapped = result.map((list) => list.where((n) => n.isEven).toList());

        // Assert
        expect(mapped.dataOrNull, [2, 4]);
      });
    });
  });
}
