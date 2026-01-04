import '../../../../core/http/api_client.dart';
import '../../../../core/utils/app_logger.dart';

/// Crops API - Fetch crop catalog from server
/// واجهة برمجية للمحاصيل - جلب كتالوج المحاصيل من السيرفر
class CropsApi {
  final ApiClient _client;

  CropsApi(this._client);

  /// Fetch all crops from the unified catalog
  ///
  /// Returns list of crop objects with full details
  Future<List<Map<String, dynamic>>> fetchAllCrops() async {
    try {
      final response = await _client.get('/crops');

      if (response is List) {
        return List<Map<String, dynamic>>.from(response);
      }

      // Handle case where response is wrapped in a data field
      if (response is Map && response['data'] is List) {
        return List<Map<String, dynamic>>.from(response['data']);
      }

      return [];
    } catch (e) {
      AppLogger.e('Failed to fetch crops', tag: 'CropsApi', error: e);
      rethrow;
    }
  }

  /// Fetch crops by category
  ///
  /// [category] - cereals, legumes, vegetables, fruits, etc.
  Future<List<Map<String, dynamic>>> fetchCropsByCategory(String category) async {
    try {
      final response = await _client.get(
        '/crops',
        queryParameters: {
          'category': category,
        },
      );

      if (response is List) {
        return List<Map<String, dynamic>>.from(response);
      }

      if (response is Map && response['data'] is List) {
        return List<Map<String, dynamic>>.from(response['data']);
      }

      return [];
    } catch (e) {
      AppLogger.e('Failed to fetch crops by category', tag: 'CropsApi', error: e);
      rethrow;
    }
  }

  /// Fetch single crop by code
  Future<Map<String, dynamic>?> fetchCropByCode(String cropCode) async {
    try {
      final response = await _client.get('/crops/$cropCode');
      return response as Map<String, dynamic>?;
    } catch (e) {
      AppLogger.e('Failed to fetch crop by code', tag: 'CropsApi', error: e);
      return null;
    }
  }

  /// Search crops by name (supports both English and Arabic)
  Future<List<Map<String, dynamic>>> searchCrops(String query) async {
    try {
      final response = await _client.get(
        '/crops/search',
        queryParameters: {
          'q': query,
        },
      );

      if (response is List) {
        return List<Map<String, dynamic>>.from(response);
      }

      if (response is Map && response['data'] is List) {
        return List<Map<String, dynamic>>.from(response['data']);
      }

      return [];
    } catch (e) {
      AppLogger.e('Failed to search crops', tag: 'CropsApi', error: e);
      return [];
    }
  }
}
