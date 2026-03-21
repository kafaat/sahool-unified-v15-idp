/// Spectral Index - مؤشرات الأقمار الصناعية الطيفية
///
/// Unified enum and colormaps for all satellite-derived spectral indices:
/// NDVI, NDWI, EVI, SAVI, NDRE, LAI
///
/// Each index has its own colormap, health categories, and bilingual labels.
library;

import 'package:flutter/material.dart';
import 'ndvi_colormap.dart';

/// Supported spectral indices
enum SpectralIndex {
  ndvi(
    code: 'NDVI',
    name: 'Normalized Difference Vegetation Index',
    nameAr: 'مؤشر الاختلاف الطبيعي للنبات',
    description: 'Measures vegetation health and density',
    descriptionAr: 'يقيس صحة وكثافة الغطاء النباتي',
    icon: Icons.grass,
    minValue: -1.0,
    maxValue: 1.0,
  ),
  ndwi(
    code: 'NDWI',
    name: 'Normalized Difference Water Index',
    nameAr: 'مؤشر الاختلاف الطبيعي للمياه',
    description: 'Measures water content and moisture stress',
    descriptionAr: 'يقيس محتوى الماء وإجهاد الرطوبة',
    icon: Icons.water_drop,
    minValue: -1.0,
    maxValue: 1.0,
  ),
  evi(
    code: 'EVI',
    name: 'Enhanced Vegetation Index',
    nameAr: 'مؤشر الغطاء النباتي المحسّن',
    description: 'Improved vegetation measurement, reduces atmospheric effects',
    descriptionAr: 'قياس محسّن للنبات، يقلل تأثيرات الغلاف الجوي',
    icon: Icons.park,
    minValue: -1.0,
    maxValue: 1.0,
  ),
  savi(
    code: 'SAVI',
    name: 'Soil Adjusted Vegetation Index',
    nameAr: 'مؤشر النبات المعدّل للتربة',
    description: 'Accounts for soil background in sparse vegetation areas',
    descriptionAr: 'يراعي تأثير التربة في المناطق ذات الغطاء النباتي المتناثر',
    icon: Icons.landscape,
    minValue: -1.0,
    maxValue: 1.0,
  ),
  ndre(
    code: 'NDRE',
    name: 'Normalized Difference Red Edge',
    nameAr: 'مؤشر الحافة الحمراء الطبيعي',
    description: 'Sensitive to nitrogen content and chlorophyll levels',
    descriptionAr: 'حساس لمحتوى النيتروجين ومستويات الكلوروفيل',
    icon: Icons.science,
    minValue: -1.0,
    maxValue: 1.0,
  ),
  lai(
    code: 'LAI',
    name: 'Leaf Area Index',
    nameAr: 'مؤشر مساحة الأوراق',
    description: 'Total leaf area per unit ground area',
    descriptionAr: 'إجمالي مساحة الأوراق لكل وحدة مساحة أرضية',
    icon: Icons.eco,
    minValue: 0.0,
    maxValue: 8.0,
  );

  final String code;
  final String name;
  final String nameAr;
  final String description;
  final String descriptionAr;
  final IconData icon;
  final double minValue;
  final double maxValue;

  const SpectralIndex({
    required this.code,
    required this.name,
    required this.nameAr,
    required this.description,
    required this.descriptionAr,
    required this.icon,
    required this.minValue,
    required this.maxValue,
  });

  /// Get label based on locale
  String getLabel(bool isArabic) => isArabic ? nameAr : name;

  /// Get description based on locale
  String getDescription(bool isArabic) => isArabic ? descriptionAr : description;

  /// Parse from code string (e.g., "NDVI", "ndwi")
  static SpectralIndex? fromCode(String code) {
    final upper = code.toUpperCase();
    for (final index in SpectralIndex.values) {
      if (index.code == upper) return index;
    }
    return null;
  }
}

/// Colormaps for all spectral indices
class SpectralColormap {
  /// Get colormap stops for an index
  static List<ColorStop> getStops(SpectralIndex index) {
    switch (index) {
      case SpectralIndex.ndvi:
        return NdviColormap.yemenStops;
      case SpectralIndex.ndwi:
        return _ndwiStops;
      case SpectralIndex.evi:
        return _eviStops;
      case SpectralIndex.savi:
        return _saviStops;
      case SpectralIndex.ndre:
        return _ndreStops;
      case SpectralIndex.lai:
        return _laiStops;
    }
  }

  /// Get color for a value on a given index
  static Color getColor(SpectralIndex index, double value) {
    final stops = getStops(index);
    final clamped = value.clamp(index.minValue, index.maxValue);

    ColorStop? lower;
    ColorStop? upper;

    for (int i = 0; i < stops.length - 1; i++) {
      if (clamped >= stops[i].value && clamped <= stops[i + 1].value) {
        lower = stops[i];
        upper = stops[i + 1];
        break;
      }
    }

    if (lower == null || upper == null) {
      if (clamped <= stops.first.value) return stops.first.color;
      return stops.last.color;
    }

    final t = (clamped - lower.value) / (upper.value - lower.value);
    return Color.lerp(lower.color, upper.color, t)!;
  }

  /// Generate gradient colors for UI legend
  static List<Color> generateGradient(SpectralIndex index, {int steps = 10}) {
    final stops = getStops(index);
    final min = stops.first.value;
    final max = stops.last.value;
    return List.generate(steps, (i) {
      final value = min + (max - min) * (i / (steps - 1));
      return getColor(index, value);
    });
  }

  /// Get legend items for an index
  static List<LegendItem> getLegend(SpectralIndex index) {
    switch (index) {
      case SpectralIndex.ndvi:
        return NdviLegend.items;
      case SpectralIndex.ndwi:
        return _ndwiLegend;
      case SpectralIndex.evi:
        return _eviLegend;
      case SpectralIndex.savi:
        return _saviLegend;
      case SpectralIndex.ndre:
        return _ndreLegend;
      case SpectralIndex.lai:
        return _laiLegend;
    }
  }

  /// Get health label from index value (bilingual)
  static String getHealthLabel(SpectralIndex index, double value, bool isArabic) {
    switch (index) {
      case SpectralIndex.ndvi:
      case SpectralIndex.evi:
      case SpectralIndex.savi:
        return _vegetationHealthLabel(value, isArabic);
      case SpectralIndex.ndwi:
        return _waterHealthLabel(value, isArabic);
      case SpectralIndex.ndre:
        return _nitrogenHealthLabel(value, isArabic);
      case SpectralIndex.lai:
        return _laiHealthLabel(value, isArabic);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // NDWI Colormap - Water Index
  // ═══════════════════════════════════════════════════════════════════════════

  static const List<ColorStop> _ndwiStops = [
    ColorStop(-1.0, Color(0xFFA0522D)), // Dry land - Sienna
    ColorStop(-0.3, Color(0xFFCD853F)), // Very dry - Peru
    ColorStop(-0.1, Color(0xFFDEB887)), // Dry - BurlyWood
    ColorStop(0.0, Color(0xFFF5DEB3)),  // Neutral - Wheat
    ColorStop(0.1, Color(0xFFADD8E6)),  // Low moisture - Light Blue
    ColorStop(0.2, Color(0xFF87CEEB)),  // Moderate moisture - Sky Blue
    ColorStop(0.3, Color(0xFF4682B4)),  // Moist - Steel Blue
    ColorStop(0.5, Color(0xFF1E90FF)),  // Wet - Dodger Blue
    ColorStop(0.7, Color(0xFF0000CD)),  // Very wet - Medium Blue
    ColorStop(1.0, Color(0xFF00008B)),  // Water body - Dark Blue
  ];

  static const List<LegendItem> _ndwiLegend = [
    LegendItem(range: '-1.0 - 0.0', label: 'جاف / أرض يابسة', labelEn: 'Dry / Land', color: Color(0xFFCD853F)),
    LegendItem(range: '0.0 - 0.2', label: 'رطوبة منخفضة', labelEn: 'Low Moisture', color: Color(0xFFADD8E6)),
    LegendItem(range: '0.2 - 0.4', label: 'رطوبة متوسطة', labelEn: 'Moderate Moisture', color: Color(0xFF4682B4)),
    LegendItem(range: '0.4 - 0.6', label: 'رطوبة عالية', labelEn: 'High Moisture', color: Color(0xFF1E90FF)),
    LegendItem(range: '0.6 - 0.8', label: 'رطب جداً', labelEn: 'Very Wet', color: Color(0xFF0000CD)),
    LegendItem(range: '0.8 - 1.0', label: 'مسطح مائي', labelEn: 'Water Body', color: Color(0xFF00008B)),
  ];

  // ═══════════════════════════════════════════════════════════════════════════
  // EVI Colormap - Enhanced Vegetation Index
  // ═══════════════════════════════════════════════════════════════════════════

  static const List<ColorStop> _eviStops = [
    ColorStop(-1.0, Color(0xFF8B4513)), // Bare - Saddle Brown
    ColorStop(-0.1, Color(0xFFA0522D)), // Very sparse - Sienna
    ColorStop(0.0, Color(0xFFD2B48C)),  // Minimal - Tan
    ColorStop(0.1, Color(0xFFEEE8AA)),  // Very low - Pale Goldenrod
    ColorStop(0.2, Color(0xFFDAA520)),  // Low - Goldenrod
    ColorStop(0.3, Color(0xFFC0D860)),  // Moderate-low - Yellow-Green
    ColorStop(0.4, Color(0xFF7CFC00)),  // Moderate - Lawn Green
    ColorStop(0.5, Color(0xFF3CB371)),  // Good - Medium Sea Green
    ColorStop(0.6, Color(0xFF2E8B57)),  // Dense - Sea Green
    ColorStop(0.7, Color(0xFF228B22)),  // Very dense - Forest Green
    ColorStop(1.0, Color(0xFF004400)),  // Maximum - Very Dark Green
  ];

  static const List<LegendItem> _eviLegend = [
    LegendItem(range: '-1.0 - 0.0', label: 'تربة / غير نباتي', labelEn: 'Soil / Non-Vegetation', color: Color(0xFFA0522D)),
    LegendItem(range: '0.0 - 0.2', label: 'نباتات ضعيفة', labelEn: 'Sparse Vegetation', color: Color(0xFFDAA520)),
    LegendItem(range: '0.2 - 0.4', label: 'نمو معتدل', labelEn: 'Moderate Growth', color: Color(0xFF7CFC00)),
    LegendItem(range: '0.4 - 0.6', label: 'نباتات جيدة', labelEn: 'Good Vegetation', color: Color(0xFF3CB371)),
    LegendItem(range: '0.6 - 0.8', label: 'نباتات كثيفة', labelEn: 'Dense Vegetation', color: Color(0xFF228B22)),
    LegendItem(range: '0.8 - 1.0', label: 'غطاء نباتي أقصى', labelEn: 'Maximum Canopy', color: Color(0xFF004400)),
  ];

  // ═══════════════════════════════════════════════════════════════════════════
  // SAVI Colormap - Soil Adjusted Vegetation Index
  // ═══════════════════════════════════════════════════════════════════════════

  static const List<ColorStop> _saviStops = [
    ColorStop(-1.0, Color(0xFF8B4513)), // Bare - Saddle Brown
    ColorStop(-0.1, Color(0xFFC19A6B)), // Very low - Camel
    ColorStop(0.0, Color(0xFFE6D5AC)),  // Sand - Sand
    ColorStop(0.1, Color(0xFFEED9C4)),  // Low - Almond
    ColorStop(0.2, Color(0xFFF0E68C)),  // Sparse - Khaki
    ColorStop(0.3, Color(0xFFBDB76B)),  // Moderate-low - Dark Khaki
    ColorStop(0.4, Color(0xFF9ACD32)),  // Moderate - Yellow Green
    ColorStop(0.5, Color(0xFF6B8E23)),  // Good - Olive Drab
    ColorStop(0.6, Color(0xFF228B22)),  // Dense - Forest Green
    ColorStop(0.8, Color(0xFF006400)),  // Very Dense - Dark Green
    ColorStop(1.0, Color(0xFF003300)),  // Maximum - Very Dark Green
  ];

  static const List<LegendItem> _saviLegend = [
    LegendItem(range: '-1.0 - 0.0', label: 'تربة مكشوفة', labelEn: 'Exposed Soil', color: Color(0xFFC19A6B)),
    LegendItem(range: '0.0 - 0.2', label: 'نباتات متناثرة', labelEn: 'Sparse Vegetation', color: Color(0xFFF0E68C)),
    LegendItem(range: '0.2 - 0.4', label: 'نمو منخفض', labelEn: 'Low Growth', color: Color(0xFF9ACD32)),
    LegendItem(range: '0.4 - 0.6', label: 'نمو معتدل', labelEn: 'Moderate Growth', color: Color(0xFF6B8E23)),
    LegendItem(range: '0.6 - 0.8', label: 'نباتات كثيفة', labelEn: 'Dense Vegetation', color: Color(0xFF228B22)),
    LegendItem(range: '0.8 - 1.0', label: 'غطاء نباتي أقصى', labelEn: 'Maximum Canopy', color: Color(0xFF003300)),
  ];

  // ═══════════════════════════════════════════════════════════════════════════
  // NDRE Colormap - Red Edge Index
  // ═══════════════════════════════════════════════════════════════════════════

  static const List<ColorStop> _ndreStops = [
    ColorStop(-1.0, Color(0xFF800000)), // Very low N - Maroon
    ColorStop(-0.2, Color(0xFFB22222)), // Low N - Fire Brick
    ColorStop(0.0, Color(0xFFCD5C5C)),  // Deficient - Indian Red
    ColorStop(0.1, Color(0xFFFF8C00)),  // Stressed - Dark Orange
    ColorStop(0.2, Color(0xFFFFD700)),  // Marginal - Gold
    ColorStop(0.3, Color(0xFFADFF2F)),  // Adequate - Green Yellow
    ColorStop(0.4, Color(0xFF7FFF00)),  // Good - Chartreuse
    ColorStop(0.5, Color(0xFF32CD32)),  // Very good - Lime Green
    ColorStop(0.6, Color(0xFF228B22)),  // Excellent - Forest Green
    ColorStop(1.0, Color(0xFF006400)),  // Maximum - Dark Green
  ];

  static const List<LegendItem> _ndreLegend = [
    LegendItem(range: '-1.0 - 0.0', label: 'نقص شديد في النيتروجين', labelEn: 'Severe N Deficiency', color: Color(0xFFCD5C5C)),
    LegendItem(range: '0.0 - 0.2', label: 'نقص نيتروجين', labelEn: 'N Deficiency', color: Color(0xFFFF8C00)),
    LegendItem(range: '0.2 - 0.3', label: 'نيتروجين حدي', labelEn: 'Marginal N', color: Color(0xFFFFD700)),
    LegendItem(range: '0.3 - 0.4', label: 'نيتروجين كافٍ', labelEn: 'Adequate N', color: Color(0xFF7FFF00)),
    LegendItem(range: '0.4 - 0.6', label: 'نيتروجين جيد', labelEn: 'Good N Status', color: Color(0xFF32CD32)),
    LegendItem(range: '0.6 - 1.0', label: 'نيتروجين ممتاز', labelEn: 'Excellent N', color: Color(0xFF006400)),
  ];

  // ═══════════════════════════════════════════════════════════════════════════
  // LAI Colormap - Leaf Area Index (0 to 8)
  // ═══════════════════════════════════════════════════════════════════════════

  static const List<ColorStop> _laiStops = [
    ColorStop(0.0, Color(0xFFD2B48C)),  // Bare - Tan
    ColorStop(0.5, Color(0xFFF0E68C)),  // Very low - Khaki
    ColorStop(1.0, Color(0xFFBDB76B)),  // Low - Dark Khaki
    ColorStop(2.0, Color(0xFF9ACD32)),  // Moderate-low - Yellow Green
    ColorStop(3.0, Color(0xFF7CFC00)),  // Moderate - Lawn Green
    ColorStop(4.0, Color(0xFF32CD32)),  // Good - Lime Green
    ColorStop(5.0, Color(0xFF228B22)),  // Dense - Forest Green
    ColorStop(6.0, Color(0xFF006400)),  // Very Dense - Dark Green
    ColorStop(8.0, Color(0xFF003300)),  // Maximum - Very Dark Green
  ];

  static const List<LegendItem> _laiLegend = [
    LegendItem(range: '0.0 - 1.0', label: 'غطاء ضعيف', labelEn: 'Low Canopy', color: Color(0xFFF0E68C)),
    LegendItem(range: '1.0 - 2.0', label: 'غطاء منخفض', labelEn: 'Sparse Canopy', color: Color(0xFFBDB76B)),
    LegendItem(range: '2.0 - 3.0', label: 'غطاء متوسط', labelEn: 'Moderate Canopy', color: Color(0xFF9ACD32)),
    LegendItem(range: '3.0 - 4.0', label: 'غطاء جيد', labelEn: 'Good Canopy', color: Color(0xFF32CD32)),
    LegendItem(range: '4.0 - 6.0', label: 'غطاء كثيف', labelEn: 'Dense Canopy', color: Color(0xFF228B22)),
    LegendItem(range: '6.0 - 8.0', label: 'غطاء كثيف جداً', labelEn: 'Very Dense Canopy', color: Color(0xFF003300)),
  ];

  // ═══════════════════════════════════════════════════════════════════════════
  // Health Label Helpers
  // ═══════════════════════════════════════════════════════════════════════════

  static String _vegetationHealthLabel(double value, bool isArabic) {
    if (value >= 0.8) return isArabic ? 'ممتاز' : 'Excellent';
    if (value >= 0.6) return isArabic ? 'جيد' : 'Good';
    if (value >= 0.4) return isArabic ? 'مقبول' : 'Fair';
    if (value >= 0.2) return isArabic ? 'ضعيف' : 'Poor';
    return isArabic ? 'حرج' : 'Critical';
  }

  static String _waterHealthLabel(double value, bool isArabic) {
    if (value >= 0.6) return isArabic ? 'مشبع بالماء' : 'Water Saturated';
    if (value >= 0.3) return isArabic ? 'رطب' : 'Moist';
    if (value >= 0.1) return isArabic ? 'رطوبة معتدلة' : 'Moderate';
    if (value >= 0.0) return isArabic ? 'جاف' : 'Dry';
    return isArabic ? 'جاف جداً' : 'Very Dry';
  }

  static String _nitrogenHealthLabel(double value, bool isArabic) {
    if (value >= 0.5) return isArabic ? 'نيتروجين ممتاز' : 'Excellent N';
    if (value >= 0.3) return isArabic ? 'نيتروجين كافٍ' : 'Adequate N';
    if (value >= 0.1) return isArabic ? 'نقص نيتروجين' : 'N Deficiency';
    return isArabic ? 'نقص حاد' : 'Severe Deficiency';
  }

  static String _laiHealthLabel(double value, bool isArabic) {
    if (value >= 5.0) return isArabic ? 'كثيف جداً' : 'Very Dense';
    if (value >= 3.0) return isArabic ? 'جيد' : 'Good';
    if (value >= 1.5) return isArabic ? 'متوسط' : 'Moderate';
    if (value >= 0.5) return isArabic ? 'منخفض' : 'Low';
    return isArabic ? 'ضعيف جداً' : 'Very Low';
  }
}
