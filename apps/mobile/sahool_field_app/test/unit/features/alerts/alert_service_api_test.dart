import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/api/kong_gateway_client.dart';
import 'package:sahool_field_app/features/alerts/data/alert_service_api.dart';

import '../../../mocks/mock_kong_gateway.dart';

void main() {
  late MockKongGatewayClient mockGateway;
  late AlertServiceApi api;

  setUpAll(() {
    registerFallbackValue(FakeKongService());
  });

  setUp(() {
    mockGateway = MockKongGatewayClient();
    api = AlertServiceApi(gateway: mockGateway);
  });

  group('AlertServiceApi', () {
    group('getFieldAlerts', () {
      test('should return alerts page on success', () async {
        // Arrange
        final responseData = {
          'alerts': [
            sampleAlertJson(id: 'a1'),
            sampleAlertJson(id: 'a2', severity: 'critical'),
          ],
          'total': 2,
          'skip': 0,
          'limit': 20,
        };

        when(() => mockGateway.get<AlertsPageResponse>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as AlertsPageResponse Function(dynamic);
          return ApiResponse.success(fromJson(responseData));
        });

        // Act
        final result = await api.getFieldAlerts(fieldId: 'field-001');

        // Assert
        expect(result.success, isTrue);
        expect(result.data, isNotNull);
        expect(result.data!.alerts.length, 2);
        expect(result.data!.total, 2);
        expect(result.data!.alerts[0].id, 'a1');
        expect(result.data!.alerts[1].severity, 'critical');

        verify(() => mockGateway.get<AlertsPageResponse>(
              KongServices.alerts,
              '/field/field-001',
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });

      test('should include optional filters in query params', () async {
        // Arrange
        when(() => mockGateway.get<AlertsPageResponse>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as AlertsPageResponse Function(dynamic);
          return ApiResponse.success(fromJson({
            'alerts': [],
            'total': 0,
            'skip': 0,
            'limit': 10,
          }));
        });

        // Act
        await api.getFieldAlerts(
          fieldId: 'field-001',
          status: 'active',
          severity: 'critical',
          type: 'irrigation',
          skip: 10,
          limit: 10,
        );

        // Assert
        verify(() => mockGateway.get<AlertsPageResponse>(
              KongServices.alerts,
              '/field/field-001',
              queryParams: {
                'skip': 10,
                'limit': 10,
                'status': 'active',
                'severity': 'critical',
                'type': 'irrigation',
              },
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });

      test('should return error on API failure', () async {
        // Arrange
        when(() => mockGateway.get<AlertsPageResponse>(
                  any(),
                  any(),
                  queryParams: any(named: 'queryParams'),
                  fromJson: any(named: 'fromJson'),
                  cancelToken: any(named: 'cancelToken'),
                ))
            .thenAnswer((_) async =>
                errorResponse<AlertsPageResponse>('ERR_500', 'Server error'));

        // Act
        final result = await api.getFieldAlerts(fieldId: 'field-001');

        // Assert
        expect(result.success, isFalse);
        expect(result.errorCode, 'ERR_500');
      });
    });

    group('getAlert', () {
      test('should return single alert on success', () async {
        // Arrange
        when(() => mockGateway.get<AlertModel>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as AlertModel Function(dynamic);
          return ApiResponse.success(fromJson(sampleAlertJson()));
        });

        // Act
        final result = await api.getAlert('alert-001');

        // Assert
        expect(result.success, isTrue);
        expect(result.data!.id, 'alert-001');
        expect(result.data!.type, 'irrigation');
      });
    });

    group('createAlert', () {
      test('should create alert and return model', () async {
        // Arrange
        when(() => mockGateway.post<AlertModel>(
              any(),
              any(),
              data: any(named: 'data'),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as AlertModel Function(dynamic);
          return ApiResponse.success(
              fromJson(sampleAlertJson(id: 'new-alert')));
        });

        // Act
        final result = await api.createAlert(
          fieldId: 'field-001',
          type: 'irrigation',
          severity: 'warning',
          title: 'تنبيه ري',
          message: 'رطوبة التربة منخفضة',
          recommendations: ['ري فوري'],
        );

        // Assert
        expect(result.success, isTrue);
        expect(result.data!.id, 'new-alert');

        verify(() => mockGateway.post<AlertModel>(
              KongServices.alerts,
              '',
              data: {
                'field_id': 'field-001',
                'type': 'irrigation',
                'severity': 'warning',
                'title': 'تنبيه ري',
                'message': 'رطوبة التربة منخفضة',
                'recommendations': ['ري فوري'],
              },
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });
    });

    group('acknowledgeAlert', () {
      test('should acknowledge alert successfully', () async {
        // Arrange
        when(() => mockGateway.post<AlertModel>(
              any(),
              any(),
              data: any(named: 'data'),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as AlertModel Function(dynamic);
          return ApiResponse.success(
              fromJson(sampleAlertJson(status: 'acknowledged')));
        });

        // Act
        final result = await api.acknowledgeAlert(
          alertId: 'alert-001',
          userId: 'user-001',
        );

        // Assert
        expect(result.success, isTrue);
        expect(result.data!.isAcknowledged, isTrue);
        expect(result.data!.isActive, isFalse);
      });
    });

    group('resolveAlert', () {
      test('should resolve alert with optional note', () async {
        // Arrange
        when(() => mockGateway.post<AlertModel>(
              any(),
              any(),
              data: any(named: 'data'),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as AlertModel Function(dynamic);
          return ApiResponse.success(
              fromJson(sampleAlertJson(status: 'resolved')));
        });

        // Act
        final result = await api.resolveAlert(
          alertId: 'alert-001',
          userId: 'user-001',
          note: 'تم حل المشكلة',
        );

        // Assert
        expect(result.success, isTrue);
        expect(result.data!.isResolved, isTrue);

        verify(() => mockGateway.post<AlertModel>(
              KongServices.alerts,
              '/alert-001/resolve',
              data: {
                'user_id': 'user-001',
                'note': 'تم حل المشكلة',
              },
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });
    });

    group('dismissAlert', () {
      test('should dismiss alert successfully', () async {
        // Arrange
        when(() => mockGateway.post<AlertModel>(
              any(),
              any(),
              data: any(named: 'data'),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as AlertModel Function(dynamic);
          return ApiResponse.success(
              fromJson(sampleAlertJson(status: 'dismissed')));
        });

        // Act
        final result = await api.dismissAlert(
          alertId: 'alert-001',
          userId: 'user-001',
        );

        // Assert
        expect(result.success, isTrue);
        expect(result.data!.isDismissed, isTrue);
      });
    });

    group('deleteAlert', () {
      test('should delete alert successfully', () async {
        // Arrange
        when(() => mockGateway.delete<void>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async => const ApiResponse(success: true));

        // Act
        final result = await api.deleteAlert('alert-001');

        // Assert
        expect(result.success, isTrue);

        verify(() => mockGateway.delete<void>(
              KongServices.alerts,
              '/alert-001',
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });
    });

    group('getAlertStats', () {
      test('should return alert statistics', () async {
        // Arrange
        final statsData = {
          'total': 50,
          'active': 20,
          'acknowledged': 10,
          'resolved': 15,
          'dismissed': 5,
          'by_severity': {'critical': 5, 'warning': 25, 'info': 20},
          'by_type': {'irrigation': 20, 'weather': 15, 'pest': 15},
        };

        when(() => mockGateway.get<AlertStats>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as AlertStats Function(dynamic);
          return ApiResponse.success(fromJson(statsData));
        });

        // Act
        final result = await api.getAlertStats(fieldId: 'field-001');

        // Assert
        expect(result.success, isTrue);
        expect(result.data!.total, 50);
        expect(result.data!.active, 20);
        expect(result.data!.bySeverity['critical'], 5);
        expect(result.data!.byType['irrigation'], 20);
      });
    });

    group('getAlertRules', () {
      test('should return alert rules', () async {
        // Arrange
        final rulesData = [
          {
            'id': 'rule-001',
            'field_id': 'field-001',
            'name': 'قاعدة رطوبة التربة',
            'condition': {
              'metric': 'soil_moisture',
              'operator': '<',
              'value': 30
            },
            'alert_config': {'severity': 'warning', 'type': 'irrigation'},
            'enabled': true,
            'cooldown_minutes': 120,
          },
        ];

        when(() => mockGateway.get<List<AlertRule>>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as List<AlertRule> Function(dynamic);
          return ApiResponse.success(fromJson(rulesData));
        });

        // Act
        final result =
            await api.getAlertRules(fieldId: 'field-001', enabled: true);

        // Assert
        expect(result.success, isTrue);
        expect(result.data!.length, 1);
        expect(result.data![0].name, 'قاعدة رطوبة التربة');
        expect(result.data![0].enabled, isTrue);
        expect(result.data![0].cooldownMinutes, 120);
      });
    });
  });
}
