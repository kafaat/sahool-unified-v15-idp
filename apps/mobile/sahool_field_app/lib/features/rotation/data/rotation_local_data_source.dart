import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/rotation_models.dart';

/// Local data source for rotation plans with offline support
/// مصدر بيانات محلي لخطط التناوب مع دعم العمل دون اتصال
class RotationLocalDataSource {
  static const String _rotationPlansKey = 'rotation_plans';
  static const String _rotationHistoryKey = 'rotation_history';
  static const String _lastSyncKey = 'rotation_last_sync';
  static const String _pendingSyncKey = 'rotation_pending_sync';

  final SharedPreferences _prefs;

  RotationLocalDataSource(this._prefs);

  /// Get all cached rotation plans
  Future<Map<String, RotationPlan>> getAllRotationPlans() async {
    final jsonStr = _prefs.getString(_rotationPlansKey);
    if (jsonStr == null || jsonStr.isEmpty) {
      return {};
    }

    try {
      final Map<String, dynamic> json = jsonDecode(jsonStr);
      return json.map((key, value) =>
          MapEntry(key, RotationPlan.fromJson(value as Map<String, dynamic>)));
    } catch (e) {
      // If parsing fails, return empty map
      return {};
    }
  }

  /// Get rotation plan for a specific field
  Future<RotationPlan?> getRotationPlan(String fieldId) async {
    final plans = await getAllRotationPlans();
    return plans[fieldId];
  }

  /// Save rotation plan to local storage
  Future<void> saveRotationPlan(RotationPlan plan) async {
    final plans = await getAllRotationPlans();
    plans[plan.fieldId] = plan;

    final jsonMap = plans.map((key, value) => MapEntry(key, value.toJson()));
    await _prefs.setString(_rotationPlansKey, jsonEncode(jsonMap));

    // Mark as pending sync
    await _markPendingSync(plan.fieldId);
  }

  /// Delete rotation plan from local storage
  Future<void> deleteRotationPlan(String fieldId) async {
    final plans = await getAllRotationPlans();
    plans.remove(fieldId);

    final jsonMap = plans.map((key, value) => MapEntry(key, value.toJson()));
    await _prefs.setString(_rotationPlansKey, jsonEncode(jsonMap));
  }

  /// Get rotation history for a field
  Future<List<RotationHistoryEntry>> getRotationHistory(String fieldId) async {
    final jsonStr = _prefs.getString('${_rotationHistoryKey}_$fieldId');
    if (jsonStr == null || jsonStr.isEmpty) {
      return [];
    }

    try {
      final List<dynamic> jsonList = jsonDecode(jsonStr);
      return jsonList
          .map((e) => RotationHistoryEntry.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      return [];
    }
  }

  /// Add entry to rotation history
  Future<void> addRotationHistoryEntry(
      String fieldId, RotationHistoryEntry entry) async {
    final history = await getRotationHistory(fieldId);
    history.add(entry);

    // Keep only last 50 entries
    if (history.length > 50) {
      history.removeRange(0, history.length - 50);
    }

    final jsonList = history.map((e) => e.toJson()).toList();
    await _prefs.setString(
        '${_rotationHistoryKey}_$fieldId', jsonEncode(jsonList));
  }

  /// Get last sync timestamp
  Future<DateTime?> getLastSyncTime() async {
    final timestamp = _prefs.getInt(_lastSyncKey);
    if (timestamp == null) return null;
    return DateTime.fromMillisecondsSinceEpoch(timestamp);
  }

  /// Update last sync timestamp
  Future<void> updateLastSyncTime() async {
    await _prefs.setInt(_lastSyncKey, DateTime.now().millisecondsSinceEpoch);
  }

  /// Get field IDs pending sync
  Future<Set<String>> getPendingSyncFieldIds() async {
    final jsonStr = _prefs.getString(_pendingSyncKey);
    if (jsonStr == null || jsonStr.isEmpty) {
      return {};
    }
    try {
      final List<dynamic> list = jsonDecode(jsonStr);
      return list.cast<String>().toSet();
    } catch (e) {
      return {};
    }
  }

  /// Mark a field as pending sync
  Future<void> _markPendingSync(String fieldId) async {
    final pending = await getPendingSyncFieldIds();
    pending.add(fieldId);
    await _prefs.setString(_pendingSyncKey, jsonEncode(pending.toList()));
  }

  /// Clear pending sync for a field
  Future<void> clearPendingSync(String fieldId) async {
    final pending = await getPendingSyncFieldIds();
    pending.remove(fieldId);
    await _prefs.setString(_pendingSyncKey, jsonEncode(pending.toList()));
  }

  /// Clear all pending sync
  Future<void> clearAllPendingSync() async {
    await _prefs.remove(_pendingSyncKey);
  }

  /// Check if there are any pending syncs
  Future<bool> hasPendingSync() async {
    final pending = await getPendingSyncFieldIds();
    return pending.isNotEmpty;
  }

  /// Clear all local rotation data
  Future<void> clearAll() async {
    await _prefs.remove(_rotationPlansKey);
    await _prefs.remove(_lastSyncKey);
    await _prefs.remove(_pendingSyncKey);
    // Note: History keys are field-specific, so they won't be cleared here
  }

  /// Get crop recommendations cache
  Future<List<CropRecommendation>?> getCachedRecommendations(
      String fieldId, int year) async {
    final key = 'rotation_recommendations_${fieldId}_$year';
    final jsonStr = _prefs.getString(key);
    if (jsonStr == null || jsonStr.isEmpty) {
      return null;
    }

    try {
      final List<dynamic> jsonList = jsonDecode(jsonStr);
      return jsonList
          .map((e) => CropRecommendation.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      return null;
    }
  }

  /// Cache crop recommendations
  Future<void> cacheRecommendations(String fieldId, int year,
      List<CropRecommendation> recommendations) async {
    final key = 'rotation_recommendations_${fieldId}_$year';
    final jsonList = recommendations.map((e) => e.toJson()).toList();
    await _prefs.setString(key, jsonEncode(jsonList));
  }
}

/// Entry for rotation history tracking
class RotationHistoryEntry {
  final String fieldId;
  final String cropId;
  final String cropNameEn;
  final String cropNameAr;
  final int year;
  final String season;
  final DateTime plantingDate;
  final DateTime? harvestDate;
  final double? yieldAmount;
  final String? notes;
  final DateTime recordedAt;

  const RotationHistoryEntry({
    required this.fieldId,
    required this.cropId,
    required this.cropNameEn,
    required this.cropNameAr,
    required this.year,
    required this.season,
    required this.plantingDate,
    this.harvestDate,
    this.yieldAmount,
    this.notes,
    required this.recordedAt,
  });

  Map<String, dynamic> toJson() => {
        'fieldId': fieldId,
        'cropId': cropId,
        'cropNameEn': cropNameEn,
        'cropNameAr': cropNameAr,
        'year': year,
        'season': season,
        'plantingDate': plantingDate.toIso8601String(),
        'harvestDate': harvestDate?.toIso8601String(),
        'yieldAmount': yieldAmount,
        'notes': notes,
        'recordedAt': recordedAt.toIso8601String(),
      };

  factory RotationHistoryEntry.fromJson(Map<String, dynamic> json) =>
      RotationHistoryEntry(
        fieldId: json['fieldId'] as String,
        cropId: json['cropId'] as String,
        cropNameEn: json['cropNameEn'] as String,
        cropNameAr: json['cropNameAr'] as String,
        year: json['year'] as int,
        season: json['season'] as String,
        plantingDate: DateTime.parse(json['plantingDate'] as String),
        harvestDate: json['harvestDate'] != null
            ? DateTime.parse(json['harvestDate'] as String)
            : null,
        yieldAmount: (json['yieldAmount'] as num?)?.toDouble(),
        notes: json['notes'] as String?,
        recordedAt: DateTime.parse(json['recordedAt'] as String),
      );
}
