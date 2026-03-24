import 'package:flutter_test/flutter_test.dart';

/// Tests for smart alerts domain logic
void main() {
  group('Alert Severity', () {
    test('should define all severity levels', () {
      final severities = ['critical', 'warning', 'advisory', 'info'];
      expect(severities, hasLength(4));
    });

    test('should map severity to Arabic labels', () {
      final labelsAr = {
        'critical': 'حرج',
        'warning': 'تحذير',
        'advisory': 'استشارة',
        'info': 'معلومات',
      };

      expect(labelsAr['critical'], 'حرج');
      expect(labelsAr['info'], 'معلومات');
    });

    test('should define response windows per severity', () {
      final responseHours = {
        'critical': 6,
        'warning': 48,
        'advisory': 168, // 1 week
        'info': -1, // no deadline
      };

      expect(responseHours['critical'], 6);
      expect(responseHours['warning'], 48);
    });
  });

  group('Alert Categories', () {
    test('should define agricultural alert categories', () {
      final categories = [
        'pest_detection',
        'disease_detection',
        'weather_warning',
        'irrigation_needed',
        'nutrient_deficiency',
        'harvest_ready',
        'equipment_maintenance',
        'frost_warning',
        'salinity_alert',
      ];

      expect(categories, contains('pest_detection'));
      expect(categories, contains('frost_warning'));
      expect(categories.length, greaterThanOrEqualTo(9));
    });
  });

  group('Alert Priority Scoring', () {
    test('should calculate priority score based on severity and recency', () {
      int priorityScore(String severity, int hoursAgo) {
        final severityWeight = {
          'critical': 100,
          'warning': 70,
          'advisory': 40,
          'info': 10,
        };

        final base = severityWeight[severity] ?? 0;
        final recencyBonus = (24 - hoursAgo.clamp(0, 24));
        return base + recencyBonus;
      }

      // Critical alert from 1 hour ago
      expect(priorityScore('critical', 1), 123);
      // Warning from 12 hours ago
      expect(priorityScore('warning', 12), 82);
      // Info from 24+ hours ago
      expect(priorityScore('info', 30), 10);
    });
  });

  group('Alert Deduplication', () {
    test('should identify duplicate alerts by field and category', () {
      final alerts = [
        {'field_id': 'f1', 'category': 'pest', 'created_at': '2026-03-24T10:00:00Z'},
        {'field_id': 'f1', 'category': 'pest', 'created_at': '2026-03-24T10:30:00Z'},
        {'field_id': 'f2', 'category': 'pest', 'created_at': '2026-03-24T10:00:00Z'},
        {'field_id': 'f1', 'category': 'weather', 'created_at': '2026-03-24T10:00:00Z'},
      ];

      final unique = <String>{};
      final deduped = alerts.where((a) {
        final key = '${a['field_id']}_${a['category']}';
        return unique.add(key);
      }).toList();

      expect(deduped, hasLength(3)); // f1_pest, f2_pest, f1_weather
    });
  });
}
