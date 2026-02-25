import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/api/kong_gateway_client.dart';
import 'package:sahool_field_app/features/pivot_irrigation/data/irrigation_engine_api.dart';

import '../../../mocks/mock_kong_gateway.dart';

void main() {
  late MockKongGatewayClient mockGateway;
  late IrrigationEngineApi api;

  setUpAll(() {
    registerFallbackValue(FakeKongService());
  });

  setUp(() {
    mockGateway = MockKongGatewayClient();
    api = IrrigationEngineApi(gateway: mockGateway);
  });

  group('IrrigationEngineApi', () {
    group('getPivotConfig', () {
      test('should return pivot configuration', () async {
        // Arrange
        when(() => mockGateway.get<Map<String, dynamic>>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as Map<String, dynamic> Function(dynamic);
          return ApiResponse.success(fromJson(samplePivotConfigJson()));
        });

        // Act
        final result = await api.getPivotConfig(pivotId: 'pivot-001');

        // Assert
        expect(result.success, isTrue);
        expect(result.data!['pivot_id'], 'pivot-001');
        expect(result.data!['radius_meters'], 400.0);
        expect(result.data!['total_sectors'], 6);

        verify(() => mockGateway.get<Map<String, dynamic>>(
              KongServices.irrigationEngine,
              '/pivots/pivot-001/config',
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });
    });

    group('getPivotStatus', () {
      test('should return real-time pivot status', () async {
        // Arrange
        final statusData = {
          'pivot_id': 'pivot-001',
          'is_running': true,
          'current_angle': 180.5,
          'speed_percent': 75,
          'water_pressure_bar': 3.2,
          'flow_rate_m3h': 90.0,
        };

        when(() => mockGateway.get<Map<String, dynamic>>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as Map<String, dynamic> Function(dynamic);
          return ApiResponse.success(fromJson(statusData));
        });

        // Act
        final result = await api.getPivotStatus(pivotId: 'pivot-001');

        // Assert
        expect(result.success, isTrue);
        expect(result.data!['is_running'], true);
        expect(result.data!['current_angle'], 180.5);
        expect(result.data!['speed_percent'], 75);
      });
    });

    group('sendCommand', () {
      test('should send start command', () async {
        // Arrange
        when(() => mockGateway.post<Map<String, dynamic>>(
              any(),
              any(),
              data: any(named: 'data'),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as Map<String, dynamic> Function(dynamic);
          return ApiResponse.success(fromJson({
            'status': 'accepted',
            'command': 'start',
            'timestamp': '2026-02-16T10:00:00Z',
          }));
        });

        // Act
        final result = await api.sendCommand(
          pivotId: 'pivot-001',
          commandType: 'start',
          params: {'speed_percent': 80, 'direction': 'forward'},
        );

        // Assert
        expect(result.success, isTrue);
        expect(result.data!['status'], 'accepted');

        verify(() => mockGateway.post<Map<String, dynamic>>(
              KongServices.irrigationEngine,
              '/pivots/pivot-001/command',
              data: {
                'command': 'start',
                'speed_percent': 80,
                'direction': 'forward',
              },
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });

      test('should send stop command without params', () async {
        // Arrange
        when(() => mockGateway.post<Map<String, dynamic>>(
              any(),
              any(),
              data: any(named: 'data'),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as Map<String, dynamic> Function(dynamic);
          return ApiResponse.success(fromJson({'status': 'accepted'}));
        });

        // Act
        await api.sendCommand(pivotId: 'pivot-001', commandType: 'stop');

        // Assert
        verify(() => mockGateway.post<Map<String, dynamic>>(
              KongServices.irrigationEngine,
              '/pivots/pivot-001/command',
              data: {'command': 'stop'},
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });

      test('should handle command rejection', () async {
        // Arrange
        when(() => mockGateway.post<Map<String, dynamic>>(
                  any(),
                  any(),
                  data: any(named: 'data'),
                  queryParams: any(named: 'queryParams'),
                  fromJson: any(named: 'fromJson'),
                  cancelToken: any(named: 'cancelToken'),
                ))
            .thenAnswer((_) async => errorResponse<Map<String, dynamic>>(
                'COMMAND_REJECTED', 'Pivot is in emergency stop'));

        // Act
        final result = await api.sendCommand(
          pivotId: 'pivot-001',
          commandType: 'start',
        );

        // Assert
        expect(result.success, isFalse);
        expect(result.errorCode, 'COMMAND_REJECTED');
      });
    });

    group('getPivotStats', () {
      test('should return statistics with default period', () async {
        // Arrange
        when(() => mockGateway.get<Map<String, dynamic>>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as Map<String, dynamic> Function(dynamic);
          return ApiResponse.success(fromJson({
            'total_water_m3': 2500,
            'total_runtime_hours': 45,
            'avg_flow_rate': 95.5,
            'cycles_completed': 12,
          }));
        });

        // Act
        final result = await api.getPivotStats(pivotId: 'pivot-001');

        // Assert
        expect(result.success, isTrue);
        expect(result.data!['total_water_m3'], 2500);
        expect(result.data!['cycles_completed'], 12);

        verify(() => mockGateway.get<Map<String, dynamic>>(
              KongServices.irrigationEngine,
              '/pivots/pivot-001/stats',
              queryParams: {'period': 'week'},
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });

      test('should accept custom period', () async {
        // Arrange
        when(() => mockGateway.get<Map<String, dynamic>>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as Map<String, dynamic> Function(dynamic);
          return ApiResponse.success(fromJson({'total_water_m3': 10000}));
        });

        // Act
        await api.getPivotStats(pivotId: 'pivot-001', period: 'month');

        // Assert
        verify(() => mockGateway.get<Map<String, dynamic>>(
              KongServices.irrigationEngine,
              '/pivots/pivot-001/stats',
              queryParams: {'period': 'month'},
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });
    });

    group('getSchedule', () {
      test('should return irrigation schedule', () async {
        // Arrange
        when(() => mockGateway.get<Map<String, dynamic>>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as Map<String, dynamic> Function(dynamic);
          return ApiResponse.success(fromJson({
            'pivot_id': 'pivot-001',
            'schedules': [
              {'day': 'sunday', 'start_time': '06:00', 'duration_hours': 4},
              {'day': 'wednesday', 'start_time': '06:00', 'duration_hours': 4},
            ],
          }));
        });

        // Act
        final result = await api.getSchedule(pivotId: 'pivot-001');

        // Assert
        expect(result.success, isTrue);
        final schedules = result.data!['schedules'] as List;
        expect(schedules.length, 2);
      });
    });

    group('updateSchedule', () {
      test('should update irrigation schedule', () async {
        // Arrange
        final scheduleData = {
          'schedules': [
            {'day': 'monday', 'start_time': '05:00', 'duration_hours': 6},
          ],
        };

        when(() => mockGateway.post<Map<String, dynamic>>(
              any(),
              any(),
              data: any(named: 'data'),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as Map<String, dynamic> Function(dynamic);
          return ApiResponse.success(fromJson({'status': 'updated'}));
        });

        // Act
        final result = await api.updateSchedule(
          pivotId: 'pivot-001',
          schedule: scheduleData,
        );

        // Assert
        expect(result.success, isTrue);

        verify(() => mockGateway.post<Map<String, dynamic>>(
              KongServices.irrigationEngine,
              '/pivots/pivot-001/schedule',
              data: scheduleData,
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });
    });

    group('getRunHistory', () {
      test('should return run history with default limit', () async {
        // Arrange
        when(() => mockGateway.get<List<dynamic>>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as List<dynamic> Function(dynamic);
          return ApiResponse.success(fromJson([
            {
              'id': 'run-1',
              'started_at': '2026-02-15T06:00:00Z',
              'water_m3': 200
            },
            {
              'id': 'run-2',
              'started_at': '2026-02-12T06:00:00Z',
              'water_m3': 185
            },
          ]));
        });

        // Act
        final result = await api.getRunHistory(pivotId: 'pivot-001');

        // Assert
        expect(result.success, isTrue);
        expect(result.data!.length, 2);

        verify(() => mockGateway.get<List<dynamic>>(
              KongServices.irrigationEngine,
              '/pivots/pivot-001/history',
              queryParams: {'limit': 20},
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });
    });

    group('updateSector', () {
      test('should update sector settings', () async {
        // Arrange
        final sectorSettings = {
          'speed_percent': 70,
          'water_application_mm': 25,
          'enabled': true,
        };

        when(() => mockGateway.put<Map<String, dynamic>>(
              any(),
              any(),
              data: any(named: 'data'),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as Map<String, dynamic> Function(dynamic);
          return ApiResponse.success(fromJson({'status': 'updated'}));
        });

        // Act
        final result = await api.updateSector(
          pivotId: 'pivot-001',
          sectorId: 'sector-3',
          settings: sectorSettings,
        );

        // Assert
        expect(result.success, isTrue);

        verify(() => mockGateway.put<Map<String, dynamic>>(
              KongServices.irrigationEngine,
              '/pivots/pivot-001/sectors/sector-3',
              data: sectorSettings,
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });
    });
  });
}
