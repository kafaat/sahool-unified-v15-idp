import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/websocket/websocket_service.dart';

void main() {
  // ===========================================================================
  // ConnectionState Enum Tests
  // ===========================================================================

  group('ConnectionState enum', () {
    test('has exactly 5 values', () {
      expect(ConnectionState.values.length, 5);
    });

    test('contains disconnected', () {
      expect(ConnectionState.values, contains(ConnectionState.disconnected));
    });

    test('contains connecting', () {
      expect(ConnectionState.values, contains(ConnectionState.connecting));
    });

    test('contains connected', () {
      expect(ConnectionState.values, contains(ConnectionState.connected));
    });

    test('contains reconnecting', () {
      expect(ConnectionState.values, contains(ConnectionState.reconnecting));
    });

    test('contains error', () {
      expect(ConnectionState.values, contains(ConnectionState.error));
    });

    test('disconnected has index 0', () {
      expect(ConnectionState.disconnected.index, 0);
    });

    test('connecting has index 1', () {
      expect(ConnectionState.connecting.index, 1);
    });

    test('connected has index 2', () {
      expect(ConnectionState.connected.index, 2);
    });

    test('reconnecting has index 3', () {
      expect(ConnectionState.reconnecting.index, 3);
    });

    test('error has index 4', () {
      expect(ConnectionState.error.index, 4);
    });

    test('all values have distinct indices', () {
      final indices = ConnectionState.values.map((v) => v.index).toSet();
      expect(indices.length, ConnectionState.values.length);
    });

    test('values have correct string names', () {
      expect(ConnectionState.disconnected.name, 'disconnected');
      expect(ConnectionState.connecting.name, 'connecting');
      expect(ConnectionState.connected.name, 'connected');
      expect(ConnectionState.reconnecting.name, 'reconnecting');
      expect(ConnectionState.error.name, 'error');
    });
  });

  // ===========================================================================
  // WebSocketEvent Tests
  // ===========================================================================

  group('WebSocketEvent constructor', () {
    test('sets type correctly', () {
      final event = WebSocketEvent(type: 'notification');
      expect(event.type, 'notification');
    });

    test('eventType defaults to null', () {
      final event = WebSocketEvent(type: 'test');
      expect(event.eventType, isNull);
    });

    test('priority defaults to null', () {
      final event = WebSocketEvent(type: 'test');
      expect(event.priority, isNull);
    });

    test('message defaults to null', () {
      final event = WebSocketEvent(type: 'test');
      expect(event.message, isNull);
    });

    test('messageAr defaults to null', () {
      final event = WebSocketEvent(type: 'test');
      expect(event.messageAr, isNull);
    });

    test('data defaults to null', () {
      final event = WebSocketEvent(type: 'test');
      expect(event.data, isNull);
    });

    test('subject defaults to null', () {
      final event = WebSocketEvent(type: 'test');
      expect(event.subject, isNull);
    });

    test('timestamp defaults to approximately now when not provided', () {
      final before = DateTime.now();
      final event = WebSocketEvent(type: 'test');
      final after = DateTime.now();
      expect(event.timestamp.isAfter(before.subtract(const Duration(seconds: 1))), isTrue);
      expect(event.timestamp.isBefore(after.add(const Duration(seconds: 1))), isTrue);
    });

    test('timestamp is set when provided', () {
      final ts = DateTime(2026, 3, 23, 12, 0, 0);
      final event = WebSocketEvent(type: 'test', timestamp: ts);
      expect(event.timestamp, ts);
    });

    test('all fields can be set via constructor', () {
      final data = {'field_id': 'F001', 'ndvi': 0.72};
      final ts = DateTime(2026, 1, 15, 10, 30);
      final event = WebSocketEvent(
        type: 'event',
        eventType: 'field.updated',
        priority: 'high',
        message: 'Field updated',
        messageAr: 'تم تحديث الحقل',
        data: data,
        subject: 'sahool.field.updated',
        timestamp: ts,
      );
      expect(event.type, 'event');
      expect(event.eventType, 'field.updated');
      expect(event.priority, 'high');
      expect(event.message, 'Field updated');
      expect(event.messageAr, 'تم تحديث الحقل');
      expect(event.data, data);
      expect(event.subject, 'sahool.field.updated');
      expect(event.timestamp, ts);
    });
  });

  group('WebSocketEvent.fromJson', () {
    test('parses type from JSON', () {
      final event = WebSocketEvent.fromJson({'type': 'notification'});
      expect(event.type, 'notification');
    });

    test('parses eventType from JSON', () {
      final event = WebSocketEvent.fromJson({
        'type': 'event',
        'event_type': 'field.updated',
      });
      expect(event.eventType, 'field.updated');
    });

    test('parses priority from JSON', () {
      final event = WebSocketEvent.fromJson({
        'type': 'event',
        'priority': 'critical',
      });
      expect(event.priority, 'critical');
    });

    test('parses message from JSON', () {
      final event = WebSocketEvent.fromJson({
        'type': 'event',
        'message': 'New alert',
      });
      expect(event.message, 'New alert');
    });

    test('parses messageAr from JSON', () {
      final event = WebSocketEvent.fromJson({
        'type': 'event',
        'message_ar': 'تنبيه جديد',
      });
      expect(event.messageAr, 'تنبيه جديد');
    });

    test('parses data map from JSON', () {
      final event = WebSocketEvent.fromJson({
        'type': 'event',
        'data': {'field_id': 'F001', 'status': 'healthy'},
      });
      expect(event.data, isNotNull);
      expect(event.data!['field_id'], 'F001');
      expect(event.data!['status'], 'healthy');
    });

    test('parses subject from JSON', () {
      final event = WebSocketEvent.fromJson({
        'type': 'event',
        'subject': 'sahool.field.created',
      });
      expect(event.subject, 'sahool.field.created');
    });

    test('parses timestamp from ISO 8601 string', () {
      final event = WebSocketEvent.fromJson({
        'type': 'event',
        'timestamp': '2026-03-23T10:30:00.000',
      });
      expect(event.timestamp, DateTime(2026, 3, 23, 10, 30));
    });

    test('timestamp defaults to now when not in JSON', () {
      final before = DateTime.now();
      final event = WebSocketEvent.fromJson({'type': 'event'});
      final after = DateTime.now();
      expect(
        event.timestamp.millisecondsSinceEpoch,
        greaterThanOrEqualTo(before.millisecondsSinceEpoch - 1000),
      );
      expect(
        event.timestamp.millisecondsSinceEpoch,
        lessThanOrEqualTo(after.millisecondsSinceEpoch + 1000),
      );
    });

    test('handles null optional fields gracefully', () {
      final event = WebSocketEvent.fromJson({
        'type': 'ping',
        'event_type': null,
        'priority': null,
        'message': null,
        'message_ar': null,
        'data': null,
        'subject': null,
        'timestamp': null,
      });
      expect(event.type, 'ping');
      expect(event.eventType, isNull);
      expect(event.priority, isNull);
      expect(event.message, isNull);
      expect(event.messageAr, isNull);
      expect(event.data, isNull);
      expect(event.subject, isNull);
    });

    test('parses complete field.updated event', () {
      final json = {
        'type': 'event',
        'event_type': 'field.updated',
        'priority': 'medium',
        'message': 'Field NDVI updated',
        'message_ar': 'تم تحديث NDVI للحقل',
        'data': {
          'field_id': 'FIELD-003',
          'ndvi': 0.72,
          'previous_ndvi': 0.68,
        },
        'subject': 'sahool.field.updated',
        'timestamp': '2026-01-15T14:30:00.000Z',
      };
      final event = WebSocketEvent.fromJson(json);
      expect(event.type, 'event');
      expect(event.eventType, 'field.updated');
      expect(event.priority, 'medium');
      expect(event.message, 'Field NDVI updated');
      expect(event.messageAr, 'تم تحديث NDVI للحقل');
      expect(event.data!['field_id'], 'FIELD-003');
      expect(event.data!['ndvi'], 0.72);
      expect(event.subject, 'sahool.field.updated');
    });

    test('parses weather.alert event', () {
      final json = {
        'type': 'alert',
        'event_type': 'weather.alert',
        'priority': 'high',
        'message': 'Frost warning',
        'message_ar': 'تحذير من الصقيع',
        'data': {'temperature': -2.0, 'region': 'central'},
        'subject': 'sahool.weather.alert',
      };
      final event = WebSocketEvent.fromJson(json);
      expect(event.eventType, 'weather.alert');
      expect(event.priority, 'high');
      expect(event.data!['temperature'], -2.0);
    });

    test('parses crop.pest.detected event', () {
      final json = {
        'type': 'event',
        'event_type': 'crop.pest.detected',
        'priority': 'critical',
        'message': 'Red Palm Weevil detected',
        'message_ar': 'تم اكتشاف سوسة النخيل الحمراء',
        'data': {
          'pest_id': 'rpw',
          'confidence': 0.95,
          'field_id': 'FIELD-004',
        },
        'subject': 'sahool.vision.pest_detected',
      };
      final event = WebSocketEvent.fromJson(json);
      expect(event.eventType, 'crop.pest.detected');
      expect(event.priority, 'critical');
      expect(event.data!['confidence'], 0.95);
    });

    test('parses task.overdue event', () {
      final json = {
        'type': 'event',
        'event_type': 'task.overdue',
        'priority': 'high',
        'message': 'Irrigation task is overdue',
        'message_ar': 'مهمة الري متأخرة',
        'data': {'task_id': 'T-100', 'task_type': 'irrigation'},
      };
      final event = WebSocketEvent.fromJson(json);
      expect(event.eventType, 'task.overdue');
      expect(event.data!['task_type'], 'irrigation');
    });

    test('parses iot.alert event', () {
      final json = {
        'type': 'event',
        'event_type': 'iot.alert',
        'priority': 'high',
        'message': 'Soil moisture critically low',
        'message_ar': 'رطوبة التربة منخفضة بشكل حرج',
        'data': {'sensor_id': 'SM-001', 'moisture': 12.5},
      };
      final event = WebSocketEvent.fromJson(json);
      expect(event.eventType, 'iot.alert');
      expect(event.data!['moisture'], 12.5);
    });

    test('parses ndvi.updated event', () {
      final json = {
        'type': 'event',
        'event_type': 'ndvi.updated',
        'data': {'field_id': 'FIELD-001', 'ndvi': 0.65},
        'subject': 'sahool.field.ndvi.updated',
      };
      final event = WebSocketEvent.fromJson(json);
      expect(event.eventType, 'ndvi.updated');
      expect(event.data!['ndvi'], 0.65);
    });

    test('parses empty data map', () {
      final event = WebSocketEvent.fromJson({
        'type': 'event',
        'data': <String, dynamic>{},
      });
      expect(event.data, isNotNull);
      expect(event.data, isEmpty);
    });

    test('parses nested data map', () {
      final json = {
        'type': 'event',
        'data': {
          'field': {
            'id': 'F001',
            'coordinates': [46.7, 24.7],
          },
        },
      };
      final event = WebSocketEvent.fromJson(json);
      expect(event.data!['field'], isA<Map>());
      expect((event.data!['field'] as Map)['id'], 'F001');
    });

    test('handles UTC timestamp with Z suffix', () {
      final event = WebSocketEvent.fromJson({
        'type': 'event',
        'timestamp': '2026-03-23T10:30:00.000Z',
      });
      expect(event.timestamp.isUtc, isTrue);
      expect(event.timestamp.hour, 10);
      expect(event.timestamp.minute, 30);
    });

    test('handles timestamp with timezone offset', () {
      final event = WebSocketEvent.fromJson({
        'type': 'event',
        'timestamp': '2026-03-23T13:30:00.000+03:00',
      });
      expect(event.timestamp, isNotNull);
    });

    test('parses inventory.low_stock event', () {
      final json = {
        'type': 'event',
        'event_type': 'inventory.low_stock',
        'priority': 'high',
        'message': 'Urea 46% stock is low',
        'message_ar': 'مخزون اليوريا 46% منخفض',
        'data': {'product': 'Urea 46%', 'remaining_kg': 50},
      };
      final event = WebSocketEvent.fromJson(json);
      expect(event.eventType, 'inventory.low_stock');
      expect(event.data!['remaining_kg'], 50);
    });

    test('parses spray.window.optimal event', () {
      final json = {
        'type': 'event',
        'event_type': 'spray.window.optimal',
        'priority': 'high',
        'message': 'Optimal spray window open',
        'data': {
          'window_start': '2026-03-24T06:00:00Z',
          'window_end': '2026-03-24T09:00:00Z',
          'wind_speed_kmh': 8,
        },
      };
      final event = WebSocketEvent.fromJson(json);
      expect(event.eventType, 'spray.window.optimal');
      expect(event.data!['wind_speed_kmh'], 8);
    });

    test('parses satellite.ready event', () {
      final json = {
        'type': 'event',
        'event_type': 'satellite.ready',
        'message': 'New satellite imagery available',
        'message_ar': 'صور جديدة من الأقمار الصناعية متاحة',
        'data': {'capture_date': '2026-03-22', 'cloud_cover': 5},
      };
      final event = WebSocketEvent.fromJson(json);
      expect(event.eventType, 'satellite.ready');
      expect(event.data!['cloud_cover'], 5);
    });

    test('parses chat.message event', () {
      final json = {
        'type': 'event',
        'event_type': 'chat.message',
        'data': {
          'room_id': 'room-42',
          'sender_id': 'user-7',
          'text': 'Hello',
        },
      };
      final event = WebSocketEvent.fromJson(json);
      expect(event.eventType, 'chat.message');
      expect(event.data!['room_id'], 'room-42');
    });
  });
}
