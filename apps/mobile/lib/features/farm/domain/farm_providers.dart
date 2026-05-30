import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/di/providers.dart';
import '../data/farm_api.dart';
import '../data/farm_entity.dart';

/// Farm API provider
final farmApiProvider = Provider<FarmApi>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return FarmApi(apiClient);
});

/// Farms list provider — fetches all farms from the backend
/// Falls back to empty list on error (offline-first behavior)
final farmsListProvider = FutureProvider<List<FarmEntity>>((ref) async {
  final api = ref.watch(farmApiProvider);
  try {
    return await api.getFarms();
  } catch (_) {
    // Return empty list when offline or backend unavailable
    return [];
  }
});

/// Create farm provider — exposes the createFarm function
final createFarmProvider = Provider<Future<FarmEntity> Function(Map<String, dynamic>)>((ref) {
  final api = ref.watch(farmApiProvider);
  return api.createFarm;
});
