/// SAHOOL Home Controller v16
/// متحكم الشاشة الرئيسية

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'home_state.dart';

final homeControllerProvider =
    StateNotifierProvider<HomeController, HomeState>((ref) {
  return HomeController();
});

class HomeController extends StateNotifier<HomeState> {
  HomeController() : super(HomeState.initial()) {
    load();
  }

  Future<void> load() async {
    try {
      state = state.copyWith(loading: true, error: null);

      // TODO: استبدل بـ API حقيقي
      await Future.delayed(const Duration(milliseconds: 500));

      state = state.copyWith(
        loading: false,
        ndviAvg: 0.63,
        alertsOpen: 3,
        weatherSummary: "صحو مع رياح خفيفة",
        tasksDue: 5,
        fieldsCount: 12,
        irrigationDue: 2.5,
      );
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
