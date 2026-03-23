/// Profitability Models - نماذج تحليل الربحية
/// تحليل ربحية المحاصيل وتكاليف الإنتاج
library;

import 'package:flutter/foundation.dart';

// ═════════════════════════════════════════════════════════════════════════════
// Enums
// ═════════════════════════════════════════════════════════════════════════════

/// نوع التكلفة
enum CostType {
  seeds('seeds', 'بذور', 'Seeds'),
  fertilizer('fertilizer', 'أسمدة', 'Fertilizer'),
  pesticides('pesticides', 'مبيدات', 'Pesticides'),
  labor('labor', 'عمالة', 'Labor'),
  irrigation('irrigation', 'ري', 'Irrigation'),
  equipment('equipment', 'معدات', 'Equipment'),
  land('land', 'إيجار أرض', 'Land Rent'),
  transport('transport', 'نقل', 'Transport'),
  storage('storage', 'تخزين', 'Storage'),
  other('other', 'أخرى', 'Other');

  final String value;
  final String nameAr;
  final String nameEn;

  const CostType(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static CostType fromString(String value) {
    return CostType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => CostType.other,
    );
  }
}

/// نوع الإيرادات
enum RevenueType {
  crop('crop', 'محصول', 'Crop'),
  byProduct('by_product', 'منتج ثانوي', 'By-product'),
  subsidy('subsidy', 'دعم', 'Subsidy'),
  other('other', 'أخرى', 'Other');

  final String value;
  final String nameAr;
  final String nameEn;

  const RevenueType(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static RevenueType fromString(String value) {
    return RevenueType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => RevenueType.other,
    );
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// Models
// ═════════════════════════════════════════════════════════════════════════════

/// نموذج فئة التكلفة
@immutable
class CostCategory {
  final String categoryId;
  final CostType type;
  final String name;
  final String? nameAr;
  final double amount; // المبلغ (ريال يمني)
  final String unit; // الوحدة
  final String? unitAr;
  final double quantity; // الكمية
  final double unitCost; // تكلفة الوحدة
  final String? description;
  final String? descriptionAr;
  final DateTime date;
  final Map<String, dynamic>? metadata;

  const CostCategory({
    required this.categoryId,
    required this.type,
    required this.name,
    this.nameAr,
    required this.amount,
    required this.unit,
    this.unitAr,
    required this.quantity,
    required this.unitCost,
    this.description,
    this.descriptionAr,
    required this.date,
    this.metadata,
  });

  /// Get display name based on locale
  String getDisplayName(String locale) {
    return locale == 'ar' && nameAr != null ? nameAr! : name;
  }

  /// Get unit based on locale
  String getUnit(String locale) {
    return locale == 'ar' && unitAr != null ? unitAr! : unit;
  }

  /// Get description based on locale
  String? getDescription(String locale) {
    return locale == 'ar' && descriptionAr != null ? descriptionAr : description;
  }

  factory CostCategory.fromJson(Map<String, dynamic> json) {
    return CostCategory(
      categoryId: json['category_id'] as String,
      type: CostType.fromString(json['type'] as String),
      name: json['name'] as String,
      nameAr: json['name_ar'] as String?,
      amount: (json['amount'] as num).toDouble(),
      unit: json['unit'] as String,
      unitAr: json['unit_ar'] as String?,
      quantity: (json['quantity'] as num).toDouble(),
      unitCost: (json['unit_cost'] as num).toDouble(),
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      date: DateTime.parse(json['date'] as String),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'category_id': categoryId,
        'type': type.value,
        'name': name,
        'name_ar': nameAr,
        'amount': amount,
        'unit': unit,
        'unit_ar': unitAr,
        'quantity': quantity,
        'unit_cost': unitCost,
        'description': description,
        'description_ar': descriptionAr,
        'date': date.toIso8601String(),
        'metadata': metadata,
      };
}

/// نموذج الإيرادات
@immutable
class Revenue {
  final String revenueId;
  final RevenueType type;
  final String name;
  final String? nameAr;
  final double amount; // المبلغ (ريال يمني)
  final double quantity; // الكمية (كجم، طن، الخ)
  final String unit; // الوحدة
  final String? unitAr;
  final double unitPrice; // سعر الوحدة
  final DateTime date;
  final String? description;
  final String? descriptionAr;
  final Map<String, dynamic>? metadata;

  const Revenue({
    required this.revenueId,
    required this.type,
    required this.name,
    this.nameAr,
    required this.amount,
    required this.quantity,
    required this.unit,
    this.unitAr,
    required this.unitPrice,
    required this.date,
    this.description,
    this.descriptionAr,
    this.metadata,
  });

  /// Get display name based on locale
  String getDisplayName(String locale) {
    return locale == 'ar' && nameAr != null ? nameAr! : name;
  }

  /// Get unit based on locale
  String getUnit(String locale) {
    return locale == 'ar' && unitAr != null ? unitAr! : unit;
  }

  /// Get description based on locale
  String? getDescription(String locale) {
    return locale == 'ar' && descriptionAr != null ? descriptionAr : description;
  }

  factory Revenue.fromJson(Map<String, dynamic> json) {
    return Revenue(
      revenueId: json['revenue_id'] as String,
      type: RevenueType.fromString(json['type'] as String),
      name: json['name'] as String,
      nameAr: json['name_ar'] as String?,
      amount: (json['amount'] as num).toDouble(),
      quantity: (json['quantity'] as num).toDouble(),
      unit: json['unit'] as String,
      unitAr: json['unit_ar'] as String?,
      unitPrice: (json['unit_price'] as num).toDouble(),
      date: DateTime.parse(json['date'] as String),
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'revenue_id': revenueId,
        'type': type.value,
        'name': name,
        'name_ar': nameAr,
        'amount': amount,
        'quantity': quantity,
        'unit': unit,
        'unit_ar': unitAr,
        'unit_price': unitPrice,
        'date': date.toIso8601String(),
        'description': description,
        'description_ar': descriptionAr,
        'metadata': metadata,
      };
}

/// نموذج تحليل نقطة التعادل
@immutable
class BreakEvenAnalysis {
  final double fixedCosts; // التكاليف الثابتة
  final double variableCosts; // التكاليف المتغيرة
  final double totalCosts; // إجمالي التكاليف
  final double expectedRevenue; // الإيرادات المتوقعة
  final double breakEvenQuantity; // كمية التعادل (كجم، طن)
  final double breakEvenRevenue; // إيرادات التعادل
  final String unit; // وحدة القياس
  final String? unitAr;
  final Map<String, dynamic>? parameters;

  const BreakEvenAnalysis({
    required this.fixedCosts,
    required this.variableCosts,
    required this.totalCosts,
    required this.expectedRevenue,
    required this.breakEvenQuantity,
    required this.breakEvenRevenue,
    required this.unit,
    this.unitAr,
    this.parameters,
  });

  /// Get unit based on locale
  String getUnit(String locale) {
    return locale == 'ar' && unitAr != null ? unitAr! : unit;
  }

  /// حساب هامش الأمان
  double getSafetyMargin() {
    if (expectedRevenue == 0) return 0;
    return ((expectedRevenue - breakEvenRevenue) / expectedRevenue) * 100;
  }

  factory BreakEvenAnalysis.fromJson(Map<String, dynamic> json) {
    return BreakEvenAnalysis(
      fixedCosts: (json['fixed_costs'] as num).toDouble(),
      variableCosts: (json['variable_costs'] as num).toDouble(),
      totalCosts: (json['total_costs'] as num).toDouble(),
      expectedRevenue: (json['expected_revenue'] as num).toDouble(),
      breakEvenQuantity: (json['break_even_quantity'] as num).toDouble(),
      breakEvenRevenue: (json['break_even_revenue'] as num).toDouble(),
      unit: json['unit'] as String,
      unitAr: json['unit_ar'] as String?,
      parameters: json['parameters'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'fixed_costs': fixedCosts,
        'variable_costs': variableCosts,
        'total_costs': totalCosts,
        'expected_revenue': expectedRevenue,
        'break_even_quantity': breakEvenQuantity,
        'break_even_revenue': breakEvenRevenue,
        'unit': unit,
        'unit_ar': unitAr,
        'parameters': parameters,
      };
}

/// نموذج ربحية المحصول
@immutable
class CropProfitability {
  final String profitabilityId;
  final String tenantId;
  final String fieldId;
  final String fieldName;
  final String? fieldNameAr;
  final String cropType;
  final String cropName;
  final String? cropNameAr;
  final String season;
  final String? seasonAr;
  final double area; // المساحة بالهكتار
  final double yield; // الإنتاجية (طن/هكتار)
  final double totalYield; // الإنتاج الإجمالي (طن)
  final List<CostCategory> costs;
  final double totalCosts; // إجمالي التكاليف
  final List<Revenue> revenues;
  final double totalRevenue; // إجمالي الإيرادات
  final double netProfit; // صافي الربح
  final double profitMargin; // هامش الربح %
  final double roi; // العائد على الاستثمار %
  final double costPerHectare; // التكلفة لكل هكتار
  final double revenuePerHectare; // الإيرادات لكل هكتار
  final double profitPerHectare; // الربح لكل هكتار
  final BreakEvenAnalysis? breakEvenAnalysis;
  final DateTime startDate;
  final DateTime? endDate;
  final DateTime createdAt;
  final DateTime updatedAt;
  final Map<String, dynamic>? metadata;

  const CropProfitability({
    required this.profitabilityId,
    required this.tenantId,
    required this.fieldId,
    required this.fieldName,
    this.fieldNameAr,
    required this.cropType,
    required this.cropName,
    this.cropNameAr,
    required this.season,
    this.seasonAr,
    required this.area,
    required this.yield,
    required this.totalYield,
    required this.costs,
    required this.totalCosts,
    required this.revenues,
    required this.totalRevenue,
    required this.netProfit,
    required this.profitMargin,
    required this.roi,
    required this.costPerHectare,
    required this.revenuePerHectare,
    required this.profitPerHectare,
    this.breakEvenAnalysis,
    required this.startDate,
    this.endDate,
    required this.createdAt,
    required this.updatedAt,
    this.metadata,
  });

  /// Get field name based on locale
  String getFieldName(String locale) {
    return locale == 'ar' && fieldNameAr != null ? fieldNameAr! : fieldName;
  }

  /// Get crop name based on locale
  String getCropName(String locale) {
    return locale == 'ar' && cropNameAr != null ? cropNameAr! : cropName;
  }

  /// Get season based on locale
  String getSeason(String locale) {
    return locale == 'ar' && seasonAr != null ? seasonAr! : season;
  }

  /// هل المحصول مربح؟
  bool get isProfitable => netProfit > 0;

  /// حساب التكاليف حسب النوع
  Map<CostType, double> getCostsByType() {
    final Map<CostType, double> costMap = {};
    for (final cost in costs) {
      costMap[cost.type] = (costMap[cost.type] ?? 0) + cost.amount;
    }
    return costMap;
  }

  /// حساب الإيرادات حسب النوع
  Map<RevenueType, double> getRevenuesByType() {
    final Map<RevenueType, double> revenueMap = {};
    for (final revenue in revenues) {
      revenueMap[revenue.type] = (revenueMap[revenue.type] ?? 0) + revenue.amount;
    }
    return revenueMap;
  }

  factory CropProfitability.fromJson(Map<String, dynamic> json) {
    return CropProfitability(
      profitabilityId: json['profitability_id'] as String,
      tenantId: json['tenant_id'] as String,
      fieldId: json['field_id'] as String,
      fieldName: json['field_name'] as String,
      fieldNameAr: json['field_name_ar'] as String?,
      cropType: json['crop_type'] as String,
      cropName: json['crop_name'] as String,
      cropNameAr: json['crop_name_ar'] as String?,
      season: json['season'] as String,
      seasonAr: json['season_ar'] as String?,
      area: (json['area'] as num).toDouble(),
      yield: (json['yield'] as num).toDouble(),
      totalYield: (json['total_yield'] as num).toDouble(),
      costs: (json['costs'] as List)
          .map((e) => CostCategory.fromJson(e as Map<String, dynamic>))
          .toList(),
      totalCosts: (json['total_costs'] as num).toDouble(),
      revenues: (json['revenues'] as List)
          .map((e) => Revenue.fromJson(e as Map<String, dynamic>))
          .toList(),
      totalRevenue: (json['total_revenue'] as num).toDouble(),
      netProfit: (json['net_profit'] as num).toDouble(),
      profitMargin: (json['profit_margin'] as num).toDouble(),
      roi: (json['roi'] as num).toDouble(),
      costPerHectare: (json['cost_per_hectare'] as num).toDouble(),
      revenuePerHectare: (json['revenue_per_hectare'] as num).toDouble(),
      profitPerHectare: (json['profit_per_hectare'] as num).toDouble(),
      breakEvenAnalysis: json['break_even_analysis'] != null
          ? BreakEvenAnalysis.fromJson(json['break_even_analysis'] as Map<String, dynamic>)
          : null,
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: json['end_date'] != null ? DateTime.parse(json['end_date'] as String) : null,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'profitability_id': profitabilityId,
        'tenant_id': tenantId,
        'field_id': fieldId,
        'field_name': fieldName,
        'field_name_ar': fieldNameAr,
        'crop_type': cropType,
        'crop_name': cropName,
        'crop_name_ar': cropNameAr,
        'season': season,
        'season_ar': seasonAr,
        'area': area,
        'yield': yield,
        'total_yield': totalYield,
        'costs': costs.map((e) => e.toJson()).toList(),
        'total_costs': totalCosts,
        'revenues': revenues.map((e) => e.toJson()).toList(),
        'total_revenue': totalRevenue,
        'net_profit': netProfit,
        'profit_margin': profitMargin,
        'roi': roi,
        'cost_per_hectare': costPerHectare,
        'revenue_per_hectare': revenuePerHectare,
        'profit_per_hectare': profitPerHectare,
        'break_even_analysis': breakEvenAnalysis?.toJson(),
        'start_date': startDate.toIso8601String(),
        'end_date': endDate?.toIso8601String(),
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
        'metadata': metadata,
      };
}

/// نموذج ملخص الموسم
@immutable
class SeasonSummary {
  final String summaryId;
  final String tenantId;
  final String farmId;
  final String farmName;
  final String? farmNameAr;
  final String season;
  final String? seasonAr;
  final int fieldsCount;
  final double totalArea;
  final List<CropProfitability> crops;
  final double totalRevenue;
  final double totalCosts;
  final double netProfit;
  final double profitMargin;
  final double avgRoi;
  final Map<String, double> costsByCategory;
  final Map<String, double> revenuesByCrop;
  final DateTime startDate;
  final DateTime? endDate;
  final DateTime createdAt;

  const SeasonSummary({
    required this.summaryId,
    required this.tenantId,
    required this.farmId,
    required this.farmName,
    this.farmNameAr,
    required this.season,
    this.seasonAr,
    required this.fieldsCount,
    required this.totalArea,
    required this.crops,
    required this.totalRevenue,
    required this.totalCosts,
    required this.netProfit,
    required this.profitMargin,
    required this.avgRoi,
    required this.costsByCategory,
    required this.revenuesByCrop,
    required this.startDate,
    this.endDate,
    required this.createdAt,
  });

  /// Get farm name based on locale
  String getFarmName(String locale) {
    return locale == 'ar' && farmNameAr != null ? farmNameAr! : farmName;
  }

  /// Get season based on locale
  String getSeason(String locale) {
    return locale == 'ar' && seasonAr != null ? seasonAr! : season;
  }

  /// الحصول على أفضل المحاصيل حسب الربح
  List<CropProfitability> getTopCropsByProfit({int limit = 5}) {
    final sorted = List<CropProfitability>.from(crops)
      ..sort((a, b) => b.netProfit.compareTo(a.netProfit));
    return sorted.take(limit).toList();
  }

  /// الحصول على أفضل المحاصيل حسب ROI
  List<CropProfitability> getTopCropsByRoi({int limit = 5}) {
    final sorted = List<CropProfitability>.from(crops)..sort((a, b) => b.roi.compareTo(a.roi));
    return sorted.take(limit).toList();
  }

  factory SeasonSummary.fromJson(Map<String, dynamic> json) {
    return SeasonSummary(
      summaryId: json['summary_id'] as String,
      tenantId: json['tenant_id'] as String,
      farmId: json['farm_id'] as String,
      farmName: json['farm_name'] as String,
      farmNameAr: json['farm_name_ar'] as String?,
      season: json['season'] as String,
      seasonAr: json['season_ar'] as String?,
      fieldsCount: json['fields_count'] as int,
      totalArea: (json['total_area'] as num).toDouble(),
      crops: (json['crops'] as List)
          .map((e) => CropProfitability.fromJson(e as Map<String, dynamic>))
          .toList(),
      totalRevenue: (json['total_revenue'] as num).toDouble(),
      totalCosts: (json['total_costs'] as num).toDouble(),
      netProfit: (json['net_profit'] as num).toDouble(),
      profitMargin: (json['profit_margin'] as num).toDouble(),
      avgRoi: (json['avg_roi'] as num).toDouble(),
      costsByCategory: (json['costs_by_category'] as Map<String, dynamic>?)?.map(
        (k, v) => MapEntry(k, (v as num).toDouble()),
      ) ?? {},
      revenuesByCrop: (json['revenues_by_crop'] as Map<String, dynamic>?)?.map(
        (k, v) => MapEntry(k, (v as num).toDouble()),
      ) ?? {},
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: json['end_date'] != null ? DateTime.parse(json['end_date'] as String) : null,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'summary_id': summaryId,
        'tenant_id': tenantId,
        'farm_id': farmId,
        'farm_name': farmName,
        'farm_name_ar': farmNameAr,
        'season': season,
        'season_ar': seasonAr,
        'fields_count': fieldsCount,
        'total_area': totalArea,
        'crops': crops.map((e) => e.toJson()).toList(),
        'total_revenue': totalRevenue,
        'total_costs': totalCosts,
        'net_profit': netProfit,
        'profit_margin': profitMargin,
        'avg_roi': avgRoi,
        'costs_by_category': costsByCategory,
        'revenues_by_crop': revenuesByCrop,
        'start_date': startDate.toIso8601String(),
        'end_date': endDate?.toIso8601String(),
        'created_at': createdAt.toIso8601String(),
      };
}

/// نموذج مقارنة الربحية
@immutable
class ProfitabilityComparison {
  final List<CropProfitability> crops;
  final Map<String, double> avgYieldByCrop;
  final Map<String, double> avgCostByCrop;
  final Map<String, double> avgRevenueByCrop;
  final Map<String, double> avgProfitByCrop;
  final Map<String, double> avgRoiByCrop;
  final String? bestCropByProfit;
  final String? bestCropByRoi;
  final String? lowestCostCrop;
  final Map<String, dynamic>? metadata;

  const ProfitabilityComparison({
    required this.crops,
    required this.avgYieldByCrop,
    required this.avgCostByCrop,
    required this.avgRevenueByCrop,
    required this.avgProfitByCrop,
    required this.avgRoiByCrop,
    this.bestCropByProfit,
    this.bestCropByRoi,
    this.lowestCostCrop,
    this.metadata,
  });

  factory ProfitabilityComparison.fromJson(Map<String, dynamic> json) {
    return ProfitabilityComparison(
      crops: (json['crops'] as List)
          .map((e) => CropProfitability.fromJson(e as Map<String, dynamic>))
          .toList(),
      avgYieldByCrop: (json['avg_yield_by_crop'] as Map<String, dynamic>?)?.map(
        (k, v) => MapEntry(k, (v as num).toDouble()),
      ) ?? {},
      avgCostByCrop: (json['avg_cost_by_crop'] as Map<String, dynamic>?)?.map(
        (k, v) => MapEntry(k, (v as num).toDouble()),
      ) ?? {},
      avgRevenueByCrop: (json['avg_revenue_by_crop'] as Map<String, dynamic>?)?.map(
        (k, v) => MapEntry(k, (v as num).toDouble()),
      ) ?? {},
      avgProfitByCrop: (json['avg_profit_by_crop'] as Map<String, dynamic>?)?.map(
        (k, v) => MapEntry(k, (v as num).toDouble()),
      ) ?? {},
      avgRoiByCrop: (json['avg_roi_by_crop'] as Map<String, dynamic>?)?.map(
        (k, v) => MapEntry(k, (v as num).toDouble()),
      ) ?? {},
      bestCropByProfit: json['best_crop_by_profit'] as String?,
      bestCropByRoi: json['best_crop_by_roi'] as String?,
      lowestCostCrop: json['lowest_cost_crop'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'crops': crops.map((e) => e.toJson()).toList(),
        'avg_yield_by_crop': avgYieldByCrop,
        'avg_cost_by_crop': avgCostByCrop,
        'avg_revenue_by_crop': avgRevenueByCrop,
        'avg_profit_by_crop': avgProfitByCrop,
        'avg_roi_by_crop': avgRoiByCrop,
        'best_crop_by_profit': bestCropByProfit,
        'best_crop_by_roi': bestCropByRoi,
        'lowest_cost_crop': lowestCostCrop,
        'metadata': metadata,
      };
}
