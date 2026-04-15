/// Research domain models
/// نماذج مجال البحث العلمي

enum ExperimentStatus {
  draft,
  active,
  paused,
  completed,
  locked,
}

class Experiment {
  final String id;
  final String title;
  final String titleEn;
  final ExperimentStatus status;
  final int plotsCount;
  final DateTime startDate;
  final String principalResearcher;
  final double progress;

  Experiment({
    required this.id,
    required this.title,
    required this.titleEn,
    required this.status,
    required this.plotsCount,
    required this.startDate,
    required this.principalResearcher,
    required this.progress,
  });

  factory Experiment.fromJson(Map<String, dynamic> json) {
    return Experiment(
      id: json['id'] as String,
      title: json['title'] as String? ?? '',
      titleEn: json['titleEn'] as String? ?? json['title'] as String? ?? '',
      status: _parseStatus(json['status'] as String?),
      plotsCount: json['plotsCount'] as int? ?? 0,
      startDate: json['startDate'] != null
          ? DateTime.tryParse(json['startDate'] as String) ?? DateTime.now()
          : DateTime.now(),
      principalResearcher: json['principalResearcher'] as String? ?? '',
      progress: (json['progress'] as num?)?.toDouble() ?? 0.0,
    );
  }

  static ExperimentStatus _parseStatus(String? status) {
    switch (status?.toLowerCase()) {
      case 'active':
        return ExperimentStatus.active;
      case 'paused':
        return ExperimentStatus.paused;
      case 'completed':
        return ExperimentStatus.completed;
      case 'locked':
        return ExperimentStatus.locked;
      default:
        return ExperimentStatus.draft;
    }
  }
}
