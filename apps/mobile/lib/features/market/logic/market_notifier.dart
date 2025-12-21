/// SAHOOL Market Notifier
/// إدارة حالة السوق - Clean Architecture Pattern
///
/// يفصل منطق البيع عن الواجهة ويوفر حالات واضحة للتتبع

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_result.dart';
import '../data/market_repository.dart';

// =============================================================================
// حالات العملية - Market Status
// =============================================================================

/// حالات عملية البيع
enum MarketStatus {
  /// الحالة الأولية
  initial,

  /// جاري التحميل
  loading,

  /// تم بنجاح
  success,

  /// حدث خطأ
  error,
}

// =============================================================================
// حالة السوق - Market State
// =============================================================================

/// حالة السوق الكاملة
class MarketState {
  final MarketStatus status;
  final String? errorMessage;
  final String? successMessage;
  final DateTime? lastUpdated;

  const MarketState({
    this.status = MarketStatus.initial,
    this.errorMessage,
    this.successMessage,
    this.lastUpdated,
  });

  /// نسخة محدثة من الحالة
  MarketState copyWith({
    MarketStatus? status,
    String? errorMessage,
    String? successMessage,
    DateTime? lastUpdated,
  }) {
    return MarketState(
      status: status ?? this.status,
      errorMessage: errorMessage,
      successMessage: successMessage,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }

  /// هل العملية جارية؟
  bool get isLoading => status == MarketStatus.loading;

  /// هل العملية ناجحة؟
  bool get isSuccess => status == MarketStatus.success;

  /// هل حدث خطأ؟
  bool get isError => status == MarketStatus.error;

  @override
  String toString() => 'MarketState(status: $status, error: $errorMessage)';
}

// =============================================================================
// Market Notifier
// =============================================================================

/// مدير حالة السوق
class MarketNotifier extends StateNotifier<MarketState> {
  final MarketRepository _repo;

  MarketNotifier(this._repo) : super(const MarketState());

  /// بيع الحصاد المتوقع
  ///
  /// يرسل بيانات الحصاد إلى الخادم لعرضها في السوق
  Future<void> sellHarvest(Map<String, dynamic> yieldData) async {
    // تحديث الحالة إلى جاري التحميل
    state = state.copyWith(status: MarketStatus.loading);

    // محاكاة تأخير بسيط لجمالية الـ UI
    await Future.delayed(const Duration(milliseconds: 800));

    // إرسال الطلب
    final result = await _repo.listHarvestForSale('user-demo-123', yieldData);

    // معالجة النتيجة
    switch (result) {
      case Success():
        state = state.copyWith(
          status: MarketStatus.success,
          successMessage: 'تم طرح المحصول في السوق بنجاح!',
          lastUpdated: DateTime.now(),
        );
        // إعادة الحالة للأولية بعد فترة
        _resetStateAfterDelay();
        break;

      case Failure(message: final msg):
        state = state.copyWith(
          status: MarketStatus.error,
          errorMessage: msg,
        );
        break;
    }
  }

  /// إعادة تعيين الحالة
  void reset() {
    state = const MarketState();
  }

  /// إعادة الحالة للأولية بعد فترة
  void _resetStateAfterDelay() {
    Future.delayed(const Duration(seconds: 3), () {
      if (mounted) {
        state = const MarketState();
      }
    });
  }
}

// =============================================================================
// بيانات الحصاد المتوقع - Yield Data
// =============================================================================

/// نموذج بيانات الحصاد للبيع
class HarvestSaleData {
  final String cropType;
  final String cropTypeAr;
  final double predictedYieldTons;
  final double pricePerTon;
  final String? harvestDate;
  final String? qualityGrade;
  final String? governorate;
  final double? aiConfidence;

  const HarvestSaleData({
    required this.cropType,
    required this.cropTypeAr,
    required this.predictedYieldTons,
    required this.pricePerTon,
    this.harvestDate,
    this.qualityGrade,
    this.governorate,
    this.aiConfidence,
  });

  /// القيمة الإجمالية المتوقعة
  double get totalValue => predictedYieldTons * pricePerTon;

  /// تحويل إلى Map للـ API
  Map<String, dynamic> toMap() => {
        'crop_type': cropType,
        'crop_type_ar': cropTypeAr,
        'predicted_yield_tons': predictedYieldTons,
        'price_per_ton': pricePerTon,
        'harvest_date': harvestDate,
        'quality_grade': qualityGrade,
        'governorate': governorate,
        'ai_confidence': aiConfidence,
        'total_value': totalValue,
      };

  /// إنشاء من بيانات yield-engine
  factory HarvestSaleData.fromYieldEngine(Map<String, dynamic> data) {
    return HarvestSaleData(
      cropType: data['crop'] ?? data['crop_type'] ?? 'Unknown',
      cropTypeAr: data['cropAr'] ?? data['crop_type_ar'] ?? 'غير معروف',
      predictedYieldTons: (data['predictedYieldTons'] ?? data['predicted_yield_tons'] ?? 0).toDouble(),
      pricePerTon: (data['marketPrice'] ?? data['price_per_ton'] ?? 0).toDouble(),
      harvestDate: data['harvestDate'] ?? data['harvest_date'],
      qualityGrade: data['qualityGrade'] ?? data['quality_grade'],
      governorate: data['governorate'],
      aiConfidence: (data['confidence'] ?? data['ai_confidence'])?.toDouble(),
    );
  }

  /// بيانات تجريبية للعرض
  static HarvestSaleData get demo => const HarvestSaleData(
        cropType: 'Wheat',
        cropTypeAr: 'قمح',
        predictedYieldTons: 12.5,
        pricePerTon: 320000,
        harvestDate: '2025-02-15',
        qualityGrade: 'A',
        governorate: 'صنعاء',
        aiConfidence: 0.87,
      );
}

// =============================================================================
// Providers
// =============================================================================

/// مزود حالة السوق
final marketNotifierProvider = StateNotifierProvider<MarketNotifier, MarketState>((ref) {
  return MarketNotifier(ref.read(marketRepoProvider));
});

/// مزود بيانات الحصاد المتوقع (من yield-engine)
final harvestSaleDataProvider = StateProvider<HarvestSaleData?>((ref) => null);

/// مزود البيانات التجريبية
final demoHarvestDataProvider = Provider<HarvestSaleData>((ref) {
  return HarvestSaleData.demo;
});
