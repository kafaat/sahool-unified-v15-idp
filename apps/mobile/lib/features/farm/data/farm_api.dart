import '../../../core/http/api_client.dart';
import '../../../core/utils/app_logger.dart';
import 'farm_entity.dart';

/// Farm API - HTTP layer wrapping ApiClient calls
class FarmApi {
  final ApiClient _client;

  FarmApi(this._client);

  /// Fetch all farms for the current user/tenant
  Future<List<FarmEntity>> getFarms() async {
    try {
      final response = await _client.get('/api/v1/farms');

      if (response is List) {
        return response
            .map((item) => FarmEntity.fromJson(item as Map<String, dynamic>))
            .toList();
      }

      // Handle paginated response with 'data' key
      if (response is Map && response['data'] is List) {
        return (response['data'] as List)
            .map((item) => FarmEntity.fromJson(item as Map<String, dynamic>))
            .toList();
      }

      return [];
    } catch (e, stackTrace) {
      AppLogger.e('Failed to fetch farms', tag: 'FarmApi', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  /// Create a new farm
  Future<FarmEntity> createFarm(Map<String, dynamic> data) async {
    try {
      final response = await _client.post('/api/v1/farms', data);
      return FarmEntity.fromJson(response as Map<String, dynamic>);
    } catch (e, stackTrace) {
      AppLogger.e('Failed to create farm', tag: 'FarmApi', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  /// Delete a farm by ID
  Future<void> deleteFarm(String id) async {
    try {
      await _client.delete('/api/v1/farms/$id');
    } catch (e, stackTrace) {
      AppLogger.e('Failed to delete farm $id', tag: 'FarmApi', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
}
