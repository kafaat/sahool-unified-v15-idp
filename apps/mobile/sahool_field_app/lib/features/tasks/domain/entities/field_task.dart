/// Field Task Domain Entity
/// كيان مهمة الحقل - Domain Layer نظيف (بدون Flutter)
///
/// يمثل المهام الزراعية المطلوبة للحقول

/// أنواع المهام الزراعية
enum TaskType {
  /// ري - سقاية المحاصيل
  irrigation,

  /// تسميد - إضافة الأسمدة
  fertilization,

  /// استكشاف - فحص الآفات والأمراض
  scouting,

  /// حصاد - جني المحاصيل
  harvest,

  /// أخرى - مهام متنوعة
  other,
}

/// أولوية المهمة
enum TaskPriority {
  /// عاجلة
  urgent,

  /// عالية
  high,

  /// عادية
  normal,

  /// منخفضة
  low,
}

/// كيان مهمة الحقل
class FieldTask {
  /// معرف فريد
  final String id;

  /// عنوان المهمة
  final String title;

  /// وصف تفصيلي (اختياري)
  final String? description;

  /// اسم الحقل المرتبط
  final String fieldName;

  /// معرف الحقل
  final String? fieldId;

  /// وقت الاستحقاق
  final DateTime dueTime;

  /// نوع المهمة
  final TaskType type;

  /// أولوية المهمة
  final TaskPriority priority;

  /// هل تم إكمالها؟
  bool isCompleted;

  /// وقت الإكمال
  DateTime? completedAt;

  /// ملاحظات إضافية
  final String? notes;

  FieldTask({
    required this.id,
    required this.title,
    this.description,
    required this.fieldName,
    this.fieldId,
    required this.dueTime,
    required this.type,
    this.priority = TaskPriority.normal,
    this.isCompleted = false,
    this.completedAt,
    this.notes,
  });

  /// هل المهمة متأخرة؟
  bool get isOverdue =>
      !isCompleted && dueTime.isBefore(DateTime.now());

  /// هل المهمة عاجلة؟
  bool get isUrgent => priority == TaskPriority.urgent;

  /// الوقت المتبقي (للعرض)
  Duration get timeRemaining => dueTime.difference(DateTime.now());

  /// إنشاء من JSON
  factory FieldTask.fromJson(Map<String, dynamic> json) {
    return FieldTask(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String?,
      fieldName: json['field_name'] as String,
      fieldId: json['field_id'] as String?,
      dueTime: DateTime.parse(json['due_time'] as String),
      type: TaskType.values.firstWhere(
        (t) => t.name == json['type'],
        orElse: () => TaskType.other,
      ),
      priority: TaskPriority.values.firstWhere(
        (p) => p.name == json['priority'],
        orElse: () => TaskPriority.normal,
      ),
      isCompleted: json['is_completed'] as bool? ?? false,
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'] as String)
          : null,
      notes: json['notes'] as String?,
    );
  }

  /// تحويل إلى JSON
  Map<String, dynamic> toJson() => {
        'id': id,
        'title': title,
        'description': description,
        'field_name': fieldName,
        'field_id': fieldId,
        'due_time': dueTime.toIso8601String(),
        'type': type.name,
        'priority': priority.name,
        'is_completed': isCompleted,
        'completed_at': completedAt?.toIso8601String(),
        'notes': notes,
      };

  /// نسخة معدلة
  FieldTask copyWith({
    String? id,
    String? title,
    String? description,
    String? fieldName,
    String? fieldId,
    DateTime? dueTime,
    TaskType? type,
    TaskPriority? priority,
    bool? isCompleted,
    DateTime? completedAt,
    String? notes,
  }) {
    return FieldTask(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      fieldName: fieldName ?? this.fieldName,
      fieldId: fieldId ?? this.fieldId,
      dueTime: dueTime ?? this.dueTime,
      type: type ?? this.type,
      priority: priority ?? this.priority,
      isCompleted: isCompleted ?? this.isCompleted,
      completedAt: completedAt ?? this.completedAt,
      notes: notes ?? this.notes,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FieldTask &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() =>
      'FieldTask($id: $title, ${type.name}, completed: $isCompleted)';
}
