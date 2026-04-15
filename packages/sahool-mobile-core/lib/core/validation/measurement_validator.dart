/// Measurement Validator - Agricultural Measurement Validation
/// مدقق القياسات - التحقق من صحة القياسات الزراعية
///
/// Provides comprehensive validation for agricultural measurements:
/// - Area (hectares, square meters, dunums)
/// - Temperature (Celsius)
/// - Humidity and moisture levels
/// - NDVI and vegetation indices
/// - Water measurements (mm, liters)
/// - Yield and production quantities
/// - Date ranges (planting, harvest)
///
/// All validation messages are bilingual (Arabic/English).
library;

import 'validators.dart';

/// Agricultural measurement validator for SAHOOL platform
class MeasurementValidator {
  // ─────────────────────────────────────────────────────────────────────────────
  // Area Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate area in hectares
  static ValidationResult areaHectares(
    double? value, {
    double minArea = 0.01,
    double maxArea = 100000,
  }) {
    if (value == null) {
      return ValidationResult.error(
        'Area is required',
        'المساحة مطلوبة',
      );
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid area value',
        'قيمة المساحة غير صالحة',
      );
    }

    if (value < minArea) {
      return ValidationResult.error(
        'Area must be at least $minArea hectares',
        'المساحة يجب أن تكون $minArea هكتار على الأقل',
      );
    }

    if (value > maxArea) {
      return ValidationResult.error(
        'Area exceeds maximum ($maxArea hectares)',
        'المساحة تتجاوز الحد الأقصى ($maxArea هكتار)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate area in square meters
  static ValidationResult areaSquareMeters(
    double? value, {
    double minArea = 100,
    double maxArea = 1000000000, // 100,000 hectares
  }) {
    if (value == null) {
      return ValidationResult.error(
        'Area is required',
        'المساحة مطلوبة',
      );
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid area value',
        'قيمة المساحة غير صالحة',
      );
    }

    if (value < minArea) {
      return ValidationResult.error(
        'Area must be at least $minArea square meters',
        'المساحة يجب أن تكون $minArea متر مربع على الأقل',
      );
    }

    if (value > maxArea) {
      return ValidationResult.error(
        'Area exceeds maximum ($maxArea square meters)',
        'المساحة تتجاوز الحد الأقصى ($maxArea متر مربع)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate area in dunums (1 dunum = 1000 m² = 0.1 hectare)
  static ValidationResult areaDunums(
    double? value, {
    double minArea = 0.1,
    double maxArea = 1000000,
  }) {
    if (value == null) {
      return ValidationResult.error(
        'Area is required',
        'المساحة مطلوبة',
      );
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid area value',
        'قيمة المساحة غير صالحة',
      );
    }

    if (value < minArea) {
      return ValidationResult.error(
        'Area must be at least $minArea dunums',
        'المساحة يجب أن تكون $minArea دونم على الأقل',
      );
    }

    if (value > maxArea) {
      return ValidationResult.error(
        'Area exceeds maximum ($maxArea dunums)',
        'المساحة تتجاوز الحد الأقصى ($maxArea دونم)',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Temperature Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate temperature in Celsius
  static ValidationResult temperatureCelsius(
    double? value, {
    double minTemp = -50,
    double maxTemp = 60,
  }) {
    if (value == null) {
      return ValidationResult.error(
        'Temperature is required',
        'درجة الحرارة مطلوبة',
      );
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid temperature value',
        'قيمة درجة الحرارة غير صالحة',
      );
    }

    if (value < minTemp) {
      return ValidationResult.error(
        'Temperature is too low (minimum: $minTemp°C)',
        'درجة الحرارة منخفضة جداً (الحد الأدنى: $minTemp°م)',
      );
    }

    if (value > maxTemp) {
      return ValidationResult.error(
        'Temperature is too high (maximum: $maxTemp°C)',
        'درجة الحرارة مرتفعة جداً (الحد الأقصى: $maxTemp°م)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate temperature for agricultural monitoring (typical outdoor range)
  static ValidationResult agriculturalTemperature(double? value) {
    return temperatureCelsius(value, minTemp: -20, maxTemp: 55);
  }

  /// Validate soil temperature
  static ValidationResult soilTemperature(double? value) {
    return temperatureCelsius(value, minTemp: -10, maxTemp: 50);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Humidity & Moisture Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate humidity percentage (0-100%)
  static ValidationResult humidity(double? value) {
    return percentage(
      value,
      fieldName: 'Humidity',
      fieldNameAr: 'الرطوبة',
    );
  }

  /// Validate soil moisture percentage (0-100%)
  static ValidationResult soilMoisture(double? value) {
    return percentage(
      value,
      fieldName: 'Soil moisture',
      fieldNameAr: 'رطوبة التربة',
    );
  }

  /// Validate percentage value (0-100%)
  static ValidationResult percentage(
    double? value, {
    double minValue = 0,
    double maxValue = 100,
    String fieldName = 'Value',
    String fieldNameAr = 'القيمة',
  }) {
    if (value == null) {
      return ValidationResult.error(
        '$fieldName is required',
        '$fieldNameAr مطلوبة',
      );
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid $fieldName value',
        'قيمة $fieldNameAr غير صالحة',
      );
    }

    if (value < minValue) {
      return ValidationResult.error(
        '$fieldName must be at least $minValue%',
        '$fieldNameAr يجب أن تكون $minValue% على الأقل',
      );
    }

    if (value > maxValue) {
      return ValidationResult.error(
        '$fieldName cannot exceed $maxValue%',
        '$fieldNameAr لا يمكن أن تتجاوز $maxValue%',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Vegetation Index Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate NDVI value (Normalized Difference Vegetation Index)
  /// Range: -1 to 1 (typically 0 to 1 for vegetation)
  static ValidationResult ndvi(
    double? value, {
    double minValue = -1,
    double maxValue = 1,
  }) {
    if (value == null) {
      return ValidationResult.success; // NDVI is often optional
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid NDVI value',
        'قيمة NDVI غير صالحة',
      );
    }

    if (value < minValue || value > maxValue) {
      return ValidationResult.error(
        'NDVI must be between $minValue and $maxValue',
        'مؤشر NDVI يجب أن يكون بين $minValue و $maxValue',
      );
    }

    return ValidationResult.success;
  }

  /// Validate LAI value (Leaf Area Index)
  /// Range: 0 to 10+ (typically 0-8 for most crops)
  static ValidationResult lai(
    double? value, {
    double minValue = 0,
    double maxValue = 15,
  }) {
    if (value == null) {
      return ValidationResult.success; // LAI is often optional
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid LAI value',
        'قيمة LAI غير صالحة',
      );
    }

    if (value < minValue || value > maxValue) {
      return ValidationResult.error(
        'LAI must be between $minValue and $maxValue',
        'مؤشر LAI يجب أن يكون بين $minValue و $maxValue',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Water Measurement Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate water amount in millimeters (precipitation/irrigation)
  static ValidationResult waterMillimeters(
    double? value, {
    double minValue = 0,
    double maxValue = 500,
  }) {
    if (value == null) {
      return ValidationResult.error(
        'Water amount is required',
        'كمية المياه مطلوبة',
      );
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid water amount',
        'كمية المياه غير صالحة',
      );
    }

    if (value < minValue) {
      return ValidationResult.error(
        'Water amount must be at least $minValue mm',
        'كمية المياه يجب أن تكون $minValue مم على الأقل',
      );
    }

    if (value > maxValue) {
      return ValidationResult.error(
        'Water amount exceeds maximum ($maxValue mm)',
        'كمية المياه تتجاوز الحد الأقصى ($maxValue مم)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate water volume in liters
  static ValidationResult waterLiters(
    double? value, {
    double minValue = 0,
    double maxValue = 10000000, // 10,000 cubic meters
  }) {
    if (value == null) {
      return ValidationResult.error(
        'Water volume is required',
        'حجم المياه مطلوب',
      );
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid water volume',
        'حجم المياه غير صالح',
      );
    }

    if (value < minValue) {
      return ValidationResult.error(
        'Water volume must be at least $minValue liters',
        'حجم المياه يجب أن يكون $minValue لتر على الأقل',
      );
    }

    if (value > maxValue) {
      return ValidationResult.error(
        'Water volume exceeds maximum ($maxValue liters)',
        'حجم المياه يتجاوز الحد الأقصى ($maxValue لتر)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate evapotranspiration (ET) in mm/day
  static ValidationResult evapotranspiration(
    double? value, {
    double minValue = 0,
    double maxValue = 20,
  }) {
    if (value == null) {
      return ValidationResult.success; // ET is often optional
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid ET value',
        'قيمة التبخر-النتح غير صالحة',
      );
    }

    if (value < minValue || value > maxValue) {
      return ValidationResult.error(
        'ET must be between $minValue and $maxValue mm/day',
        'التبخر-النتح يجب أن يكون بين $minValue و $maxValue مم/يوم',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Yield & Production Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate yield in tons per hectare
  static ValidationResult yieldTonsPerHectare(
    double? value, {
    double minValue = 0,
    double maxValue = 100,
  }) {
    if (value == null) {
      return ValidationResult.error(
        'Yield is required',
        'الإنتاجية مطلوبة',
      );
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid yield value',
        'قيمة الإنتاجية غير صالحة',
      );
    }

    if (value < minValue) {
      return ValidationResult.error(
        'Yield must be at least $minValue tons/ha',
        'الإنتاجية يجب أن تكون $minValue طن/هكتار على الأقل',
      );
    }

    if (value > maxValue) {
      return ValidationResult.error(
        'Yield exceeds maximum ($maxValue tons/ha)',
        'الإنتاجية تتجاوز الحد الأقصى ($maxValue طن/هكتار)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate weight in kilograms
  static ValidationResult weightKilograms(
    double? value, {
    double minValue = 0,
    double? maxValue,
    String fieldName = 'Weight',
    String fieldNameAr = 'الوزن',
  }) {
    if (value == null) {
      return ValidationResult.error(
        '$fieldName is required',
        '$fieldNameAr مطلوب',
      );
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid $fieldName value',
        'قيمة $fieldNameAr غير صالحة',
      );
    }

    if (value < minValue) {
      return ValidationResult.error(
        '$fieldName must be at least $minValue kg',
        '$fieldNameAr يجب أن يكون $minValue كجم على الأقل',
      );
    }

    if (maxValue != null && value > maxValue) {
      return ValidationResult.error(
        '$fieldName exceeds maximum ($maxValue kg)',
        '$fieldNameAr يتجاوز الحد الأقصى ($maxValue كجم)',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Date Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate date range
  static ValidationResult dateRange(
    DateTime? value, {
    DateTime? minDate,
    DateTime? maxDate,
    String fieldName = 'Date',
    String fieldNameAr = 'التاريخ',
  }) {
    if (value == null) {
      return ValidationResult.error(
        '$fieldName is required',
        '$fieldNameAr مطلوب',
      );
    }

    if (minDate != null && value.isBefore(minDate)) {
      final formattedMin = _formatDate(minDate);
      return ValidationResult.error(
        '$fieldName must be on or after $formattedMin',
        '$fieldNameAr يجب أن يكون في أو بعد $formattedMin',
      );
    }

    if (maxDate != null && value.isAfter(maxDate)) {
      final formattedMax = _formatDate(maxDate);
      return ValidationResult.error(
        '$fieldName must be on or before $formattedMax',
        '$fieldNameAr يجب أن يكون في أو قبل $formattedMax',
      );
    }

    return ValidationResult.success;
  }

  /// Validate date is not in the future
  static ValidationResult dateNotFuture(
    DateTime? value, {
    String fieldName = 'Date',
    String fieldNameAr = 'التاريخ',
  }) {
    if (value == null) {
      return ValidationResult.error(
        '$fieldName is required',
        '$fieldNameAr مطلوب',
      );
    }

    final now = DateTime.now();
    final endOfToday = DateTime(now.year, now.month, now.day, 23, 59, 59);

    if (value.isAfter(endOfToday)) {
      return ValidationResult.error(
        '$fieldName cannot be in the future',
        '$fieldNameAr لا يمكن أن يكون في المستقبل',
      );
    }

    return ValidationResult.success;
  }

  /// Validate date is not in the past
  static ValidationResult dateNotPast(
    DateTime? value, {
    String fieldName = 'Date',
    String fieldNameAr = 'التاريخ',
  }) {
    if (value == null) {
      return ValidationResult.error(
        '$fieldName is required',
        '$fieldNameAr مطلوب',
      );
    }

    final now = DateTime.now();
    final startOfToday = DateTime(now.year, now.month, now.day);

    if (value.isBefore(startOfToday)) {
      return ValidationResult.error(
        '$fieldName cannot be in the past',
        '$fieldNameAr لا يمكن أن يكون في الماضي',
      );
    }

    return ValidationResult.success;
  }

  /// Validate planting date (within reasonable range)
  static ValidationResult plantingDate(DateTime? value) {
    if (value == null) {
      return ValidationResult.error(
        'Planting date is required',
        'تاريخ الزراعة مطلوب',
      );
    }

    // Planting date can be up to 5 years in the past and up to 1 year in the future
    final now = DateTime.now();
    final minDate = DateTime(now.year - 5, now.month, now.day);
    final maxDate = DateTime(now.year + 1, now.month, now.day);

    return dateRange(
      value,
      minDate: minDate,
      maxDate: maxDate,
      fieldName: 'Planting date',
      fieldNameAr: 'تاريخ الزراعة',
    );
  }

  /// Validate harvest date (must be after planting)
  static ValidationResult harvestDate(
    DateTime? value, {
    DateTime? plantingDate,
  }) {
    if (value == null) {
      return ValidationResult.error(
        'Harvest date is required',
        'تاريخ الحصاد مطلوب',
      );
    }

    // Check not in future
    final futureResult = dateNotFuture(
      value,
      fieldName: 'Harvest date',
      fieldNameAr: 'تاريخ الحصاد',
    );
    if (!futureResult.isValid) {
      return futureResult;
    }

    // Check after planting date if provided
    if (plantingDate != null && value.isBefore(plantingDate)) {
      return ValidationResult.error(
        'Harvest date must be after planting date',
        'تاريخ الحصاد يجب أن يكون بعد تاريخ الزراعة',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Generic Numeric Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate numeric value with optional range
  static ValidationResult numericRange(
    double? value, {
    double? minValue,
    double? maxValue,
    String fieldName = 'Value',
    String fieldNameAr = 'القيمة',
    String? unit,
    String? unitAr,
  }) {
    if (value == null) {
      return ValidationResult.error(
        '$fieldName is required',
        '$fieldNameAr مطلوب',
      );
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid $fieldName value',
        'قيمة $fieldNameAr غير صالحة',
      );
    }

    final unitSuffix = unit != null ? ' $unit' : '';
    final unitSuffixAr = unitAr != null ? ' $unitAr' : '';

    if (minValue != null && value < minValue) {
      return ValidationResult.error(
        '$fieldName must be at least $minValue$unitSuffix',
        '$fieldNameAr يجب أن يكون $minValue$unitSuffixAr على الأقل',
      );
    }

    if (maxValue != null && value > maxValue) {
      return ValidationResult.error(
        '$fieldName cannot exceed $maxValue$unitSuffix',
        '$fieldNameAr لا يمكن أن يتجاوز $maxValue$unitSuffixAr',
      );
    }

    return ValidationResult.success;
  }

  /// Validate positive number
  static ValidationResult positiveNumber(
    double? value, {
    bool allowZero = false,
    String fieldName = 'Value',
    String fieldNameAr = 'القيمة',
  }) {
    if (value == null) {
      return ValidationResult.error(
        '$fieldName is required',
        '$fieldNameAr مطلوب',
      );
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid $fieldName value',
        'قيمة $fieldNameAr غير صالحة',
      );
    }

    if (allowZero) {
      if (value < 0) {
        return ValidationResult.error(
          '$fieldName cannot be negative',
          '$fieldNameAr لا يمكن أن يكون سالباً',
        );
      }
    } else {
      if (value <= 0) {
        return ValidationResult.error(
          '$fieldName must be greater than zero',
          '$fieldNameAr يجب أن يكون أكبر من صفر',
        );
      }
    }

    return ValidationResult.success;
  }

  /// Validate integer value
  static ValidationResult integer(
    double? value, {
    int? minValue,
    int? maxValue,
    String fieldName = 'Value',
    String fieldNameAr = 'القيمة',
  }) {
    if (value == null) {
      return ValidationResult.error(
        '$fieldName is required',
        '$fieldNameAr مطلوب',
      );
    }

    if (value.isNaN || value.isInfinite) {
      return ValidationResult.error(
        'Invalid $fieldName value',
        'قيمة $fieldNameAr غير صالحة',
      );
    }

    if (value != value.roundToDouble()) {
      return ValidationResult.error(
        '$fieldName must be a whole number',
        '$fieldNameAr يجب أن يكون رقماً صحيحاً',
      );
    }

    final intValue = value.round();

    if (minValue != null && intValue < minValue) {
      return ValidationResult.error(
        '$fieldName must be at least $minValue',
        '$fieldNameAr يجب أن يكون $minValue على الأقل',
      );
    }

    if (maxValue != null && intValue > maxValue) {
      return ValidationResult.error(
        '$fieldName cannot exceed $maxValue',
        '$fieldNameAr لا يمكن أن يتجاوز $maxValue',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Helper Methods
  // ─────────────────────────────────────────────────────────────────────────────

  /// Format date for display in error messages
  static String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }
}
