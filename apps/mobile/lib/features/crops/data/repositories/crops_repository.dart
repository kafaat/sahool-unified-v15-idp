import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

import '../../../../core/utils/app_logger.dart';
import '../models/crop_model.dart';
import '../remote/crops_api.dart';

/// Crops Repository - Offline-first data access with caching
/// مستودع المحاصيل - وصول للبيانات مع التخزين المؤقت
///
/// Handles:
/// - Fetching crops from API
/// - Local caching with SharedPreferences
/// - Cache invalidation after 24 hours
class CropsRepository {
  final CropsApi _api;
  final SharedPreferences _prefs;

  // Cache keys
  static const String _cacheKey = 'crops_cache';
  static const String _cacheTimestampKey = 'crops_cache_timestamp';
  static const Duration _cacheExpiry = Duration(hours: 24);

  // In-memory cache
  List<Crop>? _cachedCrops;

  CropsRepository({
    required CropsApi api,
    required SharedPreferences prefs,
  })  : _api = api,
        _prefs = prefs;

  /// Get all crops (with caching)
  ///
  /// 1. Returns from memory if available
  /// 2. Returns from SharedPreferences if cache is valid
  /// 3. Fetches from API and updates cache
  Future<List<Crop>> getAllCrops({bool forceRefresh = false}) async {
    // Return from memory cache if available and not force refresh
    if (!forceRefresh && _cachedCrops != null && _cachedCrops!.isNotEmpty) {
      AppLogger.d('Returning crops from memory cache', tag: 'CropsRepository');
      return _cachedCrops!;
    }

    // Check local cache
    if (!forceRefresh && await _isCacheValid()) {
      final cachedCrops = await _loadFromCache();
      if (cachedCrops != null && cachedCrops.isNotEmpty) {
        _cachedCrops = cachedCrops;
        AppLogger.d('Returning crops from local cache', tag: 'CropsRepository', data: {'count': cachedCrops.length});
        return cachedCrops;
      }
    }

    // Fetch from API
    try {
      AppLogger.i('Fetching crops from API...', tag: 'CropsRepository');
      final cropsJson = await _api.fetchAllCrops();
      final crops = cropsJson.map((json) => Crop.fromJson(json)).toList();

      // Update cache
      await _saveToCache(crops);
      _cachedCrops = crops;

      AppLogger.i('Fetched crops from API', tag: 'CropsRepository', data: {'count': crops.length});
      return crops;
    } catch (e) {
      AppLogger.e('Failed to fetch crops from API', tag: 'CropsRepository', error: e);

      // Try to return stale cache as fallback
      final cachedCrops = await _loadFromCache();
      if (cachedCrops != null && cachedCrops.isNotEmpty) {
        _cachedCrops = cachedCrops;
        AppLogger.w('Returning stale cached crops', tag: 'CropsRepository', data: {'count': cachedCrops.length});
        return cachedCrops;
      }

      // If all fails, return empty list
      AppLogger.w('No cached crops available, returning empty list', tag: 'CropsRepository');
      return [];
    }
  }

  /// Get crops by category
  Future<List<Crop>> getCropsByCategory(CropCategory category) async {
    final allCrops = await getAllCrops();
    return allCrops.where((crop) => crop.category == category).toList();
  }

  /// Get crop by code
  Future<Crop?> getCropByCode(String code) async {
    final allCrops = await getAllCrops();
    try {
      return allCrops.firstWhere((crop) => crop.code == code);
    } catch (e) {
      return null;
    }
  }

  /// Search crops by name (English or Arabic)
  Future<List<Crop>> searchCrops(String query) async {
    final allCrops = await getAllCrops();
    final queryLower = query.toLowerCase();
    return allCrops.where((crop) {
      return crop.nameEn.toLowerCase().contains(queryLower) ||
          crop.nameAr.contains(query);
    }).toList();
  }

  /// Refresh crops from API
  Future<List<Crop>> refreshCrops() async {
    return getAllCrops(forceRefresh: true);
  }

  /// Clear cache
  Future<void> clearCache() async {
    await _prefs.remove(_cacheKey);
    await _prefs.remove(_cacheTimestampKey);
    _cachedCrops = null;
    AppLogger.d('Crops cache cleared', tag: 'CropsRepository');
  }

  // ============================================================
  // Private Methods - Cache Management
  // ============================================================

  /// Check if cache is still valid
  Future<bool> _isCacheValid() async {
    final timestampStr = _prefs.getString(_cacheTimestampKey);
    if (timestampStr == null) return false;

    final timestamp = DateTime.tryParse(timestampStr);
    if (timestamp == null) return false;

    final age = DateTime.now().difference(timestamp);
    return age < _cacheExpiry;
  }

  /// Load crops from local cache
  Future<List<Crop>?> _loadFromCache() async {
    try {
      final cachedJson = _prefs.getString(_cacheKey);
      if (cachedJson == null) return null;

      final List<dynamic> decoded = jsonDecode(cachedJson);
      return decoded.map((json) => Crop.fromJson(json as Map<String, dynamic>)).toList();
    } catch (e) {
      AppLogger.e('Failed to load crops from cache', tag: 'CropsRepository', error: e);
      return null;
    }
  }

  /// Save crops to local cache
  Future<void> _saveToCache(List<Crop> crops) async {
    try {
      final cropsJson = crops.map((crop) => crop.toJson()).toList();
      final encoded = jsonEncode(cropsJson);

      await _prefs.setString(_cacheKey, encoded);
      await _prefs.setString(_cacheTimestampKey, DateTime.now().toIso8601String());

      AppLogger.d('Saved crops to cache', tag: 'CropsRepository', data: {'count': crops.length});
    } catch (e) {
      AppLogger.e('Failed to save crops to cache', tag: 'CropsRepository', error: e);
    }
  }

  /// Get cache statistics
  Future<Map<String, dynamic>> getCacheStats() async {
    final isValid = await _isCacheValid();
    final timestampStr = _prefs.getString(_cacheTimestampKey);
    final cachedCrops = await _loadFromCache();

    return {
      'is_valid': isValid,
      'cached_at': timestampStr,
      'count': cachedCrops?.length ?? 0,
      'in_memory': _cachedCrops != null,
    };
  }
}
