import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/api/kong_gateway_client.dart';
import 'package:sahool_field_app/features/alerts/data/alert_service_api.dart';
import 'package:sahool_field_app/features/smart_alerts/presentation/providers/smart_alerts_provider.dart';

import '../../../mocks/mock_kong_gateway.dart';

/// Mock AlertServiceApi for provider testing
class MockAlertServiceApi extends Mock implements AlertServiceApi {}

void main() {
  late MockAlertServiceApi mockApi;

  setUpAll(() {
    registerFallbackValue(FakeKongService());
  });

  setUp(() {
    mockApi = MockAlertServiceApi();
  });

  group('smartAlertsProvider', () {
    test('should return alerts when API succeeds', () async {
      // Arrange
      when(() => mockApi.getFieldAlerts(
            fieldId: any(named: 'fieldId'),
            status: any(named: 'status'),
            limit: any(named: 'limit'),
          )).thenAnswer((_) async => ApiResponse.success(
            AlertsPageResponse.fromJson({
              'alerts': [
                sampleAlertJson(
                    id: 'a1', type: 'irrigation', severity: 'warning'),
                sampleAlertJson(
                    id: 'a2', type: 'weather', severity: 'critical'),
              ],
              'total': 2,
            }),
          ));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      // Act
      final future = container.read(smartAlertsProvider('field-001').future);
      final alerts = await future;

      // Assert
      expect(alerts, isNotEmpty);
      container.dispose();
    });

    test('should return fallback alerts when API fails', () async {
      // Arrange
      when(() => mockApi.getFieldAlerts(
                fieldId: any(named: 'fieldId'),
                status: any(named: 'status'),
                limit: any(named: 'limit'),
              ))
          .thenAnswer((_) async =>
              errorResponse<AlertsPageResponse>('ERR_500', 'Server error'));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      // Act
      final future = container.read(smartAlertsProvider('field-001').future);
      final alerts = await future;

      // Assert - should return fallback alerts (offline-first)
      expect(alerts, isNotEmpty);
      container.dispose();
    });

    test('should return all alerts when fieldId is null', () async {
      // Arrange
      when(() => mockApi.getFieldAlerts(
            fieldId: any(named: 'fieldId'),
            status: any(named: 'status'),
            limit: any(named: 'limit'),
          )).thenAnswer((_) async => ApiResponse.success(
            AlertsPageResponse.fromJson({
              'alerts': [
                sampleAlertJson(id: 'a1'),
              ],
              'total': 1,
            }),
          ));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      // Act
      final future = container.read(smartAlertsProvider(null).future);
      final alerts = await future;

      // Assert
      expect(alerts, isNotEmpty);
      container.dispose();
    });
  });

  group('allAlertsProvider', () {
    test('should return alerts without field filter', () async {
      // Arrange
      when(() => mockApi.getFieldAlerts(
            fieldId: any(named: 'fieldId'),
            status: any(named: 'status'),
            limit: any(named: 'limit'),
          )).thenAnswer((_) async => ApiResponse.success(
            AlertsPageResponse.fromJson({
              'alerts': [
                sampleAlertJson(id: 'a1'),
                sampleAlertJson(id: 'a2'),
                sampleAlertJson(id: 'a3'),
              ],
              'total': 3,
            }),
          ));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      // Act
      final future = container.read(allAlertsProvider.future);
      final alerts = await future;

      // Assert
      expect(alerts, isNotEmpty);
      container.dispose();
    });
  });

  group('alertStatsProvider', () {
    test('should return stats for a field', () async {
      // Arrange
      when(() => mockApi.getAlertStats(
            fieldId: any(named: 'fieldId'),
          )).thenAnswer((_) async => ApiResponse.success(
            AlertStats.fromJson({
              'total': 50,
              'active': 20,
              'acknowledged': 10,
              'resolved': 15,
              'dismissed': 5,
              'by_severity': {'critical': 5},
              'by_type': {'irrigation': 20},
            }),
          ));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      // Act
      final future = container.read(alertStatsProvider('field-001').future);
      final stats = await future;

      // Assert
      expect(stats, isNotNull);
      expect(stats!.total, 50);
      expect(stats.active, 20);
      container.dispose();
    });

    test('should return null when API fails', () async {
      // Arrange
      when(() => mockApi.getAlertStats(
                fieldId: any(named: 'fieldId'),
              ))
          .thenAnswer((_) async =>
              errorResponse<AlertStats>('ERR_500', 'Server error'));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      // Act
      final future = container.read(alertStatsProvider('field-001').future);
      final stats = await future;

      // Assert
      expect(stats, isNull);
      container.dispose();
    });
  });

  group('acknowledgeAlertProvider', () {
    test('should acknowledge alert and return true', () async {
      // Arrange
      when(() => mockApi.acknowledgeAlert(
            alertId: any(named: 'alertId'),
            userId: any(named: 'userId'),
          )).thenAnswer((_) async => ApiResponse.success(
            AlertModel.fromJson(sampleAlertJson(status: 'acknowledged')),
          ));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      // Act
      final params = (alertId: 'alert-001', userId: 'user-001');
      final future = container.read(acknowledgeAlertProvider(params).future);
      final success = await future;

      // Assert
      expect(success, isTrue);
      container.dispose();
    });

    test('should return false when API fails', () async {
      // Arrange
      when(() => mockApi.acknowledgeAlert(
                alertId: any(named: 'alertId'),
                userId: any(named: 'userId'),
              ))
          .thenAnswer((_) async =>
              errorResponse<AlertModel>('ERR_500', 'Server error'));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      // Act
      final params = (alertId: 'alert-001', userId: 'user-001');
      final future = container.read(acknowledgeAlertProvider(params).future);
      final success = await future;

      // Assert
      expect(success, isFalse);
      container.dispose();
    });
  });

  group('dismissAlertProvider', () {
    test('should dismiss alert and return true', () async {
      // Arrange
      when(() => mockApi.dismissAlert(
            alertId: any(named: 'alertId'),
            userId: any(named: 'userId'),
          )).thenAnswer((_) async => ApiResponse.success(
            AlertModel.fromJson(sampleAlertJson(status: 'dismissed')),
          ));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      // Act
      final params = (alertId: 'alert-001', userId: 'user-001');
      final future = container.read(dismissAlertProvider(params).future);
      final success = await future;

      // Assert
      expect(success, isTrue);
      container.dispose();
    });
  });
}
