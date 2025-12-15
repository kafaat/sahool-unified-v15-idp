// GENERATED CODE - DO NOT MODIFY BY HAND
// Run: dart run build_runner build --delete-conflicting-outputs

part of 'database.dart';

// **************************************************************************
// DriftDatabaseGenerator
// **************************************************************************

class Task extends DataClass implements Insertable<Task> {
  final String id;
  final String tenantId;
  final String fieldId;
  final String? farmId;
  final String title;
  final String? description;
  final String status;
  final String priority;
  final DateTime? dueDate;
  final String? assignedTo;
  final String? evidenceNotes;
  final String? evidencePhotos;
  final DateTime createdAt;
  final DateTime updatedAt;
  final bool synced;

  const Task({
    required this.id,
    required this.tenantId,
    required this.fieldId,
    this.farmId,
    required this.title,
    this.description,
    required this.status,
    required this.priority,
    this.dueDate,
    this.assignedTo,
    this.evidenceNotes,
    this.evidencePhotos,
    required this.createdAt,
    required this.updatedAt,
    required this.synced,
  });

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['tenant_id'] = Variable<String>(tenantId);
    map['field_id'] = Variable<String>(fieldId);
    if (!nullToAbsent || farmId != null) {
      map['farm_id'] = Variable<String>(farmId);
    }
    map['title'] = Variable<String>(title);
    if (!nullToAbsent || description != null) {
      map['description'] = Variable<String>(description);
    }
    map['status'] = Variable<String>(status);
    map['priority'] = Variable<String>(priority);
    if (!nullToAbsent || dueDate != null) {
      map['due_date'] = Variable<DateTime>(dueDate);
    }
    if (!nullToAbsent || assignedTo != null) {
      map['assigned_to'] = Variable<String>(assignedTo);
    }
    if (!nullToAbsent || evidenceNotes != null) {
      map['evidence_notes'] = Variable<String>(evidenceNotes);
    }
    if (!nullToAbsent || evidencePhotos != null) {
      map['evidence_photos'] = Variable<String>(evidencePhotos);
    }
    map['created_at'] = Variable<DateTime>(createdAt);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    map['synced'] = Variable<bool>(synced);
    return map;
  }

  TasksCompanion toCompanion(bool nullToAbsent) {
    return TasksCompanion(
      id: Value(id),
      tenantId: Value(tenantId),
      fieldId: Value(fieldId),
      farmId: farmId == null && nullToAbsent ? const Value.absent() : Value(farmId),
      title: Value(title),
      description: description == null && nullToAbsent ? const Value.absent() : Value(description),
      status: Value(status),
      priority: Value(priority),
      dueDate: dueDate == null && nullToAbsent ? const Value.absent() : Value(dueDate),
      assignedTo: assignedTo == null && nullToAbsent ? const Value.absent() : Value(assignedTo),
      evidenceNotes: evidenceNotes == null && nullToAbsent ? const Value.absent() : Value(evidenceNotes),
      evidencePhotos: evidencePhotos == null && nullToAbsent ? const Value.absent() : Value(evidencePhotos),
      createdAt: Value(createdAt),
      updatedAt: Value(updatedAt),
      synced: Value(synced),
    );
  }

  factory Task.fromJson(Map<String, dynamic> json, {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Task(
      id: serializer.fromJson<String>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenantId']),
      fieldId: serializer.fromJson<String>(json['fieldId']),
      farmId: serializer.fromJson<String?>(json['farmId']),
      title: serializer.fromJson<String>(json['title']),
      description: serializer.fromJson<String?>(json['description']),
      status: serializer.fromJson<String>(json['status']),
      priority: serializer.fromJson<String>(json['priority']),
      dueDate: serializer.fromJson<DateTime?>(json['dueDate']),
      assignedTo: serializer.fromJson<String?>(json['assignedTo']),
      evidenceNotes: serializer.fromJson<String?>(json['evidenceNotes']),
      evidencePhotos: serializer.fromJson<String?>(json['evidencePhotos']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
      synced: serializer.fromJson<bool>(json['synced']),
    );
  }

  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'tenantId': serializer.toJson<String>(tenantId),
      'fieldId': serializer.toJson<String>(fieldId),
      'farmId': serializer.toJson<String?>(farmId),
      'title': serializer.toJson<String>(title),
      'description': serializer.toJson<String?>(description),
      'status': serializer.toJson<String>(status),
      'priority': serializer.toJson<String>(priority),
      'dueDate': serializer.toJson<DateTime?>(dueDate),
      'assignedTo': serializer.toJson<String?>(assignedTo),
      'evidenceNotes': serializer.toJson<String?>(evidenceNotes),
      'evidencePhotos': serializer.toJson<String?>(evidencePhotos),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
      'synced': serializer.toJson<bool>(synced),
    };
  }

  Task copyWith({
    String? id,
    String? tenantId,
    String? fieldId,
    Value<String?> farmId = const Value.absent(),
    String? title,
    Value<String?> description = const Value.absent(),
    String? status,
    String? priority,
    Value<DateTime?> dueDate = const Value.absent(),
    Value<String?> assignedTo = const Value.absent(),
    Value<String?> evidenceNotes = const Value.absent(),
    Value<String?> evidencePhotos = const Value.absent(),
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? synced,
  }) =>
      Task(
        id: id ?? this.id,
        tenantId: tenantId ?? this.tenantId,
        fieldId: fieldId ?? this.fieldId,
        farmId: farmId.present ? farmId.value : this.farmId,
        title: title ?? this.title,
        description: description.present ? description.value : this.description,
        status: status ?? this.status,
        priority: priority ?? this.priority,
        dueDate: dueDate.present ? dueDate.value : this.dueDate,
        assignedTo: assignedTo.present ? assignedTo.value : this.assignedTo,
        evidenceNotes: evidenceNotes.present ? evidenceNotes.value : this.evidenceNotes,
        evidencePhotos: evidencePhotos.present ? evidencePhotos.value : this.evidencePhotos,
        createdAt: createdAt ?? this.createdAt,
        updatedAt: updatedAt ?? this.updatedAt,
        synced: synced ?? this.synced,
      );

  @override
  String toString() {
    return 'Task(id: $id, title: $title, status: $status)';
  }

  @override
  int get hashCode => Object.hash(id, tenantId, fieldId, farmId, title, description, status, priority, dueDate, assignedTo, evidenceNotes, evidencePhotos, createdAt, updatedAt, synced);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Task &&
          other.id == id &&
          other.tenantId == tenantId &&
          other.fieldId == fieldId &&
          other.farmId == farmId &&
          other.title == title &&
          other.description == description &&
          other.status == status &&
          other.priority == priority &&
          other.dueDate == dueDate &&
          other.assignedTo == assignedTo &&
          other.evidenceNotes == evidenceNotes &&
          other.evidencePhotos == evidencePhotos &&
          other.createdAt == createdAt &&
          other.updatedAt == updatedAt &&
          other.synced == synced);
}

class TasksCompanion extends UpdateCompanion<Task> {
  final Value<String> id;
  final Value<String> tenantId;
  final Value<String> fieldId;
  final Value<String?> farmId;
  final Value<String> title;
  final Value<String?> description;
  final Value<String> status;
  final Value<String> priority;
  final Value<DateTime?> dueDate;
  final Value<String?> assignedTo;
  final Value<String?> evidenceNotes;
  final Value<String?> evidencePhotos;
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;
  final Value<bool> synced;

  const TasksCompanion({
    this.id = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.fieldId = const Value.absent(),
    this.farmId = const Value.absent(),
    this.title = const Value.absent(),
    this.description = const Value.absent(),
    this.status = const Value.absent(),
    this.priority = const Value.absent(),
    this.dueDate = const Value.absent(),
    this.assignedTo = const Value.absent(),
    this.evidenceNotes = const Value.absent(),
    this.evidencePhotos = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.synced = const Value.absent(),
  });

  TasksCompanion.insert({
    required String id,
    required String tenantId,
    required String fieldId,
    this.farmId = const Value.absent(),
    required String title,
    this.description = const Value.absent(),
    this.status = const Value.absent(),
    this.priority = const Value.absent(),
    this.dueDate = const Value.absent(),
    this.assignedTo = const Value.absent(),
    this.evidenceNotes = const Value.absent(),
    this.evidencePhotos = const Value.absent(),
    required DateTime createdAt,
    required DateTime updatedAt,
    this.synced = const Value.absent(),
  })  : id = Value(id),
        tenantId = Value(tenantId),
        fieldId = Value(fieldId),
        title = Value(title),
        createdAt = Value(createdAt),
        updatedAt = Value(updatedAt);

  static Insertable<Task> custom({
    Expression<String>? id,
    Expression<String>? tenantId,
    Expression<String>? fieldId,
    Expression<String>? farmId,
    Expression<String>? title,
    Expression<String>? description,
    Expression<String>? status,
    Expression<String>? priority,
    Expression<DateTime>? dueDate,
    Expression<String>? assignedTo,
    Expression<String>? evidenceNotes,
    Expression<String>? evidencePhotos,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<bool>? synced,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (tenantId != null) 'tenant_id': tenantId,
      if (fieldId != null) 'field_id': fieldId,
      if (farmId != null) 'farm_id': farmId,
      if (title != null) 'title': title,
      if (description != null) 'description': description,
      if (status != null) 'status': status,
      if (priority != null) 'priority': priority,
      if (dueDate != null) 'due_date': dueDate,
      if (assignedTo != null) 'assigned_to': assignedTo,
      if (evidenceNotes != null) 'evidence_notes': evidenceNotes,
      if (evidencePhotos != null) 'evidence_photos': evidencePhotos,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (synced != null) 'synced': synced,
    });
  }

  TasksCompanion copyWith({
    Value<String>? id,
    Value<String>? tenantId,
    Value<String>? fieldId,
    Value<String?>? farmId,
    Value<String>? title,
    Value<String?>? description,
    Value<String>? status,
    Value<String>? priority,
    Value<DateTime?>? dueDate,
    Value<String?>? assignedTo,
    Value<String?>? evidenceNotes,
    Value<String?>? evidencePhotos,
    Value<DateTime>? createdAt,
    Value<DateTime>? updatedAt,
    Value<bool>? synced,
  }) {
    return TasksCompanion(
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

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) map['id'] = Variable<String>(id.value);
    if (tenantId.present) map['tenant_id'] = Variable<String>(tenantId.value);
    if (fieldId.present) map['field_id'] = Variable<String>(fieldId.value);
    if (farmId.present) map['farm_id'] = Variable<String>(farmId.value);
    if (title.present) map['title'] = Variable<String>(title.value);
    if (description.present) map['description'] = Variable<String>(description.value);
    if (status.present) map['status'] = Variable<String>(status.value);
    if (priority.present) map['priority'] = Variable<String>(priority.value);
    if (dueDate.present) map['due_date'] = Variable<DateTime>(dueDate.value);
    if (assignedTo.present) map['assigned_to'] = Variable<String>(assignedTo.value);
    if (evidenceNotes.present) map['evidence_notes'] = Variable<String>(evidenceNotes.value);
    if (evidencePhotos.present) map['evidence_photos'] = Variable<String>(evidencePhotos.value);
    if (createdAt.present) map['created_at'] = Variable<DateTime>(createdAt.value);
    if (updatedAt.present) map['updated_at'] = Variable<DateTime>(updatedAt.value);
    if (synced.present) map['synced'] = Variable<bool>(synced.value);
    return map;
  }

  @override
  String toString() {
    return 'TasksCompanion(id: $id, tenantId: $tenantId, fieldId: $fieldId, farmId: $farmId, title: $title, description: $description, status: $status, priority: $priority, dueDate: $dueDate, assignedTo: $assignedTo, evidenceNotes: $evidenceNotes, evidencePhotos: $evidencePhotos, createdAt: $createdAt, updatedAt: $updatedAt, synced: $synced)';
  }
}

class $TasksTable extends Tasks with TableInfo<$TasksTable, Task> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;

  $TasksTable(this.attachedDatabase, [this._alias]);

  static const VerificationMeta _idMeta = VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>('id', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _tenantIdMeta = VerificationMeta('tenantId');
  @override
  late final GeneratedColumn<String> tenantId = GeneratedColumn<String>('tenant_id', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _fieldIdMeta = VerificationMeta('fieldId');
  @override
  late final GeneratedColumn<String> fieldId = GeneratedColumn<String>('field_id', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _farmIdMeta = VerificationMeta('farmId');
  @override
  late final GeneratedColumn<String> farmId = GeneratedColumn<String>('farm_id', aliasedName, true, type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _titleMeta = VerificationMeta('title');
  @override
  late final GeneratedColumn<String> title = GeneratedColumn<String>('title', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _descriptionMeta = VerificationMeta('description');
  @override
  late final GeneratedColumn<String> description = GeneratedColumn<String>('description', aliasedName, true, type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _statusMeta = VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status = GeneratedColumn<String>('status', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: false, defaultValue: const Constant('open'));

  static const VerificationMeta _priorityMeta = VerificationMeta('priority');
  @override
  late final GeneratedColumn<String> priority = GeneratedColumn<String>('priority', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: false, defaultValue: const Constant('medium'));

  static const VerificationMeta _dueDateMeta = VerificationMeta('dueDate');
  @override
  late final GeneratedColumn<DateTime> dueDate = GeneratedColumn<DateTime>('due_date', aliasedName, true, type: DriftSqlType.dateTime, requiredDuringInsert: false);

  static const VerificationMeta _assignedToMeta = VerificationMeta('assignedTo');
  @override
  late final GeneratedColumn<String> assignedTo = GeneratedColumn<String>('assigned_to', aliasedName, true, type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _evidenceNotesMeta = VerificationMeta('evidenceNotes');
  @override
  late final GeneratedColumn<String> evidenceNotes = GeneratedColumn<String>('evidence_notes', aliasedName, true, type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _evidencePhotosMeta = VerificationMeta('evidencePhotos');
  @override
  late final GeneratedColumn<String> evidencePhotos = GeneratedColumn<String>('evidence_photos', aliasedName, true, type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _createdAtMeta = VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>('created_at', aliasedName, false, type: DriftSqlType.dateTime, requiredDuringInsert: true);

  static const VerificationMeta _updatedAtMeta = VerificationMeta('updatedAt');
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>('updated_at', aliasedName, false, type: DriftSqlType.dateTime, requiredDuringInsert: true);

  static const VerificationMeta _syncedMeta = VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>('synced', aliasedName, false, type: DriftSqlType.bool, requiredDuringInsert: false, defaultConstraints: GeneratedColumn.constraintIsAlways('CHECK ("synced" IN (0, 1))'), defaultValue: const Constant(false));

  @override
  List<GeneratedColumn> get $columns => [id, tenantId, fieldId, farmId, title, description, status, priority, dueDate, assignedTo, evidenceNotes, evidencePhotos, createdAt, updatedAt, synced];

  @override
  String get aliasedName => _alias ?? actualTableName;

  @override
  String get actualTableName => $name;
  static const String $name = 'tasks';

  @override
  VerificationContext validateIntegrity(Insertable<Task> instance, {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('tenant_id')) {
      context.handle(_tenantIdMeta, tenantId.isAcceptableOrUnknown(data['tenant_id']!, _tenantIdMeta));
    } else if (isInserting) {
      context.missing(_tenantIdMeta);
    }
    if (data.containsKey('field_id')) {
      context.handle(_fieldIdMeta, fieldId.isAcceptableOrUnknown(data['field_id']!, _fieldIdMeta));
    } else if (isInserting) {
      context.missing(_fieldIdMeta);
    }
    if (data.containsKey('farm_id')) {
      context.handle(_farmIdMeta, farmId.isAcceptableOrUnknown(data['farm_id']!, _farmIdMeta));
    }
    if (data.containsKey('title')) {
      context.handle(_titleMeta, title.isAcceptableOrUnknown(data['title']!, _titleMeta));
    } else if (isInserting) {
      context.missing(_titleMeta);
    }
    if (data.containsKey('description')) {
      context.handle(_descriptionMeta, description.isAcceptableOrUnknown(data['description']!, _descriptionMeta));
    }
    if (data.containsKey('status')) {
      context.handle(_statusMeta, status.isAcceptableOrUnknown(data['status']!, _statusMeta));
    }
    if (data.containsKey('priority')) {
      context.handle(_priorityMeta, priority.isAcceptableOrUnknown(data['priority']!, _priorityMeta));
    }
    if (data.containsKey('due_date')) {
      context.handle(_dueDateMeta, dueDate.isAcceptableOrUnknown(data['due_date']!, _dueDateMeta));
    }
    if (data.containsKey('assigned_to')) {
      context.handle(_assignedToMeta, assignedTo.isAcceptableOrUnknown(data['assigned_to']!, _assignedToMeta));
    }
    if (data.containsKey('evidence_notes')) {
      context.handle(_evidenceNotesMeta, evidenceNotes.isAcceptableOrUnknown(data['evidence_notes']!, _evidenceNotesMeta));
    }
    if (data.containsKey('evidence_photos')) {
      context.handle(_evidencePhotosMeta, evidencePhotos.isAcceptableOrUnknown(data['evidence_photos']!, _evidencePhotosMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta, createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    } else if (isInserting) {
      context.missing(_createdAtMeta);
    }
    if (data.containsKey('updated_at')) {
      context.handle(_updatedAtMeta, updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta));
    } else if (isInserting) {
      context.missing(_updatedAtMeta);
    }
    if (data.containsKey('synced')) {
      context.handle(_syncedMeta, synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};

  @override
  Task map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Task(
      id: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      tenantId: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}tenant_id'])!,
      fieldId: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}field_id'])!,
      farmId: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}farm_id']),
      title: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}title'])!,
      description: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}description']),
      status: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}status'])!,
      priority: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}priority'])!,
      dueDate: attachedDatabase.typeMapping.read(DriftSqlType.dateTime, data['${effectivePrefix}due_date']),
      assignedTo: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}assigned_to']),
      evidenceNotes: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}evidence_notes']),
      evidencePhotos: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}evidence_photos']),
      createdAt: attachedDatabase.typeMapping.read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
      updatedAt: attachedDatabase.typeMapping.read(DriftSqlType.dateTime, data['${effectivePrefix}updated_at'])!,
      synced: attachedDatabase.typeMapping.read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
    );
  }

  @override
  $TasksTable createAlias(String alias) {
    return $TasksTable(attachedDatabase, alias);
  }
}

// ============================================================
// Outbox Table
// ============================================================

class OutboxData extends DataClass implements Insertable<OutboxData> {
  final String id;
  final String type;
  final String payloadJson;
  final DateTime createdAt;
  final int retryCount;
  final bool completed;

  const OutboxData({
    required this.id,
    required this.type,
    required this.payloadJson,
    required this.createdAt,
    required this.retryCount,
    required this.completed,
  });

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['type'] = Variable<String>(type);
    map['payload_json'] = Variable<String>(payloadJson);
    map['created_at'] = Variable<DateTime>(createdAt);
    map['retry_count'] = Variable<int>(retryCount);
    map['completed'] = Variable<bool>(completed);
    return map;
  }

  OutboxCompanion toCompanion(bool nullToAbsent) {
    return OutboxCompanion(
      id: Value(id),
      type: Value(type),
      payloadJson: Value(payloadJson),
      createdAt: Value(createdAt),
      retryCount: Value(retryCount),
      completed: Value(completed),
    );
  }

  factory OutboxData.fromJson(Map<String, dynamic> json, {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return OutboxData(
      id: serializer.fromJson<String>(json['id']),
      type: serializer.fromJson<String>(json['type']),
      payloadJson: serializer.fromJson<String>(json['payloadJson']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      retryCount: serializer.fromJson<int>(json['retryCount']),
      completed: serializer.fromJson<bool>(json['completed']),
    );
  }

  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'type': serializer.toJson<String>(type),
      'payloadJson': serializer.toJson<String>(payloadJson),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'retryCount': serializer.toJson<int>(retryCount),
      'completed': serializer.toJson<bool>(completed),
    };
  }

  OutboxData copyWith({
    String? id,
    String? type,
    String? payloadJson,
    DateTime? createdAt,
    int? retryCount,
    bool? completed,
  }) =>
      OutboxData(
        id: id ?? this.id,
        type: type ?? this.type,
        payloadJson: payloadJson ?? this.payloadJson,
        createdAt: createdAt ?? this.createdAt,
        retryCount: retryCount ?? this.retryCount,
        completed: completed ?? this.completed,
      );

  @override
  String toString() {
    return 'OutboxData(id: $id, type: $type, completed: $completed)';
  }

  @override
  int get hashCode => Object.hash(id, type, payloadJson, createdAt, retryCount, completed);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is OutboxData &&
          other.id == id &&
          other.type == type &&
          other.payloadJson == payloadJson &&
          other.createdAt == createdAt &&
          other.retryCount == retryCount &&
          other.completed == completed);
}

class OutboxCompanion extends UpdateCompanion<OutboxData> {
  final Value<String> id;
  final Value<String> type;
  final Value<String> payloadJson;
  final Value<DateTime> createdAt;
  final Value<int> retryCount;
  final Value<bool> completed;

  const OutboxCompanion({
    this.id = const Value.absent(),
    this.type = const Value.absent(),
    this.payloadJson = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.retryCount = const Value.absent(),
    this.completed = const Value.absent(),
  });

  OutboxCompanion.insert({
    required String id,
    required String type,
    required String payloadJson,
    required DateTime createdAt,
    this.retryCount = const Value.absent(),
    this.completed = const Value.absent(),
  })  : id = Value(id),
        type = Value(type),
        payloadJson = Value(payloadJson),
        createdAt = Value(createdAt);

  static Insertable<OutboxData> custom({
    Expression<String>? id,
    Expression<String>? type,
    Expression<String>? payloadJson,
    Expression<DateTime>? createdAt,
    Expression<int>? retryCount,
    Expression<bool>? completed,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (type != null) 'type': type,
      if (payloadJson != null) 'payload_json': payloadJson,
      if (createdAt != null) 'created_at': createdAt,
      if (retryCount != null) 'retry_count': retryCount,
      if (completed != null) 'completed': completed,
    });
  }

  OutboxCompanion copyWith({
    Value<String>? id,
    Value<String>? type,
    Value<String>? payloadJson,
    Value<DateTime>? createdAt,
    Value<int>? retryCount,
    Value<bool>? completed,
  }) {
    return OutboxCompanion(
      id: id ?? this.id,
      type: type ?? this.type,
      payloadJson: payloadJson ?? this.payloadJson,
      createdAt: createdAt ?? this.createdAt,
      retryCount: retryCount ?? this.retryCount,
      completed: completed ?? this.completed,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) map['id'] = Variable<String>(id.value);
    if (type.present) map['type'] = Variable<String>(type.value);
    if (payloadJson.present) map['payload_json'] = Variable<String>(payloadJson.value);
    if (createdAt.present) map['created_at'] = Variable<DateTime>(createdAt.value);
    if (retryCount.present) map['retry_count'] = Variable<int>(retryCount.value);
    if (completed.present) map['completed'] = Variable<bool>(completed.value);
    return map;
  }

  @override
  String toString() {
    return 'OutboxCompanion(id: $id, type: $type, payloadJson: $payloadJson, createdAt: $createdAt, retryCount: $retryCount, completed: $completed)';
  }
}

class $OutboxTable extends Outbox with TableInfo<$OutboxTable, OutboxData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;

  $OutboxTable(this.attachedDatabase, [this._alias]);

  static const VerificationMeta _idMeta = VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>('id', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _typeMeta = VerificationMeta('type');
  @override
  late final GeneratedColumn<String> type = GeneratedColumn<String>('type', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _payloadJsonMeta = VerificationMeta('payloadJson');
  @override
  late final GeneratedColumn<String> payloadJson = GeneratedColumn<String>('payload_json', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _createdAtMeta = VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>('created_at', aliasedName, false, type: DriftSqlType.dateTime, requiredDuringInsert: true);

  static const VerificationMeta _retryCountMeta = VerificationMeta('retryCount');
  @override
  late final GeneratedColumn<int> retryCount = GeneratedColumn<int>('retry_count', aliasedName, false, type: DriftSqlType.int, requiredDuringInsert: false, defaultValue: const Constant(0));

  static const VerificationMeta _completedMeta = VerificationMeta('completed');
  @override
  late final GeneratedColumn<bool> completed = GeneratedColumn<bool>('completed', aliasedName, false, type: DriftSqlType.bool, requiredDuringInsert: false, defaultConstraints: GeneratedColumn.constraintIsAlways('CHECK ("completed" IN (0, 1))'), defaultValue: const Constant(false));

  @override
  List<GeneratedColumn> get $columns => [id, type, payloadJson, createdAt, retryCount, completed];

  @override
  String get aliasedName => _alias ?? actualTableName;

  @override
  String get actualTableName => $name;
  static const String $name = 'outbox';

  @override
  VerificationContext validateIntegrity(Insertable<OutboxData> instance, {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('type')) {
      context.handle(_typeMeta, type.isAcceptableOrUnknown(data['type']!, _typeMeta));
    } else if (isInserting) {
      context.missing(_typeMeta);
    }
    if (data.containsKey('payload_json')) {
      context.handle(_payloadJsonMeta, payloadJson.isAcceptableOrUnknown(data['payload_json']!, _payloadJsonMeta));
    } else if (isInserting) {
      context.missing(_payloadJsonMeta);
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta, createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    } else if (isInserting) {
      context.missing(_createdAtMeta);
    }
    if (data.containsKey('retry_count')) {
      context.handle(_retryCountMeta, retryCount.isAcceptableOrUnknown(data['retry_count']!, _retryCountMeta));
    }
    if (data.containsKey('completed')) {
      context.handle(_completedMeta, completed.isAcceptableOrUnknown(data['completed']!, _completedMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};

  @override
  OutboxData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return OutboxData(
      id: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      type: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}type'])!,
      payloadJson: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}payload_json'])!,
      createdAt: attachedDatabase.typeMapping.read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
      retryCount: attachedDatabase.typeMapping.read(DriftSqlType.int, data['${effectivePrefix}retry_count'])!,
      completed: attachedDatabase.typeMapping.read(DriftSqlType.bool, data['${effectivePrefix}completed'])!,
    );
  }

  @override
  $OutboxTable createAlias(String alias) {
    return $OutboxTable(attachedDatabase, alias);
  }
}

// ============================================================
// Fields Table
// ============================================================

class Field extends DataClass implements Insertable<Field> {
  final String id;
  final String tenantId;
  final String? farmId;
  final String name;
  final double? areaHectares;
  final String? cropType;
  final String? status;
  final double? ndviCurrent;
  final DateTime lastUpdated;

  const Field({
    required this.id,
    required this.tenantId,
    this.farmId,
    required this.name,
    this.areaHectares,
    this.cropType,
    this.status,
    this.ndviCurrent,
    required this.lastUpdated,
  });

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['tenant_id'] = Variable<String>(tenantId);
    if (!nullToAbsent || farmId != null) {
      map['farm_id'] = Variable<String>(farmId);
    }
    map['name'] = Variable<String>(name);
    if (!nullToAbsent || areaHectares != null) {
      map['area_hectares'] = Variable<double>(areaHectares);
    }
    if (!nullToAbsent || cropType != null) {
      map['crop_type'] = Variable<String>(cropType);
    }
    if (!nullToAbsent || status != null) {
      map['status'] = Variable<String>(status);
    }
    if (!nullToAbsent || ndviCurrent != null) {
      map['ndvi_current'] = Variable<double>(ndviCurrent);
    }
    map['last_updated'] = Variable<DateTime>(lastUpdated);
    return map;
  }

  FieldsCompanion toCompanion(bool nullToAbsent) {
    return FieldsCompanion(
      id: Value(id),
      tenantId: Value(tenantId),
      farmId: farmId == null && nullToAbsent ? const Value.absent() : Value(farmId),
      name: Value(name),
      areaHectares: areaHectares == null && nullToAbsent ? const Value.absent() : Value(areaHectares),
      cropType: cropType == null && nullToAbsent ? const Value.absent() : Value(cropType),
      status: status == null && nullToAbsent ? const Value.absent() : Value(status),
      ndviCurrent: ndviCurrent == null && nullToAbsent ? const Value.absent() : Value(ndviCurrent),
      lastUpdated: Value(lastUpdated),
    );
  }

  factory Field.fromJson(Map<String, dynamic> json, {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Field(
      id: serializer.fromJson<String>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenantId']),
      farmId: serializer.fromJson<String?>(json['farmId']),
      name: serializer.fromJson<String>(json['name']),
      areaHectares: serializer.fromJson<double?>(json['areaHectares']),
      cropType: serializer.fromJson<String?>(json['cropType']),
      status: serializer.fromJson<String?>(json['status']),
      ndviCurrent: serializer.fromJson<double?>(json['ndviCurrent']),
      lastUpdated: serializer.fromJson<DateTime>(json['lastUpdated']),
    );
  }

  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'tenantId': serializer.toJson<String>(tenantId),
      'farmId': serializer.toJson<String?>(farmId),
      'name': serializer.toJson<String>(name),
      'areaHectares': serializer.toJson<double?>(areaHectares),
      'cropType': serializer.toJson<String?>(cropType),
      'status': serializer.toJson<String?>(status),
      'ndviCurrent': serializer.toJson<double?>(ndviCurrent),
      'lastUpdated': serializer.toJson<DateTime>(lastUpdated),
    };
  }

  Field copyWith({
    String? id,
    String? tenantId,
    Value<String?> farmId = const Value.absent(),
    String? name,
    Value<double?> areaHectares = const Value.absent(),
    Value<String?> cropType = const Value.absent(),
    Value<String?> status = const Value.absent(),
    Value<double?> ndviCurrent = const Value.absent(),
    DateTime? lastUpdated,
  }) =>
      Field(
        id: id ?? this.id,
        tenantId: tenantId ?? this.tenantId,
        farmId: farmId.present ? farmId.value : this.farmId,
        name: name ?? this.name,
        areaHectares: areaHectares.present ? areaHectares.value : this.areaHectares,
        cropType: cropType.present ? cropType.value : this.cropType,
        status: status.present ? status.value : this.status,
        ndviCurrent: ndviCurrent.present ? ndviCurrent.value : this.ndviCurrent,
        lastUpdated: lastUpdated ?? this.lastUpdated,
      );

  @override
  String toString() {
    return 'Field(id: $id, name: $name, cropType: $cropType)';
  }

  @override
  int get hashCode => Object.hash(id, tenantId, farmId, name, areaHectares, cropType, status, ndviCurrent, lastUpdated);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Field &&
          other.id == id &&
          other.tenantId == tenantId &&
          other.farmId == farmId &&
          other.name == name &&
          other.areaHectares == areaHectares &&
          other.cropType == cropType &&
          other.status == status &&
          other.ndviCurrent == ndviCurrent &&
          other.lastUpdated == lastUpdated);
}

class FieldsCompanion extends UpdateCompanion<Field> {
  final Value<String> id;
  final Value<String> tenantId;
  final Value<String?> farmId;
  final Value<String> name;
  final Value<double?> areaHectares;
  final Value<String?> cropType;
  final Value<String?> status;
  final Value<double?> ndviCurrent;
  final Value<DateTime> lastUpdated;

  const FieldsCompanion({
    this.id = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.farmId = const Value.absent(),
    this.name = const Value.absent(),
    this.areaHectares = const Value.absent(),
    this.cropType = const Value.absent(),
    this.status = const Value.absent(),
    this.ndviCurrent = const Value.absent(),
    this.lastUpdated = const Value.absent(),
  });

  FieldsCompanion.insert({
    required String id,
    required String tenantId,
    this.farmId = const Value.absent(),
    required String name,
    this.areaHectares = const Value.absent(),
    this.cropType = const Value.absent(),
    this.status = const Value.absent(),
    this.ndviCurrent = const Value.absent(),
    required DateTime lastUpdated,
  })  : id = Value(id),
        tenantId = Value(tenantId),
        name = Value(name),
        lastUpdated = Value(lastUpdated);

  static Insertable<Field> custom({
    Expression<String>? id,
    Expression<String>? tenantId,
    Expression<String>? farmId,
    Expression<String>? name,
    Expression<double>? areaHectares,
    Expression<String>? cropType,
    Expression<String>? status,
    Expression<double>? ndviCurrent,
    Expression<DateTime>? lastUpdated,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (tenantId != null) 'tenant_id': tenantId,
      if (farmId != null) 'farm_id': farmId,
      if (name != null) 'name': name,
      if (areaHectares != null) 'area_hectares': areaHectares,
      if (cropType != null) 'crop_type': cropType,
      if (status != null) 'status': status,
      if (ndviCurrent != null) 'ndvi_current': ndviCurrent,
      if (lastUpdated != null) 'last_updated': lastUpdated,
    });
  }

  FieldsCompanion copyWith({
    Value<String>? id,
    Value<String>? tenantId,
    Value<String?>? farmId,
    Value<String>? name,
    Value<double?>? areaHectares,
    Value<String?>? cropType,
    Value<String?>? status,
    Value<double?>? ndviCurrent,
    Value<DateTime>? lastUpdated,
  }) {
    return FieldsCompanion(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      farmId: farmId ?? this.farmId,
      name: name ?? this.name,
      areaHectares: areaHectares ?? this.areaHectares,
      cropType: cropType ?? this.cropType,
      status: status ?? this.status,
      ndviCurrent: ndviCurrent ?? this.ndviCurrent,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) map['id'] = Variable<String>(id.value);
    if (tenantId.present) map['tenant_id'] = Variable<String>(tenantId.value);
    if (farmId.present) map['farm_id'] = Variable<String>(farmId.value);
    if (name.present) map['name'] = Variable<String>(name.value);
    if (areaHectares.present) map['area_hectares'] = Variable<double>(areaHectares.value);
    if (cropType.present) map['crop_type'] = Variable<String>(cropType.value);
    if (status.present) map['status'] = Variable<String>(status.value);
    if (ndviCurrent.present) map['ndvi_current'] = Variable<double>(ndviCurrent.value);
    if (lastUpdated.present) map['last_updated'] = Variable<DateTime>(lastUpdated.value);
    return map;
  }

  @override
  String toString() {
    return 'FieldsCompanion(id: $id, tenantId: $tenantId, farmId: $farmId, name: $name, areaHectares: $areaHectares, cropType: $cropType, status: $status, ndviCurrent: $ndviCurrent, lastUpdated: $lastUpdated)';
  }
}

class $FieldsTable extends Fields with TableInfo<$FieldsTable, Field> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;

  $FieldsTable(this.attachedDatabase, [this._alias]);

  static const VerificationMeta _idMeta = VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>('id', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _tenantIdMeta = VerificationMeta('tenantId');
  @override
  late final GeneratedColumn<String> tenantId = GeneratedColumn<String>('tenant_id', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _farmIdMeta = VerificationMeta('farmId');
  @override
  late final GeneratedColumn<String> farmId = GeneratedColumn<String>('farm_id', aliasedName, true, type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _nameMeta = VerificationMeta('name');
  @override
  late final GeneratedColumn<String> name = GeneratedColumn<String>('name', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _areaHectaresMeta = VerificationMeta('areaHectares');
  @override
  late final GeneratedColumn<double> areaHectares = GeneratedColumn<double>('area_hectares', aliasedName, true, type: DriftSqlType.double, requiredDuringInsert: false);

  static const VerificationMeta _cropTypeMeta = VerificationMeta('cropType');
  @override
  late final GeneratedColumn<String> cropType = GeneratedColumn<String>('crop_type', aliasedName, true, type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _statusMeta = VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status = GeneratedColumn<String>('status', aliasedName, true, type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _ndviCurrentMeta = VerificationMeta('ndviCurrent');
  @override
  late final GeneratedColumn<double> ndviCurrent = GeneratedColumn<double>('ndvi_current', aliasedName, true, type: DriftSqlType.double, requiredDuringInsert: false);

  static const VerificationMeta _lastUpdatedMeta = VerificationMeta('lastUpdated');
  @override
  late final GeneratedColumn<DateTime> lastUpdated = GeneratedColumn<DateTime>('last_updated', aliasedName, false, type: DriftSqlType.dateTime, requiredDuringInsert: true);

  @override
  List<GeneratedColumn> get $columns => [id, tenantId, farmId, name, areaHectares, cropType, status, ndviCurrent, lastUpdated];

  @override
  String get aliasedName => _alias ?? actualTableName;

  @override
  String get actualTableName => $name;
  static const String $name = 'fields';

  @override
  VerificationContext validateIntegrity(Insertable<Field> instance, {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('tenant_id')) {
      context.handle(_tenantIdMeta, tenantId.isAcceptableOrUnknown(data['tenant_id']!, _tenantIdMeta));
    } else if (isInserting) {
      context.missing(_tenantIdMeta);
    }
    if (data.containsKey('farm_id')) {
      context.handle(_farmIdMeta, farmId.isAcceptableOrUnknown(data['farm_id']!, _farmIdMeta));
    }
    if (data.containsKey('name')) {
      context.handle(_nameMeta, name.isAcceptableOrUnknown(data['name']!, _nameMeta));
    } else if (isInserting) {
      context.missing(_nameMeta);
    }
    if (data.containsKey('area_hectares')) {
      context.handle(_areaHectaresMeta, areaHectares.isAcceptableOrUnknown(data['area_hectares']!, _areaHectaresMeta));
    }
    if (data.containsKey('crop_type')) {
      context.handle(_cropTypeMeta, cropType.isAcceptableOrUnknown(data['crop_type']!, _cropTypeMeta));
    }
    if (data.containsKey('status')) {
      context.handle(_statusMeta, status.isAcceptableOrUnknown(data['status']!, _statusMeta));
    }
    if (data.containsKey('ndvi_current')) {
      context.handle(_ndviCurrentMeta, ndviCurrent.isAcceptableOrUnknown(data['ndvi_current']!, _ndviCurrentMeta));
    }
    if (data.containsKey('last_updated')) {
      context.handle(_lastUpdatedMeta, lastUpdated.isAcceptableOrUnknown(data['last_updated']!, _lastUpdatedMeta));
    } else if (isInserting) {
      context.missing(_lastUpdatedMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};

  @override
  Field map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Field(
      id: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      tenantId: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}tenant_id'])!,
      farmId: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}farm_id']),
      name: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}name'])!,
      areaHectares: attachedDatabase.typeMapping.read(DriftSqlType.double, data['${effectivePrefix}area_hectares']),
      cropType: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}crop_type']),
      status: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}status']),
      ndviCurrent: attachedDatabase.typeMapping.read(DriftSqlType.double, data['${effectivePrefix}ndvi_current']),
      lastUpdated: attachedDatabase.typeMapping.read(DriftSqlType.dateTime, data['${effectivePrefix}last_updated'])!,
    );
  }

  @override
  $FieldsTable createAlias(String alias) {
    return $FieldsTable(attachedDatabase, alias);
  }
}

// ============================================================
// SyncLogs Table
// ============================================================

class SyncLog extends DataClass implements Insertable<SyncLog> {
  final int id;
  final String type;
  final String status;
  final String? message;
  final DateTime timestamp;

  const SyncLog({
    required this.id,
    required this.type,
    required this.status,
    this.message,
    required this.timestamp,
  });

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['type'] = Variable<String>(type);
    map['status'] = Variable<String>(status);
    if (!nullToAbsent || message != null) {
      map['message'] = Variable<String>(message);
    }
    map['timestamp'] = Variable<DateTime>(timestamp);
    return map;
  }

  SyncLogsCompanion toCompanion(bool nullToAbsent) {
    return SyncLogsCompanion(
      id: Value(id),
      type: Value(type),
      status: Value(status),
      message: message == null && nullToAbsent ? const Value.absent() : Value(message),
      timestamp: Value(timestamp),
    );
  }

  factory SyncLog.fromJson(Map<String, dynamic> json, {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SyncLog(
      id: serializer.fromJson<int>(json['id']),
      type: serializer.fromJson<String>(json['type']),
      status: serializer.fromJson<String>(json['status']),
      message: serializer.fromJson<String?>(json['message']),
      timestamp: serializer.fromJson<DateTime>(json['timestamp']),
    );
  }

  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'type': serializer.toJson<String>(type),
      'status': serializer.toJson<String>(status),
      'message': serializer.toJson<String?>(message),
      'timestamp': serializer.toJson<DateTime>(timestamp),
    };
  }

  SyncLog copyWith({
    int? id,
    String? type,
    String? status,
    Value<String?> message = const Value.absent(),
    DateTime? timestamp,
  }) =>
      SyncLog(
        id: id ?? this.id,
        type: type ?? this.type,
        status: status ?? this.status,
        message: message.present ? message.value : this.message,
        timestamp: timestamp ?? this.timestamp,
      );

  @override
  String toString() {
    return 'SyncLog(id: $id, type: $type, status: $status)';
  }

  @override
  int get hashCode => Object.hash(id, type, status, message, timestamp);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is SyncLog &&
          other.id == id &&
          other.type == type &&
          other.status == status &&
          other.message == message &&
          other.timestamp == timestamp);
}

class SyncLogsCompanion extends UpdateCompanion<SyncLog> {
  final Value<int> id;
  final Value<String> type;
  final Value<String> status;
  final Value<String?> message;
  final Value<DateTime> timestamp;

  const SyncLogsCompanion({
    this.id = const Value.absent(),
    this.type = const Value.absent(),
    this.status = const Value.absent(),
    this.message = const Value.absent(),
    this.timestamp = const Value.absent(),
  });

  SyncLogsCompanion.insert({
    this.id = const Value.absent(),
    required String type,
    required String status,
    this.message = const Value.absent(),
    required DateTime timestamp,
  })  : type = Value(type),
        status = Value(status),
        timestamp = Value(timestamp);

  static Insertable<SyncLog> custom({
    Expression<int>? id,
    Expression<String>? type,
    Expression<String>? status,
    Expression<String>? message,
    Expression<DateTime>? timestamp,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (type != null) 'type': type,
      if (status != null) 'status': status,
      if (message != null) 'message': message,
      if (timestamp != null) 'timestamp': timestamp,
    });
  }

  SyncLogsCompanion copyWith({
    Value<int>? id,
    Value<String>? type,
    Value<String>? status,
    Value<String?>? message,
    Value<DateTime>? timestamp,
  }) {
    return SyncLogsCompanion(
      id: id ?? this.id,
      type: type ?? this.type,
      status: status ?? this.status,
      message: message ?? this.message,
      timestamp: timestamp ?? this.timestamp,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) map['id'] = Variable<int>(id.value);
    if (type.present) map['type'] = Variable<String>(type.value);
    if (status.present) map['status'] = Variable<String>(status.value);
    if (message.present) map['message'] = Variable<String>(message.value);
    if (timestamp.present) map['timestamp'] = Variable<DateTime>(timestamp.value);
    return map;
  }

  @override
  String toString() {
    return 'SyncLogsCompanion(id: $id, type: $type, status: $status, message: $message, timestamp: $timestamp)';
  }
}

class $SyncLogsTable extends SyncLogs with TableInfo<$SyncLogsTable, SyncLog> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;

  $SyncLogsTable(this.attachedDatabase, [this._alias]);

  static const VerificationMeta _idMeta = VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>('id', aliasedName, false, hasAutoIncrement: true, type: DriftSqlType.int, requiredDuringInsert: false, defaultConstraints: GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));

  static const VerificationMeta _typeMeta = VerificationMeta('type');
  @override
  late final GeneratedColumn<String> type = GeneratedColumn<String>('type', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _statusMeta = VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status = GeneratedColumn<String>('status', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _messageMeta = VerificationMeta('message');
  @override
  late final GeneratedColumn<String> message = GeneratedColumn<String>('message', aliasedName, true, type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _timestampMeta = VerificationMeta('timestamp');
  @override
  late final GeneratedColumn<DateTime> timestamp = GeneratedColumn<DateTime>('timestamp', aliasedName, false, type: DriftSqlType.dateTime, requiredDuringInsert: true);

  @override
  List<GeneratedColumn> get $columns => [id, type, status, message, timestamp];

  @override
  String get aliasedName => _alias ?? actualTableName;

  @override
  String get actualTableName => $name;
  static const String $name = 'sync_logs';

  @override
  VerificationContext validateIntegrity(Insertable<SyncLog> instance, {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('type')) {
      context.handle(_typeMeta, type.isAcceptableOrUnknown(data['type']!, _typeMeta));
    } else if (isInserting) {
      context.missing(_typeMeta);
    }
    if (data.containsKey('status')) {
      context.handle(_statusMeta, status.isAcceptableOrUnknown(data['status']!, _statusMeta));
    } else if (isInserting) {
      context.missing(_statusMeta);
    }
    if (data.containsKey('message')) {
      context.handle(_messageMeta, message.isAcceptableOrUnknown(data['message']!, _messageMeta));
    }
    if (data.containsKey('timestamp')) {
      context.handle(_timestampMeta, timestamp.isAcceptableOrUnknown(data['timestamp']!, _timestampMeta));
    } else if (isInserting) {
      context.missing(_timestampMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};

  @override
  SyncLog map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return SyncLog(
      id: attachedDatabase.typeMapping.read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      type: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}type'])!,
      status: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}status'])!,
      message: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}message']),
      timestamp: attachedDatabase.typeMapping.read(DriftSqlType.dateTime, data['${effectivePrefix}timestamp'])!,
    );
  }

  @override
  $SyncLogsTable createAlias(String alias) {
    return $SyncLogsTable(attachedDatabase, alias);
  }
}

// ============================================================
// SyncEvents Table
// ============================================================

class SyncEvent extends DataClass implements Insertable<SyncEvent> {
  final int id;
  final String tenantId;
  final String type;
  final String? entityType;
  final String? entityId;
  final String message;
  final bool isRead;
  final DateTime createdAt;

  const SyncEvent({
    required this.id,
    required this.tenantId,
    required this.type,
    this.entityType,
    this.entityId,
    required this.message,
    required this.isRead,
    required this.createdAt,
  });

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['tenant_id'] = Variable<String>(tenantId);
    map['type'] = Variable<String>(type);
    if (!nullToAbsent || entityType != null) {
      map['entity_type'] = Variable<String>(entityType);
    }
    if (!nullToAbsent || entityId != null) {
      map['entity_id'] = Variable<String>(entityId);
    }
    map['message'] = Variable<String>(message);
    map['is_read'] = Variable<bool>(isRead);
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  SyncEventsCompanion toCompanion(bool nullToAbsent) {
    return SyncEventsCompanion(
      id: Value(id),
      tenantId: Value(tenantId),
      type: Value(type),
      entityType: entityType == null && nullToAbsent ? const Value.absent() : Value(entityType),
      entityId: entityId == null && nullToAbsent ? const Value.absent() : Value(entityId),
      message: Value(message),
      isRead: Value(isRead),
      createdAt: Value(createdAt),
    );
  }

  factory SyncEvent.fromJson(Map<String, dynamic> json, {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SyncEvent(
      id: serializer.fromJson<int>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenantId']),
      type: serializer.fromJson<String>(json['type']),
      entityType: serializer.fromJson<String?>(json['entityType']),
      entityId: serializer.fromJson<String?>(json['entityId']),
      message: serializer.fromJson<String>(json['message']),
      isRead: serializer.fromJson<bool>(json['isRead']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
    );
  }

  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'tenantId': serializer.toJson<String>(tenantId),
      'type': serializer.toJson<String>(type),
      'entityType': serializer.toJson<String?>(entityType),
      'entityId': serializer.toJson<String?>(entityId),
      'message': serializer.toJson<String>(message),
      'isRead': serializer.toJson<bool>(isRead),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  SyncEvent copyWith({
    int? id,
    String? tenantId,
    String? type,
    Value<String?> entityType = const Value.absent(),
    Value<String?> entityId = const Value.absent(),
    String? message,
    bool? isRead,
    DateTime? createdAt,
  }) =>
      SyncEvent(
        id: id ?? this.id,
        tenantId: tenantId ?? this.tenantId,
        type: type ?? this.type,
        entityType: entityType.present ? entityType.value : this.entityType,
        entityId: entityId.present ? entityId.value : this.entityId,
        message: message ?? this.message,
        isRead: isRead ?? this.isRead,
        createdAt: createdAt ?? this.createdAt,
      );

  @override
  String toString() {
    return 'SyncEvent(id: $id, tenantId: $tenantId, type: $type, entityType: $entityType, entityId: $entityId, message: $message, isRead: $isRead, createdAt: $createdAt)';
  }

  @override
  int get hashCode => Object.hash(id, tenantId, type, entityType, entityId, message, isRead, createdAt);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is SyncEvent &&
          other.id == id &&
          other.tenantId == tenantId &&
          other.type == type &&
          other.entityType == entityType &&
          other.entityId == entityId &&
          other.message == message &&
          other.isRead == isRead &&
          other.createdAt == createdAt);
}

class SyncEventsCompanion extends UpdateCompanion<SyncEvent> {
  final Value<int> id;
  final Value<String> tenantId;
  final Value<String> type;
  final Value<String?> entityType;
  final Value<String?> entityId;
  final Value<String> message;
  final Value<bool> isRead;
  final Value<DateTime> createdAt;

  const SyncEventsCompanion({
    this.id = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.type = const Value.absent(),
    this.entityType = const Value.absent(),
    this.entityId = const Value.absent(),
    this.message = const Value.absent(),
    this.isRead = const Value.absent(),
    this.createdAt = const Value.absent(),
  });

  SyncEventsCompanion.insert({
    this.id = const Value.absent(),
    required String tenantId,
    required String type,
    this.entityType = const Value.absent(),
    this.entityId = const Value.absent(),
    required String message,
    this.isRead = const Value.absent(),
    this.createdAt = const Value.absent(),
  })  : tenantId = Value(tenantId),
        type = Value(type),
        message = Value(message);

  static Insertable<SyncEvent> custom({
    Expression<int>? id,
    Expression<String>? tenantId,
    Expression<String>? type,
    Expression<String>? entityType,
    Expression<String>? entityId,
    Expression<String>? message,
    Expression<bool>? isRead,
    Expression<DateTime>? createdAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (tenantId != null) 'tenant_id': tenantId,
      if (type != null) 'type': type,
      if (entityType != null) 'entity_type': entityType,
      if (entityId != null) 'entity_id': entityId,
      if (message != null) 'message': message,
      if (isRead != null) 'is_read': isRead,
      if (createdAt != null) 'created_at': createdAt,
    });
  }

  SyncEventsCompanion copyWith({
    Value<int>? id,
    Value<String>? tenantId,
    Value<String>? type,
    Value<String?>? entityType,
    Value<String?>? entityId,
    Value<String>? message,
    Value<bool>? isRead,
    Value<DateTime>? createdAt,
  }) {
    return SyncEventsCompanion(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      type: type ?? this.type,
      entityType: entityType ?? this.entityType,
      entityId: entityId ?? this.entityId,
      message: message ?? this.message,
      isRead: isRead ?? this.isRead,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) map['id'] = Variable<int>(id.value);
    if (tenantId.present) map['tenant_id'] = Variable<String>(tenantId.value);
    if (type.present) map['type'] = Variable<String>(type.value);
    if (entityType.present) map['entity_type'] = Variable<String>(entityType.value);
    if (entityId.present) map['entity_id'] = Variable<String>(entityId.value);
    if (message.present) map['message'] = Variable<String>(message.value);
    if (isRead.present) map['is_read'] = Variable<bool>(isRead.value);
    if (createdAt.present) map['created_at'] = Variable<DateTime>(createdAt.value);
    return map;
  }

  @override
  String toString() {
    return 'SyncEventsCompanion(id: $id, tenantId: $tenantId, type: $type, entityType: $entityType, entityId: $entityId, message: $message, isRead: $isRead, createdAt: $createdAt)';
  }
}

class $SyncEventsTable extends SyncEvents with TableInfo<$SyncEventsTable, SyncEvent> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;

  $SyncEventsTable(this.attachedDatabase, [this._alias]);

  static const VerificationMeta _idMeta = VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>('id', aliasedName, false, hasAutoIncrement: true, type: DriftSqlType.int, requiredDuringInsert: false, defaultConstraints: GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));

  static const VerificationMeta _tenantIdMeta = VerificationMeta('tenantId');
  @override
  late final GeneratedColumn<String> tenantId = GeneratedColumn<String>('tenant_id', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _typeMeta = VerificationMeta('type');
  @override
  late final GeneratedColumn<String> type = GeneratedColumn<String>('type', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _entityTypeMeta = VerificationMeta('entityType');
  @override
  late final GeneratedColumn<String> entityType = GeneratedColumn<String>('entity_type', aliasedName, true, type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _entityIdMeta = VerificationMeta('entityId');
  @override
  late final GeneratedColumn<String> entityId = GeneratedColumn<String>('entity_id', aliasedName, true, type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _messageMeta = VerificationMeta('message');
  @override
  late final GeneratedColumn<String> message = GeneratedColumn<String>('message', aliasedName, false, type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _isReadMeta = VerificationMeta('isRead');
  @override
  late final GeneratedColumn<bool> isRead = GeneratedColumn<bool>('is_read', aliasedName, false, type: DriftSqlType.bool, requiredDuringInsert: false, defaultConstraints: GeneratedColumn.constraintIsAlways('CHECK ("is_read" IN (0, 1))'), defaultValue: const Constant(false));

  static const VerificationMeta _createdAtMeta = VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>('created_at', aliasedName, false, type: DriftSqlType.dateTime, requiredDuringInsert: false, defaultValue: currentDateAndTime);

  @override
  List<GeneratedColumn> get $columns => [id, tenantId, type, entityType, entityId, message, isRead, createdAt];

  @override
  String get aliasedName => _alias ?? actualTableName;

  @override
  String get actualTableName => $name;
  static const String $name = 'sync_events';

  @override
  VerificationContext validateIntegrity(Insertable<SyncEvent> instance, {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('tenant_id')) {
      context.handle(_tenantIdMeta, tenantId.isAcceptableOrUnknown(data['tenant_id']!, _tenantIdMeta));
    } else if (isInserting) {
      context.missing(_tenantIdMeta);
    }
    if (data.containsKey('type')) {
      context.handle(_typeMeta, type.isAcceptableOrUnknown(data['type']!, _typeMeta));
    } else if (isInserting) {
      context.missing(_typeMeta);
    }
    if (data.containsKey('entity_type')) {
      context.handle(_entityTypeMeta, entityType.isAcceptableOrUnknown(data['entity_type']!, _entityTypeMeta));
    }
    if (data.containsKey('entity_id')) {
      context.handle(_entityIdMeta, entityId.isAcceptableOrUnknown(data['entity_id']!, _entityIdMeta));
    }
    if (data.containsKey('message')) {
      context.handle(_messageMeta, message.isAcceptableOrUnknown(data['message']!, _messageMeta));
    } else if (isInserting) {
      context.missing(_messageMeta);
    }
    if (data.containsKey('is_read')) {
      context.handle(_isReadMeta, isRead.isAcceptableOrUnknown(data['is_read']!, _isReadMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta, createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};

  @override
  SyncEvent map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return SyncEvent(
      id: attachedDatabase.typeMapping.read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      tenantId: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}tenant_id'])!,
      type: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}type'])!,
      entityType: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}entity_type']),
      entityId: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}entity_id']),
      message: attachedDatabase.typeMapping.read(DriftSqlType.string, data['${effectivePrefix}message'])!,
      isRead: attachedDatabase.typeMapping.read(DriftSqlType.bool, data['${effectivePrefix}is_read'])!,
      createdAt: attachedDatabase.typeMapping.read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $SyncEventsTable createAlias(String alias) {
    return $SyncEventsTable(attachedDatabase, alias);
  }
}

// ============================================================
// Database Mixin
// ============================================================

abstract class _$AppDatabase extends GeneratedDatabase {
  _$AppDatabase(QueryExecutor e) : super(e);

  late final $TasksTable tasks = $TasksTable(this);
  late final $OutboxTable outbox = $OutboxTable(this);
  late final $FieldsTable fields = $FieldsTable(this);
  late final $SyncLogsTable syncLogs = $SyncLogsTable(this);
  late final $SyncEventsTable syncEvents = $SyncEventsTable(this);

  @override
  Iterable<TableInfo<Table, Object?>> get allTables => allSchemaEntities.whereType<TableInfo<Table, Object?>>();

  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [tasks, outbox, fields, syncLogs, syncEvents];
}
