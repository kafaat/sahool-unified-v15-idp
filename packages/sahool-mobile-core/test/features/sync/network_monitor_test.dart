import 'dart:async';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import 'sync_mocks.dart';

/// Network Monitor Tests
/// اختبارات مراقب الشبكة
///
/// Tests for:
/// - Network status detection
/// - Online/offline transitions
/// - Stream-based status updates
/// - Multiple connectivity results handling

void main() {
  setUpAll(() {
    registerSyncFallbackValues();
  });

  group('MockNetworkStatus', () {
    late MockNetworkStatus networkStatus;

    setUp(() {
      networkStatus = MockNetworkStatus();
    });

    tearDown(() {
      networkStatus.dispose();
    });

    test('should default to online', () {
      expect(networkStatus.isOnline, isTrue);
    });

    test('should update online status', () {
      networkStatus.setOnline(false);
      expect(networkStatus.isOnline, isFalse);

      networkStatus.setOnline(true);
      expect(networkStatus.isOnline, isTrue);
    });

    test('should emit status changes via stream', () async {
      final statuses = <bool>[];
      final subscription = networkStatus.onlineStream.listen(statuses.add);

      networkStatus.setOnline(false);
      networkStatus.setOnline(true);
      networkStatus.setOnline(false);

      await Future<void>.delayed(const Duration(milliseconds: 10));

      expect(statuses, equals([false, true, false]));

      await subscription.cancel();
    });

    test('checkOnline should return current status', () async {
      networkStatus.setOnline(true);
      expect(await networkStatus.checkOnline(), isTrue);

      networkStatus.setOnline(false);
      expect(await networkStatus.checkOnline(), isFalse);
    });
  });

  group('MockConnectivity', () {
    late MockConnectivity mockConnectivity;

    setUp(() {
      mockConnectivity = MockConnectivity();
    });

    test('should mock checkConnectivity for WiFi', () async {
      when(() => mockConnectivity.checkConnectivity())
          .thenAnswer((_) async => [ConnectivityResult.wifi]);

      final result = await mockConnectivity.checkConnectivity();

      expect(result, contains(ConnectivityResult.wifi));
    });

    test('should mock checkConnectivity for mobile', () async {
      when(() => mockConnectivity.checkConnectivity())
          .thenAnswer((_) async => [ConnectivityResult.mobile]);

      final result = await mockConnectivity.checkConnectivity();

      expect(result, contains(ConnectivityResult.mobile));
    });

    test('should mock checkConnectivity for none', () async {
      when(() => mockConnectivity.checkConnectivity())
          .thenAnswer((_) async => [ConnectivityResult.none]);

      final result = await mockConnectivity.checkConnectivity();

      expect(result, contains(ConnectivityResult.none));
    });

    test('should mock checkConnectivity for multiple results', () async {
      when(() => mockConnectivity.checkConnectivity())
          .thenAnswer((_) async => [ConnectivityResult.wifi, ConnectivityResult.mobile]);

      final result = await mockConnectivity.checkConnectivity();

      expect(result.length, equals(2));
      expect(result, contains(ConnectivityResult.wifi));
      expect(result, contains(ConnectivityResult.mobile));
    });
  });

  group('Network Status Logic', () {
    test('should be online when WiFi connected', () {
      final results = [ConnectivityResult.wifi];
      final isOnline = results.isNotEmpty &&
          !results.every((r) => r == ConnectivityResult.none);

      expect(isOnline, isTrue);
    });

    test('should be online when mobile connected', () {
      final results = [ConnectivityResult.mobile];
      final isOnline = results.isNotEmpty &&
          !results.every((r) => r == ConnectivityResult.none);

      expect(isOnline, isTrue);
    });

    test('should be online when ethernet connected', () {
      final results = [ConnectivityResult.ethernet];
      final isOnline = results.isNotEmpty &&
          !results.every((r) => r == ConnectivityResult.none);

      expect(isOnline, isTrue);
    });

    test('should be offline when no connectivity', () {
      final results = [ConnectivityResult.none];
      final isOnline = results.isNotEmpty &&
          !results.every((r) => r == ConnectivityResult.none);

      expect(isOnline, isFalse);
    });

    test('should be offline when results list is empty', () {
      final results = <ConnectivityResult>[];
      final isOnline = results.isNotEmpty &&
          !results.every((r) => r == ConnectivityResult.none);

      expect(isOnline, isFalse);
    });

    test('should be online when multiple results include connectivity', () {
      final results = [ConnectivityResult.wifi, ConnectivityResult.mobile];
      final isOnline = results.isNotEmpty &&
          !results.every((r) => r == ConnectivityResult.none);

      expect(isOnline, isTrue);
    });

    test('should be online with vpn connection', () {
      final results = [ConnectivityResult.vpn];
      final isOnline = results.isNotEmpty &&
          !results.every((r) => r == ConnectivityResult.none);

      expect(isOnline, isTrue);
    });

    test('should be online with bluetooth connection', () {
      final results = [ConnectivityResult.bluetooth];
      final isOnline = results.isNotEmpty &&
          !results.every((r) => r == ConnectivityResult.none);

      expect(isOnline, isTrue);
    });
  });

  group('Online to Offline Transition', () {
    late MockNetworkStatus networkStatus;
    late StreamController<bool> transitionController;
    late List<bool> transitions;

    setUp(() {
      networkStatus = MockNetworkStatus();
      transitionController = StreamController<bool>.broadcast();
      transitions = [];
    });

    tearDown(() {
      networkStatus.dispose();
      transitionController.close();
    });

    test('should detect transition from online to offline', () async {
      final subscription = networkStatus.onlineStream.listen(transitions.add);

      // Start online (default)
      expect(networkStatus.isOnline, isTrue);

      // Go offline
      networkStatus.setOnline(false);
      await Future<void>.delayed(const Duration(milliseconds: 10));

      expect(networkStatus.isOnline, isFalse);
      expect(transitions, contains(false));

      await subscription.cancel();
    });

    test('should trigger sync-related actions on offline transition', () async {
      bool syncPaused = false;
      bool queueEnabled = false;

      networkStatus.onlineStream.listen((isOnline) {
        if (!isOnline) {
          syncPaused = true;
          queueEnabled = true;
        }
      });

      networkStatus.setOnline(false);
      await Future<void>.delayed(const Duration(milliseconds: 10));

      expect(syncPaused, isTrue);
      expect(queueEnabled, isTrue);
    });

    test('should handle rapid online/offline transitions', () async {
      final subscription = networkStatus.onlineStream.listen(transitions.add);

      // Rapid transitions
      networkStatus.setOnline(false);
      networkStatus.setOnline(true);
      networkStatus.setOnline(false);
      networkStatus.setOnline(true);

      await Future<void>.delayed(const Duration(milliseconds: 50));

      expect(transitions.length, equals(4));
      expect(transitions.last, isTrue);

      await subscription.cancel();
    });
  });

  group('Offline to Online Sync', () {
    late MockNetworkStatus networkStatus;
    late MockSyncDatabase mockDb;

    setUp(() {
      networkStatus = MockNetworkStatus();
      mockDb = MockSyncDatabase();
    });

    tearDown(() {
      networkStatus.dispose();
      mockDb.reset();
    });

    test('should trigger sync when coming back online', () async {
      bool syncTriggered = false;

      networkStatus.onlineStream.listen((isOnline) {
        if (isOnline) {
          syncTriggered = true;
        }
      });

      // Start offline
      networkStatus.setOnline(false);
      await Future<void>.delayed(const Duration(milliseconds: 10));

      // Queue some items while offline
      await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{}',
      );

      final pendingBefore = await mockDb.getPendingOutbox();
      expect(pendingBefore.length, equals(1));

      // Come back online
      networkStatus.setOnline(true);
      await Future<void>.delayed(const Duration(milliseconds: 10));

      expect(syncTriggered, isTrue);
    });

    test('should process pending queue when coming back online', () async {
      // Start offline
      networkStatus.setOnline(false);

      // Queue items while offline
      final id1 = await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{}',
      );
      final id2 = await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'task',
        entityId: 'task_001',
        apiEndpoint: '/api/v1/tasks',
        method: 'POST',
        payload: '{}',
      );

      // Verify items are queued
      var pending = await mockDb.getPendingOutbox();
      expect(pending.length, equals(2));

      // Simulate sync when coming back online
      networkStatus.setOnline(true);

      // Process sync (mark items as done)
      await mockDb.markOutboxDone(id1);
      await mockDb.markOutboxDone(id2);

      // Verify queue is processed
      pending = await mockDb.getPendingOutbox();
      expect(pending.length, equals(0));
    });

    test('should handle partial sync failure on reconnection', () async {
      // Queue items
      final id1 = await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{}',
      );
      await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'task',
        entityId: 'task_001',
        apiEndpoint: '/api/v1/tasks',
        method: 'POST',
        payload: '{}',
      );

      // Simulate partial sync - first succeeds, second fails
      await mockDb.markOutboxDone(id1);
      // Second item stays pending (simulates failure)

      // Verify partial state
      final pending = await mockDb.getPendingOutbox();
      expect(pending.length, equals(1));
      expect(pending.first.entityType, equals('task'));
    });
  });

  group('Network Quality Simulation', () {
    test('should handle slow network scenario', () async {
      // Simulate slow network with delayed response
      final completer = Completer<bool>();

      // Simulate 2 second network check
      Future.delayed(const Duration(seconds: 2), () {
        if (!completer.isCompleted) {
          completer.complete(true);
        }
      });

      // With timeout
      final result = await completer.future.timeout(
        const Duration(seconds: 5),
        onTimeout: () => false,
      );

      expect(result, isTrue);
    });

    test('should handle network timeout', () async {
      final completer = Completer<bool>();

      // Never complete - simulate complete timeout

      final result = await completer.future.timeout(
        const Duration(milliseconds: 100),
        onTimeout: () => false,
      );

      expect(result, isFalse);
    });

    test('should handle intermittent connectivity', () async {
      final networkStatus = MockNetworkStatus();
      final connectivityEvents = <bool>[];

      networkStatus.onlineStream.listen(connectivityEvents.add);

      // Simulate intermittent connectivity
      networkStatus.setOnline(true);
      await Future<void>.delayed(const Duration(milliseconds: 10));

      networkStatus.setOnline(false);
      await Future<void>.delayed(const Duration(milliseconds: 50));

      networkStatus.setOnline(true);
      await Future<void>.delayed(const Duration(milliseconds: 10));

      networkStatus.setOnline(false);
      await Future<void>.delayed(const Duration(milliseconds: 50));

      networkStatus.setOnline(true);
      await Future<void>.delayed(const Duration(milliseconds: 10));

      expect(connectivityEvents.length, equals(5));
      expect(connectivityEvents.last, isTrue);

      networkStatus.dispose();
    });
  });

  group('ConnectivityResult Handling', () {
    test('should correctly identify all connectivity types', () {
      expect(ConnectivityResult.wifi.name, equals('wifi'));
      expect(ConnectivityResult.mobile.name, equals('mobile'));
      expect(ConnectivityResult.ethernet.name, equals('ethernet'));
      expect(ConnectivityResult.vpn.name, equals('vpn'));
      expect(ConnectivityResult.bluetooth.name, equals('bluetooth'));
      expect(ConnectivityResult.other.name, equals('other'));
      expect(ConnectivityResult.none.name, equals('none'));
    });

    test('should handle mixed connectivity results', () {
      // WiFi + VPN
      var results = [ConnectivityResult.wifi, ConnectivityResult.vpn];
      var isOnline = results.isNotEmpty &&
          !results.every((r) => r == ConnectivityResult.none);
      expect(isOnline, isTrue);

      // Mobile + Bluetooth (tethering scenario)
      results = [ConnectivityResult.mobile, ConnectivityResult.bluetooth];
      isOnline = results.isNotEmpty &&
          !results.every((r) => r == ConnectivityResult.none);
      expect(isOnline, isTrue);
    });
  });

  group('Edge Cases', () {
    test('should handle dispose during stream emission', () async {
      final networkStatus = MockNetworkStatus();
      var receivedEvents = 0;

      final subscription = networkStatus.onlineStream.listen((_) {
        receivedEvents++;
      });

      networkStatus.setOnline(false);
      await Future<void>.delayed(const Duration(milliseconds: 5));

      // Dispose while potentially emitting
      networkStatus.dispose();
      await subscription.cancel();

      // Should have received at least the initial event
      expect(receivedEvents, greaterThanOrEqualTo(1));
    });

    test('should handle multiple subscriptions', () async {
      final networkStatus = MockNetworkStatus();
      final events1 = <bool>[];
      final events2 = <bool>[];

      final sub1 = networkStatus.onlineStream.listen(events1.add);
      final sub2 = networkStatus.onlineStream.listen(events2.add);

      networkStatus.setOnline(false);
      networkStatus.setOnline(true);

      await Future<void>.delayed(const Duration(milliseconds: 10));

      // Both subscriptions should receive same events
      expect(events1.length, equals(2));
      expect(events2.length, equals(2));
      expect(events1, equals(events2));

      await sub1.cancel();
      await sub2.cancel();
      networkStatus.dispose();
    });

    test('should handle subscription after events', () async {
      final networkStatus = MockNetworkStatus();

      // Emit events before subscription
      networkStatus.setOnline(false);
      networkStatus.setOnline(true);

      // Subscribe after events
      final events = <bool>[];
      final subscription = networkStatus.onlineStream.listen(events.add);

      // Emit new event
      networkStatus.setOnline(false);
      await Future<void>.delayed(const Duration(milliseconds: 10));

      // Should only receive events after subscription
      expect(events.length, equals(1));
      expect(events.first, isFalse);

      await subscription.cancel();
      networkStatus.dispose();
    });
  });
}
