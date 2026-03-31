/// Report Filter Models - نماذج فلاتر التقارير
/// Filter configurations for report generation
library;

/// Date range preset - فترة زمنية مسبقة التحديد
enum DateRangePreset {
  /// Today - اليوم
  today,

  /// Yesterday - أمس
  yesterday,

  /// Last 7 days - آخر 7 أيام
  last7Days,

  /// Last 30 days - آخر 30 يوم
  last30Days,

  /// Last 90 days - آخر 90 يوم
  last90Days,

  /// This month - هذا الشهر
  thisMonth,

  /// Last month - الشهر الماضي
  lastMonth,

  /// This quarter - هذا الربع
  thisQuarter,

  /// This year - هذه السنة
  thisYear,

  /// Last year - السنة الماضية
  lastYear,

  /// Custom range - فترة مخصصة
  custom,

  /// All time - كل الوقت
  allTime,
}

/// Extension for date range preset
extension DateRangePresetX on DateRangePreset {
  /// Get display name (English)
  String get displayName {
    switch (this) {
      case DateRangePreset.today:
        return 'Today';
      case DateRangePreset.yesterday:
        return 'Yesterday';
      case DateRangePreset.last7Days:
        return 'Last 7 days';
      case DateRangePreset.last30Days:
        return 'Last 30 days';
      case DateRangePreset.last90Days:
        return 'Last 90 days';
      case DateRangePreset.thisMonth:
        return 'This month';
      case DateRangePreset.lastMonth:
        return 'Last month';
      case DateRangePreset.thisQuarter:
        return 'This quarter';
      case DateRangePreset.thisYear:
        return 'This year';
      case DateRangePreset.lastYear:
        return 'Last year';
      case DateRangePreset.custom:
        return 'Custom range';
      case DateRangePreset.allTime:
        return 'All time';
    }
  }

  /// Get display name (Arabic) - الاسم بالعربية
  String get displayNameAr {
    switch (this) {
      case DateRangePreset.today:
        return 'اليوم';
      case DateRangePreset.yesterday:
        return 'أمس';
      case DateRangePreset.last7Days:
        return 'آخر 7 أيام';
      case DateRangePreset.last30Days:
        return 'آخر 30 يوم';
      case DateRangePreset.last90Days:
        return 'آخر 90 يوم';
      case DateRangePreset.thisMonth:
        return 'هذا الشهر';
      case DateRangePreset.lastMonth:
        return 'الشهر الماضي';
      case DateRangePreset.thisQuarter:
        return 'هذا الربع';
      case DateRangePreset.thisYear:
        return 'هذه السنة';
      case DateRangePreset.lastYear:
        return 'السنة الماضية';
      case DateRangePreset.custom:
        return 'فترة مخصصة';
      case DateRangePreset.allTime:
        return 'كل الوقت';
    }
  }

  /// Calculate date range from preset
  DateRange toDateRange() {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);

    switch (this) {
      case DateRangePreset.today:
        return DateRange(
          start: today,
          end: today.add(const Duration(days: 1)).subtract(const Duration(milliseconds: 1)),
        );
      case DateRangePreset.yesterday:
        final yesterday = today.subtract(const Duration(days: 1));
        return DateRange(
          start: yesterday,
          end: today.subtract(const Duration(milliseconds: 1)),
        );
      case DateRangePreset.last7Days:
        return DateRange(
          start: today.subtract(const Duration(days: 6)),
          end: now,
        );
      case DateRangePreset.last30Days:
        return DateRange(
          start: today.subtract(const Duration(days: 29)),
          end: now,
        );
      case DateRangePreset.last90Days:
        return DateRange(
          start: today.subtract(const Duration(days: 89)),
          end: now,
        );
      case DateRangePreset.thisMonth:
        return DateRange(
          start: DateTime(now.year, now.month, 1),
          end: now,
        );
      case DateRangePreset.lastMonth:
        final lastMonth = DateTime(now.year, now.month - 1, 1);
        final lastDayOfLastMonth = DateTime(now.year, now.month, 0);
        return DateRange(
          start: lastMonth,
          end: lastDayOfLastMonth,
        );
      case DateRangePreset.thisQuarter:
        final quarterStart = DateTime(now.year, ((now.month - 1) ~/ 3) * 3 + 1, 1);
        return DateRange(
          start: quarterStart,
          end: now,
        );
      case DateRangePreset.thisYear:
        return DateRange(
          start: DateTime(now.year, 1, 1),
          end: now,
        );
      case DateRangePreset.lastYear:
        return DateRange(
          start: DateTime(now.year - 1, 1, 1),
          end: DateTime(now.year - 1, 12, 31, 23, 59, 59),
        );
      case DateRangePreset.custom:
        return DateRange(
          start: today.subtract(const Duration(days: 29)),
          end: now,
        );
      case DateRangePreset.allTime:
        return DateRange(
          start: DateTime(2020, 1, 1),
          end: now,
        );
    }
  }
}

/// Date range model - نطاق التاريخ
class DateRange {
  /// Start date
  final DateTime start;

  /// End date
  final DateTime end;

  const DateRange({
    required this.start,
    required this.end,
  });

  /// Number of days in range
  int get days => end.difference(start).inDays + 1;

  /// Is single day
  bool get isSingleDay => days == 1;

  /// Format as string
  String get formatted => '${_formatDate(start)} - ${_formatDate(end)}';

  /// Format as Arabic string
  String get formattedAr => '${_formatDateAr(start)} - ${_formatDateAr(end)}';

  String _formatDate(DateTime date) =>
      '${date.year}/${date.month.toString().padLeft(2, '0')}/${date.day.toString().padLeft(2, '0')}';

  String _formatDateAr(DateTime date) =>
      '${date.day}/${date.month}/${date.year}';

  factory DateRange.fromJson(Map<String, dynamic> json) {
    return DateRange(
      start: DateTime.tryParse(json['start'] as String) ?? DateTime.now(),
      end: DateTime.tryParse(json['end'] as String) ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() => {
        'start': start.toIso8601String(),
        'end': end.toIso8601String(),
      };

  DateRange copyWith({
    DateTime? start,
    DateTime? end,
  }) {
    return DateRange(
      start: start ?? this.start,
      end: end ?? this.end,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is DateRange &&
          runtimeType == other.runtimeType &&
          start == other.start &&
          end == other.end;

  @override
  int get hashCode => start.hashCode ^ end.hashCode;
}

/// Field filter item - عنصر فلتر الحقل
class FieldFilterItem {
  /// Field ID
  final String id;

  /// Field name
  final String name;

  /// Field name (Arabic)
  final String? nameAr;

  /// Is selected
  final bool isSelected;

  const FieldFilterItem({
    required this.id,
    required this.name,
    this.nameAr,
    this.isSelected = false,
  });

  factory FieldFilterItem.fromJson(Map<String, dynamic> json) {
    return FieldFilterItem(
      id: json['id'] as String,
      name: json['name'] as String,
      nameAr: json['name_ar'] as String?,
      isSelected: json['is_selected'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'name_ar': nameAr,
        'is_selected': isSelected,
      };

  FieldFilterItem copyWith({
    String? id,
    String? name,
    String? nameAr,
    bool? isSelected,
  }) {
    return FieldFilterItem(
      id: id ?? this.id,
      name: name ?? this.name,
      nameAr: nameAr ?? this.nameAr,
      isSelected: isSelected ?? this.isSelected,
    );
  }
}

/// Farm filter item - عنصر فلتر المزرعة
class FarmFilterItem {
  /// Farm ID
  final String id;

  /// Farm name
  final String name;

  /// Farm name (Arabic)
  final String? nameAr;

  /// Is selected
  final bool isSelected;

  /// Number of fields
  final int fieldCount;

  const FarmFilterItem({
    required this.id,
    required this.name,
    this.nameAr,
    this.isSelected = false,
    this.fieldCount = 0,
  });

  factory FarmFilterItem.fromJson(Map<String, dynamic> json) {
    return FarmFilterItem(
      id: json['id'] as String,
      name: json['name'] as String,
      nameAr: json['name_ar'] as String?,
      isSelected: json['is_selected'] as bool? ?? false,
      fieldCount: json['field_count'] as int? ?? 0,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'name_ar': nameAr,
        'is_selected': isSelected,
        'field_count': fieldCount,
      };

  FarmFilterItem copyWith({
    String? id,
    String? name,
    String? nameAr,
    bool? isSelected,
    int? fieldCount,
  }) {
    return FarmFilterItem(
      id: id ?? this.id,
      name: name ?? this.name,
      nameAr: nameAr ?? this.nameAr,
      isSelected: isSelected ?? this.isSelected,
      fieldCount: fieldCount ?? this.fieldCount,
    );
  }
}

/// Report filter model - نموذج فلتر التقرير
class ReportFilter {
  /// Date range preset
  final DateRangePreset dateRangePreset;

  /// Custom date range (when preset is custom)
  final DateRange dateRange;

  /// Selected field IDs
  final List<String> fieldIds;

  /// Selected farm IDs
  final List<String> farmIds;

  /// Crop type filter
  final String? cropType;

  /// Task type filter
  final String? taskType;

  /// Assignee filter (for task reports)
  final String? assigneeId;

  /// Compare with previous period
  final bool compareWithPrevious;

  /// Group by option
  final String? groupBy;

  /// Sort by option
  final String? sortBy;

  /// Sort ascending
  final bool sortAscending;

  /// Custom parameters
  final Map<String, dynamic> customParams;

  const ReportFilter({
    this.dateRangePreset = DateRangePreset.last30Days,
    required this.dateRange,
    this.fieldIds = const [],
    this.farmIds = const [],
    this.cropType,
    this.taskType,
    this.assigneeId,
    this.compareWithPrevious = false,
    this.groupBy,
    this.sortBy,
    this.sortAscending = true,
    this.customParams = const {},
  });

  /// Create default filter
  factory ReportFilter.defaults() {
    return ReportFilter(
      dateRangePreset: DateRangePreset.last30Days,
      dateRange: DateRangePreset.last30Days.toDateRange(),
    );
  }

  /// Has any filter applied
  bool get hasFilters =>
      fieldIds.isNotEmpty ||
      farmIds.isNotEmpty ||
      cropType != null ||
      taskType != null ||
      assigneeId != null;

  /// Number of active filters
  int get activeFilterCount {
    int count = 0;
    if (fieldIds.isNotEmpty) count++;
    if (farmIds.isNotEmpty) count++;
    if (cropType != null) count++;
    if (taskType != null) count++;
    if (assigneeId != null) count++;
    return count;
  }

  factory ReportFilter.fromJson(Map<String, dynamic> json) {
    return ReportFilter(
      dateRangePreset: DateRangePreset.values.firstWhere(
        (e) => e.name == json['date_range_preset'],
        orElse: () => DateRangePreset.last30Days,
      ),
      dateRange: DateRange.fromJson(json['date_range'] as Map<String, dynamic>),
      fieldIds: (json['field_ids'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      farmIds: (json['farm_ids'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      cropType: json['crop_type'] as String?,
      taskType: json['task_type'] as String?,
      assigneeId: json['assignee_id'] as String?,
      compareWithPrevious: json['compare_with_previous'] as bool? ?? false,
      groupBy: json['group_by'] as String?,
      sortBy: json['sort_by'] as String?,
      sortAscending: json['sort_ascending'] as bool? ?? true,
      customParams:
          json['custom_params'] as Map<String, dynamic>? ?? {},
    );
  }

  Map<String, dynamic> toJson() => {
        'date_range_preset': dateRangePreset.name,
        'date_range': dateRange.toJson(),
        'field_ids': fieldIds,
        'farm_ids': farmIds,
        'crop_type': cropType,
        'task_type': taskType,
        'assignee_id': assigneeId,
        'compare_with_previous': compareWithPrevious,
        'group_by': groupBy,
        'sort_by': sortBy,
        'sort_ascending': sortAscending,
        'custom_params': customParams,
      };

  ReportFilter copyWith({
    DateRangePreset? dateRangePreset,
    DateRange? dateRange,
    List<String>? fieldIds,
    List<String>? farmIds,
    String? cropType,
    String? taskType,
    String? assigneeId,
    bool? compareWithPrevious,
    String? groupBy,
    String? sortBy,
    bool? sortAscending,
    Map<String, dynamic>? customParams,
  }) {
    return ReportFilter(
      dateRangePreset: dateRangePreset ?? this.dateRangePreset,
      dateRange: dateRange ?? this.dateRange,
      fieldIds: fieldIds ?? this.fieldIds,
      farmIds: farmIds ?? this.farmIds,
      cropType: cropType ?? this.cropType,
      taskType: taskType ?? this.taskType,
      assigneeId: assigneeId ?? this.assigneeId,
      compareWithPrevious: compareWithPrevious ?? this.compareWithPrevious,
      groupBy: groupBy ?? this.groupBy,
      sortBy: sortBy ?? this.sortBy,
      sortAscending: sortAscending ?? this.sortAscending,
      customParams: customParams ?? this.customParams,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ReportFilter &&
          runtimeType == other.runtimeType &&
          dateRangePreset == other.dateRangePreset &&
          dateRange == other.dateRange;

  @override
  int get hashCode => dateRangePreset.hashCode ^ dateRange.hashCode;
}
