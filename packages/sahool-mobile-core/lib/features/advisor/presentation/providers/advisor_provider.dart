/// Advisor Feature Provider - Riverpod State Management
/// موفر ميزة المستشار - إدارة الحالة بـ Riverpod
///
/// Manages agricultural advisory recommendations including
/// irrigation, fertilizer, and pest management advice.
/// Complements the existing advisor_providers.dart (form-level providers)
/// with a screen-level StateNotifier for the full advisory dashboard.
library;

import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import '../../../../core/config/api_config.dart';

// =============================================================================
// Recommendation Model
// نموذج التوصية
// =============================================================================

/// Priority level for recommendations
/// مستوى أولوية التوصيات
enum RecommendationPriority {
  critical('critical', 'حرج'),
  warning('warning', 'تحذير'),
  advisory('advisory', 'استشارة'),
  info('info', 'معلومات');

  final String code;
  final String nameAr;
  const RecommendationPriority(this.code, this.nameAr);
}

/// Type of recommendation
/// نوع التوصية
enum RecommendationType {
  irrigation('irrigation', 'ري', 'Irrigation'),
  fertilizer('fertilizer', 'تسميد', 'Fertilizer'),
  pest('pest', 'آفات', 'Pest Control'),
  disease('disease', 'امراض', 'Disease'),
  weather('weather', 'طقس', 'Weather'),
  harvest('harvest', 'حصاد', 'Harvest'),
  general('general', 'عام', 'General');

  final String code;
  final String nameAr;
  final String nameEn;
  const RecommendationType(this.code, this.nameAr, this.nameEn);
}

/// Agricultural recommendation
/// توصية زراعية
class Recommendation {
  final String id;
  final RecommendationType type;
  final RecommendationPriority priority;
  final String title;
  final String titleAr;
  final String description;
  final String descriptionAr;
  final String? fieldId;
  final String? fieldName;
  final String? actionLabel;
  final String? actionLabelAr;
  final double? estimatedCost;
  final double? estimatedROI;
  final String? roiExplanation;
  final String? roiExplanationAr;
  final DateTime createdAt;
  final bool isCompleted;

  const Recommendation({
    required this.id,
    required this.type,
    required this.priority,
    required this.title,
    required this.titleAr,
    required this.description,
    required this.descriptionAr,
    this.fieldId,
    this.fieldName,
    this.actionLabel,
    this.actionLabelAr,
    this.estimatedCost,
    this.estimatedROI,
    this.roiExplanation,
    this.roiExplanationAr,
    required this.createdAt,
    this.isCompleted = false,
  });

  Recommendation copyWith({bool? isCompleted}) {
    return Recommendation(
      id: id,
      type: type,
      priority: priority,
      title: title,
      titleAr: titleAr,
      description: description,
      descriptionAr: descriptionAr,
      fieldId: fieldId,
      fieldName: fieldName,
      actionLabel: actionLabel,
      actionLabelAr: actionLabelAr,
      estimatedCost: estimatedCost,
      estimatedROI: estimatedROI,
      roiExplanation: roiExplanation,
      roiExplanationAr: roiExplanationAr,
      createdAt: createdAt,
      isCompleted: isCompleted ?? this.isCompleted,
    );
  }
}

// =============================================================================
// State
// الحالة
// =============================================================================

/// Advisor dashboard state
/// حالة لوحة المستشار
class AdvisorDashboardState {
  final List<Recommendation> recommendations;
  final bool isLoading;
  final String? error;
  final String? selectedFieldId;

  const AdvisorDashboardState({
    this.recommendations = const [],
    this.isLoading = false,
    this.error,
    this.selectedFieldId,
  });

  AdvisorDashboardState copyWith({
    List<Recommendation>? recommendations,
    bool? isLoading,
    String? error,
    String? selectedFieldId,
  }) {
    return AdvisorDashboardState(
      recommendations: recommendations ?? this.recommendations,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      selectedFieldId: selectedFieldId ?? this.selectedFieldId,
    );
  }

  /// Get recommendations sorted by priority
  /// الحصول على التوصيات مرتبة حسب الاولوية
  List<Recommendation> get sortedRecommendations {
    final sorted = List<Recommendation>.from(recommendations);
    sorted.sort((a, b) => a.priority.index.compareTo(b.priority.index));
    return sorted;
  }

  /// Critical and warning recommendations
  /// التوصيات الحرجة والتحذيرية
  List<Recommendation> get urgentRecommendations =>
      recommendations
          .where((r) =>
              r.priority == RecommendationPriority.critical ||
              r.priority == RecommendationPriority.warning)
          .toList();

  /// Filter by field
  /// تصفية حسب الحقل
  List<Recommendation> get filteredRecommendations {
    if (selectedFieldId == null || selectedFieldId == 'all') {
      return sortedRecommendations;
    }
    return sortedRecommendations
        .where((r) => r.fieldId == selectedFieldId)
        .toList();
  }
}

// =============================================================================
// StateNotifier
// مُعلم الحالة
// =============================================================================

/// Advisor dashboard notifier
/// مُعلم لوحة المستشار
class AdvisorDashboardNotifier extends StateNotifier<AdvisorDashboardState> {
  final http.Client _client;

  AdvisorDashboardNotifier({http.Client? client})
      : _client = client ?? http.Client(),
        super(const AdvisorDashboardState()) {
    loadRecommendations();
  }

  /// Load recommendations from advisory service
  /// تحميل التوصيات من خدمة المستشار
  Future<void> loadRecommendations() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      // Attempt to fetch from advisory-service (port 8093)
      final recommendations = await _fetchRecommendations();
      state = state.copyWith(
        recommendations: recommendations,
        isLoading: false,
      );
    } catch (e) {
      // Fallback to mock data when API is unavailable
      final recommendations = _getMockRecommendations();
      state = state.copyWith(
        recommendations: recommendations,
        isLoading: false,
      );
    }
  }

  /// Advisory service base URL (port 8093, gateway-aware)
  /// رابط خدمة الاستشارات الأساسي (المنفذ 8093، متوافق مع البوابة)
  static String get _advisoryBase => ApiConfig.useDirectServices
      ? '${ApiConfig.fertilizerServiceUrl}/api/v1/advisories'
      : '${ApiConfig.effectiveBaseUrl}/api/v1/fertilizer/advisories';

  /// Fetch recommendations from the advisory service API
  /// جلب التوصيات من واجهة خدمة المستشار
  Future<List<Recommendation>> _fetchRecommendations() async {
    final response = await _client
        .get(
          Uri.parse(_advisoryBase),
          headers: ApiConfig.defaultHeaders,
        )
        .timeout(ApiConfig.connectTimeout);

    if (response.statusCode != 200) {
      throw Exception('Advisory API returned ${response.statusCode}');
    }

    final data = json.decode(response.body);
    final items = (data is List) ? data : (data['items'] as List?) ?? [];

    return items.map<Recommendation>((item) {
      return Recommendation(
        id: item['id']?.toString() ?? '',
        type: _parseRecommendationType(item['type']?.toString()),
        priority: _parseRecommendationPriority(item['priority']?.toString()),
        title: item['title']?.toString() ?? '',
        titleAr: item['title_ar']?.toString() ?? item['title']?.toString() ?? '',
        description: item['description']?.toString() ?? '',
        descriptionAr: item['description_ar']?.toString() ?? item['description']?.toString() ?? '',
        fieldId: item['field_id']?.toString(),
        fieldName: item['field_name']?.toString(),
        actionLabel: item['action_label']?.toString(),
        actionLabelAr: item['action_label_ar']?.toString(),
        estimatedCost: (item['estimated_cost'] as num?)?.toDouble(),
        estimatedROI: (item['estimated_roi'] as num?)?.toDouble(),
        roiExplanation: item['roi_explanation']?.toString(),
        roiExplanationAr: item['roi_explanation_ar']?.toString(),
        createdAt: DateTime.tryParse(item['created_at']?.toString() ?? '') ?? DateTime.now(),
        isCompleted: item['is_completed'] == true,
      );
    }).toList();
  }

  /// Parse recommendation type from API string
  RecommendationType _parseRecommendationType(String? code) {
    for (final type in RecommendationType.values) {
      if (type.code == code) return type;
    }
    return RecommendationType.general;
  }

  /// Parse recommendation priority from API string
  RecommendationPriority _parseRecommendationPriority(String? code) {
    for (final priority in RecommendationPriority.values) {
      if (priority.code == code) return priority;
    }
    return RecommendationPriority.info;
  }

  /// Get irrigation-specific advice
  /// الحصول على نصيحة خاصة بالري
  List<Recommendation> getIrrigationAdvice() {
    return state.recommendations
        .where((r) => r.type == RecommendationType.irrigation)
        .toList();
  }

  /// Get fertilizer-specific advice
  /// الحصول على نصيحة خاصة بالتسميد
  List<Recommendation> getFertilizerAdvice() {
    return state.recommendations
        .where((r) => r.type == RecommendationType.fertilizer)
        .toList();
  }

  /// Mark a recommendation as completed
  /// تحديد التوصية كمكتملة
  void markCompleted(String recommendationId) {
    final updated = state.recommendations.map((r) {
      if (r.id == recommendationId) {
        return r.copyWith(isCompleted: true);
      }
      return r;
    }).toList();

    state = state.copyWith(recommendations: updated);
  }

  /// Select field filter
  /// تحديد فلتر الحقل
  void selectField(String? fieldId) {
    state = state.copyWith(selectedFieldId: fieldId);
  }

  /// Dispose HTTP client resources
  @override
  void dispose() {
    _client.close();
    super.dispose();
  }

  List<Recommendation> _getMockRecommendations() {
    return [
      Recommendation(
        id: 'rec_1',
        type: RecommendationType.irrigation,
        priority: RecommendationPriority.critical,
        title: 'Urgent Irrigation Needed',
        titleAr: 'ري عاجل مطلوب',
        description:
            'Soil moisture at 22% (critical threshold: 25%). Irrigate Field 1 within 6 hours to prevent crop stress.',
        descriptionAr:
            'رطوبة التربة 22% (الحد الحرج: 25%). اسقِ الحقل 1 خلال 6 ساعات لمنع اجهاد المحصول.',
        fieldId: 'field_1',
        fieldName: 'Field 1 | الحقل 1',
        actionLabel: 'Start Irrigation',
        actionLabelAr: 'بدء الري',
        estimatedCost: 45.0,
        estimatedROI: 850.0,
        roiExplanation: 'Prevents yield loss of 0.5 t/ha',
        roiExplanationAr: 'يمنع خسارة محصول 0.5 طن/هكتار',
        createdAt: DateTime.now().subtract(const Duration(hours: 1)),
      ),
      Recommendation(
        id: 'rec_2',
        type: RecommendationType.fertilizer,
        priority: RecommendationPriority.warning,
        title: 'Nitrogen Deficiency Detected',
        titleAr: 'كشف نقص النيتروجين',
        description:
            'Soil nitrogen at 18 ppm (target: 25 ppm). Apply Urea 46% at 46 kg/ha as top dressing.',
        descriptionAr:
            'نيتروجين التربة 18 جزء بالمليون (الهدف: 25). ضع يوريا 46% بمعدل 46 كجم/هكتار.',
        fieldId: 'field_1',
        fieldName: 'Field 1 | الحقل 1',
        actionLabel: 'Apply Fertilizer',
        actionLabelAr: 'تطبيق السماد',
        estimatedCost: 115.0,
        estimatedROI: 1295.0,
        roiExplanation: 'ROI: 1,025% - saves 0.7 t/ha yield',
        roiExplanationAr: 'العائد: 1,025% - يحفظ 0.7 طن/هكتار',
        createdAt: DateTime.now().subtract(const Duration(hours: 3)),
      ),
      Recommendation(
        id: 'rec_3',
        type: RecommendationType.pest,
        priority: RecommendationPriority.warning,
        title: 'Aphid Population Increasing',
        titleAr: 'تزايد اعداد حشرات المن',
        description:
            'Aphid count exceeding threshold (15/leaf). Consider biological control or targeted spray.',
        descriptionAr:
            'عدد المن يتجاوز الحد (15/ورقة). فكر في المكافحة البيولوجية او الرش الموجه.',
        fieldId: 'field_2',
        fieldName: 'Field 2 | الحقل 2',
        actionLabel: 'View IPM Plan',
        actionLabelAr: 'عرض خطة المكافحة',
        estimatedCost: 200.0,
        estimatedROI: 3500.0,
        createdAt: DateTime.now().subtract(const Duration(hours: 8)),
      ),
      Recommendation(
        id: 'rec_4',
        type: RecommendationType.weather,
        priority: RecommendationPriority.advisory,
        title: 'Frost Warning - Tomorrow Night',
        titleAr: 'تحذير صقيع - الليلة القادمة',
        description:
            'Temperature expected to drop to 2C. Delay morning irrigation and consider frost protection.',
        descriptionAr:
            'الحرارة المتوقعة تنخفض الى 2 مئوية. اخر رية الصباح وفكر في حماية من الصقيع.',
        actionLabel: 'View Weather',
        actionLabelAr: 'عرض الطقس',
        createdAt: DateTime.now().subtract(const Duration(hours: 2)),
      ),
      Recommendation(
        id: 'rec_5',
        type: RecommendationType.harvest,
        priority: RecommendationPriority.info,
        title: 'Barley Approaching Harvest',
        titleAr: 'الشعير يقترب من الحصاد',
        description:
            'Field 3 barley at heading stage. Expected harvest in 45-50 days. Start planning logistics.',
        descriptionAr:
            'شعير الحقل 3 في مرحلة طرد السنابل. الحصاد المتوقع خلال 45-50 يوم. ابدأ التخطيط.',
        fieldId: 'field_3',
        fieldName: 'Field 3 | الحقل 3',
        actionLabel: 'Plan Harvest',
        actionLabelAr: 'تخطيط الحصاد',
        createdAt: DateTime.now().subtract(const Duration(days: 1)),
      ),
      Recommendation(
        id: 'rec_6',
        type: RecommendationType.irrigation,
        priority: RecommendationPriority.advisory,
        title: 'Optimize Drip Irrigation Schedule',
        titleAr: 'تحسين جدول الري بالتنقيط',
        description:
            'Current schedule uses 15% more water than needed. Adjust to 3 cycles of 45min instead of 2 cycles of 80min.',
        descriptionAr:
            'الجدول الحالي يستخدم 15% ماء اكثر من الحاجة. عدل الى 3 دورات 45 دقيقة بدلا من دورتين 80 دقيقة.',
        fieldId: 'field_2',
        fieldName: 'Field 2 | الحقل 2',
        actionLabel: 'Update Schedule',
        actionLabelAr: 'تحديث الجدول',
        estimatedCost: 0,
        estimatedROI: 340.0,
        roiExplanation: 'Saves 340 SAR/month in water costs',
        roiExplanationAr: 'يوفر 340 ريال/شهر تكاليف مياه',
        createdAt: DateTime.now().subtract(const Duration(days: 1)),
      ),
    ];
  }
}

// =============================================================================
// Providers
// الموفرون
// =============================================================================

/// Main advisor dashboard provider
/// الموفر الرئيسي للوحة المستشار
final advisorDashboardProvider =
    StateNotifierProvider.autoDispose<AdvisorDashboardNotifier, AdvisorDashboardState>(
        (ref) {
  return AdvisorDashboardNotifier();
});
