/// Maintenance Record Models - نماذج سجل الصيانة
/// Maintenance tracking, scheduling, and history
library;

import 'package:flutter/foundation.dart';
import 'equipment_status.dart';

/// نوع الصيانة - Maintenance Type
enum MaintenanceType {
  oilChange('oil_change', 'تغيير زيت', 'Oil Change'),
  filterChange('filter_change', 'تغيير فلتر', 'Filter Change'),
  tireCheck('tire_check', 'فحص إطارات', 'Tire Check'),
  batteryCheck('battery_check', 'فحص بطارية', 'Battery Check'),
  calibration('calibration', 'معايرة', 'Calibration'),
  generalService('general_service', 'صيانة عامة', 'General Service'),
  repair('repair', 'إصلاح', 'Repair'),
  inspection('inspection', 'فحص', 'Inspection'),
  cleaning('cleaning', 'تنظيف', 'Cleaning'),
  partReplacement('part_replacement', 'استبدال قطع', 'Part Replacement'),
  softwareUpdate('software_update', 'تحديث برمجي', 'Software Update'),
  other('other', 'أخرى', 'Other');

  final String value;
  final String nameAr;
  final String nameEn;

  const MaintenanceType(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static MaintenanceType fromString(String value) {
    return MaintenanceType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => MaintenanceType.other,
    );
  }

  /// Get recommended interval in hours
  int? get recommendedIntervalHours {
    switch (this) {
      case MaintenanceType.oilChange:
        return 250;
      case MaintenanceType.filterChange:
        return 500;
      case MaintenanceType.tireCheck:
        return 100;
      case MaintenanceType.batteryCheck:
        return 200;
      case MaintenanceType.calibration:
        return 500;
      case MaintenanceType.generalService:
        return 500;
      case MaintenanceType.inspection:
        return 100;
      case MaintenanceType.cleaning:
        return 50;
      default:
        return null;
    }
  }
}

/// حالة الصيانة - Maintenance Status
enum MaintenanceStatus {
  scheduled('scheduled', 'مجدولة', 'Scheduled'),
  inProgress('in_progress', 'قيد التنفيذ', 'In Progress'),
  completed('completed', 'مكتملة', 'Completed'),
  cancelled('cancelled', 'ملغية', 'Cancelled'),
  overdue('overdue', 'متأخرة', 'Overdue');

  final String value;
  final String nameAr;
  final String nameEn;

  const MaintenanceStatus(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static MaintenanceStatus fromString(String value) {
    return MaintenanceStatus.values.firstWhere(
      (e) => e.value == value,
      orElse: () => MaintenanceStatus.scheduled,
    );
  }
}

/// سجل صيانة - Maintenance Record
@immutable
class MaintenanceRecord {
  final String recordId;
  final String equipmentId;
  final MaintenanceType maintenanceType;
  final MaintenanceStatus status;
  final String description;
  final String? descriptionAr;
  final String? performedBy;
  final double? cost;
  final String? currency;
  final String? notes;
  final String? notesAr;
  final List<String>? partsReplaced;
  final List<String>? partsReplacedAr;
  final double? hoursAtMaintenance;
  final DateTime? scheduledAt;
  final DateTime? performedAt;
  final DateTime? completedAt;
  final DateTime createdAt;
  final DateTime updatedAt;
  final List<String>? attachments;
  final Map<String, dynamic>? metadata;

  const MaintenanceRecord({
    required this.recordId,
    required this.equipmentId,
    required this.maintenanceType,
    this.status = MaintenanceStatus.completed,
    required this.description,
    this.descriptionAr,
    this.performedBy,
    this.cost,
    this.currency = 'SAR',
    this.notes,
    this.notesAr,
    this.partsReplaced,
    this.partsReplacedAr,
    this.hoursAtMaintenance,
    this.scheduledAt,
    this.performedAt,
    this.completedAt,
    required this.createdAt,
    required this.updatedAt,
    this.attachments,
    this.metadata,
  });

  String getDescription(String locale) {
    return locale == 'ar' && descriptionAr != null ? descriptionAr! : description;
  }

  String? getNotes(String locale) {
    if (notes == null && notesAr == null) return null;
    return locale == 'ar' && notesAr != null ? notesAr : notes;
  }

  List<String>? getPartsReplaced(String locale) {
    if (partsReplaced == null && partsReplacedAr == null) return null;
    return locale == 'ar' && partsReplacedAr != null
        ? partsReplacedAr
        : partsReplaced;
  }

  /// Get formatted cost string
  String get formattedCost {
    if (cost == null) return '-';
    return '${cost!.toStringAsFixed(2)} ${currency ?? 'SAR'}';
  }

  /// Check if maintenance is overdue
  bool get isOverdue {
    if (status == MaintenanceStatus.overdue) return true;
    if (status != MaintenanceStatus.scheduled) return false;
    if (scheduledAt == null) return false;
    return scheduledAt!.isBefore(DateTime.now());
  }

  /// Get duration if completed
  Duration? get duration {
    if (performedAt == null || completedAt == null) return null;
    return completedAt!.difference(performedAt!);
  }

  factory MaintenanceRecord.fromJson(Map<String, dynamic> json) {
    return MaintenanceRecord(
      recordId: json['record_id'] as String? ?? json['id'] as String? ?? '',
      equipmentId: json['equipment_id'] as String,
      maintenanceType:
          MaintenanceType.fromString(json['maintenance_type'] as String),
      status: json['status'] != null
          ? MaintenanceStatus.fromString(json['status'] as String)
          : MaintenanceStatus.completed,
      description: json['description'] as String,
      descriptionAr: json['description_ar'] as String?,
      performedBy: json['performed_by'] as String?,
      cost: (json['cost'] as num?)?.toDouble(),
      currency: json['currency'] as String? ?? 'SAR',
      notes: json['notes'] as String?,
      notesAr: json['notes_ar'] as String?,
      partsReplaced: json['parts_replaced'] != null
          ? List<String>.from(json['parts_replaced'] as List)
          : null,
      partsReplacedAr: json['parts_replaced_ar'] != null
          ? List<String>.from(json['parts_replaced_ar'] as List)
          : null,
      hoursAtMaintenance:
          (json['hours_at_maintenance'] as num?)?.toDouble(),
      scheduledAt: json['scheduled_at'] != null
          ? DateTime.parse(json['scheduled_at'] as String)
          : null,
      performedAt: json['performed_at'] != null
          ? DateTime.parse(json['performed_at'] as String)
          : (json['created_at'] != null
              ? DateTime.parse(json['created_at'] as String)
              : null),
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'] as String)
          : null,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : DateTime.parse(json['created_at'] as String),
      attachments: json['attachments'] != null
          ? List<String>.from(json['attachments'] as List)
          : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'record_id': recordId,
        'equipment_id': equipmentId,
        'maintenance_type': maintenanceType.value,
        'status': status.value,
        'description': description,
        'description_ar': descriptionAr,
        'performed_by': performedBy,
        'cost': cost,
        'currency': currency,
        'notes': notes,
        'notes_ar': notesAr,
        'parts_replaced': partsReplaced,
        'parts_replaced_ar': partsReplacedAr,
        'hours_at_maintenance': hoursAtMaintenance,
        'scheduled_at': scheduledAt?.toIso8601String(),
        'performed_at': performedAt?.toIso8601String(),
        'completed_at': completedAt?.toIso8601String(),
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
        'attachments': attachments,
        'metadata': metadata,
      };

  MaintenanceRecord copyWith({
    MaintenanceStatus? status,
    String? performedBy,
    double? cost,
    String? notes,
    String? notesAr,
    List<String>? partsReplaced,
    DateTime? performedAt,
    DateTime? completedAt,
    DateTime? updatedAt,
  }) {
    return MaintenanceRecord(
      recordId: recordId,
      equipmentId: equipmentId,
      maintenanceType: maintenanceType,
      status: status ?? this.status,
      description: description,
      descriptionAr: descriptionAr,
      performedBy: performedBy ?? this.performedBy,
      cost: cost ?? this.cost,
      currency: currency,
      notes: notes ?? this.notes,
      notesAr: notesAr ?? this.notesAr,
      partsReplaced: partsReplaced ?? this.partsReplaced,
      partsReplacedAr: partsReplacedAr,
      hoursAtMaintenance: hoursAtMaintenance,
      scheduledAt: scheduledAt,
      performedAt: performedAt ?? this.performedAt,
      completedAt: completedAt ?? this.completedAt,
      createdAt: createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      attachments: attachments,
      metadata: metadata,
    );
  }
}

/// صيانة مجدولة - Scheduled Maintenance
@immutable
class ScheduledMaintenance {
  final String scheduleId;
  final String equipmentId;
  final String equipmentName;
  final MaintenanceType maintenanceType;
  final MaintenancePriority priority;
  final String description;
  final String? descriptionAr;
  final DateTime scheduledDate;
  final double? scheduledAtHours;
  final bool isRecurring;
  final int? recurringIntervalDays;
  final int? recurringIntervalHours;
  final bool reminderSent;
  final DateTime? reminderSentAt;
  final DateTime createdAt;
  final String? createdBy;

  const ScheduledMaintenance({
    required this.scheduleId,
    required this.equipmentId,
    required this.equipmentName,
    required this.maintenanceType,
    required this.priority,
    required this.description,
    this.descriptionAr,
    required this.scheduledDate,
    this.scheduledAtHours,
    this.isRecurring = false,
    this.recurringIntervalDays,
    this.recurringIntervalHours,
    this.reminderSent = false,
    this.reminderSentAt,
    required this.createdAt,
    this.createdBy,
  });

  String getDescription(String locale) {
    return locale == 'ar' && descriptionAr != null ? descriptionAr! : description;
  }

  /// Days until scheduled
  int get daysUntil => scheduledDate.difference(DateTime.now()).inDays;

  /// Is overdue
  bool get isOverdue => scheduledDate.isBefore(DateTime.now());

  /// Is due soon (within 7 days)
  bool get isDueSoon => daysUntil <= 7 && daysUntil >= 0;

  factory ScheduledMaintenance.fromJson(Map<String, dynamic> json) {
    return ScheduledMaintenance(
      scheduleId: json['schedule_id'] as String,
      equipmentId: json['equipment_id'] as String,
      equipmentName: json['equipment_name'] as String,
      maintenanceType:
          MaintenanceType.fromString(json['maintenance_type'] as String),
      priority: MaintenancePriority.fromString(json['priority'] as String),
      description: json['description'] as String,
      descriptionAr: json['description_ar'] as String?,
      scheduledDate: DateTime.parse(json['scheduled_date'] as String),
      scheduledAtHours: (json['scheduled_at_hours'] as num?)?.toDouble(),
      isRecurring: json['is_recurring'] as bool? ?? false,
      recurringIntervalDays: json['recurring_interval_days'] as int?,
      recurringIntervalHours: json['recurring_interval_hours'] as int?,
      reminderSent: json['reminder_sent'] as bool? ?? false,
      reminderSentAt: json['reminder_sent_at'] != null
          ? DateTime.parse(json['reminder_sent_at'] as String)
          : null,
      createdAt: DateTime.parse(json['created_at'] as String),
      createdBy: json['created_by'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'schedule_id': scheduleId,
        'equipment_id': equipmentId,
        'equipment_name': equipmentName,
        'maintenance_type': maintenanceType.value,
        'priority': priority.value,
        'description': description,
        'description_ar': descriptionAr,
        'scheduled_date': scheduledDate.toIso8601String(),
        'scheduled_at_hours': scheduledAtHours,
        'is_recurring': isRecurring,
        'recurring_interval_days': recurringIntervalDays,
        'recurring_interval_hours': recurringIntervalHours,
        'reminder_sent': reminderSent,
        'reminder_sent_at': reminderSentAt?.toIso8601String(),
        'created_at': createdAt.toIso8601String(),
        'created_by': createdBy,
      };
}

/// تنبيه صيانة - Maintenance Alert
@immutable
class MaintenanceAlert {
  final String alertId;
  final String equipmentId;
  final String equipmentName;
  final MaintenanceType maintenanceType;
  final String description;
  final String? descriptionAr;
  final MaintenancePriority priority;
  final DateTime? dueAt;
  final double? dueHours;
  final bool isOverdue;
  final DateTime createdAt;

  const MaintenanceAlert({
    required this.alertId,
    required this.equipmentId,
    required this.equipmentName,
    required this.maintenanceType,
    required this.description,
    this.descriptionAr,
    required this.priority,
    this.dueAt,
    this.dueHours,
    required this.isOverdue,
    required this.createdAt,
  });

  String getDescription(String locale) {
    return locale == 'ar' && descriptionAr != null ? descriptionAr! : description;
  }

  /// Days until due or days overdue
  int? get daysRemaining {
    if (dueAt == null) return null;
    return dueAt!.difference(DateTime.now()).inDays;
  }

  factory MaintenanceAlert.fromJson(Map<String, dynamic> json) {
    return MaintenanceAlert(
      alertId: json['alert_id'] as String,
      equipmentId: json['equipment_id'] as String,
      equipmentName: json['equipment_name'] as String,
      maintenanceType:
          MaintenanceType.fromString(json['maintenance_type'] as String),
      description: json['description'] as String,
      descriptionAr: json['description_ar'] as String?,
      priority: MaintenancePriority.fromString(json['priority'] as String),
      dueAt: json['due_at'] != null
          ? DateTime.parse(json['due_at'] as String)
          : null,
      dueHours: (json['due_hours'] as num?)?.toDouble(),
      isOverdue: json['is_overdue'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'alert_id': alertId,
        'equipment_id': equipmentId,
        'equipment_name': equipmentName,
        'maintenance_type': maintenanceType.value,
        'description': description,
        'description_ar': descriptionAr,
        'priority': priority.value,
        'due_at': dueAt?.toIso8601String(),
        'due_hours': dueHours,
        'is_overdue': isOverdue,
        'created_at': createdAt.toIso8601String(),
      };
}
