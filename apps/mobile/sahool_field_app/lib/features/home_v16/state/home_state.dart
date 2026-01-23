/// SAHOOL Home State v16
/// حالة الشاشة الرئيسية

class HomeState {
  final bool loading;
  final String? error;

  final double ndviAvg;
  final int alertsOpen;
  final String weatherSummary;
  final int tasksDue;
  final int fieldsCount;
  final double irrigationDue;

  HomeState({
    required this.loading,
    this.error,
    required this.ndviAvg,
    required this.alertsOpen,
    required this.weatherSummary,
    required this.tasksDue,
    required this.fieldsCount,
    required this.irrigationDue,
  });

  factory HomeState.initial() => HomeState(
        loading: true,
        ndviAvg: 0.0,
        alertsOpen: 0,
        weatherSummary: "—",
        tasksDue: 0,
        fieldsCount: 0,
        irrigationDue: 0.0,
      );

  HomeState copyWith({
    bool? loading,
    String? error,
    double? ndviAvg,
    int? alertsOpen,
    String? weatherSummary,
    int? tasksDue,
    int? fieldsCount,
    double? irrigationDue,
  }) {
    return HomeState(
      loading: loading ?? this.loading,
      error: error,
      ndviAvg: ndviAvg ?? this.ndviAvg,
      alertsOpen: alertsOpen ?? this.alertsOpen,
      weatherSummary: weatherSummary ?? this.weatherSummary,
      tasksDue: tasksDue ?? this.tasksDue,
      fieldsCount: fieldsCount ?? this.fieldsCount,
      irrigationDue: irrigationDue ?? this.irrigationDue,
    );
  }

  bool get hasError => error != null;
  bool get isReady => !loading && !hasError;
}
