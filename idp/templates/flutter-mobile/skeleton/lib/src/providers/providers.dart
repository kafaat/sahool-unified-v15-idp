/// Riverpod providers for ${{ values.name }} module
/// مزودات Riverpod لوحدة ${{ values.name }}

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

{%- if values.has_api_integration %}
import '../services/api_service.dart';
{%- endif %}
{%- if values.has_offline_support %}
import '../database/database.dart';
{%- endif %}

part 'providers.g.dart';

{%- if values.has_api_integration %}
/// API Service Provider
/// مزود خدمة API
@riverpod
${{ values.name | pascal_case }}ApiService apiService(Ref ref) {
  return ${{ values.name | pascal_case }}ApiService();
}
{%- endif %}

{%- if values.has_offline_support %}
/// Database Provider
/// مزود قاعدة البيانات
@riverpod
${{ values.name | pascal_case }}Database database(Ref ref) {
  return ${{ values.name | pascal_case }}Database();
}

/// Sync Status Provider
/// مزود حالة المزامنة
@riverpod
class SyncStatus extends _$SyncStatus {
  @override
  AsyncValue<bool> build() => const AsyncValue.data(true);

  Future<void> sync() async {
    state = const AsyncValue.loading();
    try {
      // Implement sync logic
      state = const AsyncValue.data(true);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}
{%- endif %}

/// Module State Provider
/// مزود حالة الوحدة
@riverpod
class ${{ values.name | pascal_case }}State extends _$${{ values.name | pascal_case }}State {
  @override
  FutureOr<Map<String, dynamic>> build() async {
    return {
      'initialized': true,
      'module': '${{ values.name }}',
      'layer': '${{ values.layer }}',
    };
  }
}
