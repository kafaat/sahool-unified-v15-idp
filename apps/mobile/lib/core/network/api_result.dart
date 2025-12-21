/// Sahool API Result Wrapper
/// نمط النتيجة للتعامل الآمن مع الشبكة
///
/// يضمن معالجة كل حالات الاستجابة:
/// - Success: البيانات وصلت بنجاح
/// - Failure: حدث خطأ مع رسالة واضحة

// Sealed class لإجبار معالجة كل الحالات
sealed class ApiResult<T> {
  const ApiResult();

  /// تحويل النتيجة باستخدام دالة
  R when<R>({
    required R Function(T data) success,
    required R Function(String message, int? statusCode) failure,
  }) {
    return switch (this) {
      Success<T>(data: final d) => success(d),
      Failure<T>(message: final m, statusCode: final c) => failure(m, c),
    };
  }

  /// تحويل البيانات في حالة النجاح فقط
  ApiResult<R> map<R>(R Function(T data) transform) {
    return switch (this) {
      Success<T>(data: final d) => Success(transform(d)),
      Failure<T>(message: final m, statusCode: final c) => Failure(m, statusCode: c),
    };
  }

  /// التحقق من النجاح
  bool get isSuccess => this is Success<T>;

  /// التحقق من الفشل
  bool get isFailure => this is Failure<T>;

  /// الحصول على البيانات (null إذا فشل)
  T? get dataOrNull => switch (this) {
    Success<T>(data: final d) => d,
    Failure<T>() => null,
  };

  /// الحصول على رسالة الخطأ (null إذا نجح)
  String? get errorOrNull => switch (this) {
    Success<T>() => null,
    Failure<T>(message: final m) => m,
  };
}

/// حالة النجاح مع البيانات
class Success<T> extends ApiResult<T> {
  final T data;
  const Success(this.data);

  @override
  String toString() => 'Success(data: $data)';

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Success<T> && runtimeType == other.runtimeType && data == other.data;

  @override
  int get hashCode => data.hashCode;
}

/// حالة الفشل مع رسالة الخطأ
class Failure<T> extends ApiResult<T> {
  final String message;
  final int? statusCode;
  final dynamic originalError;

  const Failure(
    this.message, {
    this.statusCode,
    this.originalError,
  });

  @override
  String toString() => 'Failure(message: $message, statusCode: $statusCode)';

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Failure<T> &&
          runtimeType == other.runtimeType &&
          message == other.message &&
          statusCode == other.statusCode;

  @override
  int get hashCode => message.hashCode ^ statusCode.hashCode;
}

/// أنواع الأخطاء الشائعة
enum ApiErrorType {
  network,       // لا يوجد اتصال
  timeout,       // انتهت المهلة
  server,        // خطأ السيرفر (5xx)
  unauthorized,  // غير مصرح (401)
  notFound,      // غير موجود (404)
  badRequest,    // طلب خاطئ (400)
  unknown,       // خطأ غير معروف
}

/// Extension للحصول على نوع الخطأ
extension FailureExtension<T> on Failure<T> {
  ApiErrorType get errorType {
    if (statusCode == null) return ApiErrorType.network;
    return switch (statusCode!) {
      401 => ApiErrorType.unauthorized,
      404 => ApiErrorType.notFound,
      400 => ApiErrorType.badRequest,
      >= 500 && < 600 => ApiErrorType.server,
      _ => ApiErrorType.unknown,
    };
  }
}
