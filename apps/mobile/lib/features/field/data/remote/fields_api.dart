import '../../../../core/http/api_client.dart';

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
      return List<Map<String, dynamic>>.from(response['features'] ?? []);
    }

    // Handle array of features
    if (response is List) {
      return List<Map<String, dynamic>>.from(response);
    }

    return [];
  }

  /// Fetch single field by ID
  Future<Map<String, dynamic>?> fetchFieldById(String fieldId) async {
    try {
      final response = await _client.get('/fields/$fieldId');
      return response as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }

  /// Create field with GeoJSON geometry
  ///
  /// [geoJsonFeature] should be a GeoJSON Feature object
  Future<Map<String, dynamic>> createField(
    Map<String, dynamic> geoJsonFeature,
  ) async {
    final response = await _client.post('/fields', geoJsonFeature);
    return response as Map<String, dynamic>;
  }

  /// Update field boundary
  Future<Map<String, dynamic>> updateFieldBoundary({
    required String fieldId,
    required Map<String, dynamic> geometry,
    required double areaHectares,
  }) async {
    final response = await _client.put(
      '/fields/$fieldId/geometry',
      {
        'geometry': geometry,
        'area_hectares': areaHectares,
      },
    );
    return response as Map<String, dynamic>;
  }

  /// Update field properties
  Future<Map<String, dynamic>> updateFieldProperties({
    required String fieldId,
    String? name,
    String? cropType,
    String? status,
  }) async {
    final response = await _client.put(
      '/fields/$fieldId',
      {
        if (name != null) 'name': name,
        if (cropType != null) 'crop_type': cropType,
        if (status != null) 'status': status,
      },
    );
    return response as Map<String, dynamic>;
  }

  /// Delete field (soft delete)
  Future<void> deleteField(String fieldId) async {
    await _client.delete('/fields/$fieldId');
  }

  /// Get field NDVI history
  Future<List<Map<String, dynamic>>> fetchNdviHistory({
    required String fieldId,
    DateTime? from,
    DateTime? to,
  }) async {
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
  }
}
