import '../../../../core/http/api_client.dart';
import '../../../../core/utils/app_logger.dart';

/// Fields API - GeoJSON communication with PostGIS backend
class FieldsApi {
  final ApiClient _client;

  FieldsApi(this._client);

  /// Fetch fields as GeoJSON FeatureCollection
  ///
  /// Returns list of GeoJSON Features with Polygon geometries
  Future<List<Map<String, dynamic>>> fetchFields({
    required String tenantId,
    String? farmId,
  }) async {
    try {
      final response = await _client.get(
        '/fields',
        queryParameters: {
          'tenant_id': tenantId,
          if (farmId != null) 'farm_id': farmId,
          'format': 'geojson',
        },
      );

      // Handle FeatureCollection response
      if (response is Map && response['type'] == 'FeatureCollection') {
        return List<Map<String, dynamic>>.from((response['features'] ?? []) as Iterable);
      }

      // Handle array of features
      if (response is List) {
        return List<Map<String, dynamic>>.from(response);
      }

      return [];
    } catch (e, stackTrace) {
      AppLogger.e('Failed to fetch fields', tag: 'FieldsApi', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  /// Fetch single field by ID
  Future<Map<String, dynamic>?> fetchFieldById(String fieldId) async {
    try {
      final response = await _client.get('/fields/$fieldId');
      return response as Map<String, dynamic>;
    } catch (e, stackTrace) {
      AppLogger.e('Failed to fetch field $fieldId', tag: 'FieldsApi', error: e, stackTrace: stackTrace);
      return null;
    }
  }

  /// Create field with GeoJSON geometry
  ///
  /// [geoJsonFeature] should be a GeoJSON Feature object
  Future<Map<String, dynamic>> createField(
    Map<String, dynamic> geoJsonFeature,
  ) async {
    try {
      final response = await _client.post('/fields', geoJsonFeature);
      return response as Map<String, dynamic>;
    } catch (e, stackTrace) {
      AppLogger.e('Failed to create field', tag: 'FieldsApi', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  /// Update field boundary
  Future<Map<String, dynamic>> updateFieldBoundary({
    required String fieldId,
    required Map<String, dynamic> geometry,
    required double areaHectares,
  }) async {
    try {
      final response = await _client.put(
        '/fields/$fieldId/geometry',
        {
          'geometry': geometry,
          'area_hectares': areaHectares,
        },
      );
      return response as Map<String, dynamic>;
    } catch (e, stackTrace) {
      AppLogger.e('Failed to update field boundary $fieldId', tag: 'FieldsApi', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  /// Update field properties
  Future<Map<String, dynamic>> updateFieldProperties({
    required String fieldId,
    String? name,
    String? cropType,
    String? status,
  }) async {
    try {
      final response = await _client.put(
        '/fields/$fieldId',
        {
          if (name != null) 'name': name,
          if (cropType != null) 'crop_type': cropType,
          if (status != null) 'status': status,
        },
      );
      return response as Map<String, dynamic>;
    } catch (e, stackTrace) {
      AppLogger.e('Failed to update field properties $fieldId', tag: 'FieldsApi', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  /// Delete field (soft delete)
  Future<void> deleteField(String fieldId) async {
    try {
      await _client.delete('/fields/$fieldId');
    } catch (e, stackTrace) {
      AppLogger.e('Failed to delete field $fieldId', tag: 'FieldsApi', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  /// Get field NDVI history
  Future<List<Map<String, dynamic>>> fetchNdviHistory({
    required String fieldId,
    DateTime? from,
    DateTime? to,
  }) async {
    try {
      final response = await _client.get(
        '/fields/$fieldId/ndvi-history',
        queryParameters: {
          if (from != null) 'from': from.toIso8601String(),
          if (to != null) 'to': to.toIso8601String(),
        },
      );

      if (response is List) {
        return List<Map<String, dynamic>>.from(response);
      }
      return [];
    } catch (e, stackTrace) {
      AppLogger.e('Failed to fetch NDVI history for field $fieldId', tag: 'FieldsApi', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
}
