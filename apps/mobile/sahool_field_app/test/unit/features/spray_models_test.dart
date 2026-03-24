/// Spray Models Tests - اختبارات نماذج الرش
/// Tests for spray timing, weather suitability, drift risk calculations
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/spray/models/spray_models.dart';

// ═════════════════════════════════════════════════════════════════════════════
// Test Helpers
// ═════════════════════════════════════════════════════════════════════════════

WeatherCondition _makeWeather({
  double temperature = 20,
  double humidity = 60,
  double windSpeed = 10,
  double rainProbability = 10,
  String conditionId = 'w1',
  String windDirection = 'NW',
  String? windDirectionAr,
  String condition = 'clear',
  String? conditionAr,
}) {
  return WeatherCondition(
    conditionId: conditionId,
    timestamp: DateTime(2026, 3, 20, 10, 0),
    temperature: temperature,
    humidity: humidity,
    windSpeed: windSpeed,
    windDirection: windDirection,
    windDirectionAr: windDirectionAr,
    rainProbability: rainProbability,
    condition: condition,
    conditionAr: conditionAr,
  );
}

SprayProduct _makeProduct({
  SprayType type = SprayType.insecticide,
  String? targetPest = 'Aphid',
  String? targetPestAr = 'المن',
  String? targetDisease,
  String? targetDiseaseAr,
}) {
  return SprayProduct(
    productId: 'p1',
    name: 'TestProduct',
    nameAr: 'منتج اختبار',
    type: type,
    manufacturer: 'Mfg',
    manufacturerAr: 'شركة',
    activeIngredient: 'AI',
    activeIngredientAr: 'مادة فعالة',
    concentration: 25.0,
    unit: 'L/ha',
    unitAr: 'لتر/هكتار',
    recommendedRate: 2.0,
    minRate: 1.0,
    maxRate: 3.0,
    phi: 14,
    rei: 24,
    targetPest: targetPest,
    targetPestAr: targetPestAr,
    targetDisease: targetDisease,
    targetDiseaseAr: targetDiseaseAr,
    notes: 'Test notes',
    notesAr: 'ملاحظات',
    createdAt: DateTime(2026, 1, 1),
    updatedAt: DateTime(2026, 1, 1),
  );
}

Map<String, dynamic> _weatherJson() => {
      'condition_id': 'w1',
      'timestamp': '2026-03-20T10:00:00.000',
      'temperature': 20.0,
      'humidity': 60.0,
      'wind_speed': 10.0,
      'wind_direction': 'NW',
      'wind_direction_ar': 'شمال غرب',
      'rain_probability': 10.0,
      'rainfall': 0.0,
      'pressure': 1013.0,
      'condition': 'clear',
      'condition_ar': 'صافي',
    };

Map<String, dynamic> _productJson() => {
      'product_id': 'p1',
      'name': 'TestProduct',
      'name_ar': 'منتج',
      'type': 'insecticide',
      'manufacturer': 'Mfg',
      'manufacturer_ar': 'شركة',
      'active_ingredient': 'AI',
      'active_ingredient_ar': 'مادة',
      'concentration': 25.0,
      'unit': 'L/ha',
      'unit_ar': 'لتر/هكتار',
      'recommended_rate': 2.0,
      'min_rate': 1.0,
      'max_rate': 3.0,
      'phi': 14,
      'rei': 24,
      'target_pest': 'Aphid',
      'target_pest_ar': 'المن',
      'notes': 'notes',
      'notes_ar': 'ملاحظات',
      'is_yemen_product': true,
      'created_at': '2026-01-01T00:00:00.000',
      'updated_at': '2026-01-01T00:00:00.000',
    };

void main() {
  // ═════════════════════════════════════════════════════════════════════════
  // Enum Tests
  // ═════════════════════════════════════════════════════════════════════════

  group('SprayType', () {
    test('has exactly 4 values', () {
      expect(SprayType.values.length, 4);
    });
    test('getName returns Arabic for ar locale', () {
      expect(SprayType.herbicide.getName('ar'), 'مبيد أعشاب');
      expect(SprayType.fungicide.getName('ar'), 'مبيد فطري');
      expect(SprayType.insecticide.getName('ar'), 'مبيد حشري');
      expect(SprayType.foliar.getName('ar'), 'سماد ورقي');
    });
    test('getName returns English for en locale', () {
      expect(SprayType.herbicide.getName('en'), 'Herbicide');
      expect(SprayType.fungicide.getName('en'), 'Fungicide');
      expect(SprayType.insecticide.getName('en'), 'Insecticide');
      expect(SprayType.foliar.getName('en'), 'Foliar Fertilizer');
    });
    test('fromString parses valid values', () {
      expect(SprayType.fromString('herbicide'), SprayType.herbicide);
      expect(SprayType.fromString('fungicide'), SprayType.fungicide);
      expect(SprayType.fromString('insecticide'), SprayType.insecticide);
      expect(SprayType.fromString('foliar'), SprayType.foliar);
    });
    test('fromString returns herbicide for unknown', () {
      expect(SprayType.fromString('unknown'), SprayType.herbicide);
      expect(SprayType.fromString(''), SprayType.herbicide);
    });
  });

  group('SprayWindowStatus', () {
    test('has exactly 3 values', () {
      expect(SprayWindowStatus.values.length, 3);
    });
    test('getName returns correct locale', () {
      expect(SprayWindowStatus.optimal.getName('ar'), 'مثالي');
      expect(SprayWindowStatus.optimal.getName('en'), 'Optimal');
      expect(SprayWindowStatus.caution.getName('ar'), 'حذر');
      expect(SprayWindowStatus.avoid.getName('ar'), 'تجنب');
    });
    test('fromString returns caution for unknown', () {
      expect(SprayWindowStatus.fromString('unknown'), SprayWindowStatus.caution);
    });
  });

  group('RecommendationStatus', () {
    test('has exactly 4 values', () {
      expect(RecommendationStatus.values.length, 4);
    });
    test('fromString parses all values', () {
      expect(RecommendationStatus.fromString('active'), RecommendationStatus.active);
      expect(RecommendationStatus.fromString('completed'), RecommendationStatus.completed);
      expect(RecommendationStatus.fromString('expired'), RecommendationStatus.expired);
      expect(RecommendationStatus.fromString('cancelled'), RecommendationStatus.cancelled);
    });
    test('fromString returns active for unknown', () {
      expect(RecommendationStatus.fromString('xyz'), RecommendationStatus.active);
    });
  });

  group('DriftRiskLevel', () {
    test('has exactly 3 values', () {
      expect(DriftRiskLevel.values.length, 3);
    });
    test('fromString returns medium for unknown', () {
      expect(DriftRiskLevel.fromString('xyz'), DriftRiskLevel.medium);
    });
    test('getName locale support', () {
      expect(DriftRiskLevel.low.getName('ar'), 'منخفض');
      expect(DriftRiskLevel.high.getName('en'), 'High');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════
  // WeatherCondition - Suitability & Drift Risk
  // ═════════════════════════════════════════════════════════════════════════

  group('WeatherCondition.isSuitableForSpraying', () {
    test('ideal conditions return true', () {
      final w = _makeWeather(temperature: 20, humidity: 60, windSpeed: 10, rainProbability: 10);
      expect(w.isSuitableForSpraying, true);
    });
    test('boundary: temp exactly 15 is suitable', () {
      expect(_makeWeather(temperature: 15).isSuitableForSpraying, true);
    });
    test('boundary: temp exactly 25 is suitable', () {
      expect(_makeWeather(temperature: 25).isSuitableForSpraying, true);
    });
    test('temp below 15 not suitable', () {
      expect(_makeWeather(temperature: 14.9).isSuitableForSpraying, false);
    });
    test('temp above 25 not suitable', () {
      expect(_makeWeather(temperature: 25.1).isSuitableForSpraying, false);
    });
    test('humidity exactly 50 is suitable', () {
      expect(_makeWeather(humidity: 50).isSuitableForSpraying, true);
    });
    test('humidity exactly 70 is suitable', () {
      expect(_makeWeather(humidity: 70).isSuitableForSpraying, true);
    });
    test('humidity below 50 not suitable', () {
      expect(_makeWeather(humidity: 49).isSuitableForSpraying, false);
    });
    test('wind exactly 14.9 is suitable', () {
      expect(_makeWeather(windSpeed: 14.9).isSuitableForSpraying, true);
    });
    test('wind 15 is NOT suitable (strict less-than)', () {
      expect(_makeWeather(windSpeed: 15).isSuitableForSpraying, false);
    });
    test('rain 19.9 is suitable', () {
      expect(_makeWeather(rainProbability: 19.9).isSuitableForSpraying, true);
    });
    test('rain 20 is NOT suitable', () {
      expect(_makeWeather(rainProbability: 20).isSuitableForSpraying, false);
    });
  });

  group('WeatherCondition.spraySuitabilityScore', () {
    test('perfect conditions score 100', () {
      expect(_makeWeather(temperature: 20, humidity: 60, windSpeed: 5, rainProbability: 5).spraySuitabilityScore, 100);
    });
    test('temp <10 deducts 40', () {
      expect(_makeWeather(temperature: 9).spraySuitabilityScore, 60);
    });
    test('temp >30 deducts 40', () {
      expect(_makeWeather(temperature: 31).spraySuitabilityScore, 60);
    });
    test('temp 10-15 deducts 20', () {
      expect(_makeWeather(temperature: 12).spraySuitabilityScore, 80);
    });
    test('temp 25-30 deducts 20', () {
      expect(_makeWeather(temperature: 28).spraySuitabilityScore, 80);
    });
    test('humidity <40 deducts 30', () {
      expect(_makeWeather(humidity: 35).spraySuitabilityScore, 70);
    });
    test('humidity >80 deducts 30', () {
      expect(_makeWeather(humidity: 85).spraySuitabilityScore, 70);
    });
    test('humidity 40-50 deducts 15', () {
      expect(_makeWeather(humidity: 45).spraySuitabilityScore, 85);
    });
    test('wind >20 deducts 40', () {
      expect(_makeWeather(windSpeed: 25).spraySuitabilityScore, 60);
    });
    test('wind 15-20 deducts 20', () {
      expect(_makeWeather(windSpeed: 18).spraySuitabilityScore, 80);
    });
    test('rain >40 deducts 30', () {
      expect(_makeWeather(rainProbability: 50).spraySuitabilityScore, 70);
    });
    test('rain 20-40 deducts 15', () {
      expect(_makeWeather(rainProbability: 30).spraySuitabilityScore, 85);
    });
    test('worst conditions clamp to 0', () {
      final w = _makeWeather(temperature: 5, humidity: 30, windSpeed: 25, rainProbability: 50);
      expect(w.spraySuitabilityScore, greaterThanOrEqualTo(0));
    });
    test('multiple deductions combine correctly', () {
      // temp<10: -40, humidity<40: -30, wind>20: -40, rain>40: -30 = -140 → clamped to 0
      final w = _makeWeather(temperature: 5, humidity: 30, windSpeed: 25, rainProbability: 50);
      expect(w.spraySuitabilityScore, 0);
    });
  });

  group('WeatherCondition.driftRiskScore', () {
    test('calm conditions low risk', () {
      final w = _makeWeather(temperature: 20, humidity: 70, windSpeed: 3);
      expect(w.driftRiskScore, 0);
    });
    test('wind >=5 adds 10', () {
      expect(_makeWeather(windSpeed: 5, humidity: 70).driftRiskScore, 10);
    });
    test('wind >=10 adds 20 (not cumulative)', () {
      expect(_makeWeather(windSpeed: 10, humidity: 70).driftRiskScore, 20);
    });
    test('wind >=15 adds 35', () {
      expect(_makeWeather(windSpeed: 15, humidity: 70).driftRiskScore, 35);
    });
    test('wind >=20 adds 50', () {
      expect(_makeWeather(windSpeed: 20, humidity: 70).driftRiskScore, 50);
    });
    test('temp >30 adds 25', () {
      expect(_makeWeather(temperature: 35, humidity: 70, windSpeed: 3).driftRiskScore, 25);
    });
    test('temp >25 adds 15', () {
      expect(_makeWeather(temperature: 28, humidity: 70, windSpeed: 3).driftRiskScore, 15);
    });
    test('temp <10 adds 10', () {
      expect(_makeWeather(temperature: 5, humidity: 70, windSpeed: 3).driftRiskScore, 10);
    });
    test('humidity <40 adds 25', () {
      expect(_makeWeather(humidity: 35, windSpeed: 3).driftRiskScore, 25);
    });
    test('humidity <50 adds 15', () {
      expect(_makeWeather(humidity: 45, windSpeed: 3).driftRiskScore, 15);
    });
    test('humidity <60 adds 5', () {
      expect(_makeWeather(humidity: 55, windSpeed: 3).driftRiskScore, 5);
    });
    test('combined worst case clamped to 100', () {
      // wind>=20: 50, temp>30: 25, humidity<40: 25 = 100
      final w = _makeWeather(windSpeed: 25, temperature: 35, humidity: 30);
      expect(w.driftRiskScore, 100);
    });
  });

  group('WeatherCondition.driftRiskLevel', () {
    test('score >=60 is high', () {
      // wind>=20: 50 + humidity<40: 25 = 75 → high
      expect(_makeWeather(windSpeed: 25, humidity: 30).driftRiskLevel, DriftRiskLevel.high);
    });
    test('score 30-59 is medium', () {
      // wind>=15: 35 → medium
      expect(_makeWeather(windSpeed: 15, humidity: 70).driftRiskLevel, DriftRiskLevel.medium);
    });
    test('score <30 is low', () {
      expect(_makeWeather(windSpeed: 3, humidity: 70).driftRiskLevel, DriftRiskLevel.low);
    });
  });

  group('WeatherCondition.isDriftRiskAcceptable', () {
    test('score <40 is acceptable', () {
      expect(_makeWeather(windSpeed: 10, humidity: 70).isDriftRiskAcceptable, true);
    });
    test('score >=40 is not acceptable', () {
      // wind>=15: 35 + humidity<50: 15 = 50
      expect(_makeWeather(windSpeed: 15, humidity: 45).isDriftRiskAcceptable, false);
    });
  });

  group('WeatherCondition locale getters', () {
    test('getWindDirection returns Arabic when available', () {
      final w = _makeWeather(windDirection: 'NW', windDirectionAr: 'شمال غرب');
      expect(w.getWindDirection('ar'), 'شمال غرب');
      expect(w.getWindDirection('en'), 'NW');
    });
    test('getWindDirection fallback to English when Arabic null', () {
      final w = _makeWeather(windDirection: 'NW');
      expect(w.getWindDirection('ar'), 'NW');
    });
    test('getCondition locale support', () {
      final w = _makeWeather(condition: 'clear', conditionAr: 'صافي');
      expect(w.getCondition('ar'), 'صافي');
      expect(w.getCondition('en'), 'clear');
    });
  });

  group('WeatherCondition fromJson/toJson', () {
    test('round-trip preserves data', () {
      final json = _weatherJson();
      final w = WeatherCondition.fromJson(json);
      final result = w.toJson();
      expect(result['condition_id'], 'w1');
      expect(result['temperature'], 20.0);
      expect(result['humidity'], 60.0);
      expect(result['wind_speed'], 10.0);
      expect(result['rain_probability'], 10.0);
      expect(result['condition'], 'clear');
      expect(result['condition_ar'], 'صافي');
    });
    test('fromJson parses timestamp correctly', () {
      final w = WeatherCondition.fromJson(_weatherJson());
      expect(w.timestamp.year, 2026);
      expect(w.timestamp.month, 3);
    });
  });

  group('WeatherCondition.copyWith', () {
    test('changes only specified fields', () {
      final w = _makeWeather(temperature: 20, humidity: 60);
      final w2 = w.copyWith(temperature: 30);
      expect(w2.temperature, 30);
      expect(w2.humidity, 60); // unchanged
    });
  });

  // ═════════════════════════════════════════════════════════════════════════
  // SprayProduct
  // ═════════════════════════════════════════════════════════════════════════

  group('SprayProduct', () {
    test('fromJson round-trip', () {
      final json = _productJson();
      final p = SprayProduct.fromJson(json);
      final result = p.toJson();
      expect(result['product_id'], 'p1');
      expect(result['type'], 'insecticide');
      expect(result['concentration'], 25.0);
      expect(result['is_yemen_product'], true);
    });
    test('getDisplayName locale', () {
      final p = _makeProduct();
      expect(p.getDisplayName('ar'), 'منتج اختبار');
      expect(p.getDisplayName('en'), 'TestProduct');
    });
    test('getManufacturer locale', () {
      final p = _makeProduct();
      expect(p.getManufacturer('ar'), 'شركة');
      expect(p.getManufacturer('en'), 'Mfg');
    });
    test('getTarget returns pest for insecticide', () {
      final p = _makeProduct(type: SprayType.insecticide, targetPest: 'Aphid', targetPestAr: 'المن');
      expect(p.getTarget('en'), 'Aphid');
      expect(p.getTarget('ar'), 'المن');
    });
    test('getTarget returns pest for herbicide', () {
      final p = _makeProduct(type: SprayType.herbicide, targetPest: 'Weed');
      expect(p.getTarget('en'), 'Weed');
    });
    test('getTarget returns disease for fungicide', () {
      final p = _makeProduct(type: SprayType.fungicide, targetDisease: 'Rust', targetDiseaseAr: 'صدأ');
      expect(p.getTarget('en'), 'Rust');
      expect(p.getTarget('ar'), 'صدأ');
    });
    test('getTarget returns disease for foliar', () {
      final p = _makeProduct(type: SprayType.foliar, targetDisease: 'Blight');
      expect(p.getTarget('en'), 'Blight');
    });
    test('getNotes locale support', () {
      final p = _makeProduct();
      expect(p.getNotes('ar'), 'ملاحظات');
      expect(p.getNotes('en'), 'Test notes');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════
  // SprayWindow
  // ═════════════════════════════════════════════════════════════════════════

  group('SprayWindow', () {
    late SprayWindow window;
    setUp(() {
      window = SprayWindow(
        windowId: 'sw1',
        startTime: DateTime(2026, 3, 20, 6, 0),
        endTime: DateTime(2026, 3, 20, 12, 0),
        status: SprayWindowStatus.optimal,
        weatherCondition: _makeWeather(),
        confidenceScore: 85,
        reason: 'Good conditions',
        reasonAr: 'ظروف جيدة',
        warnings: ['Wind may increase'],
        warningsAr: ['قد تزداد الرياح'],
      );
    });

    test('durationHours calculates correctly', () {
      expect(window.durationHours, 6);
    });
    test('durationHours for short window', () {
      final w = window.copyWith(
        startTime: DateTime(2026, 3, 20, 10, 0),
        endTime: DateTime(2026, 3, 20, 11, 30),
      );
      expect(w.durationHours, 1); // inHours truncates
    });
    test('getReason returns Arabic for ar', () {
      expect(window.getReason('ar'), 'ظروف جيدة');
      expect(window.getReason('en'), 'Good conditions');
    });
    test('getWarnings returns Arabic for ar', () {
      expect(window.getWarnings('ar'), ['قد تزداد الرياح']);
      expect(window.getWarnings('en'), ['Wind may increase']);
    });
    test('getWarnings returns English when Arabic empty', () {
      final w = window.copyWith(warningsAr: []);
      expect(w.getWarnings('ar'), ['Wind may increase']);
    });

    test('fromJson/toJson round-trip', () {
      final json = {
        'window_id': 'sw1',
        'start_time': '2026-03-20T06:00:00.000',
        'end_time': '2026-03-20T12:00:00.000',
        'status': 'optimal',
        'weather_condition': _weatherJson(),
        'confidence_score': 85,
        'reason': 'Good',
        'warnings': ['warn1'],
        'warnings_ar': ['تحذير1'],
      };
      final sw = SprayWindow.fromJson(json);
      expect(sw.windowId, 'sw1');
      expect(sw.status, SprayWindowStatus.optimal);
      expect(sw.confidenceScore, 85);
      final result = sw.toJson();
      expect(result['window_id'], 'sw1');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════
  // SprayRecommendation
  // ═════════════════════════════════════════════════════════════════════════

  group('SprayRecommendation', () {
    SprayRecommendation makeRec({RecommendationStatus status = RecommendationStatus.active}) {
      return SprayRecommendation(
        recommendationId: 'r1',
        tenantId: 't1',
        fieldId: 'f1',
        fieldName: 'Field 1',
        fieldNameAr: 'حقل 1',
        title: 'Spray Now',
        titleAr: 'رش الآن',
        description: 'Apply herbicide',
        descriptionAr: 'تطبيق مبيد',
        sprayType: SprayType.herbicide,
        status: status,
        recommendedRate: 2.5,
        unit: 'L/ha',
        unitAr: 'لتر/هـ',
        priority: 3,
        createdAt: DateTime(2026, 1, 1),
        updatedAt: DateTime(2026, 1, 1),
      );
    }

    test('isActive returns true for active status', () {
      expect(makeRec(status: RecommendationStatus.active).isActive, true);
      expect(makeRec(status: RecommendationStatus.completed).isActive, false);
    });
    test('isCompleted returns true for completed status', () {
      expect(makeRec(status: RecommendationStatus.completed).isCompleted, true);
      expect(makeRec(status: RecommendationStatus.active).isCompleted, false);
    });
    test('isExpired returns true for expired status', () {
      expect(makeRec(status: RecommendationStatus.expired).isExpired, true);
      expect(makeRec(status: RecommendationStatus.active).isExpired, false);
    });
    test('getTitle locale', () {
      final r = makeRec();
      expect(r.getTitle('ar'), 'رش الآن');
      expect(r.getTitle('en'), 'Spray Now');
    });
    test('getDescription locale', () {
      final r = makeRec();
      expect(r.getDescription('ar'), 'تطبيق مبيد');
      expect(r.getDescription('en'), 'Apply herbicide');
    });
    test('getFieldName locale', () {
      final r = makeRec();
      expect(r.getFieldName('ar'), 'حقل 1');
      expect(r.getFieldName('en'), 'Field 1');
    });
    test('daysUntilTarget returns null when no targetDate', () {
      expect(makeRec().daysUntilTarget, null);
    });
    test('nextOptimalWindow returns null when no windows', () {
      expect(makeRec().nextOptimalWindow, null);
    });

    test('fromJson with full data', () {
      final json = {
        'recommendation_id': 'r1',
        'tenant_id': 't1',
        'field_id': 'f1',
        'field_name': 'Field',
        'title': 'Title',
        'description': 'Desc',
        'spray_type': 'herbicide',
        'status': 'active',
        'recommended_rate': 2.5,
        'unit': 'L/ha',
        'priority': 3,
        'created_at': '2026-01-01T00:00:00.000',
        'updated_at': '2026-01-01T00:00:00.000',
      };
      final r = SprayRecommendation.fromJson(json);
      expect(r.recommendationId, 'r1');
      expect(r.sprayType, SprayType.herbicide);
      expect(r.status, RecommendationStatus.active);
      expect(r.recommendedRate, 2.5);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════
  // SprayApplicationLog
  // ═════════════════════════════════════════════════════════════════════════

  group('SprayApplicationLog', () {
    test('fromJson/toJson round-trip', () {
      final json = {
        'log_id': 'l1',
        'tenant_id': 't1',
        'field_id': 'f1',
        'field_name': 'Field',
        'field_name_ar': 'حقل',
        'spray_type': 'insecticide',
        'product': _productJson(),
        'applied_rate': 2.0,
        'unit': 'L/ha',
        'unit_ar': 'لتر/هـ',
        'area': 5.0,
        'total_quantity': 10.0,
        'application_date': '2026-03-20T08:00:00.000',
        'weather_condition': _weatherJson(),
        'applicator_name': 'Ahmed',
        'equipment_used': 'Sprayer',
        'equipment_used_ar': 'رشاش',
        'photo_urls': ['url1'],
        'notes': 'Done',
        'notes_ar': 'تم',
        'created_by': 'u1',
        'created_by_name': 'User',
        'created_at': '2026-03-20T08:00:00.000',
        'updated_at': '2026-03-20T08:00:00.000',
      };
      final log = SprayApplicationLog.fromJson(json);
      expect(log.logId, 'l1');
      expect(log.area, 5.0);
      expect(log.photoUrls.length, 1);
      final result = log.toJson();
      expect(result['log_id'], 'l1');
      expect(result['area'], 5.0);
    });
    test('getFieldName locale', () {
      final json = {
        'log_id': 'l1',
        'tenant_id': 't1',
        'field_id': 'f1',
        'field_name': 'Field',
        'field_name_ar': 'حقل',
        'spray_type': 'insecticide',
        'product': _productJson(),
        'applied_rate': 2.0,
        'unit': 'L/ha',
        'area': 5.0,
        'total_quantity': 10.0,
        'application_date': '2026-03-20T08:00:00.000',
        'weather_condition': _weatherJson(),
        'created_by': 'u1',
        'created_at': '2026-03-20T08:00:00.000',
        'updated_at': '2026-03-20T08:00:00.000',
      };
      final log = SprayApplicationLog.fromJson(json);
      expect(log.getFieldName('ar'), 'حقل');
      expect(log.getFieldName('en'), 'Field');
    });
    test('getEquipment locale', () {
      final log = SprayApplicationLog(
        logId: 'l1',
        tenantId: 't1',
        fieldId: 'f1',
        fieldName: 'Field',
        sprayType: SprayType.insecticide,
        product: _makeProduct(),
        appliedRate: 2.0,
        unit: 'L/ha',
        area: 5.0,
        totalQuantity: 10.0,
        applicationDate: DateTime(2026, 3, 20),
        weatherCondition: _makeWeather(),
        equipmentUsed: 'Sprayer',
        equipmentUsedAr: 'رشاش',
        createdBy: 'u1',
        createdAt: DateTime(2026, 3, 20),
        updatedAt: DateTime(2026, 3, 20),
      );
      expect(log.getEquipment('ar'), 'رشاش');
      expect(log.getEquipment('en'), 'Sprayer');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════
  // Edge Cases / Bug Detection Tests
  // ═════════════════════════════════════════════════════════════════════════

  group('Edge Cases - Bug Detection', () {
    test('BUG: spraySuitabilityScore boundary - temp exactly 10', () {
      // temp=10 is >=10 but <15, so should deduct 20 (not 40)
      final w = _makeWeather(temperature: 10);
      expect(w.spraySuitabilityScore, 80);
    });

    test('BUG: spraySuitabilityScore boundary - temp exactly 30', () {
      // temp=30 is NOT >30, so should deduct 20 (in 25-30 range)
      final w = _makeWeather(temperature: 30);
      expect(w.spraySuitabilityScore, 80);
    });

    test('BUG: spraySuitabilityScore boundary - temp exactly 15', () {
      // temp=15 is NOT <15, so should NOT deduct anything
      final w = _makeWeather(temperature: 15);
      expect(w.spraySuitabilityScore, 100);
    });

    test('BUG: driftRiskScore zero wind zero risk', () {
      final w = _makeWeather(windSpeed: 0, humidity: 70, temperature: 20);
      expect(w.driftRiskScore, 0);
    });

    test('BUG: extreme values handled', () {
      final w = _makeWeather(temperature: -40, humidity: 0, windSpeed: 100, rainProbability: 100);
      expect(w.spraySuitabilityScore, 0);
      expect(w.driftRiskScore, lessThanOrEqualTo(100));
    });

    test('BUG: SprayWindow with same start and end time', () {
      final w = SprayWindow(
        windowId: 'sw1',
        startTime: DateTime(2026, 3, 20, 10, 0),
        endTime: DateTime(2026, 3, 20, 10, 0),
        status: SprayWindowStatus.optimal,
        weatherCondition: _makeWeather(),
        confidenceScore: 50,
      );
      expect(w.durationHours, 0);
    });

    test('SprayProduct with null Arabic fields falls back to English', () {
      final p = SprayProduct(
        productId: 'p1',
        name: 'TestProduct',
        type: SprayType.herbicide,
        manufacturer: 'Mfg',
        activeIngredient: 'AI',
        concentration: 25.0,
        unit: 'L/ha',
        recommendedRate: 2.0,
        minRate: 1.0,
        maxRate: 3.0,
        createdAt: DateTime(2026, 1, 1),
        updatedAt: DateTime(2026, 1, 1),
      );
      expect(p.getDisplayName('ar'), 'TestProduct'); // fallback
      expect(p.getManufacturer('ar'), 'Mfg'); // fallback
    });

    test('WeatherCondition.copyWith preserves all fields', () {
      final w = _makeWeather(
        temperature: 20,
        humidity: 60,
        windSpeed: 10,
        rainProbability: 10,
        windDirectionAr: 'شرق',
        conditionAr: 'غائم',
      );
      final w2 = w.copyWith(temperature: 25);
      expect(w2.humidity, 60);
      expect(w2.windSpeed, 10);
      expect(w2.rainProbability, 10);
      expect(w2.conditionAr, 'غائم');
    });
  });
}
