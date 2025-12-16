/// SAHOOL Market Repository
/// مستودع السوق - Clean Architecture Pattern
///
/// يوفر طبقة تجريد للوصول إلى بيانات السوق والمحفظة
/// مع استخدام نمط ApiResult للتعامل الآمن مع الأخطاء

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/config/api_config.dart';
import '../../../core/network/api_result.dart';
import 'market_models.dart';

// =============================================================================
// Providers
// =============================================================================

/// مزود Repository السوق
final marketRepoProvider = Provider<MarketRepository>((ref) {
  return MarketRepository();
});

/// مزود معرف المستخدم الحالي
final currentUserIdProvider = StateProvider<String>((ref) => 'user-demo-123');

/// مزود المحفظة
final walletFutureProvider = FutureProvider<ApiResult<WalletModel>>((ref) async {
  final userId = ref.watch(currentUserIdProvider);
  return ref.read(marketRepoProvider).getWallet(userId);
});

/// مزود المنتجات
final productsFutureProvider = FutureProvider.family<ApiResult<List<ProductModel>>, String?>((ref, category) async {
  return ref.read(marketRepoProvider).getProducts(category: category);
});

/// مزود المنتجات المميزة
final featuredProductsProvider = FutureProvider<ApiResult<List<ProductModel>>>((ref) async {
  return ref.read(marketRepoProvider).getFeaturedProducts();
});

/// مزود إحصائيات السوق
final marketStatsProvider = FutureProvider<ApiResult<MarketStats>>((ref) async {
  return ref.read(marketRepoProvider).getMarketStats();
});

/// مزود طلبات المستخدم
final userOrdersProvider = FutureProvider<ApiResult<List<OrderModel>>>((ref) async {
  final userId = ref.watch(currentUserIdProvider);
  return ref.read(marketRepoProvider).getUserOrders(userId);
});

/// مزود قروض المستخدم
final userLoansProvider = FutureProvider.family<ApiResult<List<LoanModel>>, String>((ref, walletId) async {
  return ref.read(marketRepoProvider).getUserLoans(walletId);
});

// =============================================================================
// Repository
// =============================================================================

/// مستودع السوق والمحفظة
class MarketRepository {
  final Dio _dio;

  MarketRepository({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              connectTimeout: ApiConfig.connectTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  // ═══════════════════════════════════════════════════════════════════════════
  // المحفظة - Wallet
  // ═══════════════════════════════════════════════════════════════════════════

  /// جلب محفظة المستخدم
  Future<ApiResult<WalletModel>> getWallet(String userId) async {
    try {
      final response = await _dio.get(ApiConfig.wallet(userId));
      return Success(WalletModel.fromJson(response.data));
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل تحميل المحفظة'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// إيداع في المحفظة
  Future<ApiResult<WalletModel>> deposit(String walletId, double amount, {String? description}) async {
    try {
      final response = await _dio.post(
        ApiConfig.walletDeposit(walletId),
        data: {
          'amount': amount,
          'description': description,
        },
      );
      return Success(WalletModel.fromJson(response.data['wallet']));
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل الإيداع'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// سحب من المحفظة
  Future<ApiResult<WalletModel>> withdraw(String walletId, double amount, {String? description}) async {
    try {
      final response = await _dio.post(
        ApiConfig.walletWithdraw(walletId),
        data: {
          'amount': amount,
          'description': description,
        },
      );
      return Success(WalletModel.fromJson(response.data['wallet']));
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل السحب'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// جلب سجل المعاملات
  Future<ApiResult<List<TransactionModel>>> getTransactions(String walletId, {int limit = 20}) async {
    try {
      final response = await _dio.get(
        ApiConfig.walletTransactions(walletId),
        queryParameters: {'limit': limit},
      );
      final List data = response.data;
      return Success(data.map((e) => TransactionModel.fromJson(e)).toList());
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل تحميل المعاملات'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// حساب التصنيف الائتماني
  Future<ApiResult<CreditScoreResult>> calculateCreditScore(String userId, FarmData farmData) async {
    try {
      final response = await _dio.post(
        ApiConfig.calculateCreditScore,
        data: {
          'userId': userId,
          'farmData': farmData.toJson(),
        },
      );
      return Success(CreditScoreResult.fromJson(response.data));
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل حساب التصنيف'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // القروض - Loans
  // ═══════════════════════════════════════════════════════════════════════════

  /// طلب قرض جديد
  Future<ApiResult<LoanRequestResult>> requestLoan({
    required String walletId,
    required double amount,
    required int termMonths,
    required String purpose,
    String? purposeDetails,
    String? collateralType,
    double? collateralValue,
  }) async {
    try {
      final response = await _dio.post(
        ApiConfig.loans,
        data: {
          'walletId': walletId,
          'amount': amount,
          'termMonths': termMonths,
          'purpose': purpose,
          'purposeDetails': purposeDetails,
          'collateralType': collateralType,
          'collateralValue': collateralValue,
        },
      );
      return Success(LoanRequestResult.fromJson(response.data));
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل طلب القرض'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// جلب قروض المستخدم
  Future<ApiResult<List<LoanModel>>> getUserLoans(String walletId) async {
    try {
      final response = await _dio.get(ApiConfig.userLoans(walletId));
      final List data = response.data;
      return Success(data.map((e) => LoanModel.fromJson(e)).toList());
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل تحميل القروض'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// سداد قرض
  Future<ApiResult<LoanRepaymentResult>> repayLoan(String loanId, double amount) async {
    try {
      final response = await _dio.post(
        ApiConfig.repayLoan(loanId),
        data: {'amount': amount},
      );
      return Success(LoanRepaymentResult.fromJson(response.data));
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل السداد'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // السوق - Marketplace
  // ═══════════════════════════════════════════════════════════════════════════

  /// جلب المنتجات
  Future<ApiResult<List<ProductModel>>> getProducts({
    String? category,
    String? governorate,
    double? minPrice,
    double? maxPrice,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (category != null) queryParams['category'] = category;
      if (governorate != null) queryParams['governorate'] = governorate;
      if (minPrice != null) queryParams['minPrice'] = minPrice;
      if (maxPrice != null) queryParams['maxPrice'] = maxPrice;

      final response = await _dio.get(
        ApiConfig.marketProducts,
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      );
      final List data = response.data;
      return Success(data.map((e) => ProductModel.fromJson(e)).toList());
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل تحميل المنتجات'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// جلب المنتجات المميزة
  Future<ApiResult<List<ProductModel>>> getFeaturedProducts() async {
    final result = await getProducts();
    return result.map((products) => products.where((p) => p.featured).toList());
  }

  /// جلب منتج بالمعرف
  Future<ApiResult<ProductModel>> getProductById(String productId) async {
    try {
      final response = await _dio.get(ApiConfig.marketProductById(productId));
      return Success(ProductModel.fromJson(response.data));
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل تحميل المنتج'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// عرض الحصاد في السوق
  Future<ApiResult<ProductModel>> listHarvest({
    required String userId,
    required String crop,
    required String cropAr,
    required double predictedYieldTons,
    required double pricePerTon,
    String? harvestDate,
    String? qualityGrade,
    String? governorate,
  }) async {
    try {
      final response = await _dio.post(
        ApiConfig.listHarvest,
        data: {
          'userId': userId,
          'yieldData': {
            'crop': crop,
            'cropAr': cropAr,
            'predictedYieldTons': predictedYieldTons,
            'pricePerTon': pricePerTon,
            'harvestDate': harvestDate,
            'qualityGrade': qualityGrade,
            'governorate': governorate,
          },
        },
      );
      return Success(ProductModel.fromJson(response.data));
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل عرض الحصاد'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// إنشاء طلب شراء
  Future<ApiResult<OrderModel>> createOrder({
    required String buyerId,
    required List<CartItem> items,
    String? deliveryAddress,
    String? paymentMethod,
  }) async {
    try {
      final response = await _dio.post(
        ApiConfig.marketOrders,
        data: {
          'buyerId': buyerId,
          'items': items.map((item) => {
            'productId': item.productId,
            'quantity': item.quantity,
          }).toList(),
          'deliveryAddress': deliveryAddress,
          'paymentMethod': paymentMethod,
        },
      );
      return Success(OrderModel.fromJson(response.data));
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل إنشاء الطلب'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// جلب طلبات المستخدم
  Future<ApiResult<List<OrderModel>>> getUserOrders(String userId, {String role = 'buyer'}) async {
    try {
      final response = await _dio.get(
        ApiConfig.userMarketOrders(userId),
        queryParameters: {'role': role},
      );
      final List data = response.data;
      return Success(data.map((e) => OrderModel.fromJson(e)).toList());
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل تحميل الطلبات'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// جلب إحصائيات السوق
  Future<ApiResult<MarketStats>> getMarketStats() async {
    try {
      final response = await _dio.get(ApiConfig.marketStats);
      return Success(MarketStats.fromJson(response.data));
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل تحميل الإحصائيات'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Helper Methods
  // ═══════════════════════════════════════════════════════════════════════════

  String _getErrorMessage(DioException e, String defaultMessage) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return 'انتهت مهلة الاتصال. تحقق من اتصالك بالإنترنت.';
    }

    if (e.type == DioExceptionType.connectionError) {
      return 'لا يمكن الاتصال بالخادم. تأكد من اتصالك بالإنترنت.';
    }

    if (e.response?.data != null && e.response?.data is Map) {
      final data = e.response?.data as Map;
      if (data.containsKey('message')) {
        return data['message'].toString();
      }
      if (data.containsKey('detail')) {
        return data['detail'].toString();
      }
    }

    return defaultMessage;
  }
}
