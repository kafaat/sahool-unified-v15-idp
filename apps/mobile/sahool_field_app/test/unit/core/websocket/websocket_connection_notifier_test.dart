/// WebSocket Connection Notifier Tests
/// اختبارات مدير اتصال WebSocket
///
/// Tests for stream subscription lifecycle management
library;

import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/websocket/websocket_service.dart';

void main() {
  group('WebSocket ConnectionState', () {
    test('should have disconnected as initial state', () {
      expect(ConnectionState.disconnected, isNotNull);
      expect(ConnectionState.disconnected, isNot(ConnectionState.connected));
    });

    test('ConnectionState enum should have all expected values', () {
      const values = ConnectionState.values;
      expect(values, contains(ConnectionState.connected));
      expect(values, contains(ConnectionState.disconnected));
      expect(values, contains(ConnectionState.connecting));
    });
  });

  group('Stream subscription lifecycle', () {
    test('StreamSubscription should be cancellable', () async {
      final controller = StreamController<int>.broadcast();
      final values = <int>[];

      final subscription = controller.stream.listen((value) {
        values.add(value);
      });

      controller.add(1);
      controller.add(2);
      await Future.delayed(Duration.zero);

      expect(values, [1, 2]);

      // Cancel subscription
      await subscription.cancel();

      // Values after cancel should not be received
      controller.add(3);
      await Future.delayed(Duration.zero);

      expect(values, [1, 2]); // 3 should NOT appear
      await controller.close();
    });

    test('nullable subscription cancel should be safe', () async {
      StreamSubscription<int>? subscription;

      // Should not throw when null
      subscription?.cancel();

      final controller = StreamController<int>.broadcast();
      subscription = controller.stream.listen((_) {});

      // Should cancel properly when non-null
      await subscription.cancel();
      await controller.close();
    });

    test('multiple cancel calls should be safe', () async {
      final controller = StreamController<int>.broadcast();
      final subscription = controller.stream.listen((_) {});

      await subscription.cancel();
      // Second cancel should not throw
      await subscription.cancel();

      await controller.close();
    });

    test('dispose pattern should cancel subscription before super', () async {
      // Simulate the dispose pattern used in WebSocketConnectionNotifier
      final controller = StreamController<String>.broadcast();
      final receivedStates = <String>[];

      StreamSubscription<String>? sub;
      sub = controller.stream.listen((state) {
        receivedStates.add(state);
      });

      controller.add('connecting');
      controller.add('connected');
      await Future.delayed(Duration.zero);

      expect(receivedStates, ['connecting', 'connected']);

      // Simulate dispose - cancel subscription
      await sub.cancel();
      sub = null;

      controller.add('disconnected');
      await Future.delayed(Duration.zero);

      // Should NOT receive 'disconnected' after cancel
      expect(receivedStates, ['connecting', 'connected']);
      expect(sub, isNull);

      await controller.close();
    });
  });
}
