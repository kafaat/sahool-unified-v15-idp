/// Smart Alerts Models Comprehensive Tests
/// اختبارات شاملة لنماذج التنبيهات الذكية
///
/// Tests all smart alerts models: SmartAlert, AlertAction, enums,
/// mapping functions, and fallback behavior.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/api/kong_gateway_client.dart';
import 'package:sahool_field_app/features/alerts/data/alert_service_api.dart';
import 'package:sahool_field_app/features/smart_alerts/presentation/providers/smart_alerts_provider.dart';

import '../../../mocks/mock_kong_gateway.dart';

/// Mock AlertServiceApi for testing mapping functions via provider
class MockAlertServiceApi extends Mock implements AlertServiceApi {}

void main() {
  // =========================================================================
  // AlertType Enum
  // =========================================================================

  group('AlertType', () {
    test('has exactly 7 values', () {
      expect(AlertType.values.length, 7);
    });

    test('contains all expected values', () {
      expect(AlertType.values, contains(AlertType.irrigation));
      expect(AlertType.values, contains(AlertType.weather));
      expect(AlertType.values, contains(AlertType.ndvi));
      expect(AlertType.values, contains(AlertType.sensor));
      expect(AlertType.values, contains(AlertType.task));
      expect(AlertType.values, contains(AlertType.pest));
      expect(AlertType.values, contains(AlertType.system));
    });

    test('values are in expected order', () {
      expect(AlertType.values[0], AlertType.irrigation);
      expect(AlertType.values[1], AlertType.weather);
      expect(AlertType.values[2], AlertType.ndvi);
      expect(AlertType.values[3], AlertType.sensor);
      expect(AlertType.values[4], AlertType.task);
      expect(AlertType.values[5], AlertType.pest);
      expect(AlertType.values[6], AlertType.system);
    });
  });

  // =========================================================================
  // AlertSeverity Enum
  // =========================================================================

  group('AlertSeverity', () {
    test('has exactly 4 values', () {
      expect(AlertSeverity.values.length, 4);
    });

    test('contains all expected values', () {
      expect(AlertSeverity.values, contains(AlertSeverity.critical));
      expect(AlertSeverity.values, contains(AlertSeverity.warning));
      expect(AlertSeverity.values, contains(AlertSeverity.info));
      expect(AlertSeverity.values, contains(AlertSeverity.success));
    });

    test('values are in expected order', () {
      expect(AlertSeverity.values[0], AlertSeverity.critical);
      expect(AlertSeverity.values[1], AlertSeverity.warning);
      expect(AlertSeverity.values[2], AlertSeverity.info);
      expect(AlertSeverity.values[3], AlertSeverity.success);
    });
  });

  // =========================================================================
  // AlertActionType Enum
  // =========================================================================

  group('AlertActionType', () {
    test('has exactly 5 values', () {
      expect(AlertActionType.values.length, 5);
    });

    test('contains all expected values', () {
      expect(AlertActionType.values, contains(AlertActionType.irrigate));
      expect(AlertActionType.values, contains(AlertActionType.inspect));
      expect(AlertActionType.values, contains(AlertActionType.createTask));
      expect(AlertActionType.values, contains(AlertActionType.viewDetails));
      expect(AlertActionType.values, contains(AlertActionType.dismiss));
    });

    test('values are in expected order', () {
      expect(AlertActionType.values[0], AlertActionType.irrigate);
      expect(AlertActionType.values[1], AlertActionType.inspect);
      expect(AlertActionType.values[2], AlertActionType.createTask);
      expect(AlertActionType.values[3], AlertActionType.viewDetails);
      expect(AlertActionType.values[4], AlertActionType.dismiss);
    });
  });

  // =========================================================================
  // SmartAlert
  // =========================================================================

  group('SmartAlert', () {
    test('construction with all fields', () {
      final now = DateTime(2026, 3, 20, 10, 30);
      final action = AlertAction(
        label: 'View Details',
        type: AlertActionType.viewDetails,
        route: '/alerts/a1',
        params: {'fieldId': 'f1'},
      );

      final alert = SmartAlert(
        id: 'alert-001',
        title: 'تنبيه الري',
        message: 'مستوى الرطوبة منخفض',
        type: AlertType.irrigation,
        severity: AlertSeverity.warning,
        source: 'sensor-hub',
        timeAgo: 'منذ 5 دقيقة',
        action: action,
        isRead: true,
        createdAt: now,
      );

      expect(alert.id, 'alert-001');
      expect(alert.title, 'تنبيه الري');
      expect(alert.message, 'مستوى الرطوبة منخفض');
      expect(alert.type, AlertType.irrigation);
      expect(alert.severity, AlertSeverity.warning);
      expect(alert.source, 'sensor-hub');
      expect(alert.timeAgo, 'منذ 5 دقيقة');
      expect(alert.action, isNotNull);
      expect(alert.action!.label, 'View Details');
      expect(alert.isRead, true);
      expect(alert.createdAt, now);
    });

    test('construction with optional fields null', () {
      final alert = SmartAlert(
        id: 'alert-002',
        title: 'System Alert',
        type: AlertType.system,
        severity: AlertSeverity.info,
        source: 'النظام',
        timeAgo: 'الآن',
      );

      expect(alert.id, 'alert-002');
      expect(alert.title, 'System Alert');
      expect(alert.message, isNull);
      expect(alert.type, AlertType.system);
      expect(alert.severity, AlertSeverity.info);
      expect(alert.source, 'النظام');
      expect(alert.timeAgo, 'الآن');
      expect(alert.action, isNull);
      expect(alert.isRead, false);
      expect(alert.createdAt, isNull);
    });

    test('isRead defaults to false', () {
      final alert = SmartAlert(
        id: 'a1',
        title: 'Test',
        type: AlertType.weather,
        severity: AlertSeverity.critical,
        source: 'weather',
        timeAgo: 'now',
      );

      expect(alert.isRead, false);
    });

    test('construction with each AlertType', () {
      for (final alertType in AlertType.values) {
        final alert = SmartAlert(
          id: 'type-${alertType.name}',
          title: 'Test ${alertType.name}',
          type: alertType,
          severity: AlertSeverity.info,
          source: 'test',
          timeAgo: 'now',
        );
        expect(alert.type, alertType);
      }
    });

    test('construction with each AlertSeverity', () {
      for (final severity in AlertSeverity.values) {
        final alert = SmartAlert(
          id: 'sev-${severity.name}',
          title: 'Test ${severity.name}',
          type: AlertType.system,
          severity: severity,
          source: 'test',
          timeAgo: 'now',
        );
        expect(alert.severity, severity);
      }
    });
  });

  // =========================================================================
  // AlertAction
  // =========================================================================

  group('AlertAction', () {
    test('construction with all fields', () {
      final action = AlertAction(
        label: 'Irrigate Now',
        type: AlertActionType.irrigate,
        route: '/irrigation/field-001',
        params: {'fieldId': 'field-001', 'amount': 25.0},
      );

      expect(action.label, 'Irrigate Now');
      expect(action.type, AlertActionType.irrigate);
      expect(action.route, '/irrigation/field-001');
      expect(action.params, isNotNull);
      expect(action.params!['fieldId'], 'field-001');
      expect(action.params!['amount'], 25.0);
    });

    test('construction with route and params null', () {
      final action = AlertAction(
        label: 'Dismiss',
        type: AlertActionType.dismiss,
      );

      expect(action.label, 'Dismiss');
      expect(action.type, AlertActionType.dismiss);
      expect(action.route, isNull);
      expect(action.params, isNull);
    });

    test('construction with route but no params', () {
      final action = AlertAction(
        label: 'Inspect Field',
        type: AlertActionType.inspect,
        route: '/fields/field-001/inspect',
      );

      expect(action.label, 'Inspect Field');
      expect(action.type, AlertActionType.inspect);
      expect(action.route, '/fields/field-001/inspect');
      expect(action.params, isNull);
    });

    test('construction with empty params map', () {
      final action = AlertAction(
        label: 'Create Task',
        type: AlertActionType.createTask,
        route: '/tasks/new',
        params: {},
      );

      expect(action.params, isNotNull);
      expect(action.params, isEmpty);
    });

    test('each AlertActionType can be used', () {
      for (final actionType in AlertActionType.values) {
        final action = AlertAction(
          label: 'Test ${actionType.name}',
          type: actionType,
        );
        expect(action.type, actionType);
      }
    });
  });

  // =========================================================================
  // _mapAlertType (tested indirectly via provider)
  // =========================================================================

  group('_mapAlertType (via provider mapping)', () {
    late MockAlertServiceApi mockApi;

    setUpAll(() {
      registerFallbackValue(FakeKongService());
    });

    setUp(() {
      mockApi = MockAlertServiceApi();
    });

    /// Helper: creates a provider container that returns alerts with a given type
    Future<List<SmartAlert>> fetchAlertsWithType(
      MockAlertServiceApi api,
      String alertType,
    ) async {
      when(() => api.getFieldAlerts(
            fieldId: any(named: 'fieldId'),
            status: any(named: 'status'),
            limit: any(named: 'limit'),
          )).thenAnswer((_) async => ApiResponse.success(
            AlertsPageResponse.fromJson({
              'alerts': [
                {
                  'id': 'map-test',
                  'field_id': 'f1',
                  'type': alertType,
                  'severity': 'info',
                  'title': 'Test',
                  'status': 'active',
                  'recommendations': <String>[],
                  'created_at': '2026-03-20T10:00:00Z',
                },
              ],
              'total': 1,
            }),
          ));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(api),
        ],
      );

      try {
        return await container.read(smartAlertsProvider('f1').future);
      } finally {
        container.dispose();
      }
    }

    test('irrigation type maps to AlertType.irrigation', () async {
      final alerts = await fetchAlertsWithType(mockApi, 'irrigation');
      expect(alerts.first.type, AlertType.irrigation);
    });

    test('weather type maps to AlertType.weather', () async {
      final alerts = await fetchAlertsWithType(mockApi, 'weather');
      expect(alerts.first.type, AlertType.weather);
    });

    test('ndvi type maps to AlertType.ndvi', () async {
      final alerts = await fetchAlertsWithType(mockApi, 'ndvi');
      expect(alerts.first.type, AlertType.ndvi);
    });

    test('sensor type maps to AlertType.sensor', () async {
      final alerts = await fetchAlertsWithType(mockApi, 'sensor');
      expect(alerts.first.type, AlertType.sensor);
    });

    test('task type maps to AlertType.task', () async {
      final alerts = await fetchAlertsWithType(mockApi, 'task');
      expect(alerts.first.type, AlertType.task);
    });

    test('pest type maps to AlertType.pest', () async {
      final alerts = await fetchAlertsWithType(mockApi, 'pest');
      expect(alerts.first.type, AlertType.pest);
    });

    test('unknown type defaults to AlertType.system', () async {
      final alerts = await fetchAlertsWithType(mockApi, 'unknown_type');
      expect(alerts.first.type, AlertType.system);
    });

    test('empty string type defaults to AlertType.system', () async {
      final alerts = await fetchAlertsWithType(mockApi, '');
      expect(alerts.first.type, AlertType.system);
    });
  });

  // =========================================================================
  // _mapAlertSeverity (tested indirectly via provider)
  // =========================================================================

  group('_mapAlertSeverity (via provider mapping)', () {
    late MockAlertServiceApi mockApi;

    setUpAll(() {
      registerFallbackValue(FakeKongService());
    });

    setUp(() {
      mockApi = MockAlertServiceApi();
    });

    /// Helper: creates a provider container that returns alerts with a given severity
    Future<List<SmartAlert>> fetchAlertsWithSeverity(
      MockAlertServiceApi api,
      String severity,
    ) async {
      when(() => api.getFieldAlerts(
            fieldId: any(named: 'fieldId'),
            status: any(named: 'status'),
            limit: any(named: 'limit'),
          )).thenAnswer((_) async => ApiResponse.success(
            AlertsPageResponse.fromJson({
              'alerts': [
                {
                  'id': 'sev-test',
                  'field_id': 'f1',
                  'type': 'system',
                  'severity': severity,
                  'title': 'Test',
                  'status': 'active',
                  'recommendations': <String>[],
                  'created_at': '2026-03-20T10:00:00Z',
                },
              ],
              'total': 1,
            }),
          ));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(api),
        ],
      );

      try {
        return await container.read(smartAlertsProvider('f1').future);
      } finally {
        container.dispose();
      }
    }

    test('critical severity maps to AlertSeverity.critical', () async {
      final alerts = await fetchAlertsWithSeverity(mockApi, 'critical');
      expect(alerts.first.severity, AlertSeverity.critical);
    });

    test('warning severity maps to AlertSeverity.warning', () async {
      final alerts = await fetchAlertsWithSeverity(mockApi, 'warning');
      expect(alerts.first.severity, AlertSeverity.warning);
    });

    test('info severity maps to AlertSeverity.info', () async {
      final alerts = await fetchAlertsWithSeverity(mockApi, 'info');
      expect(alerts.first.severity, AlertSeverity.info);
    });

    test('success severity maps to AlertSeverity.success', () async {
      final alerts = await fetchAlertsWithSeverity(mockApi, 'success');
      expect(alerts.first.severity, AlertSeverity.success);
    });

    test('unknown severity defaults to AlertSeverity.info', () async {
      final alerts = await fetchAlertsWithSeverity(mockApi, 'unknown');
      expect(alerts.first.severity, AlertSeverity.info);
    });

    test('empty string severity defaults to AlertSeverity.info', () async {
      final alerts = await fetchAlertsWithSeverity(mockApi, '');
      expect(alerts.first.severity, AlertSeverity.info);
    });
  });

  // =========================================================================
  // _mapToSmartAlert mapping details (via provider)
  // =========================================================================

  group('_mapToSmartAlert mapping details', () {
    late MockAlertServiceApi mockApi;

    setUpAll(() {
      registerFallbackValue(FakeKongService());
    });

    setUp(() {
      mockApi = MockAlertServiceApi();
    });

    test('maps AlertModel fields to SmartAlert correctly', () async {
      when(() => mockApi.getFieldAlerts(
            fieldId: any(named: 'fieldId'),
            status: any(named: 'status'),
            limit: any(named: 'limit'),
          )).thenAnswer((_) async => ApiResponse.success(
            AlertsPageResponse.fromJson({
              'alerts': [
                {
                  'id': 'mapped-alert',
                  'field_id': 'field-123',
                  'type': 'irrigation',
                  'severity': 'warning',
                  'title': 'Low Soil Moisture',
                  'message': 'Soil moisture below threshold',
                  'status': 'active',
                  'recommendations': ['Irrigate now', 'Check sensors'],
                  'metadata': {'source': 'sensor-hub-01'},
                  'created_at': '2026-03-20T10:00:00Z',
                },
              ],
              'total': 1,
            }),
          ));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      final alerts =
          await container.read(smartAlertsProvider('field-123').future);
      container.dispose();

      expect(alerts.length, 1);
      final alert = alerts.first;

      expect(alert.id, 'mapped-alert');
      expect(alert.title, 'Low Soil Moisture');
      expect(alert.message, 'Soil moisture below threshold');
      expect(alert.type, AlertType.irrigation);
      expect(alert.severity, AlertSeverity.warning);
      // source comes from metadata['source']
      expect(alert.source, 'sensor-hub-01');
      // timeAgo is formatted from createdAt
      expect(alert.timeAgo, isNotEmpty);
      // action is built from first recommendation
      expect(alert.action, isNotNull);
      expect(alert.action!.label, 'Irrigate now');
      expect(alert.action!.type, AlertActionType.viewDetails);
      expect(alert.action!.route, '/alerts/mapped-alert');
      // isRead is !isActive => !true => false
      expect(alert.isRead, false);
      expect(alert.createdAt, DateTime.utc(2026, 3, 20, 10, 0));
    });

    test('maps source to fieldId when metadata has no source', () async {
      when(() => mockApi.getFieldAlerts(
            fieldId: any(named: 'fieldId'),
            status: any(named: 'status'),
            limit: any(named: 'limit'),
          )).thenAnswer((_) async => ApiResponse.success(
            AlertsPageResponse.fromJson({
              'alerts': [
                {
                  'id': 'no-source',
                  'field_id': 'field-xyz',
                  'type': 'pest',
                  'severity': 'critical',
                  'title': 'Pest Detected',
                  'status': 'active',
                  'recommendations': <String>[],
                  'created_at': '2026-03-20T10:00:00Z',
                },
              ],
              'total': 1,
            }),
          ));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      final alerts =
          await container.read(smartAlertsProvider('field-xyz').future);
      container.dispose();

      // When no metadata source, fallback to fieldId
      expect(alerts.first.source, 'field-xyz');
    });

    test('sets action to null when recommendations are empty', () async {
      when(() => mockApi.getFieldAlerts(
            fieldId: any(named: 'fieldId'),
            status: any(named: 'status'),
            limit: any(named: 'limit'),
          )).thenAnswer((_) async => ApiResponse.success(
            AlertsPageResponse.fromJson({
              'alerts': [
                {
                  'id': 'no-rec',
                  'field_id': 'f1',
                  'type': 'system',
                  'severity': 'info',
                  'title': 'Info Alert',
                  'status': 'active',
                  'recommendations': <String>[],
                  'created_at': '2026-03-20T10:00:00Z',
                },
              ],
              'total': 1,
            }),
          ));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      final alerts = await container.read(smartAlertsProvider('f1').future);
      container.dispose();

      expect(alerts.first.action, isNull);
    });

    test('sets isRead to true when alert status is not active', () async {
      when(() => mockApi.getFieldAlerts(
            fieldId: any(named: 'fieldId'),
            status: any(named: 'status'),
            limit: any(named: 'limit'),
          )).thenAnswer((_) async => ApiResponse.success(
            AlertsPageResponse.fromJson({
              'alerts': [
                {
                  'id': 'acknowledged-alert',
                  'field_id': 'f1',
                  'type': 'task',
                  'severity': 'info',
                  'title': 'Task Complete',
                  'status': 'acknowledged',
                  'recommendations': <String>[],
                  'created_at': '2026-03-20T10:00:00Z',
                },
              ],
              'total': 1,
            }),
          ));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      final alerts = await container.read(smartAlertsProvider('f1').future);
      container.dispose();

      // isRead = !isActive; acknowledged status -> isActive = false -> isRead = true
      expect(alerts.first.isRead, true);
    });
  });

  // =========================================================================
  // Fallback alerts (offline-first pattern)
  // =========================================================================

  group('Fallback alerts (offline-first)', () {
    late MockAlertServiceApi mockApi;

    setUpAll(() {
      registerFallbackValue(FakeKongService());
    });

    setUp(() {
      mockApi = MockAlertServiceApi();
    });

    test('returns fallback alerts when API returns error response', () async {
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

      final alerts =
          await container.read(smartAlertsProvider('field-001').future);
      container.dispose();

      expect(alerts, isNotEmpty);
      expect(alerts.length, 1);
      expect(alerts.first.id, 'offline_1');
      expect(alerts.first.type, AlertType.system);
      expect(alerts.first.severity, AlertSeverity.info);
      expect(alerts.first.isRead, false);
      expect(alerts.first.source, 'النظام');
      expect(alerts.first.timeAgo, 'الآن');
      expect(alerts.first.title, contains('غير متصل'));
    });

    test('returns fallback alerts when API returns null data', () async {
      when(() => mockApi.getFieldAlerts(
            fieldId: any(named: 'fieldId'),
            status: any(named: 'status'),
            limit: any(named: 'limit'),
          )).thenAnswer((_) async => const ApiResponse<AlertsPageResponse>(
            success: true,
            data: null,
          ));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      final alerts =
          await container.read(smartAlertsProvider('field-001').future);
      container.dispose();

      expect(alerts, isNotEmpty);
      expect(alerts.first.id, 'offline_1');
    });

    test('fallback alerts when null fieldId and API fails', () async {
      when(() => mockApi.getFieldAlerts(
                fieldId: any(named: 'fieldId'),
                status: any(named: 'status'),
                limit: any(named: 'limit'),
              ))
          .thenAnswer((_) async =>
              errorResponse<AlertsPageResponse>('ERR_503', 'Unavailable'));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      final alerts = await container.read(smartAlertsProvider(null).future);
      container.dispose();

      expect(alerts.length, 1);
      expect(alerts.first.type, AlertType.system);
    });
  });

  // =========================================================================
  // Provider returns multiple mapped alerts
  // =========================================================================

  group('Provider with multiple alerts', () {
    late MockAlertServiceApi mockApi;

    setUpAll(() {
      registerFallbackValue(FakeKongService());
    });

    setUp(() {
      mockApi = MockAlertServiceApi();
    });

    test('maps multiple alerts with different types correctly', () async {
      when(() => mockApi.getFieldAlerts(
            fieldId: any(named: 'fieldId'),
            status: any(named: 'status'),
            limit: any(named: 'limit'),
          )).thenAnswer((_) async => ApiResponse.success(
            AlertsPageResponse.fromJson({
              'alerts': [
                {
                  'id': 'a1',
                  'field_id': 'f1',
                  'type': 'irrigation',
                  'severity': 'warning',
                  'title': 'Irrigation Alert',
                  'status': 'active',
                  'recommendations': ['Check moisture'],
                  'created_at': '2026-03-20T10:00:00Z',
                },
                {
                  'id': 'a2',
                  'field_id': 'f1',
                  'type': 'sensor',
                  'severity': 'critical',
                  'title': 'Sensor Offline',
                  'status': 'active',
                  'recommendations': ['Reset sensor'],
                  'created_at': '2026-03-20T09:00:00Z',
                },
                {
                  'id': 'a3',
                  'field_id': 'f1',
                  'type': 'ndvi',
                  'severity': 'info',
                  'title': 'NDVI Update',
                  'status': 'active',
                  'recommendations': <String>[],
                  'created_at': '2026-03-19T08:00:00Z',
                },
                {
                  'id': 'a4',
                  'field_id': 'f1',
                  'type': 'weather',
                  'severity': 'warning',
                  'title': 'Rain Expected',
                  'status': 'acknowledged',
                  'recommendations': ['Postpone spray'],
                  'created_at': '2026-03-18T07:00:00Z',
                },
                {
                  'id': 'a5',
                  'field_id': 'f1',
                  'type': 'task',
                  'severity': 'success',
                  'title': 'Task Complete',
                  'status': 'resolved',
                  'recommendations': <String>[],
                  'created_at': '2026-03-17T06:00:00Z',
                },
              ],
              'total': 5,
            }),
          ));

      final container = ProviderContainer(
        overrides: [
          alertServiceApiProvider.overrideWithValue(mockApi),
        ],
      );

      final alerts = await container.read(smartAlertsProvider('f1').future);
      container.dispose();

      expect(alerts.length, 5);

      // Verify types
      expect(alerts[0].type, AlertType.irrigation);
      expect(alerts[1].type, AlertType.sensor);
      expect(alerts[2].type, AlertType.ndvi);
      expect(alerts[3].type, AlertType.weather);
      expect(alerts[4].type, AlertType.task);

      // Verify severities
      expect(alerts[0].severity, AlertSeverity.warning);
      expect(alerts[1].severity, AlertSeverity.critical);
      expect(alerts[2].severity, AlertSeverity.info);
      expect(alerts[3].severity, AlertSeverity.warning);
      expect(alerts[4].severity, AlertSeverity.success);

      // Verify isRead based on status
      expect(alerts[0].isRead, false); // active -> !isActive = false
      expect(alerts[1].isRead, false); // active
      expect(alerts[2].isRead, false); // active
      expect(alerts[3].isRead, true); // acknowledged -> !isActive = true
      expect(alerts[4].isRead, true); // resolved -> !isActive = true

      // Verify actions (present only when recommendations non-empty)
      expect(alerts[0].action, isNotNull);
      expect(alerts[0].action!.label, 'Check moisture');
      expect(alerts[1].action, isNotNull);
      expect(alerts[1].action!.label, 'Reset sensor');
      expect(alerts[2].action, isNull); // empty recommendations
      expect(alerts[3].action, isNotNull);
      expect(alerts[3].action!.label, 'Postpone spray');
      expect(alerts[4].action, isNull); // empty recommendations
    });
  });
}
