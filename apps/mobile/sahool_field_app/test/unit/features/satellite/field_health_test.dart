import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/satellite/data/models/field_health.dart';

void main() {
  group('HealthStatus', () {
    test('has 5 statuses', () {
      expect(HealthStatus.values, hasLength(5));
    });

    test('fromString parses valid values', () {
      expect(HealthStatus.fromString('excellent'), HealthStatus.excellent);
      expect(HealthStatus.fromString('good'), HealthStatus.good);
      expect(HealthStatus.fromString('warning'), HealthStatus.warning);
      expect(HealthStatus.fromString('critical'), HealthStatus.critical);
    });

    test('fromString is case insensitive', () {
      expect(HealthStatus.fromString('EXCELLENT'), HealthStatus.excellent);
      expect(HealthStatus.fromString('Good'), HealthStatus.good);
    });

    test('fromString returns unknown for invalid', () {
      expect(HealthStatus.fromString('invalid'), HealthStatus.unknown);
    });

    test('fromScore classifies correctly', () {
      expect(HealthStatus.fromScore(85), HealthStatus.excellent);
      expect(HealthStatus.fromScore(70), HealthStatus.good);
      expect(HealthStatus.fromScore(50), HealthStatus.warning);
      expect(HealthStatus.fromScore(30), HealthStatus.critical);
    });

    test('has Arabic labels', () {
      expect(HealthStatus.excellent.arabicLabel, 'ممتاز');
      expect(HealthStatus.good.arabicLabel, 'جيد');
      expect(HealthStatus.warning.arabicLabel, 'تحذير');
      expect(HealthStatus.critical.arabicLabel, 'حرج');
    });

    test('getLabel returns correct language', () {
      expect(HealthStatus.good.getLabel(true), 'جيد');
      expect(HealthStatus.good.getLabel(false), 'good');
    });

    test('has color hex codes', () {
      expect(HealthStatus.excellent.colorHex, '#4CAF50');
      expect(HealthStatus.critical.colorHex, '#F44336');
    });
  });

  group('AlertType', () {
    test('has 6 types', () {
      expect(AlertType.values, hasLength(6));
    });

    test('fromString parses valid values', () {
      expect(AlertType.fromString('water_stress'), AlertType.waterStress);
      expect(AlertType.fromString('disease_risk'), AlertType.diseaseRisk);
      expect(AlertType.fromString('pest_risk'), AlertType.pestRisk);
    });

    test('fromString returns other for unknown', () {
      expect(AlertType.fromString('unknown'), AlertType.other);
    });

    test('has Arabic labels', () {
      expect(AlertType.waterStress.arabicLabel, 'إجهاد مائي');
      expect(AlertType.nutrientDeficiency.arabicLabel, 'نقص المغذيات');
    });
  });

  group('AlertSeverity', () {
    test('has 3 levels', () {
      expect(AlertSeverity.values, hasLength(3));
    });

    test('fromString parses valid values', () {
      expect(AlertSeverity.fromString('info'), AlertSeverity.info);
      expect(AlertSeverity.fromString('warning'), AlertSeverity.warning);
      expect(AlertSeverity.fromString('critical'), AlertSeverity.critical);
    });

    test('fromString returns info for unknown', () {
      expect(AlertSeverity.fromString('unknown'), AlertSeverity.info);
    });
  });

  group('RecommendationType', () {
    test('has 6 types', () {
      expect(RecommendationType.values, hasLength(6));
    });

    test('fromString parses valid values', () {
      expect(RecommendationType.fromString('irrigation'), RecommendationType.irrigation);
      expect(RecommendationType.fromString('fertilization'), RecommendationType.fertilization);
      expect(RecommendationType.fromString('pest_control'), RecommendationType.pestControl);
    });

    test('fromString returns general for unknown', () {
      expect(RecommendationType.fromString('unknown'), RecommendationType.general);
    });
  });

  group('RecommendationPriority', () {
    test('has 3 levels', () {
      expect(RecommendationPriority.values, hasLength(3));
    });

    test('fromString returns medium for unknown', () {
      expect(RecommendationPriority.fromString('unknown'), RecommendationPriority.medium);
    });
  });

  group('HealthAlert', () {
    test('fromJson and toJson round-trip', () {
      final json = {
        'id': 'alert-1',
        'type': 'water_stress',
        'severity': 'warning',
        'message': 'Low soil moisture detected',
        'message_ar': 'تم اكتشاف رطوبة منخفضة',
        'detected_at': '2026-01-15T10:00:00.000',
        'affected_zone': 'zone-A',
      };

      final alert = HealthAlert.fromJson(json);
      expect(alert.id, 'alert-1');
      expect(alert.type, AlertType.waterStress);
      expect(alert.severity, AlertSeverity.warning);
      expect(alert.message, 'Low soil moisture detected');
      expect(alert.messageAr, 'تم اكتشاف رطوبة منخفضة');
      expect(alert.affectedZone, 'zone-A');

      final exported = alert.toJson();
      expect(exported['id'], 'alert-1');
      expect(exported['type'], 'water_stress');
      expect(exported['severity'], 'warning');
    });
  });

  group('Recommendation', () {
    test('fromJson and toJson round-trip', () {
      final json = {
        'id': 'rec-1',
        'type': 'irrigation',
        'title': 'Increase irrigation',
        'title_ar': 'زيادة الري',
        'description': 'Apply 25mm of water',
        'description_ar': 'تطبيق 25 ملم من الماء',
        'priority': 'high',
        'due_date': '2026-01-20T00:00:00.000',
      };

      final rec = Recommendation.fromJson(json);
      expect(rec.id, 'rec-1');
      expect(rec.type, RecommendationType.irrigation);
      expect(rec.title, 'Increase irrigation');
      expect(rec.titleAr, 'زيادة الري');
      expect(rec.priority, RecommendationPriority.high);
      expect(rec.dueDate, isNotNull);

      final exported = rec.toJson();
      expect(exported['type'], 'irrigation');
      expect(exported['priority'], 'high');
    });
  });

  group('FieldHealth', () {
    test('fromJson parses complete health assessment', () {
      final json = {
        'field_id': 'field-001',
        'health_score': 85.0,
        'status': 'excellent',
        'ndvi': 0.78,
        'ndwi': 0.35,
        'evi': 0.55,
        'soil_moisture': 42.0,
        'alerts': [
          {'id': 'a1', 'type': 'water_stress', 'severity': 'info', 'message': 'Low', 'message_ar': 'منخفض', 'detected_at': '2026-01-01T00:00:00.000'},
        ],
        'recommendations': [
          {'id': 'r1', 'type': 'monitoring', 'title': 'Monitor', 'title_ar': 'مراقبة', 'description': 'Check weekly', 'description_ar': 'فحص أسبوعي', 'priority': 'low'},
        ],
        'assessed_at': '2026-03-01T00:00:00.000',
        'zone_scores': {'north': 90.0, 'south': 80.0},
      };

      final health = FieldHealth.fromJson(json);
      expect(health.fieldId, 'field-001');
      expect(health.healthScore, 85.0);
      expect(health.status, HealthStatus.excellent);
      expect(health.ndvi, 0.78);
      expect(health.ndwi, 0.35);
      expect(health.evi, 0.55);
      expect(health.soilMoisture, 42.0);
      expect(health.alerts, hasLength(1));
      expect(health.recommendations, hasLength(1));
      expect(health.zoneScores!['north'], 90.0);
    });

    test('toJson produces correct output', () {
      final health = FieldHealth(
        fieldId: 'f1',
        healthScore: 75.0,
        status: HealthStatus.good,
        ndvi: 0.7,
        ndwi: 0.3,
        evi: 0.5,
        assessedAt: DateTime(2026, 3, 1),
      );

      final json = health.toJson();
      expect(json['field_id'], 'f1');
      expect(json['health_score'], 75.0);
      expect(json['status'], 'good');
      expect(json['ndvi'], 0.7);
    });

    test('fromJson handles camelCase keys', () {
      final json = {
        'fieldId': 'f2',
        'healthScore': 60.0,
        'status': 'warning',
        'ndvi': 0.45,
        'ndwi': 0.2,
        'evi': 0.3,
        'assessedAt': '2026-01-01T00:00:00.000',
      };

      final health = FieldHealth.fromJson(json);
      expect(health.fieldId, 'f2');
      expect(health.healthScore, 60.0);
    });

    test('equality works with Equatable', () {
      final a = FieldHealth(fieldId: 'f1', healthScore: 80, status: HealthStatus.excellent, ndvi: 0.8, ndwi: 0.3, evi: 0.5, assessedAt: DateTime(2026, 1, 1));
      final b = FieldHealth(fieldId: 'f1', healthScore: 80, status: HealthStatus.excellent, ndvi: 0.8, ndwi: 0.3, evi: 0.5, assessedAt: DateTime(2026, 1, 1));
      expect(a, equals(b));
    });
  });
}
