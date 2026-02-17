import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/api/kong_gateway_client.dart';

/// Mock Kong Gateway Client for testing
/// عميل بوابة Kong الوهمي للاختبارات
class MockKongGatewayClient extends Mock implements KongGatewayClient {}

/// Fallback values for mocktail
class FakeKongService extends Fake implements KongService {}

/// Helper to create successful ApiResponse
ApiResponse<T> successResponse<T>(T data) =>
    ApiResponse<T>.success(data, requestId: 'test-req-001');

/// Helper to create error ApiResponse
ApiResponse<T> errorResponse<T>(String code, String message) =>
    ApiResponse<T>.error(code, message, messageAr: 'خطأ في الاختبار');

/// Sample alert JSON data for tests
Map<String, dynamic> sampleAlertJson({
  String id = 'alert-001',
  String fieldId = 'field-001',
  String type = 'irrigation',
  String severity = 'warning',
  String status = 'active',
}) =>
    {
      'id': id,
      'field_id': fieldId,
      'type': type,
      'severity': severity,
      'title': 'تنبيه اختباري',
      'message': 'رسالة تنبيه للاختبار',
      'status': status,
      'recommendations': ['توصية 1', 'توصية 2'],
      'created_at': '2026-02-16T10:00:00Z',
    };

/// Sample soil sample JSON data for tests
Map<String, dynamic> sampleSoilJson({
  String id = 'sample-001',
  String barcode = 'BC-2026-001',
  String type = 'soil',
  String status = 'pending',
}) =>
    {
      'id': id,
      'barcode': barcode,
      'type': type,
      'status': status,
      'experiment_name': 'تجربة القمح 2026',
      'plot_code': 'P-01',
      'collected_by': 'أحمد',
      'collected_at': '2026-02-16T08:00:00Z',
    };

/// Sample pivot config JSON for tests
Map<String, dynamic> samplePivotConfigJson({
  String pivotId = 'pivot-001',
}) =>
    {
      'pivot_id': pivotId,
      'name': 'المحوري الرئيسي',
      'radius_meters': 400.0,
      'total_sectors': 6,
      'flow_rate_m3h': 120.0,
    };
