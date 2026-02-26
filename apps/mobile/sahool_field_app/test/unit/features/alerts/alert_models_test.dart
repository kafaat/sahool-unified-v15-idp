import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/alerts/data/alert_service_api.dart';

void main() {
  group('AlertModel', () {
    group('fromJson', () {
      test('should parse complete JSON correctly', () {
        // Arrange
        final json = {
          'id': 'alert-001',
          'field_id': 'field-001',
          'type': 'irrigation',
          'severity': 'critical',
          'title': 'رطوبة منخفضة',
          'message': 'رطوبة التربة أقل من 20%',
          'status': 'active',
          'recommendations': ['ري فوري', 'فحص المضخة'],
          'metadata': {'sensor_id': 'sensor-001', 'value': 18.5},
          'created_at': '2026-02-16T10:00:00Z',
          'acknowledged_at': '2026-02-16T10:30:00Z',
          'acknowledged_by': 'user-001',
        };

        // Act
        final model = AlertModel.fromJson(json);

        // Assert
        expect(model.id, 'alert-001');
        expect(model.fieldId, 'field-001');
        expect(model.type, 'irrigation');
        expect(model.severity, 'critical');
        expect(model.title, 'رطوبة منخفضة');
        expect(model.message, 'رطوبة التربة أقل من 20%');
        expect(model.status, 'active');
        expect(model.recommendations.length, 2);
        expect(model.metadata!['sensor_id'], 'sensor-001');
        expect(model.acknowledgedBy, 'user-001');
      });

      test('should handle missing optional fields with defaults', () {
        // Arrange
        final json = <String, dynamic>{};

        // Act
        final model = AlertModel.fromJson(json);

        // Assert
        expect(model.id, '');
        expect(model.fieldId, '');
        expect(model.type, 'system');
        expect(model.severity, 'info');
        expect(model.status, 'active');
        expect(model.recommendations, isEmpty);
        expect(model.metadata, isNull);
        expect(model.acknowledgedAt, isNull);
        expect(model.resolvedAt, isNull);
      });

      test('should parse items key as fallback for alerts', () {
        final json = {
          'items': [
            {
              'id': 'a1',
              'field_id': 'f1',
              'type': 'pest',
              'severity': 'warning',
              'title': 'آفة',
              'status': 'active',
              'created_at': '2026-01-01T00:00:00Z'
            },
          ],
          'total': 1,
        };

        final page = AlertsPageResponse.fromJson(json);
        expect(page.alerts.length, 1);
        expect(page.alerts[0].type, 'pest');
      });
    });

    group('status getters', () {
      test('isActive returns true for active status', () {
        final model = AlertModel.fromJson(
            {'status': 'active', 'created_at': '2026-01-01T00:00:00Z'});
        expect(model.isActive, isTrue);
        expect(model.isAcknowledged, isFalse);
        expect(model.isResolved, isFalse);
        expect(model.isDismissed, isFalse);
      });

      test('isAcknowledged returns true for acknowledged status', () {
        final model = AlertModel.fromJson(
            {'status': 'acknowledged', 'created_at': '2026-01-01T00:00:00Z'});
        expect(model.isActive, isFalse);
        expect(model.isAcknowledged, isTrue);
      });

      test('isResolved returns true for resolved status', () {
        final model = AlertModel.fromJson(
            {'status': 'resolved', 'created_at': '2026-01-01T00:00:00Z'});
        expect(model.isResolved, isTrue);
      });

      test('isDismissed returns true for dismissed status', () {
        final model = AlertModel.fromJson(
            {'status': 'dismissed', 'created_at': '2026-01-01T00:00:00Z'});
        expect(model.isDismissed, isTrue);
      });

      test('isCritical returns true for critical severity', () {
        final model = AlertModel.fromJson(
            {'severity': 'critical', 'created_at': '2026-01-01T00:00:00Z'});
        expect(model.isCritical, isTrue);
        expect(model.isWarning, isFalse);
      });

      test('isWarning returns true for warning severity', () {
        final model = AlertModel.fromJson(
            {'severity': 'warning', 'created_at': '2026-01-01T00:00:00Z'});
        expect(model.isWarning, isTrue);
        expect(model.isCritical, isFalse);
      });
    });
  });

  group('AlertsPageResponse', () {
    test('should parse page response with alerts key', () {
      final json = {
        'alerts': [
          {'id': 'a1', 'created_at': '2026-01-01T00:00:00Z'},
          {'id': 'a2', 'created_at': '2026-01-01T00:00:00Z'},
        ],
        'total': 50,
        'skip': 0,
        'limit': 20,
      };

      final page = AlertsPageResponse.fromJson(json);

      expect(page.alerts.length, 2);
      expect(page.total, 50);
      expect(page.skip, 0);
      expect(page.limit, 20);
    });

    test('should handle empty alerts list', () {
      final json = {
        'alerts': <dynamic>[],
        'total': 0,
      };

      final page = AlertsPageResponse.fromJson(json);

      expect(page.alerts, isEmpty);
      expect(page.total, 0);
    });
  });

  group('AlertStats', () {
    test('should parse statistics correctly', () {
      final json = {
        'total': 100,
        'active': 40,
        'acknowledged': 20,
        'resolved': 30,
        'dismissed': 10,
        'by_severity': {'critical': 10, 'warning': 50, 'info': 40},
        'by_type': {'irrigation': 30, 'weather': 25, 'pest': 20, 'ndvi': 25},
      };

      final stats = AlertStats.fromJson(json);

      expect(stats.total, 100);
      expect(stats.active, 40);
      expect(stats.acknowledged, 20);
      expect(stats.resolved, 30);
      expect(stats.dismissed, 10);
      expect(stats.bySeverity['critical'], 10);
      expect(stats.byType['irrigation'], 30);
    });

    test('should handle missing fields with defaults', () {
      final stats = AlertStats.fromJson(<String, dynamic>{});

      expect(stats.total, 0);
      expect(stats.active, 0);
      expect(stats.bySeverity, isEmpty);
      expect(stats.byType, isEmpty);
    });
  });

  group('AlertRule', () {
    test('should parse alert rule correctly', () {
      final json = {
        'id': 'rule-001',
        'field_id': 'field-001',
        'name': 'قاعدة رطوبة التربة',
        'condition': {'metric': 'soil_moisture', 'operator': '<', 'value': 30},
        'alert_config': {'severity': 'warning', 'type': 'irrigation'},
        'enabled': true,
        'cooldown_minutes': 120,
      };

      final rule = AlertRule.fromJson(json);

      expect(rule.id, 'rule-001');
      expect(rule.fieldId, 'field-001');
      expect(rule.name, 'قاعدة رطوبة التربة');
      expect(rule.condition['metric'], 'soil_moisture');
      expect(rule.alertConfig['severity'], 'warning');
      expect(rule.enabled, isTrue);
      expect(rule.cooldownMinutes, 120);
    });

    test('should handle missing fields with defaults', () {
      final rule = AlertRule.fromJson(<String, dynamic>{});

      expect(rule.id, '');
      expect(rule.enabled, isTrue);
      expect(rule.cooldownMinutes, 60);
      expect(rule.condition, isEmpty);
    });
  });
}
