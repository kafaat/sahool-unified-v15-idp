/// خدمة بوابة ثروات للمدفوعات
/// Tharwatt Payment Gateway Service
///
/// بوابة المدفوعات المحلية اليمنية
/// https://developers-test.tharwatt.com:5253/

import 'package:dio/dio.dart';
import '../../../core/network/api_result.dart';
import 'payment_models.dart';

/// خدمة ثروات للمدفوعات
class TharwattPaymentService {
  final Dio _dio;
  final TharwattConfig config;

  TharwattPaymentService({
    required this.config,
    Dio? dio,
  }) : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: config.baseUrl,
              connectTimeout: const Duration(seconds: 30),
              receiveTimeout: const Duration(seconds: 30),
              headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                if (config.apiKey != null) 'X-API-Key': config.apiKey,
                if (config.merchantId != null) 'X-Merchant-Id': config.merchantId,
              },
            ));

  /// بدء عملية إيداع
  Future<ApiResult<TharwattPaymentResponse>> initiateDeposit({
    required String walletId,
    required double amount,
    required String phoneNumber,
    String? description,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/payment/deposit',
        data: {
          'walletId': walletId,
          'amount': amount,
          'currency': 'YER',
          'phoneNumber': phoneNumber,
          'description': description ?? 'إيداع في محفظة SAHOOL',
          'callbackUrl': 'sahool://payment/callback',
          'metadata': {
            'source': 'sahool_app',
            'type': 'deposit',
          },
        },
      );

      final paymentResponse = TharwattPaymentResponse.fromJson(response.data);
      return Success(paymentResponse);
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e),
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      return Failure('حدث خطأ غير متوقع: $e');
    }
  }

  /// بدء عملية سحب
  Future<ApiResult<TharwattPaymentResponse>> initiateWithdraw({
    required String walletId,
    required double amount,
    required String phoneNumber,
    String? accountNumber,
    String? description,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/payment/withdraw',
        data: {
          'walletId': walletId,
          'amount': amount,
          'currency': 'YER',
          'phoneNumber': phoneNumber,
          'accountNumber': accountNumber,
          'description': description ?? 'سحب من محفظة SAHOOL',
          'callbackUrl': 'sahool://payment/callback',
          'metadata': {
            'source': 'sahool_app',
            'type': 'withdraw',
          },
        },
      );

      final paymentResponse = TharwattPaymentResponse.fromJson(response.data);
      return Success(paymentResponse);
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e),
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      return Failure('حدث خطأ غير متوقع: $e');
    }
  }

  /// بدء عملية تحويل
  Future<ApiResult<TharwattPaymentResponse>> initiateTransfer({
    required String fromWalletId,
    required String toPhoneNumber,
    required double amount,
    String? description,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/payment/transfer',
        data: {
          'fromWalletId': fromWalletId,
          'toPhoneNumber': toPhoneNumber,
          'amount': amount,
          'currency': 'YER',
          'description': description ?? 'تحويل عبر SAHOOL',
          'callbackUrl': 'sahool://payment/callback',
          'metadata': {
            'source': 'sahool_app',
            'type': 'transfer',
          },
        },
      );

      final paymentResponse = TharwattPaymentResponse.fromJson(response.data);
      return Success(paymentResponse);
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e),
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      return Failure('حدث خطأ غير متوقع: $e');
    }
  }

  /// شحن رصيد موبايل
  Future<ApiResult<TharwattPaymentResponse>> topupMobile({
    required String walletId,
    required String mobileNumber,
    required double amount,
    required String operator, // 'yemen_mobile', 'mtn', 'sabafon', 'y'
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/payment/topup',
        data: {
          'walletId': walletId,
          'mobileNumber': mobileNumber,
          'amount': amount,
          'operator': operator,
          'currency': 'YER',
          'callbackUrl': 'sahool://payment/callback',
        },
      );

      final paymentResponse = TharwattPaymentResponse.fromJson(response.data);
      return Success(paymentResponse);
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e),
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      return Failure('حدث خطأ غير متوقع: $e');
    }
  }

  /// التحقق من حالة المعاملة
  Future<ApiResult<PaymentTransaction>> checkTransactionStatus(
    String transactionId,
  ) async {
    try {
      final response = await _dio.get(
        '/api/v1/payment/status/$transactionId',
      );

      final transaction = PaymentTransaction.fromJson(response.data);
      return Success(transaction);
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e),
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      return Failure('حدث خطأ غير متوقع: $e');
    }
  }

  /// الحصول على سجل المعاملات
  Future<ApiResult<List<PaymentTransaction>>> getTransactionHistory({
    required String walletId,
    int page = 1,
    int limit = 20,
    String? status,
    String? type,
  }) async {
    try {
      final response = await _dio.get(
        '/api/v1/payment/transactions',
        queryParameters: {
          'walletId': walletId,
          'page': page,
          'limit': limit,
          if (status != null) 'status': status,
          if (type != null) 'type': type,
        },
      );

      final List<dynamic> data = response.data['data'] ?? response.data;
      final transactions =
          data.map((json) => PaymentTransaction.fromJson(json)).toList();
      return Success(transactions);
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e),
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      return Failure('حدث خطأ غير متوقع: $e');
    }
  }

  /// التحقق من رصيد المحفظة
  Future<ApiResult<double>> checkBalance(String walletId) async {
    try {
      final response = await _dio.get(
        '/api/v1/payment/balance/$walletId',
      );

      final balance = (response.data['balance'] ?? 0).toDouble();
      return Success(balance);
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e),
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      return Failure('حدث خطأ غير متوقع: $e');
    }
  }

  /// التحقق من صحة رقم الهاتف
  Future<ApiResult<bool>> validatePhoneNumber(String phoneNumber) async {
    try {
      final response = await _dio.post(
        '/api/v1/payment/validate-phone',
        data: {'phoneNumber': phoneNumber},
      );

      final isValid = response.data['valid'] == true;
      return Success(isValid);
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e),
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      return Failure('حدث خطأ غير متوقع: $e');
    }
  }

  /// الحصول على قائمة المشغلين المدعومين
  Future<ApiResult<List<MobileOperator>>> getSupportedOperators() async {
    try {
      final response = await _dio.get('/api/v1/payment/operators');

      final List<dynamic> data = response.data['operators'] ?? response.data;
      final operators =
          data.map((json) => MobileOperator.fromJson(json)).toList();
      return Success(operators);
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e),
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      return Failure('حدث خطأ غير متوقع: $e');
    }
  }

  /// إلغاء معاملة معلقة
  Future<ApiResult<bool>> cancelTransaction(String transactionId) async {
    try {
      await _dio.post(
        '/api/v1/payment/cancel/$transactionId',
      );
      return const Success(true);
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e),
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      return Failure('حدث خطأ غير متوقع: $e');
    }
  }

  /// تحويل أخطاء Dio إلى رسائل عربية
  String _getErrorMessage(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
        return 'انتهت مهلة الاتصال. يرجى التحقق من اتصالك بالإنترنت.';
      case DioExceptionType.sendTimeout:
        return 'انتهت مهلة إرسال البيانات.';
      case DioExceptionType.receiveTimeout:
        return 'انتهت مهلة استلام البيانات.';
      case DioExceptionType.badCertificate:
        return 'خطأ في شهادة الأمان.';
      case DioExceptionType.badResponse:
        return _parseErrorResponse(e.response);
      case DioExceptionType.cancel:
        return 'تم إلغاء العملية.';
      case DioExceptionType.connectionError:
        return 'خطأ في الاتصال. يرجى التحقق من اتصالك بالإنترنت.';
      case DioExceptionType.unknown:
      default:
        return 'حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.';
    }
  }

  String _parseErrorResponse(Response? response) {
    if (response == null) {
      return 'لم يتم استلام استجابة من الخادم.';
    }

    final statusCode = response.statusCode;
    final data = response.data;

    // محاولة استخراج رسالة الخطأ من الاستجابة
    String? message;
    if (data is Map) {
      message = data['message'] ?? data['error'] ?? data['msg'];
    }

    switch (statusCode) {
      case 400:
        return message ?? 'طلب غير صحيح. يرجى التحقق من البيانات المدخلة.';
      case 401:
        return 'غير مصرح. يرجى تسجيل الدخول مرة أخرى.';
      case 403:
        return 'ليس لديك صلاحية للقيام بهذه العملية.';
      case 404:
        return message ?? 'لم يتم العثور على المورد المطلوب.';
      case 422:
        return message ?? 'البيانات المدخلة غير صحيحة.';
      case 429:
        return 'تم تجاوز الحد الأقصى للطلبات. يرجى الانتظار قليلاً.';
      case 500:
        return 'خطأ في الخادم. يرجى المحاولة لاحقاً.';
      case 502:
        return 'بوابة الدفع غير متاحة حالياً.';
      case 503:
        return 'الخدمة غير متاحة مؤقتاً.';
      default:
        return message ?? 'حدث خطأ (رمز: $statusCode)';
    }
  }
}

/// مشغل الهاتف المحمول
class MobileOperator {
  final String id;
  final String name;
  final String nameAr;
  final String? logo;
  final List<double> denominations;

  MobileOperator({
    required this.id,
    required this.name,
    required this.nameAr,
    this.logo,
    this.denominations = const [],
  });

  factory MobileOperator.fromJson(Map<String, dynamic> json) {
    return MobileOperator(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      nameAr: json['nameAr'] ?? json['name_ar'] ?? json['name'] ?? '',
      logo: json['logo'],
      denominations: (json['denominations'] as List<dynamic>?)
              ?.map((e) => (e as num).toDouble())
              .toList() ??
          [],
    );
  }

  /// المشغلين الافتراضيين
  static List<MobileOperator> get defaultOperators => [
        MobileOperator(
          id: 'yemen_mobile',
          name: 'Yemen Mobile',
          nameAr: 'يمن موبايل',
          denominations: [100, 200, 500, 1000, 2000],
        ),
        MobileOperator(
          id: 'mtn',
          name: 'MTN Yemen',
          nameAr: 'MTN اليمن',
          denominations: [100, 200, 500, 1000, 2000],
        ),
        MobileOperator(
          id: 'sabafon',
          name: 'Sabafon',
          nameAr: 'سبأفون',
          denominations: [100, 200, 500, 1000, 2000],
        ),
        MobileOperator(
          id: 'y_telecom',
          name: 'Y Telecom',
          nameAr: 'واي',
          denominations: [100, 200, 500, 1000, 2000],
        ),
      ];
}
