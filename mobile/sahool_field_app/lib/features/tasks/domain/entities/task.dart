/// Task Entity - Domain model for field tasks
class FieldTask {
  final String id;
  final String tenantId;
  final String fieldId;
  final String? farmId;
  final String title;
  final String? description;
  final TaskStatus status;
  final TaskPriority priority;
  final DateTime? dueDate;
  final String? assignedTo;
  final String? evidenceNotes;
  final List<String> evidencePhotos;
  final DateTime createdAt;
  final DateTime updatedAt;
  final bool synced;

  const FieldTask({
    required this.id,
    required this.tenantId,
    required this.fieldId,
    this.farmId,
    required this.title,
    this.description,
    this.status = TaskStatus.open,
    this.priority = TaskPriority.medium,
    this.dueDate,
    this.assignedTo,
    this.evidenceNotes,
    this.evidencePhotos = const [],
    required this.createdAt,
    required this.updatedAt,
    this.synced = false,
  });

  /// Create from database row
  factory FieldTask.fromDb(Map<String, dynamic> row) {
    return FieldTask(
      id: row['id'] as String,
      tenantId: row['tenant_id'] as String,
      fieldId: row['field_id'] as String,
      farmId: row['farm_id'] as String?,
      title: row['title'] as String,
      description: row['description'] as String?,
      status: TaskStatus.fromString(row['status'] as String? ?? 'open'),
      priority: TaskPriority.fromString(row['priority'] as String? ?? 'medium'),
      dueDate: row['due_date'] != null
          ? DateTime.parse(row['due_date'] as String)
          : null,
      assignedTo: row['assigned_to'] as String?,
      evidenceNotes: row['evidence_notes'] as String?,
      evidencePhotos: row['evidence_photos'] != null
          ? (row['evidence_photos'] as String).split(',')
          : [],
      createdAt: DateTime.parse(row['created_at'] as String),
      updatedAt: DateTime.parse(row['updated_at'] as String),
      synced: row['synced'] == 1 || row['synced'] == true,
    );
  }

  /// Create from API response
  factory FieldTask.fromJson(Map<String, dynamic> json) {
    return FieldTask(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      fieldId: json['field_id'] as String,
      farmId: json['farm_id'] as String?,
      title: json['title'] as String,
      description: json['description'] as String?,
      status: TaskStatus.fromString(json['status'] as String? ?? 'open'),
      priority: TaskPriority.fromString(json['priority'] as String? ?? 'medium'),
      dueDate: json['due_date'] != null
          ? DateTime.parse(json['due_date'] as String)
          : null,
      assignedTo: json['assigned_to'] as String?,
      evidenceNotes: json['evidence_notes'] as String?,
      evidencePhotos: json['evidence_photos'] != null
          ? List<String>.from(json['evidence_photos'] as List)
          : [],
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      synced: true,
    );
  }

  /// Convert to JSON for API
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'tenant_id': tenantId,
      'field_id': fieldId,
      'farm_id': farmId,
      'title': title,
      'description': description,
      'status': status.value,
      'priority': priority.value,
      'due_date': dueDate?.toIso8601String(),
      'assigned_to': assignedTo,
      'evidence_notes': evidenceNotes,
      'evidence_photos': evidencePhotos,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  /// Copy with new values
  FieldTask copyWith({
    String? id,
    String? tenantId,
    String? fieldId,
    String? farmId,
    String? title,
    String? description,
    TaskStatus? status,
    TaskPriority? priority,
    DateTime? dueDate,
    String? assignedTo,
    String? evidenceNotes,
    List<String>? evidencePhotos,
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? synced,
  }) {
    return FieldTask(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      fieldId: fieldId ?? this.fieldId,
      farmId: farmId ?? this.farmId,
      title: title ?? this.title,
      description: description ?? this.description,
      status: status ?? this.status,
      priority: priority ?? this.priority,
      dueDate: dueDate ?? this.dueDate,
      assignedTo: assignedTo ?? this.assignedTo,
      evidenceNotes: evidenceNotes ?? this.evidenceNotes,
      evidencePhotos: evidencePhotos ?? this.evidencePhotos,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      synced: synced ?? this.synced,
    );
  }

  /// Check if task is overdue
  bool get isOverdue {
    if (dueDate == null) return false;
    if (status == TaskStatus.done) return false;
    return dueDate!.isBefore(DateTime.now());
  }

  /// Check if task is due today
  bool get isDueToday {
    if (dueDate == null) return false;
    final now = DateTime.now();
    return dueDate!.year == now.year &&
        dueDate!.month == now.month &&
        dueDate!.day == now.day;
  }

  @override
  String toString() => 'FieldTask($id: $title)';
}

/// Task status enum
enum TaskStatus {
  open('open', 'مفتوحة'),
  inProgress('in_progress', 'قيد التنفيذ'),
  done('done', 'مكتملة'),
  cancelled('cancelled', 'ملغاة');

  final String value;
  final String arabicLabel;

  const TaskStatus(this.value, this.arabicLabel);

  static TaskStatus fromString(String value) {
    return TaskStatus.values.firstWhere(
      (s) => s.value == value,
      orElse: () => TaskStatus.open,
    );
  }
}

/// Task priority enum
enum TaskPriority {
  low('low', 'منخفضة'),
  medium('medium', 'متوسطة'),
  high('high', 'عالية'),
  urgent('urgent', 'عاجلة');

  final String value;
  final String arabicLabel;

  const TaskPriority(this.value, this.arabicLabel);

  static TaskPriority fromString(String value) {
    return TaskPriority.values.firstWhere(
      (p) => p.value == value,
      orElse: () => TaskPriority.medium,
    );
  }
}
