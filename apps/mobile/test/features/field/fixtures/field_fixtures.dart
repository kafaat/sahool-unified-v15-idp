/// Field Test Fixtures for SAHOOL Field App
/// بيانات اختبار الحقول
///
/// Contains mock data for field-related unit tests including:
/// - Field entities with GeoJSON boundaries
/// - NDVI data samples
/// - API response mocks
/// - GeoJSON features and collections
library;

import 'package:latlong2/latlong.dart';

/// Field entity fixtures for testing
class FieldTestFixtures {
  // ==========================================================================
  // Sample Boundary Polygons (List<LatLng>)
  // ==========================================================================

  /// Simple rectangular field boundary (4 points)
  static final List<LatLng> simpleRectangleBoundary = [
    const LatLng(15.3700, 44.1900),
    const LatLng(15.3700, 44.1950),
    const LatLng(15.3750, 44.1950),
    const LatLng(15.3750, 44.1900),
  ];

  /// Triangle boundary (minimum valid polygon - 3 points)
  static final List<LatLng> triangleBoundary = [
    const LatLng(15.3700, 44.1900),
    const LatLng(15.3750, 44.1925),
    const LatLng(15.3700, 44.1950),
  ];

  /// Irregular polygon boundary (complex shape)
  static final List<LatLng> irregularBoundary = [
    const LatLng(15.3700, 44.1900),
    const LatLng(15.3710, 44.1920),
    const LatLng(15.3720, 44.1910),
    const LatLng(15.3730, 44.1940),
    const LatLng(15.3720, 44.1960),
    const LatLng(15.3700, 44.1950),
  ];

  /// Large field boundary (more points)
  static final List<LatLng> largeFieldBoundary = [
    const LatLng(15.3700, 44.1900),
    const LatLng(15.3700, 44.1920),
    const LatLng(15.3710, 44.1940),
    const LatLng(15.3720, 44.1950),
    const LatLng(15.3740, 44.1950),
    const LatLng(15.3760, 44.1940),
    const LatLng(15.3770, 44.1920),
    const LatLng(15.3770, 44.1900),
    const LatLng(15.3750, 44.1880),
    const LatLng(15.3720, 44.1880),
  ];

  /// Empty boundary (invalid)
  static final List<LatLng> emptyBoundary = [];

  /// Single point (invalid polygon)
  static final List<LatLng> singlePointBoundary = [
    const LatLng(15.3700, 44.1900),
  ];

  /// Two points (invalid polygon)
  static final List<LatLng> twoPointsBoundary = [
    const LatLng(15.3700, 44.1900),
    const LatLng(15.3750, 44.1950),
  ];

  // ==========================================================================
  // Sample Field JSON Data (API Responses)
  // ==========================================================================

  /// Sample field with full data
  static final Map<String, dynamic> sampleFieldJson = {
    'id': 'field_001',
    'remote_id': 'remote_field_001',
    'tenant_id': 'tenant_1',
    'farm_id': 'farm_001',
    'name': 'الحقل الشمالي',
    'crop_type': 'wheat',
    'area_hectares': 5.5,
    'status': 'active',
    'ndvi_current': 0.72,
    'ndvi_updated_at': '2024-01-15T10:30:00Z',
    'synced': true,
    'is_deleted': false,
    'created_at': '2024-01-01T00:00:00Z',
    'updated_at': '2024-01-15T10:30:00Z',
    'pending_tasks': 3,
  };

  /// Sample GeoJSON Feature for field
  static final Map<String, dynamic> sampleGeoJsonFeature = {
    'type': 'Feature',
    'id': 'field_001',
    'geometry': {
      'type': 'Polygon',
      'coordinates': [
        [
          [44.1900, 15.3700],
          [44.1950, 15.3700],
          [44.1950, 15.3750],
          [44.1900, 15.3750],
          [44.1900, 15.3700], // Closed polygon
        ],
      ],
    },
    'properties': {
      'id': 'field_001',
      'remote_id': 'remote_field_001',
      'tenant_id': 'tenant_1',
      'farm_id': 'farm_001',
      'name': 'الحقل الشمالي',
      'crop_type': 'wheat',
      'area_hectares': 5.5,
      'status': 'active',
      'ndvi_current': 0.72,
      'ndvi_updated_at': '2024-01-15T10:30:00Z',
      'created_at': '2024-01-01T00:00:00Z',
      'updated_at': '2024-01-15T10:30:00Z',
    },
  };

  /// Sample field with critical NDVI (stressed)
  static final Map<String, dynamic> stressedFieldJson = {
    'type': 'Feature',
    'id': 'field_002',
    'geometry': {
      'type': 'Polygon',
      'coordinates': [
        [
          [44.2000, 15.3800],
          [44.2050, 15.3800],
          [44.2050, 15.3850],
          [44.2000, 15.3850],
          [44.2000, 15.3800],
        ],
      ],
    },
    'properties': {
      'id': 'field_002',
      'tenant_id': 'tenant_1',
      'name': 'حقل الجفاف',
      'crop_type': 'barley',
      'area_hectares': 3.2,
      'status': 'active',
      'ndvi_current': 0.45,
      'ndvi_updated_at': '2024-01-15T10:30:00Z',
      'created_at': '2024-01-01T00:00:00Z',
      'updated_at': '2024-01-15T10:30:00Z',
    },
  };

  /// Sample field with critical NDVI (critical)
  static final Map<String, dynamic> criticalFieldJson = {
    'type': 'Feature',
    'id': 'field_003',
    'geometry': {
      'type': 'Polygon',
      'coordinates': [
        [
          [44.2100, 15.3900],
          [44.2150, 15.3900],
          [44.2150, 15.3950],
          [44.2100, 15.3950],
          [44.2100, 15.3900],
        ],
      ],
    },
    'properties': {
      'id': 'field_003',
      'tenant_id': 'tenant_1',
      'name': 'حقل المرض',
      'crop_type': 'tomato',
      'area_hectares': 2.1,
      'status': 'active',
      'ndvi_current': 0.25,
      'ndvi_updated_at': '2024-01-15T10:30:00Z',
      'created_at': '2024-01-01T00:00:00Z',
      'updated_at': '2024-01-15T10:30:00Z',
    },
  };

  /// Sample field without NDVI data
  static final Map<String, dynamic> fieldWithoutNdviJson = {
    'type': 'Feature',
    'id': 'field_004',
    'geometry': {
      'type': 'Polygon',
      'coordinates': [
        [
          [44.2200, 15.4000],
          [44.2250, 15.4000],
          [44.2250, 15.4050],
          [44.2200, 15.4050],
          [44.2200, 15.4000],
        ],
      ],
    },
    'properties': {
      'id': 'field_004',
      'tenant_id': 'tenant_1',
      'name': 'حقل جديد',
      'crop_type': null,
      'area_hectares': 1.5,
      'status': 'preparing',
      'ndvi_current': null,
      'ndvi_updated_at': null,
      'created_at': '2024-01-10T00:00:00Z',
      'updated_at': '2024-01-10T00:00:00Z',
    },
  };

  /// Unsynced field (offline created)
  static final Map<String, dynamic> unsyncedFieldJson = {
    'type': 'Feature',
    'id': 'local_field_001',
    'geometry': {
      'type': 'Polygon',
      'coordinates': [
        [
          [44.2300, 15.4100],
          [44.2350, 15.4100],
          [44.2350, 15.4150],
          [44.2300, 15.4150],
          [44.2300, 15.4100],
        ],
      ],
    },
    'properties': {
      'id': 'local_field_001',
      'remote_id': null,
      'tenant_id': 'tenant_1',
      'name': 'حقل محلي',
      'crop_type': 'corn',
      'area_hectares': 4.0,
      'status': 'active',
      'synced': false,
      'is_deleted': false,
      'created_at': '2024-01-14T00:00:00Z',
      'updated_at': '2024-01-14T00:00:00Z',
    },
  };

  // ==========================================================================
  // GeoJSON FeatureCollection (Multiple Fields)
  // ==========================================================================

  /// Sample FeatureCollection with multiple fields
  static final Map<String, dynamic> sampleFeatureCollection = {
    'type': 'FeatureCollection',
    'features': [
      sampleGeoJsonFeature,
      stressedFieldJson,
      criticalFieldJson,
    ],
  };

  /// Empty FeatureCollection
  static final Map<String, dynamic> emptyFeatureCollection = {
    'type': 'FeatureCollection',
    'features': [],
  };

  // ==========================================================================
  // API Response Mocks
  // ==========================================================================

  /// Successful fetch fields response
  static final Map<String, dynamic> successfulFetchResponse = {
    'success': true,
    'data': sampleFeatureCollection,
  };

  /// Error response - unauthorized
  static final Map<String, dynamic> unauthorizedErrorResponse = {
    'success': false,
    'error': 'Unauthorized',
    'message': 'غير مصرح بالوصول',
    'code': 401,
  };

  /// Error response - server error
  static final Map<String, dynamic> serverErrorResponse = {
    'success': false,
    'error': 'Internal Server Error',
    'message': 'حدث خطأ في الخادم',
    'code': 500,
  };

  /// Error response - not found
  static final Map<String, dynamic> notFoundErrorResponse = {
    'success': false,
    'error': 'Not Found',
    'message': 'الحقل غير موجود',
    'code': 404,
  };

  // ==========================================================================
  // NDVI Data Fixtures
  // ==========================================================================

  /// Sample NDVI history for a field
  static final List<Map<String, dynamic>> ndviHistory = [
    {'date': '2024-01-15', 'ndvi': 0.72, 'cloud_cover': 5},
    {'date': '2024-01-10', 'ndvi': 0.68, 'cloud_cover': 10},
    {'date': '2024-01-05', 'ndvi': 0.65, 'cloud_cover': 15},
    {'date': '2024-01-01', 'ndvi': 0.60, 'cloud_cover': 8},
    {'date': '2023-12-25', 'ndvi': 0.55, 'cloud_cover': 20},
  ];

  /// NDVI values for different health statuses
  static const double healthyNdvi = 0.72;      // > 0.6
  static const double stressedNdvi = 0.45;     // 0.4 - 0.6
  static const double criticalNdvi = 0.25;     // < 0.4
  static const double unknownNdvi = 0.0;       // 0 or null

  // ==========================================================================
  // Test Constants
  // ==========================================================================

  static const String testTenantId = 'tenant_1';
  static const String testFarmId = 'farm_001';
  static const String testFieldId = 'field_001';
  static const String testFieldName = 'الحقل الشمالي';

  // Centroids
  static const LatLng rectangleCentroid = LatLng(15.3725, 44.1925);
  static const LatLng triangleCentroid = LatLng(15.3716666, 44.1925);

  // Areas (approximate in hectares)
  static const double rectangleAreaHa = 2.75; // Approximate
  static const double triangleAreaHa = 1.37;  // Approximate

  // ==========================================================================
  // Outbox Data Fixtures
  // ==========================================================================

  /// Sample outbox item for field creation
  static final Map<String, dynamic> createFieldOutboxItem = {
    'id': 1,
    'tenant_id': testTenantId,
    'entity_type': 'field',
    'entity_id': 'local_field_001',
    'api_endpoint': '/api/v1/fields',
    'method': 'POST',
    'payload': '{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[44.19,15.37],[44.195,15.37],[44.195,15.375],[44.19,15.375],[44.19,15.37]]]},"properties":{"name":"حقل جديد","tenant_id":"tenant_1"}}',
    'retry_count': 0,
    'is_synced': false,
    'created_at': '2024-01-15T12:00:00Z',
  };

  /// Sample outbox item for field update
  static final Map<String, dynamic> updateFieldOutboxItem = {
    'id': 2,
    'tenant_id': testTenantId,
    'entity_type': 'field',
    'entity_id': testFieldId,
    'api_endpoint': '/api/v1/fields/$testFieldId',
    'method': 'PATCH',
    'payload': '{"name":"الحقل المحدث","crop_type":"barley"}',
    'retry_count': 0,
    'is_synced': false,
    'created_at': '2024-01-15T13:00:00Z',
  };

  /// Sample outbox item for field deletion
  static final Map<String, dynamic> deleteFieldOutboxItem = {
    'id': 3,
    'tenant_id': testTenantId,
    'entity_type': 'field',
    'entity_id': testFieldId,
    'api_endpoint': '/api/v1/fields/$testFieldId',
    'method': 'DELETE',
    'payload': '{"field_id":"$testFieldId"}',
    'retry_count': 0,
    'is_synced': false,
    'created_at': '2024-01-15T14:00:00Z',
  };
}
