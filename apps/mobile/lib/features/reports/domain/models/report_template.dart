/// Report Template Models - نماذج قوالب التقارير
/// Defines the structure for various report types in SAHOOL
library;

/// Report type enum - أنواع التقارير
enum ReportType {
  /// Field performance report - تقرير أداء الحقل
  fieldPerformance,

  /// NDVI trend report - تقرير اتجاه NDVI
  ndviTrend,

  /// Irrigation summary - ملخص الري
  irrigationSummary,

  /// Task completion report - تقرير إنجاز المهام
  taskCompletion,

  /// Weather analysis - تحليل الطقس
  weatherAnalysis,

  /// Cost/profit analysis - تحليل التكاليف والأرباح
  costProfit,

  /// Yield prediction report - تقرير توقع الإنتاج
  yieldPrediction,
}

/// Report template model - نموذج قالب التقرير
class ReportTemplate {
  /// Unique identifier
  final String id;

  /// Template name (English)
  final String name;

  /// Template name (Arabic) - اسم القالب
  final String nameAr;

  /// Description (English)
  final String description;

  /// Description (Arabic) - الوصف
  final String descriptionAr;

  /// Report type
  final ReportType type;

  /// Icon name
  final String iconName;

  /// Available chart types
  final List<String> availableCharts;

  /// Required data fields
  final List<String> requiredFields;

  /// Optional data fields
  final List<String> optionalFields;

  /// Default date range in days
  final int defaultDateRangeDays;

  /// Whether the template supports field filtering
  final bool supportsFieldFilter;

  /// Whether the template supports farm filtering
  final bool supportsFarmFilter;

  /// Whether the template supports offline generation
  final bool supportsOffline;

  /// Premium feature flag
  final bool isPremium;

  const ReportTemplate({
    required this.id,
    required this.name,
    required this.nameAr,
    required this.description,
    required this.descriptionAr,
    required this.type,
    required this.iconName,
    this.availableCharts = const [],
    this.requiredFields = const [],
    this.optionalFields = const [],
    this.defaultDateRangeDays = 30,
    this.supportsFieldFilter = true,
    this.supportsFarmFilter = true,
    this.supportsOffline = true,
    this.isPremium = false,
  });

  /// Create from JSON
  factory ReportTemplate.fromJson(Map<String, dynamic> json) {
    return ReportTemplate(
      id: json['id'] as String,
      name: json['name'] as String,
      nameAr: json['name_ar'] as String? ?? json['name'] as String,
      description: json['description'] as String? ?? '',
      descriptionAr: json['description_ar'] as String? ?? '',
      type: ReportType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => ReportType.fieldPerformance,
      ),
      iconName: json['icon_name'] as String? ?? 'description',
      availableCharts: (json['available_charts'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      requiredFields: (json['required_fields'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      optionalFields: (json['optional_fields'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      defaultDateRangeDays: json['default_date_range_days'] as int? ?? 30,
      supportsFieldFilter: json['supports_field_filter'] as bool? ?? true,
      supportsFarmFilter: json['supports_farm_filter'] as bool? ?? true,
      supportsOffline: json['supports_offline'] as bool? ?? true,
      isPremium: json['is_premium'] as bool? ?? false,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'name_ar': nameAr,
        'description': description,
        'description_ar': descriptionAr,
        'type': type.name,
        'icon_name': iconName,
        'available_charts': availableCharts,
        'required_fields': requiredFields,
        'optional_fields': optionalFields,
        'default_date_range_days': defaultDateRangeDays,
        'supports_field_filter': supportsFieldFilter,
        'supports_farm_filter': supportsFarmFilter,
        'supports_offline': supportsOffline,
        'is_premium': isPremium,
      };

  /// Copy with
  ReportTemplate copyWith({
    String? id,
    String? name,
    String? nameAr,
    String? description,
    String? descriptionAr,
    ReportType? type,
    String? iconName,
    List<String>? availableCharts,
    List<String>? requiredFields,
    List<String>? optionalFields,
    int? defaultDateRangeDays,
    bool? supportsFieldFilter,
    bool? supportsFarmFilter,
    bool? supportsOffline,
    bool? isPremium,
  }) {
    return ReportTemplate(
      id: id ?? this.id,
      name: name ?? this.name,
      nameAr: nameAr ?? this.nameAr,
      description: description ?? this.description,
      descriptionAr: descriptionAr ?? this.descriptionAr,
      type: type ?? this.type,
      iconName: iconName ?? this.iconName,
      availableCharts: availableCharts ?? this.availableCharts,
      requiredFields: requiredFields ?? this.requiredFields,
      optionalFields: optionalFields ?? this.optionalFields,
      defaultDateRangeDays: defaultDateRangeDays ?? this.defaultDateRangeDays,
      supportsFieldFilter: supportsFieldFilter ?? this.supportsFieldFilter,
      supportsFarmFilter: supportsFarmFilter ?? this.supportsFarmFilter,
      supportsOffline: supportsOffline ?? this.supportsOffline,
      isPremium: isPremium ?? this.isPremium,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ReportTemplate &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() => 'ReportTemplate($id: $name)';
}

/// Predefined report templates - القوالب المعرفة مسبقاً
class ReportTemplates {
  /// Field performance template
  static const fieldPerformance = ReportTemplate(
    id: 'field_performance',
    name: 'Field Performance Report',
    nameAr: 'تقرير أداء الحقل',
    description: 'Comprehensive analysis of field productivity and health',
    descriptionAr: 'تحليل شامل لإنتاجية الحقل وصحته',
    type: ReportType.fieldPerformance,
    iconName: 'landscape',
    availableCharts: ['line', 'bar', 'pie'],
    requiredFields: ['field_id', 'date_range'],
    optionalFields: ['crop_type', 'compare_fields'],
    defaultDateRangeDays: 30,
  );

  /// NDVI trend template
  static const ndviTrend = ReportTemplate(
    id: 'ndvi_trend',
    name: 'NDVI Trend Report',
    nameAr: 'تقرير اتجاه NDVI',
    description: 'Vegetation health index trends over time',
    descriptionAr: 'اتجاهات مؤشر صحة الغطاء النباتي عبر الزمن',
    type: ReportType.ndviTrend,
    iconName: 'show_chart',
    availableCharts: ['line', 'area'],
    requiredFields: ['field_id', 'date_range'],
    optionalFields: ['zone_filter'],
    defaultDateRangeDays: 90,
  );

  /// Irrigation summary template
  static const irrigationSummary = ReportTemplate(
    id: 'irrigation_summary',
    name: 'Irrigation Summary',
    nameAr: 'ملخص الري',
    description: 'Water usage and irrigation efficiency analysis',
    descriptionAr: 'تحليل استهلاك المياه وكفاءة الري',
    type: ReportType.irrigationSummary,
    iconName: 'water_drop',
    availableCharts: ['bar', 'line', 'pie'],
    requiredFields: ['field_id', 'date_range'],
    optionalFields: ['irrigation_method'],
    defaultDateRangeDays: 30,
  );

  /// Task completion template
  static const taskCompletion = ReportTemplate(
    id: 'task_completion',
    name: 'Task Completion Report',
    nameAr: 'تقرير إنجاز المهام',
    description: 'Team productivity and task management analysis',
    descriptionAr: 'تحليل إنتاجية الفريق وإدارة المهام',
    type: ReportType.taskCompletion,
    iconName: 'task_alt',
    availableCharts: ['bar', 'pie', 'line'],
    requiredFields: ['date_range'],
    optionalFields: ['field_id', 'task_type', 'assignee'],
    defaultDateRangeDays: 7,
  );

  /// Weather analysis template
  static const weatherAnalysis = ReportTemplate(
    id: 'weather_analysis',
    name: 'Weather Analysis',
    nameAr: 'تحليل الطقس',
    description: 'Historical weather patterns and impact analysis',
    descriptionAr: 'أنماط الطقس التاريخية وتحليل التأثير',
    type: ReportType.weatherAnalysis,
    iconName: 'cloud',
    availableCharts: ['line', 'area', 'bar'],
    requiredFields: ['location', 'date_range'],
    optionalFields: ['metrics'],
    defaultDateRangeDays: 30,
  );

  /// Cost/profit analysis template
  static const costProfit = ReportTemplate(
    id: 'cost_profit',
    name: 'Cost/Profit Analysis',
    nameAr: 'تحليل التكاليف والأرباح',
    description: 'Financial performance and cost breakdown',
    descriptionAr: 'الأداء المالي وتفصيل التكاليف',
    type: ReportType.costProfit,
    iconName: 'account_balance',
    availableCharts: ['bar', 'pie', 'line'],
    requiredFields: ['date_range'],
    optionalFields: ['field_id', 'category'],
    defaultDateRangeDays: 90,
    isPremium: true,
  );

  /// Yield prediction template
  static const yieldPrediction = ReportTemplate(
    id: 'yield_prediction',
    name: 'Yield Prediction Report',
    nameAr: 'تقرير توقع الإنتاج',
    description: 'AI-powered yield forecasting and analysis',
    descriptionAr: 'توقعات الإنتاج المدعومة بالذكاء الاصطناعي',
    type: ReportType.yieldPrediction,
    iconName: 'trending_up',
    availableCharts: ['line', 'bar', 'area'],
    requiredFields: ['field_id'],
    optionalFields: ['crop_type', 'season'],
    defaultDateRangeDays: 180,
    isPremium: true,
  );

  /// Get all templates
  static List<ReportTemplate> get all => [
        fieldPerformance,
        ndviTrend,
        irrigationSummary,
        taskCompletion,
        weatherAnalysis,
        costProfit,
        yieldPrediction,
      ];

  /// Get template by type
  static ReportTemplate getByType(ReportType type) {
    return all.firstWhere(
      (t) => t.type == type,
      orElse: () => fieldPerformance,
    );
  }

  /// Get template by ID
  static ReportTemplate? getById(String id) {
    try {
      return all.firstWhere((t) => t.id == id);
    } catch (e) {
      return null;
    }
  }

  /// Get free templates only
  static List<ReportTemplate> get freeTemplates =>
      all.where((t) => !t.isPremium).toList();

  /// Get premium templates
  static List<ReportTemplate> get premiumTemplates =>
      all.where((t) => t.isPremium).toList();
}
