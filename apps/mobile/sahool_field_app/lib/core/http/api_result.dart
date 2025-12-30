import 'api_error_handler.dart';

/// Type-safe result wrapper for API responses
/// This allows for functional error handling without exceptions
///
/// Usage:
/// ```dart
/// final result = await someApiCall();
/// result.when(
///   success: (data) => print('Success: $data'),
///   failure: (error) => print('Error: ${error.message}'),
/// );
/// ```
sealed class ApiResult<T> {
  const ApiResult();

  /// Create a successful result
  const factory ApiResult.success(T data) = Success<T>;

  /// Create a failed result
  const factory ApiResult.failure(ApiError error) = Failure<T>;

  /// Check if result is successful
  bool get isSuccess => this is Success<T>;

  /// Check if result is failed
  bool get isFailure => this is Failure<T>;

  /// Get data if success, null otherwise
  T? get dataOrNull => switch (this) {
        Success(data: final data) => data,
        Failure() => null,
      };

  /// Get error if failure, null otherwise
  ApiError? get errorOrNull => switch (this) {
        Success() => null,
        Failure(error: final error) => error,
      };

  /// Get data or throw error
  T get data => switch (this) {
        Success(data: final data) => data,
        Failure(error: final error) => throw error.exception,
      };

  /// Get data or return default value
  T getOrElse(T defaultValue) => switch (this) {
        Success(data: final data) => data,
        Failure() => defaultValue,
      };

  /// Get data or compute default value
  T getOrElseCompute(T Function() defaultValue) => switch (this) {
        Success(data: final data) => data,
        Failure() => defaultValue(),
      };

  /// Transform success value
  ApiResult<R> map<R>(R Function(T data) transform) => switch (this) {
        Success(data: final data) => Success(transform(data)),
        Failure(error: final error) => Failure(error),
      };

  /// Transform success value with another result
  ApiResult<R> flatMap<R>(ApiResult<R> Function(T data) transform) =>
      switch (this) {
        Success(data: final data) => transform(data),
        Failure(error: final error) => Failure(error),
      };

  /// Transform error
  ApiResult<T> mapError(ApiError Function(ApiError error) transform) =>
      switch (this) {
        Success(data: final data) => Success(data),
        Failure(error: final error) => Failure(transform(error)),
      };

  /// Handle both success and failure cases
  R when<R>({
    required R Function(T data) success,
    required R Function(ApiError error) failure,
  }) =>
      switch (this) {
        Success(data: final data) => success(data),
        Failure(error: final error) => failure(error),
      };

  /// Handle both cases with optional handlers
  void whenOrNull({
    void Function(T data)? success,
    void Function(ApiError error)? failure,
  }) {
    switch (this) {
      case Success(data: final data):
        success?.call(data);
        break;
      case Failure(error: final error):
        failure?.call(error);
        break;
    }
  }

  /// Execute action only on success
  ApiResult<T> onSuccess(void Function(T data) action) {
    if (this case Success(data: final data)) {
      action(data);
    }
    return this;
  }

  /// Execute action only on failure
  ApiResult<T> onFailure(void Function(ApiError error) action) {
    if (this case Failure(error: final error)) {
      action(error);
    }
    return this;
  }
}

/// Success result
final class Success<T> extends ApiResult<T> {
  final T data;

  const Success(this.data);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Success<T> &&
          runtimeType == other.runtimeType &&
          data == other.data;

  @override
  int get hashCode => data.hashCode;

  @override
  String toString() => 'Success(data: $data)';
}

/// Failure result
final class Failure<T> extends ApiResult<T> {
  final ApiError error;

  const Failure(this.error);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Failure<T> &&
          runtimeType == other.runtimeType &&
          error == other.error;

  @override
  int get hashCode => error.hashCode;

  @override
  String toString() => 'Failure(error: $error)';
}

/// Extension for Future<ApiResult<T>>
extension ApiResultFuture<T> on Future<ApiResult<T>> {
  /// Map success value asynchronously
  Future<ApiResult<R>> mapAsync<R>(
    Future<R> Function(T data) transform,
  ) async {
    final result = await this;
    return switch (result) {
      Success(data: final data) => Success(await transform(data)),
      Failure(error: final error) => Failure(error),
    };
  }

  /// FlatMap success value asynchronously
  Future<ApiResult<R>> flatMapAsync<R>(
    Future<ApiResult<R>> Function(T data) transform,
  ) async {
    final result = await this;
    return switch (result) {
      Success(data: final data) => await transform(data),
      Failure(error: final error) => Failure(error),
    };
  }

  /// Handle both cases asynchronously
  Future<R> whenAsync<R>({
    required Future<R> Function(T data) success,
    required Future<R> Function(ApiError error) failure,
  }) async {
    final result = await this;
    return switch (result) {
      Success(data: final data) => await success(data),
      Failure(error: final error) => await failure(error),
    };
  }

  /// Execute action only on success asynchronously
  Future<ApiResult<T>> onSuccessAsync(
    Future<void> Function(T data) action,
  ) async {
    final result = await this;
    if (result case Success(data: final data)) {
      await action(data);
    }
    return result;
  }

  /// Execute action only on failure asynchronously
  Future<ApiResult<T>> onFailureAsync(
    Future<void> Function(ApiError error) action,
  ) async {
    final result = await this;
    if (result case Failure(error: final error)) {
      await action(error);
    }
    return result;
  }
}
