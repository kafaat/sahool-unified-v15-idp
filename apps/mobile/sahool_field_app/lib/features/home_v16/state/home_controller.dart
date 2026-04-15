library;

/// SAHOOL Home Controller v16
/// متحكم الشاشة الرئيسية

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/di/providers.dart';
import '../../../core/http/api_client.dart';
import '../data/home_api.dart';
import 'home_state.dart';

/// Home API Provider
final homeApiProvider = Provider<HomeApi>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return HomeApi(apiClient);
});

final homeControllerProvider =
    StateNotifierProvider<HomeController, HomeState>((ref) {
  final homeApi = ref.watch(homeApiProvider);
  final apiClient = ref.watch(apiClientProvider);
  return HomeController(homeApi: homeApi, tenantId: apiClient.tenantId);
});

class HomeController extends StateNotifier<HomeState> {
  final HomeApi _homeApi;
  final String _tenantId;

  HomeController({
    required HomeApi homeApi,
    required String tenantId,
  })  : _homeApi = homeApi,
        _tenantId = tenantId,
        super(HomeState.initial()) {
    load();
  }

  Future<void> load() async {
    try {
      state = state.copyWith(loading: true, error: null);

      final summary = await _homeApi.fetchDashboardSummary(
        tenantId: _tenantId,
      );

      state = state.copyWith(
        loading: false,
        ndviAvg: summary.ndviAvg,
        alertsOpen: summary.alertsOpen,
        weatherSummary: summary.weatherSummary,
        tasksDue: summary.tasksDue,
        fieldsCount: summary.fieldsCount,
        irrigationDue: summary.irrigationDue,
      );
    } on ApiException catch (e) {
      state = state.copyWith(loading: false, error: e.message);
    } catch (e) {
      state = state.copyWith(loading: false, error: e.toString());
    }
  }

  Future<void> refresh() async {
    await load();
  }

  void setNdviAvg(double value) {
    state = state.copyWith(ndviAvg: value);
  }

  void setAlertsOpen(int count) {
    state = state.copyWith(alertsOpen: count);
  }

  void setWeatherSummary(String summary) {
    state = state.copyWith(weatherSummary: summary);
  }

  void setTasksDue(int count) {
    state = state.copyWith(tasksDue: count);
  }
}
