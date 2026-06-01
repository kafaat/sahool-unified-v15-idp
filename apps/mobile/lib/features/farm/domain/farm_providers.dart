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
final farmsListProvider = FutureProvider<List<FarmEntity>>((ref) async {
  final api = ref.watch(farmApiProvider);
  return api.getFarms();
});

/// Create farm provider — exposes the createFarm function
final createFarmProvider = Provider<Future<FarmEntity> Function(Map<String, dynamic>)>((ref) {
  final api = ref.watch(farmApiProvider);
  return api.createFarm;
});
