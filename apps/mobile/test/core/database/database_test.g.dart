// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'database_test.dart';

// ignore_for_file: type=lint

// **************************************************************************
// DriftDatabaseGenerator
// **************************************************************************

class TestTask extends DataClass implements Insertable<TestTask> {
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
  final DateTime createdAt;
  final DateTime updatedAt;
  final bool synced;

  const TestTask({
    required this.id,
    required this.tenantId,
    required this.fieldId,
    this.farmId,
    required this.title,
    this.description,
    this.status,
    this.priority,
    this.dueDate,
    this.assignedTo,
    required this.createdAt,
    required this.updatedAt,
    this.synced,
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
    map['created_at'] = Variable<DateTime>(createdAt);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    map['synced'] = Variable<bool>(synced);
    return map;
  }

  factory TestTask.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return TestTask(
      id: serializer.fromJson<String>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenant_id']),
      fieldId: serializer.fromJson<String>(json['field_id']),
      farmId: serializer.fromJson<String?>(json['farm_id']),
      title: serializer.fromJson<String>(json['title']),
      description: serializer.fromJson<String?>(json['description']),
      status: serializer.fromJson<String>(json['status']),
      priority: serializer.fromJson<String>(json['priority']),
      dueDate: serializer.fromJson<DateTime?>(json['due_date']),
      assignedTo: serializer.fromJson<String?>(json['assigned_to']),
      createdAt: serializer.fromJson<DateTime>(json['created_at']),
      updatedAt: serializer.fromJson<DateTime>(json['updated_at']),
      synced: serializer.fromJson<bool>(json['synced']),
    );
  }

  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'tenant_id': serializer.toJson<String>(tenantId),
      'field_id': serializer.toJson<String>(fieldId),
      'farm_id': serializer.toJson<String?>(farmId),
      'title': serializer.toJson<String>(title),
      'description': serializer.toJson<String?>(description),
      'status': serializer.toJson<String>(status),
      'priority': serializer.toJson<String>(priority),
      'due_date': serializer.toJson<DateTime?>(dueDate),
      'assigned_to': serializer.toJson<String?>(assignedTo),
      'created_at': serializer.toJson<DateTime>(createdAt),
      'updated_at': serializer.toJson<DateTime>(updatedAt),
      'synced': serializer.toJson<bool>(synced),
    };
  }

  TestTask copyWith({
    String? id,
    String? tenantId,
    String? fieldId,
    Value<String> farmId = const Value.absent(),
    String? title,
    Value<String> description = const Value.absent(),
    String? status,
    String? priority,
    Value<DateTime> dueDate = const Value.absent(),
    Value<String> assignedTo = const Value.absent(),
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? synced,
  }) {
    return TestTask(
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
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      synced: synced ?? this.synced,
    );
  }

  @override
  String toString() {
    return (StringBuffer('TestTask(')
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('fieldId: ${fieldId}, ')
          ..write('farmId: ${farmId}, ')
          ..write('title: ${title}, ')
          ..write('description: ${description}, ')
          ..write('status: ${status}, ')
          ..write('priority: ${priority}, ')
          ..write('dueDate: ${dueDate}, ')
          ..write('assignedTo: ${assignedTo}, ')
          ..write('createdAt: ${createdAt}, ')
          ..write('updatedAt: ${updatedAt}, ')
          ..write('synced: ${synced}')
          ..write(')')
      ).toString();
  }

  @override
  int get hashCode => Object.hash(id, tenantId, fieldId, farmId, title, description, status, priority, dueDate, assignedTo, createdAt, updatedAt, synced);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is TestTask &&
          other.id == this.id &&
          other.tenantId == this.tenantId &&
          other.fieldId == this.fieldId &&
          other.farmId == this.farmId &&
          other.title == this.title &&
          other.description == this.description &&
          other.status == this.status &&
          other.priority == this.priority &&
          other.dueDate == this.dueDate &&
          other.assignedTo == this.assignedTo &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt &&
          other.synced == this.synced)
  ;
}

class TestTasksCompanion extends UpdateCompanion<TestTask> {
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
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;
  final Value<bool> synced;

  const TestTasksCompanion({
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
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.synced = const Value.absent(),
  });

  TestTasksCompanion.insert({
    required String id,
    required String tenantId,
    required String fieldId,
    Value<String?> farmId = const Value.absent(),
    required String title,
    Value<String?> description = const Value.absent(),
    Value<String> status = const Value.absent(),
    Value<String> priority = const Value.absent(),
    Value<DateTime?> dueDate = const Value.absent(),
    Value<String?> assignedTo = const Value.absent(),
    required DateTime createdAt,
    required DateTime updatedAt,
    Value<bool> synced = const Value.absent(),
  })
      : id = Value(id),
        tenantId = Value(tenantId),
        fieldId = Value(fieldId),
        title = Value(title),
        createdAt = Value(createdAt),
        updatedAt = Value(updatedAt);

  static Insertable<TestTask> custom({
    Expression<dynamic>? id,
    Expression<dynamic>? tenantId,
    Expression<dynamic>? fieldId,
    Expression<dynamic>? farmId,
    Expression<dynamic>? title,
    Expression<dynamic>? description,
    Expression<dynamic>? status,
    Expression<dynamic>? priority,
    Expression<dynamic>? dueDate,
    Expression<dynamic>? assignedTo,
    Expression<dynamic>? createdAt,
    Expression<dynamic>? updatedAt,
    Expression<dynamic>? synced,
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
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (synced != null) 'synced': synced,
    });
  }

  TestTasksCompanion copyWith({
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
    Value<DateTime>? createdAt,
    Value<DateTime>? updatedAt,
    Value<bool>? synced,
  }) {
    return TestTasksCompanion(
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
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      synced: synced ?? this.synced,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (tenantId.present) {
      map['tenant_id'] = Variable<String>(tenantId.value);
    }
    if (fieldId.present) {
      map['field_id'] = Variable<String>(fieldId.value);
    }
    if (farmId.present) {
      map['farm_id'] = Variable<String?>(farmId.value);
    }
    if (title.present) {
      map['title'] = Variable<String>(title.value);
    }
    if (description.present) {
      map['description'] = Variable<String?>(description.value);
    }
    if (status.present) {
      map['status'] = Variable<String>(status.value);
    }
    if (priority.present) {
      map['priority'] = Variable<String>(priority.value);
    }
    if (dueDate.present) {
      map['due_date'] = Variable<DateTime?>(dueDate.value);
    }
    if (assignedTo.present) {
      map['assigned_to'] = Variable<String?>(assignedTo.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (synced.present) {
      map['synced'] = Variable<bool>(synced.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('TestTasksCompanion(')
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('fieldId: ${fieldId}, ')
          ..write('farmId: ${farmId}, ')
          ..write('title: ${title}, ')
          ..write('description: ${description}, ')
          ..write('status: ${status}, ')
          ..write('priority: ${priority}, ')
          ..write('dueDate: ${dueDate}, ')
          ..write('assignedTo: ${assignedTo}, ')
          ..write('createdAt: ${createdAt}, ')
          ..write('updatedAt: ${updatedAt}, ')
          ..write('synced: ${synced}')
          ..write(')')
      ).toString();
  }
}

class \$TestTasksTable extends TestTasks
    with TableInfo<\$TestTasksTable, TestTask> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  \$TestTasksTable(this.attachedDatabase, [this._alias]);

  static const VerificationMeta _idMeta = VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id =
      GeneratedColumn<String>(
          'id', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _tenantIdMeta = VerificationMeta('tenantId');
  @override
  late final GeneratedColumn<String> tenantId =
      GeneratedColumn<String>(
          'tenant_id', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _fieldIdMeta = VerificationMeta('fieldId');
  @override
  late final GeneratedColumn<String> fieldId =
      GeneratedColumn<String>(
          'field_id', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _farmIdMeta = VerificationMeta('farmId');
  @override
  late final GeneratedColumn<String> farmId =
      GeneratedColumn<String>(
          'farm_id', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _titleMeta = VerificationMeta('title');
  @override
  late final GeneratedColumn<String> title =
      GeneratedColumn<String>(
          'title', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _descriptionMeta = VerificationMeta('description');
  @override
  late final GeneratedColumn<String> description =
      GeneratedColumn<String>(
          'description', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _statusMeta = VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status =
      GeneratedColumn<String>(
          'status', aliasedName, false,
          defaultValue: const Constant('open'),
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _priorityMeta = VerificationMeta('priority');
  @override
  late final GeneratedColumn<String> priority =
      GeneratedColumn<String>(
          'priority', aliasedName, false,
          defaultValue: const Constant('medium'),
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _dueDateMeta = VerificationMeta('dueDate');
  @override
  late final GeneratedColumn<DateTime> dueDate =
      GeneratedColumn<DateTime>(
          'due_date', aliasedName, true,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: false);

  static const VerificationMeta _assignedToMeta = VerificationMeta('assignedTo');
  @override
  late final GeneratedColumn<String> assignedTo =
      GeneratedColumn<String>(
          'assigned_to', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _createdAtMeta = VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt =
      GeneratedColumn<DateTime>(
          'created_at', aliasedName, false,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: true);

  static const VerificationMeta _updatedAtMeta = VerificationMeta('updatedAt');
  @override
  late final GeneratedColumn<DateTime> updatedAt =
      GeneratedColumn<DateTime>(
          'updated_at', aliasedName, false,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: true);

  static const VerificationMeta _syncedMeta = VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced =
      GeneratedColumn<bool>(
          'synced', aliasedName, false,
          defaultValue: const Constant(false),
          type: DriftSqlType.bool,
          requiredDuringInsert: false);

  @override
  List<GeneratedColumn> get $columns => [id, tenantId, fieldId, farmId, title, description, status, priority, dueDate, assignedTo, createdAt, updatedAt, synced];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String \$name = 'test_tasks';

  @override
  VerificationContext validateIntegrity(Insertable<TestTask> instance,
      {{bool isInserting = false}}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta,
          id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    else if (isInserting) {
      context.addError(_idMeta,
          const VerificationError('id must be provided when inserting.'));
    }
    if (data.containsKey('tenant_id')) {
      context.handle(_tenantIdMeta,
          tenantId.isAcceptableOrUnknown(data['tenant_id']!, _tenantIdMeta));
    }
    else if (isInserting) {
      context.addError(_tenantIdMeta,
          const VerificationError('tenantId must be provided when inserting.'));
    }
    if (data.containsKey('field_id')) {
      context.handle(_fieldIdMeta,
          fieldId.isAcceptableOrUnknown(data['field_id']!, _fieldIdMeta));
    }
    else if (isInserting) {
      context.addError(_fieldIdMeta,
          const VerificationError('fieldId must be provided when inserting.'));
    }
    if (data.containsKey('farm_id')) {
      context.handle(_farmIdMeta,
          farmId.isAcceptableOrUnknown(data['farm_id']!, _farmIdMeta));
    }
    if (data.containsKey('title')) {
      context.handle(_titleMeta,
          title.isAcceptableOrUnknown(data['title']!, _titleMeta));
    }
    else if (isInserting) {
      context.addError(_titleMeta,
          const VerificationError('title must be provided when inserting.'));
    }
    if (data.containsKey('description')) {
      context.handle(_descriptionMeta,
          description.isAcceptableOrUnknown(data['description']!, _descriptionMeta));
    }
    if (data.containsKey('status')) {
      context.handle(_statusMeta,
          status.isAcceptableOrUnknown(data['status']!, _statusMeta));
    }
    if (data.containsKey('priority')) {
      context.handle(_priorityMeta,
          priority.isAcceptableOrUnknown(data['priority']!, _priorityMeta));
    }
    if (data.containsKey('due_date')) {
      context.handle(_dueDateMeta,
          dueDate.isAcceptableOrUnknown(data['due_date']!, _dueDateMeta));
    }
    if (data.containsKey('assigned_to')) {
      context.handle(_assignedToMeta,
          assignedTo.isAcceptableOrUnknown(data['assigned_to']!, _assignedToMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    else if (isInserting) {
      context.addError(_createdAtMeta,
          const VerificationError('createdAt must be provided when inserting.'));
    }
    if (data.containsKey('updated_at')) {
      context.handle(_updatedAtMeta,
          updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta));
    }
    else if (isInserting) {
      context.addError(_updatedAtMeta,
          const VerificationError('updatedAt must be provided when inserting.'));
    }
    if (data.containsKey('synced')) {
      context.handle(_syncedMeta,
          synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};

  @override
  TestTask map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '\$tablePrefix.' : '';
    return TestTask(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}id'])!,
      tenantId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}tenant_id'])!,
      fieldId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}field_id'])!,
      farmId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}farm_id']),
      title: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}title'])!,
      description: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}description']),
      status: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}status'])!,
      priority: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}priority'])!,
      dueDate: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}due_date']),
      assignedTo: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}assigned_to']),
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}created_at'])!,
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}updated_at'])!,
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['\${effectivePrefix}synced'])!,
    );
  }

  @override
  \$TestTasksTable createAlias(String alias) {
    return \$TestTasksTable(attachedDatabase, alias);
  }
}

class TestOutboxData extends DataClass implements Insertable<TestOutboxData> {
  final int id;
  final String tenantId;
  final String entityType;
  final String entityId;
  final String apiEndpoint;
  final String method;
  final String payload;
  final String? ifMatch;
  final int retryCount;
  final bool isSynced;
  final DateTime createdAt;

  const TestOutboxData({
    this.id,
    required this.tenantId,
    required this.entityType,
    required this.entityId,
    required this.apiEndpoint,
    this.method,
    required this.payload,
    this.ifMatch,
    this.retryCount,
    this.isSynced,
    this.createdAt,
  });

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['tenant_id'] = Variable<String>(tenantId);
    map['entity_type'] = Variable<String>(entityType);
    map['entity_id'] = Variable<String>(entityId);
    map['api_endpoint'] = Variable<String>(apiEndpoint);
    map['method'] = Variable<String>(method);
    map['payload'] = Variable<String>(payload);
    if (!nullToAbsent || ifMatch != null) {
      map['if_match'] = Variable<String>(ifMatch);
    }
    map['retry_count'] = Variable<int>(retryCount);
    map['is_synced'] = Variable<bool>(isSynced);
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  factory TestOutboxData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return TestOutboxData(
      id: serializer.fromJson<int>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenant_id']),
      entityType: serializer.fromJson<String>(json['entity_type']),
      entityId: serializer.fromJson<String>(json['entity_id']),
      apiEndpoint: serializer.fromJson<String>(json['api_endpoint']),
      method: serializer.fromJson<String>(json['method']),
      payload: serializer.fromJson<String>(json['payload']),
      ifMatch: serializer.fromJson<String?>(json['if_match']),
      retryCount: serializer.fromJson<int>(json['retry_count']),
      isSynced: serializer.fromJson<bool>(json['is_synced']),
      createdAt: serializer.fromJson<DateTime>(json['created_at']),
    );
  }

  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'tenant_id': serializer.toJson<String>(tenantId),
      'entity_type': serializer.toJson<String>(entityType),
      'entity_id': serializer.toJson<String>(entityId),
      'api_endpoint': serializer.toJson<String>(apiEndpoint),
      'method': serializer.toJson<String>(method),
      'payload': serializer.toJson<String>(payload),
      'if_match': serializer.toJson<String?>(ifMatch),
      'retry_count': serializer.toJson<int>(retryCount),
      'is_synced': serializer.toJson<bool>(isSynced),
      'created_at': serializer.toJson<DateTime>(createdAt),
    };
  }

  TestOutboxData copyWith({
    int? id,
    String? tenantId,
    String? entityType,
    String? entityId,
    String? apiEndpoint,
    String? method,
    String? payload,
    Value<String> ifMatch = const Value.absent(),
    int? retryCount,
    bool? isSynced,
    DateTime? createdAt,
  }) {
    return TestOutboxData(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      entityType: entityType ?? this.entityType,
      entityId: entityId ?? this.entityId,
      apiEndpoint: apiEndpoint ?? this.apiEndpoint,
      method: method ?? this.method,
      payload: payload ?? this.payload,
      ifMatch: ifMatch.present ? ifMatch.value : this.ifMatch,
      retryCount: retryCount ?? this.retryCount,
      isSynced: isSynced ?? this.isSynced,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('TestOutboxData(')
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('entityType: ${entityType}, ')
          ..write('entityId: ${entityId}, ')
          ..write('apiEndpoint: ${apiEndpoint}, ')
          ..write('method: ${method}, ')
          ..write('payload: ${payload}, ')
          ..write('ifMatch: ${ifMatch}, ')
          ..write('retryCount: ${retryCount}, ')
          ..write('isSynced: ${isSynced}, ')
          ..write('createdAt: ${createdAt}')
          ..write(')')
      ).toString();
  }

  @override
  int get hashCode => Object.hash(id, tenantId, entityType, entityId, apiEndpoint, method, payload, ifMatch, retryCount, isSynced, createdAt);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is TestOutboxData &&
          other.id == this.id &&
          other.tenantId == this.tenantId &&
          other.entityType == this.entityType &&
          other.entityId == this.entityId &&
          other.apiEndpoint == this.apiEndpoint &&
          other.method == this.method &&
          other.payload == this.payload &&
          other.ifMatch == this.ifMatch &&
          other.retryCount == this.retryCount &&
          other.isSynced == this.isSynced &&
          other.createdAt == this.createdAt)
  ;
}

class TestOutboxCompanion extends UpdateCompanion<TestOutboxData> {
  final Value<int> id;
  final Value<String> tenantId;
  final Value<String> entityType;
  final Value<String> entityId;
  final Value<String> apiEndpoint;
  final Value<String> method;
  final Value<String> payload;
  final Value<String?> ifMatch;
  final Value<int> retryCount;
  final Value<bool> isSynced;
  final Value<DateTime> createdAt;

  const TestOutboxCompanion({
    this.id = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.entityType = const Value.absent(),
    this.entityId = const Value.absent(),
    this.apiEndpoint = const Value.absent(),
    this.method = const Value.absent(),
    this.payload = const Value.absent(),
    this.ifMatch = const Value.absent(),
    this.retryCount = const Value.absent(),
    this.isSynced = const Value.absent(),
    this.createdAt = const Value.absent(),
  });

  TestOutboxCompanion.insert({
    this.id = const Value.absent(),
    required String tenantId,
    required String entityType,
    required String entityId,
    required String apiEndpoint,
    Value<String> method = const Value.absent(),
    required String payload,
    Value<String?> ifMatch = const Value.absent(),
    Value<int> retryCount = const Value.absent(),
    Value<bool> isSynced = const Value.absent(),
    Value<DateTime> createdAt = const Value.absent(),
  })
      : tenantId = Value(tenantId),
        entityType = Value(entityType),
        entityId = Value(entityId),
        apiEndpoint = Value(apiEndpoint),
        payload = Value(payload);

  static Insertable<TestOutboxData> custom({
    Expression<dynamic>? id,
    Expression<dynamic>? tenantId,
    Expression<dynamic>? entityType,
    Expression<dynamic>? entityId,
    Expression<dynamic>? apiEndpoint,
    Expression<dynamic>? method,
    Expression<dynamic>? payload,
    Expression<dynamic>? ifMatch,
    Expression<dynamic>? retryCount,
    Expression<dynamic>? isSynced,
    Expression<dynamic>? createdAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (tenantId != null) 'tenant_id': tenantId,
      if (entityType != null) 'entity_type': entityType,
      if (entityId != null) 'entity_id': entityId,
      if (apiEndpoint != null) 'api_endpoint': apiEndpoint,
      if (method != null) 'method': method,
      if (payload != null) 'payload': payload,
      if (ifMatch != null) 'if_match': ifMatch,
      if (retryCount != null) 'retry_count': retryCount,
      if (isSynced != null) 'is_synced': isSynced,
      if (createdAt != null) 'created_at': createdAt,
    });
  }

  TestOutboxCompanion copyWith({
    Value<int>? id,
    Value<String>? tenantId,
    Value<String>? entityType,
    Value<String>? entityId,
    Value<String>? apiEndpoint,
    Value<String>? method,
    Value<String>? payload,
    Value<String?>? ifMatch,
    Value<int>? retryCount,
    Value<bool>? isSynced,
    Value<DateTime>? createdAt,
  }) {
    return TestOutboxCompanion(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      entityType: entityType ?? this.entityType,
      entityId: entityId ?? this.entityId,
      apiEndpoint: apiEndpoint ?? this.apiEndpoint,
      method: method ?? this.method,
      payload: payload ?? this.payload,
      ifMatch: ifMatch ?? this.ifMatch,
      retryCount: retryCount ?? this.retryCount,
      isSynced: isSynced ?? this.isSynced,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (tenantId.present) {
      map['tenant_id'] = Variable<String>(tenantId.value);
    }
    if (entityType.present) {
      map['entity_type'] = Variable<String>(entityType.value);
    }
    if (entityId.present) {
      map['entity_id'] = Variable<String>(entityId.value);
    }
    if (apiEndpoint.present) {
      map['api_endpoint'] = Variable<String>(apiEndpoint.value);
    }
    if (method.present) {
      map['method'] = Variable<String>(method.value);
    }
    if (payload.present) {
      map['payload'] = Variable<String>(payload.value);
    }
    if (ifMatch.present) {
      map['if_match'] = Variable<String?>(ifMatch.value);
    }
    if (retryCount.present) {
      map['retry_count'] = Variable<int>(retryCount.value);
    }
    if (isSynced.present) {
      map['is_synced'] = Variable<bool>(isSynced.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('TestOutboxCompanion(')
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('entityType: ${entityType}, ')
          ..write('entityId: ${entityId}, ')
          ..write('apiEndpoint: ${apiEndpoint}, ')
          ..write('method: ${method}, ')
          ..write('payload: ${payload}, ')
          ..write('ifMatch: ${ifMatch}, ')
          ..write('retryCount: ${retryCount}, ')
          ..write('isSynced: ${isSynced}, ')
          ..write('createdAt: ${createdAt}')
          ..write(')')
      ).toString();
  }
}

class \$TestOutboxTable extends TestOutbox
    with TableInfo<\$TestOutboxTable, TestOutboxData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  \$TestOutboxTable(this.attachedDatabase, [this._alias]);

  static const VerificationMeta _idMeta = VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id =
      GeneratedColumn<int>(
          'id', aliasedName, false,
          hasAutoIncrement: true,
          type: DriftSqlType.int,
          requiredDuringInsert: false);

  static const VerificationMeta _tenantIdMeta = VerificationMeta('tenantId');
  @override
  late final GeneratedColumn<String> tenantId =
      GeneratedColumn<String>(
          'tenant_id', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _entityTypeMeta = VerificationMeta('entityType');
  @override
  late final GeneratedColumn<String> entityType =
      GeneratedColumn<String>(
          'entity_type', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _entityIdMeta = VerificationMeta('entityId');
  @override
  late final GeneratedColumn<String> entityId =
      GeneratedColumn<String>(
          'entity_id', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _apiEndpointMeta = VerificationMeta('apiEndpoint');
  @override
  late final GeneratedColumn<String> apiEndpoint =
      GeneratedColumn<String>(
          'api_endpoint', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _methodMeta = VerificationMeta('method');
  @override
  late final GeneratedColumn<String> method =
      GeneratedColumn<String>(
          'method', aliasedName, false,
          defaultValue: const Constant('POST'),
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _payloadMeta = VerificationMeta('payload');
  @override
  late final GeneratedColumn<String> payload =
      GeneratedColumn<String>(
          'payload', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _ifMatchMeta = VerificationMeta('ifMatch');
  @override
  late final GeneratedColumn<String> ifMatch =
      GeneratedColumn<String>(
          'if_match', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _retryCountMeta = VerificationMeta('retryCount');
  @override
  late final GeneratedColumn<int> retryCount =
      GeneratedColumn<int>(
          'retry_count', aliasedName, false,
          defaultValue: const Constant(0),
          type: DriftSqlType.int,
          requiredDuringInsert: false);

  static const VerificationMeta _isSyncedMeta = VerificationMeta('isSynced');
  @override
  late final GeneratedColumn<bool> isSynced =
      GeneratedColumn<bool>(
          'is_synced', aliasedName, false,
          defaultValue: const Constant(false),
          type: DriftSqlType.bool,
          requiredDuringInsert: false);

  static const VerificationMeta _createdAtMeta = VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt =
      GeneratedColumn<DateTime>(
          'created_at', aliasedName, false,
          defaultValue: currentDateAndTime,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: false);

  @override
  List<GeneratedColumn> get $columns => [id, tenantId, entityType, entityId, apiEndpoint, method, payload, ifMatch, retryCount, isSynced, createdAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String \$name = 'test_outbox';

  @override
  VerificationContext validateIntegrity(Insertable<TestOutboxData> instance,
      {{bool isInserting = false}}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta,
          id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('tenant_id')) {
      context.handle(_tenantIdMeta,
          tenantId.isAcceptableOrUnknown(data['tenant_id']!, _tenantIdMeta));
    }
    else if (isInserting) {
      context.addError(_tenantIdMeta,
          const VerificationError('tenantId must be provided when inserting.'));
    }
    if (data.containsKey('entity_type')) {
      context.handle(_entityTypeMeta,
          entityType.isAcceptableOrUnknown(data['entity_type']!, _entityTypeMeta));
    }
    else if (isInserting) {
      context.addError(_entityTypeMeta,
          const VerificationError('entityType must be provided when inserting.'));
    }
    if (data.containsKey('entity_id')) {
      context.handle(_entityIdMeta,
          entityId.isAcceptableOrUnknown(data['entity_id']!, _entityIdMeta));
    }
    else if (isInserting) {
      context.addError(_entityIdMeta,
          const VerificationError('entityId must be provided when inserting.'));
    }
    if (data.containsKey('api_endpoint')) {
      context.handle(_apiEndpointMeta,
          apiEndpoint.isAcceptableOrUnknown(data['api_endpoint']!, _apiEndpointMeta));
    }
    else if (isInserting) {
      context.addError(_apiEndpointMeta,
          const VerificationError('apiEndpoint must be provided when inserting.'));
    }
    if (data.containsKey('method')) {
      context.handle(_methodMeta,
          method.isAcceptableOrUnknown(data['method']!, _methodMeta));
    }
    if (data.containsKey('payload')) {
      context.handle(_payloadMeta,
          payload.isAcceptableOrUnknown(data['payload']!, _payloadMeta));
    }
    else if (isInserting) {
      context.addError(_payloadMeta,
          const VerificationError('payload must be provided when inserting.'));
    }
    if (data.containsKey('if_match')) {
      context.handle(_ifMatchMeta,
          ifMatch.isAcceptableOrUnknown(data['if_match']!, _ifMatchMeta));
    }
    if (data.containsKey('retry_count')) {
      context.handle(_retryCountMeta,
          retryCount.isAcceptableOrUnknown(data['retry_count']!, _retryCountMeta));
    }
    if (data.containsKey('is_synced')) {
      context.handle(_isSyncedMeta,
          isSynced.isAcceptableOrUnknown(data['is_synced']!, _isSyncedMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};

  @override
  TestOutboxData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '\$tablePrefix.' : '';
    return TestOutboxData(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['\${effectivePrefix}id'])!,
      tenantId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}tenant_id'])!,
      entityType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}entity_type'])!,
      entityId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}entity_id'])!,
      apiEndpoint: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}api_endpoint'])!,
      method: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}method'])!,
      payload: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}payload'])!,
      ifMatch: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}if_match']),
      retryCount: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['\${effectivePrefix}retry_count'])!,
      isSynced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['\${effectivePrefix}is_synced'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}created_at'])!,
    );
  }

  @override
  \$TestOutboxTable createAlias(String alias) {
    return \$TestOutboxTable(attachedDatabase, alias);
  }
}

class TestField extends DataClass implements Insertable<TestField> {
  final String id;
  final String? remoteId;
  final String tenantId;
  final String? farmId;
  final String name;
  final String? cropType;
  final String boundary;
  final String? centroid;
  final double areaHectares;
  final String? status;
  final double? ndviCurrent;
  final DateTime? ndviUpdatedAt;
  final bool synced;
  final bool isDeleted;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? etag;
  final DateTime? serverUpdatedAt;

  const TestField({
    required this.id,
    this.remoteId,
    required this.tenantId,
    this.farmId,
    required this.name,
    this.cropType,
    required this.boundary,
    this.centroid,
    required this.areaHectares,
    this.status,
    this.ndviCurrent,
    this.ndviUpdatedAt,
    this.synced,
    this.isDeleted,
    required this.createdAt,
    required this.updatedAt,
    this.etag,
    this.serverUpdatedAt,
  });

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    if (!nullToAbsent || remoteId != null) {
      map['remote_id'] = Variable<String>(remoteId);
    }
    map['tenant_id'] = Variable<String>(tenantId);
    if (!nullToAbsent || farmId != null) {
      map['farm_id'] = Variable<String>(farmId);
    }
    map['name'] = Variable<String>(name);
    if (!nullToAbsent || cropType != null) {
      map['crop_type'] = Variable<String>(cropType);
    }
    map['boundary'] = Variable<String>(boundary);
    if (!nullToAbsent || centroid != null) {
      map['centroid'] = Variable<String>(centroid);
    }
    map['area_hectares'] = Variable<double>(areaHectares);
    if (!nullToAbsent || status != null) {
      map['status'] = Variable<String>(status);
    }
    if (!nullToAbsent || ndviCurrent != null) {
      map['ndvi_current'] = Variable<double>(ndviCurrent);
    }
    if (!nullToAbsent || ndviUpdatedAt != null) {
      map['ndvi_updated_at'] = Variable<DateTime>(ndviUpdatedAt);
    }
    map['synced'] = Variable<bool>(synced);
    map['is_deleted'] = Variable<bool>(isDeleted);
    map['created_at'] = Variable<DateTime>(createdAt);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    if (!nullToAbsent || etag != null) {
      map['etag'] = Variable<String>(etag);
    }
    if (!nullToAbsent || serverUpdatedAt != null) {
      map['server_updated_at'] = Variable<DateTime>(serverUpdatedAt);
    }
    return map;
  }

  factory TestField.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return TestField(
      id: serializer.fromJson<String>(json['id']),
      remoteId: serializer.fromJson<String?>(json['remote_id']),
      tenantId: serializer.fromJson<String>(json['tenant_id']),
      farmId: serializer.fromJson<String?>(json['farm_id']),
      name: serializer.fromJson<String>(json['name']),
      cropType: serializer.fromJson<String?>(json['crop_type']),
      boundary: serializer.fromJson<String>(json['boundary']),
      centroid: serializer.fromJson<String?>(json['centroid']),
      areaHectares: serializer.fromJson<double>(json['area_hectares']),
      status: serializer.fromJson<String?>(json['status']),
      ndviCurrent: serializer.fromJson<double?>(json['ndvi_current']),
      ndviUpdatedAt: serializer.fromJson<DateTime?>(json['ndvi_updated_at']),
      synced: serializer.fromJson<bool>(json['synced']),
      isDeleted: serializer.fromJson<bool>(json['is_deleted']),
      createdAt: serializer.fromJson<DateTime>(json['created_at']),
      updatedAt: serializer.fromJson<DateTime>(json['updated_at']),
      etag: serializer.fromJson<String?>(json['etag']),
      serverUpdatedAt: serializer.fromJson<DateTime?>(json['server_updated_at']),
    );
  }

  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'remote_id': serializer.toJson<String?>(remoteId),
      'tenant_id': serializer.toJson<String>(tenantId),
      'farm_id': serializer.toJson<String?>(farmId),
      'name': serializer.toJson<String>(name),
      'crop_type': serializer.toJson<String?>(cropType),
      'boundary': serializer.toJson<String>(boundary),
      'centroid': serializer.toJson<String?>(centroid),
      'area_hectares': serializer.toJson<double>(areaHectares),
      'status': serializer.toJson<String?>(status),
      'ndvi_current': serializer.toJson<double?>(ndviCurrent),
      'ndvi_updated_at': serializer.toJson<DateTime?>(ndviUpdatedAt),
      'synced': serializer.toJson<bool>(synced),
      'is_deleted': serializer.toJson<bool>(isDeleted),
      'created_at': serializer.toJson<DateTime>(createdAt),
      'updated_at': serializer.toJson<DateTime>(updatedAt),
      'etag': serializer.toJson<String?>(etag),
      'server_updated_at': serializer.toJson<DateTime?>(serverUpdatedAt),
    };
  }

  TestField copyWith({
    String? id,
    Value<String> remoteId = const Value.absent(),
    String? tenantId,
    Value<String> farmId = const Value.absent(),
    String? name,
    Value<String> cropType = const Value.absent(),
    String? boundary,
    Value<String> centroid = const Value.absent(),
    double? areaHectares,
    Value<String> status = const Value.absent(),
    Value<double> ndviCurrent = const Value.absent(),
    Value<DateTime> ndviUpdatedAt = const Value.absent(),
    bool? synced,
    bool? isDeleted,
    DateTime? createdAt,
    DateTime? updatedAt,
    Value<String> etag = const Value.absent(),
    Value<DateTime> serverUpdatedAt = const Value.absent(),
  }) {
    return TestField(
      id: id ?? this.id,
      remoteId: remoteId.present ? remoteId.value : this.remoteId,
      tenantId: tenantId ?? this.tenantId,
      farmId: farmId.present ? farmId.value : this.farmId,
      name: name ?? this.name,
      cropType: cropType.present ? cropType.value : this.cropType,
      boundary: boundary ?? this.boundary,
      centroid: centroid.present ? centroid.value : this.centroid,
      areaHectares: areaHectares ?? this.areaHectares,
      status: status.present ? status.value : this.status,
      ndviCurrent: ndviCurrent.present ? ndviCurrent.value : this.ndviCurrent,
      ndviUpdatedAt: ndviUpdatedAt.present ? ndviUpdatedAt.value : this.ndviUpdatedAt,
      synced: synced ?? this.synced,
      isDeleted: isDeleted ?? this.isDeleted,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      etag: etag.present ? etag.value : this.etag,
      serverUpdatedAt: serverUpdatedAt.present ? serverUpdatedAt.value : this.serverUpdatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('TestField(')
          ..write('id: ${id}, ')
          ..write('remoteId: ${remoteId}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('farmId: ${farmId}, ')
          ..write('name: ${name}, ')
          ..write('cropType: ${cropType}, ')
          ..write('boundary: ${boundary}, ')
          ..write('centroid: ${centroid}, ')
          ..write('areaHectares: ${areaHectares}, ')
          ..write('status: ${status}, ')
          ..write('ndviCurrent: ${ndviCurrent}, ')
          ..write('ndviUpdatedAt: ${ndviUpdatedAt}, ')
          ..write('synced: ${synced}, ')
          ..write('isDeleted: ${isDeleted}, ')
          ..write('createdAt: ${createdAt}, ')
          ..write('updatedAt: ${updatedAt}, ')
          ..write('etag: ${etag}, ')
          ..write('serverUpdatedAt: ${serverUpdatedAt}')
          ..write(')')
      ).toString();
  }

  @override
  int get hashCode => Object.hash(id, remoteId, tenantId, farmId, name, cropType, boundary, centroid, areaHectares, status, ndviCurrent, ndviUpdatedAt, synced, isDeleted, createdAt, updatedAt, etag, serverUpdatedAt);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is TestField &&
          other.id == this.id &&
          other.remoteId == this.remoteId &&
          other.tenantId == this.tenantId &&
          other.farmId == this.farmId &&
          other.name == this.name &&
          other.cropType == this.cropType &&
          other.boundary == this.boundary &&
          other.centroid == this.centroid &&
          other.areaHectares == this.areaHectares &&
          other.status == this.status &&
          other.ndviCurrent == this.ndviCurrent &&
          other.ndviUpdatedAt == this.ndviUpdatedAt &&
          other.synced == this.synced &&
          other.isDeleted == this.isDeleted &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt &&
          other.etag == this.etag &&
          other.serverUpdatedAt == this.serverUpdatedAt)
  ;
}

class TestFieldsCompanion extends UpdateCompanion<TestField> {
  final Value<String> id;
  final Value<String?> remoteId;
  final Value<String> tenantId;
  final Value<String?> farmId;
  final Value<String> name;
  final Value<String?> cropType;
  final Value<String> boundary;
  final Value<String?> centroid;
  final Value<double> areaHectares;
  final Value<String?> status;
  final Value<double?> ndviCurrent;
  final Value<DateTime?> ndviUpdatedAt;
  final Value<bool> synced;
  final Value<bool> isDeleted;
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;
  final Value<String?> etag;
  final Value<DateTime?> serverUpdatedAt;

  const TestFieldsCompanion({
    this.id = const Value.absent(),
    this.remoteId = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.farmId = const Value.absent(),
    this.name = const Value.absent(),
    this.cropType = const Value.absent(),
    this.boundary = const Value.absent(),
    this.centroid = const Value.absent(),
    this.areaHectares = const Value.absent(),
    this.status = const Value.absent(),
    this.ndviCurrent = const Value.absent(),
    this.ndviUpdatedAt = const Value.absent(),
    this.synced = const Value.absent(),
    this.isDeleted = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.etag = const Value.absent(),
    this.serverUpdatedAt = const Value.absent(),
  });

  TestFieldsCompanion.insert({
    required String id,
    Value<String?> remoteId = const Value.absent(),
    required String tenantId,
    Value<String?> farmId = const Value.absent(),
    required String name,
    Value<String?> cropType = const Value.absent(),
    required String boundary,
    Value<String?> centroid = const Value.absent(),
    required double areaHectares,
    Value<String?> status = const Value.absent(),
    Value<double?> ndviCurrent = const Value.absent(),
    Value<DateTime?> ndviUpdatedAt = const Value.absent(),
    Value<bool> synced = const Value.absent(),
    Value<bool> isDeleted = const Value.absent(),
    required DateTime createdAt,
    required DateTime updatedAt,
    Value<String?> etag = const Value.absent(),
    Value<DateTime?> serverUpdatedAt = const Value.absent(),
  })
      : id = Value(id),
        tenantId = Value(tenantId),
        name = Value(name),
        boundary = Value(boundary),
        areaHectares = Value(areaHectares),
        createdAt = Value(createdAt),
        updatedAt = Value(updatedAt);

  static Insertable<TestField> custom({
    Expression<dynamic>? id,
    Expression<dynamic>? remoteId,
    Expression<dynamic>? tenantId,
    Expression<dynamic>? farmId,
    Expression<dynamic>? name,
    Expression<dynamic>? cropType,
    Expression<dynamic>? boundary,
    Expression<dynamic>? centroid,
    Expression<dynamic>? areaHectares,
    Expression<dynamic>? status,
    Expression<dynamic>? ndviCurrent,
    Expression<dynamic>? ndviUpdatedAt,
    Expression<dynamic>? synced,
    Expression<dynamic>? isDeleted,
    Expression<dynamic>? createdAt,
    Expression<dynamic>? updatedAt,
    Expression<dynamic>? etag,
    Expression<dynamic>? serverUpdatedAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (remoteId != null) 'remote_id': remoteId,
      if (tenantId != null) 'tenant_id': tenantId,
      if (farmId != null) 'farm_id': farmId,
      if (name != null) 'name': name,
      if (cropType != null) 'crop_type': cropType,
      if (boundary != null) 'boundary': boundary,
      if (centroid != null) 'centroid': centroid,
      if (areaHectares != null) 'area_hectares': areaHectares,
      if (status != null) 'status': status,
      if (ndviCurrent != null) 'ndvi_current': ndviCurrent,
      if (ndviUpdatedAt != null) 'ndvi_updated_at': ndviUpdatedAt,
      if (synced != null) 'synced': synced,
      if (isDeleted != null) 'is_deleted': isDeleted,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (etag != null) 'etag': etag,
      if (serverUpdatedAt != null) 'server_updated_at': serverUpdatedAt,
    });
  }

  TestFieldsCompanion copyWith({
    Value<String>? id,
    Value<String?>? remoteId,
    Value<String>? tenantId,
    Value<String?>? farmId,
    Value<String>? name,
    Value<String?>? cropType,
    Value<String>? boundary,
    Value<String?>? centroid,
    Value<double>? areaHectares,
    Value<String?>? status,
    Value<double?>? ndviCurrent,
    Value<DateTime?>? ndviUpdatedAt,
    Value<bool>? synced,
    Value<bool>? isDeleted,
    Value<DateTime>? createdAt,
    Value<DateTime>? updatedAt,
    Value<String?>? etag,
    Value<DateTime?>? serverUpdatedAt,
  }) {
    return TestFieldsCompanion(
      id: id ?? this.id,
      remoteId: remoteId ?? this.remoteId,
      tenantId: tenantId ?? this.tenantId,
      farmId: farmId ?? this.farmId,
      name: name ?? this.name,
      cropType: cropType ?? this.cropType,
      boundary: boundary ?? this.boundary,
      centroid: centroid ?? this.centroid,
      areaHectares: areaHectares ?? this.areaHectares,
      status: status ?? this.status,
      ndviCurrent: ndviCurrent ?? this.ndviCurrent,
      ndviUpdatedAt: ndviUpdatedAt ?? this.ndviUpdatedAt,
      synced: synced ?? this.synced,
      isDeleted: isDeleted ?? this.isDeleted,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      etag: etag ?? this.etag,
      serverUpdatedAt: serverUpdatedAt ?? this.serverUpdatedAt,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (remoteId.present) {
      map['remote_id'] = Variable<String?>(remoteId.value);
    }
    if (tenantId.present) {
      map['tenant_id'] = Variable<String>(tenantId.value);
    }
    if (farmId.present) {
      map['farm_id'] = Variable<String?>(farmId.value);
    }
    if (name.present) {
      map['name'] = Variable<String>(name.value);
    }
    if (cropType.present) {
      map['crop_type'] = Variable<String?>(cropType.value);
    }
    if (boundary.present) {
      map['boundary'] = Variable<String>(boundary.value);
    }
    if (centroid.present) {
      map['centroid'] = Variable<String?>(centroid.value);
    }
    if (areaHectares.present) {
      map['area_hectares'] = Variable<double>(areaHectares.value);
    }
    if (status.present) {
      map['status'] = Variable<String?>(status.value);
    }
    if (ndviCurrent.present) {
      map['ndvi_current'] = Variable<double?>(ndviCurrent.value);
    }
    if (ndviUpdatedAt.present) {
      map['ndvi_updated_at'] = Variable<DateTime?>(ndviUpdatedAt.value);
    }
    if (synced.present) {
      map['synced'] = Variable<bool>(synced.value);
    }
    if (isDeleted.present) {
      map['is_deleted'] = Variable<bool>(isDeleted.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (etag.present) {
      map['etag'] = Variable<String?>(etag.value);
    }
    if (serverUpdatedAt.present) {
      map['server_updated_at'] = Variable<DateTime?>(serverUpdatedAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('TestFieldsCompanion(')
          ..write('id: ${id}, ')
          ..write('remoteId: ${remoteId}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('farmId: ${farmId}, ')
          ..write('name: ${name}, ')
          ..write('cropType: ${cropType}, ')
          ..write('boundary: ${boundary}, ')
          ..write('centroid: ${centroid}, ')
          ..write('areaHectares: ${areaHectares}, ')
          ..write('status: ${status}, ')
          ..write('ndviCurrent: ${ndviCurrent}, ')
          ..write('ndviUpdatedAt: ${ndviUpdatedAt}, ')
          ..write('synced: ${synced}, ')
          ..write('isDeleted: ${isDeleted}, ')
          ..write('createdAt: ${createdAt}, ')
          ..write('updatedAt: ${updatedAt}, ')
          ..write('etag: ${etag}, ')
          ..write('serverUpdatedAt: ${serverUpdatedAt}')
          ..write(')')
      ).toString();
  }
}

class \$TestFieldsTable extends TestFields
    with TableInfo<\$TestFieldsTable, TestField> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  \$TestFieldsTable(this.attachedDatabase, [this._alias]);

  static const VerificationMeta _idMeta = VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id =
      GeneratedColumn<String>(
          'id', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _remoteIdMeta = VerificationMeta('remoteId');
  @override
  late final GeneratedColumn<String> remoteId =
      GeneratedColumn<String>(
          'remote_id', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _tenantIdMeta = VerificationMeta('tenantId');
  @override
  late final GeneratedColumn<String> tenantId =
      GeneratedColumn<String>(
          'tenant_id', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _farmIdMeta = VerificationMeta('farmId');
  @override
  late final GeneratedColumn<String> farmId =
      GeneratedColumn<String>(
          'farm_id', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _nameMeta = VerificationMeta('name');
  @override
  late final GeneratedColumn<String> name =
      GeneratedColumn<String>(
          'name', aliasedName, false,
          additionalChecks: GeneratedColumn.checkTextLength(
              minTextLength: 1,
              maxTextLength: 100),
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _cropTypeMeta = VerificationMeta('cropType');
  @override
  late final GeneratedColumn<String> cropType =
      GeneratedColumn<String>(
          'crop_type', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _boundaryMeta = VerificationMeta('boundary');
  @override
  late final GeneratedColumn<String> boundary =
      GeneratedColumn<String>(
          'boundary', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _centroidMeta = VerificationMeta('centroid');
  @override
  late final GeneratedColumn<String> centroid =
      GeneratedColumn<String>(
          'centroid', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _areaHectaresMeta = VerificationMeta('areaHectares');
  @override
  late final GeneratedColumn<double> areaHectares =
      GeneratedColumn<double>(
          'area_hectares', aliasedName, false,
          type: DriftSqlType.double,
          requiredDuringInsert: true);

  static const VerificationMeta _statusMeta = VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status =
      GeneratedColumn<String>(
          'status', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _ndviCurrentMeta = VerificationMeta('ndviCurrent');
  @override
  late final GeneratedColumn<double> ndviCurrent =
      GeneratedColumn<double>(
          'ndvi_current', aliasedName, true,
          type: DriftSqlType.double,
          requiredDuringInsert: false);

  static const VerificationMeta _ndviUpdatedAtMeta = VerificationMeta('ndviUpdatedAt');
  @override
  late final GeneratedColumn<DateTime> ndviUpdatedAt =
      GeneratedColumn<DateTime>(
          'ndvi_updated_at', aliasedName, true,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: false);

  static const VerificationMeta _syncedMeta = VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced =
      GeneratedColumn<bool>(
          'synced', aliasedName, false,
          defaultValue: const Constant(false),
          type: DriftSqlType.bool,
          requiredDuringInsert: false);

  static const VerificationMeta _isDeletedMeta = VerificationMeta('isDeleted');
  @override
  late final GeneratedColumn<bool> isDeleted =
      GeneratedColumn<bool>(
          'is_deleted', aliasedName, false,
          defaultValue: const Constant(false),
          type: DriftSqlType.bool,
          requiredDuringInsert: false);

  static const VerificationMeta _createdAtMeta = VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt =
      GeneratedColumn<DateTime>(
          'created_at', aliasedName, false,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: true);

  static const VerificationMeta _updatedAtMeta = VerificationMeta('updatedAt');
  @override
  late final GeneratedColumn<DateTime> updatedAt =
      GeneratedColumn<DateTime>(
          'updated_at', aliasedName, false,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: true);

  static const VerificationMeta _etagMeta = VerificationMeta('etag');
  @override
  late final GeneratedColumn<String> etag =
      GeneratedColumn<String>(
          'etag', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _serverUpdatedAtMeta = VerificationMeta('serverUpdatedAt');
  @override
  late final GeneratedColumn<DateTime> serverUpdatedAt =
      GeneratedColumn<DateTime>(
          'server_updated_at', aliasedName, true,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: false);

  @override
  List<GeneratedColumn> get $columns => [id, remoteId, tenantId, farmId, name, cropType, boundary, centroid, areaHectares, status, ndviCurrent, ndviUpdatedAt, synced, isDeleted, createdAt, updatedAt, etag, serverUpdatedAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String \$name = 'test_fields';

  @override
  VerificationContext validateIntegrity(Insertable<TestField> instance,
      {{bool isInserting = false}}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta,
          id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    else if (isInserting) {
      context.addError(_idMeta,
          const VerificationError('id must be provided when inserting.'));
    }
    if (data.containsKey('remote_id')) {
      context.handle(_remoteIdMeta,
          remoteId.isAcceptableOrUnknown(data['remote_id']!, _remoteIdMeta));
    }
    if (data.containsKey('tenant_id')) {
      context.handle(_tenantIdMeta,
          tenantId.isAcceptableOrUnknown(data['tenant_id']!, _tenantIdMeta));
    }
    else if (isInserting) {
      context.addError(_tenantIdMeta,
          const VerificationError('tenantId must be provided when inserting.'));
    }
    if (data.containsKey('farm_id')) {
      context.handle(_farmIdMeta,
          farmId.isAcceptableOrUnknown(data['farm_id']!, _farmIdMeta));
    }
    if (data.containsKey('name')) {
      context.handle(_nameMeta,
          name.isAcceptableOrUnknown(data['name']!, _nameMeta));
    }
    else if (isInserting) {
      context.addError(_nameMeta,
          const VerificationError('name must be provided when inserting.'));
    }
    if (data.containsKey('crop_type')) {
      context.handle(_cropTypeMeta,
          cropType.isAcceptableOrUnknown(data['crop_type']!, _cropTypeMeta));
    }
    if (data.containsKey('boundary')) {
      context.handle(_boundaryMeta,
          boundary.isAcceptableOrUnknown(data['boundary']!, _boundaryMeta));
    }
    else if (isInserting) {
      context.addError(_boundaryMeta,
          const VerificationError('boundary must be provided when inserting.'));
    }
    if (data.containsKey('centroid')) {
      context.handle(_centroidMeta,
          centroid.isAcceptableOrUnknown(data['centroid']!, _centroidMeta));
    }
    if (data.containsKey('area_hectares')) {
      context.handle(_areaHectaresMeta,
          areaHectares.isAcceptableOrUnknown(data['area_hectares']!, _areaHectaresMeta));
    }
    else if (isInserting) {
      context.addError(_areaHectaresMeta,
          const VerificationError('areaHectares must be provided when inserting.'));
    }
    if (data.containsKey('status')) {
      context.handle(_statusMeta,
          status.isAcceptableOrUnknown(data['status']!, _statusMeta));
    }
    if (data.containsKey('ndvi_current')) {
      context.handle(_ndviCurrentMeta,
          ndviCurrent.isAcceptableOrUnknown(data['ndvi_current']!, _ndviCurrentMeta));
    }
    if (data.containsKey('ndvi_updated_at')) {
      context.handle(_ndviUpdatedAtMeta,
          ndviUpdatedAt.isAcceptableOrUnknown(data['ndvi_updated_at']!, _ndviUpdatedAtMeta));
    }
    if (data.containsKey('synced')) {
      context.handle(_syncedMeta,
          synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta));
    }
    if (data.containsKey('is_deleted')) {
      context.handle(_isDeletedMeta,
          isDeleted.isAcceptableOrUnknown(data['is_deleted']!, _isDeletedMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    else if (isInserting) {
      context.addError(_createdAtMeta,
          const VerificationError('createdAt must be provided when inserting.'));
    }
    if (data.containsKey('updated_at')) {
      context.handle(_updatedAtMeta,
          updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta));
    }
    else if (isInserting) {
      context.addError(_updatedAtMeta,
          const VerificationError('updatedAt must be provided when inserting.'));
    }
    if (data.containsKey('etag')) {
      context.handle(_etagMeta,
          etag.isAcceptableOrUnknown(data['etag']!, _etagMeta));
    }
    if (data.containsKey('server_updated_at')) {
      context.handle(_serverUpdatedAtMeta,
          serverUpdatedAt.isAcceptableOrUnknown(data['server_updated_at']!, _serverUpdatedAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};

  @override
  TestField map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '\$tablePrefix.' : '';
    return TestField(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}id'])!,
      remoteId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}remote_id']),
      tenantId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}tenant_id'])!,
      farmId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}farm_id']),
      name: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}name'])!,
      cropType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}crop_type']),
      boundary: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}boundary'])!,
      centroid: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}centroid']),
      areaHectares: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}area_hectares'])!,
      status: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}status']),
      ndviCurrent: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}ndvi_current']),
      ndviUpdatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}ndvi_updated_at']),
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['\${effectivePrefix}synced'])!,
      isDeleted: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['\${effectivePrefix}is_deleted'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}created_at'])!,
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}updated_at'])!,
      etag: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}etag']),
      serverUpdatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}server_updated_at']),
    );
  }

  @override
  \$TestFieldsTable createAlias(String alias) {
    return \$TestFieldsTable(attachedDatabase, alias);
  }
}

class TestSyncLog extends DataClass implements Insertable<TestSyncLog> {
  final int id;
  final String type;
  final String status;
  final String? message;
  final DateTime timestamp;

  const TestSyncLog({
    this.id,
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

  factory TestSyncLog.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return TestSyncLog(
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

  TestSyncLog copyWith({
    int? id,
    String? type,
    String? status,
    Value<String> message = const Value.absent(),
    DateTime? timestamp,
  }) {
    return TestSyncLog(
      id: id ?? this.id,
      type: type ?? this.type,
      status: status ?? this.status,
      message: message.present ? message.value : this.message,
      timestamp: timestamp ?? this.timestamp,
    );
  }

  @override
  String toString() {
    return (StringBuffer('TestSyncLog(')
          ..write('id: ${id}, ')
          ..write('type: ${type}, ')
          ..write('status: ${status}, ')
          ..write('message: ${message}, ')
          ..write('timestamp: ${timestamp}')
          ..write(')')
      ).toString();
  }

  @override
  int get hashCode => Object.hash(id, type, status, message, timestamp);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is TestSyncLog &&
          other.id == this.id &&
          other.type == this.type &&
          other.status == this.status &&
          other.message == this.message &&
          other.timestamp == this.timestamp)
  ;
}

class TestSyncLogsCompanion extends UpdateCompanion<TestSyncLog> {
  final Value<int> id;
  final Value<String> type;
  final Value<String> status;
  final Value<String?> message;
  final Value<DateTime> timestamp;

  const TestSyncLogsCompanion({
    this.id = const Value.absent(),
    this.type = const Value.absent(),
    this.status = const Value.absent(),
    this.message = const Value.absent(),
    this.timestamp = const Value.absent(),
  });

  TestSyncLogsCompanion.insert({
    this.id = const Value.absent(),
    required String type,
    required String status,
    Value<String?> message = const Value.absent(),
    required DateTime timestamp,
  })
      : type = Value(type),
        status = Value(status),
        timestamp = Value(timestamp);

  static Insertable<TestSyncLog> custom({
    Expression<dynamic>? id,
    Expression<dynamic>? type,
    Expression<dynamic>? status,
    Expression<dynamic>? message,
    Expression<dynamic>? timestamp,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (type != null) 'type': type,
      if (status != null) 'status': status,
      if (message != null) 'message': message,
      if (timestamp != null) 'timestamp': timestamp,
    });
  }

  TestSyncLogsCompanion copyWith({
    Value<int>? id,
    Value<String>? type,
    Value<String>? status,
    Value<String?>? message,
    Value<DateTime>? timestamp,
  }) {
    return TestSyncLogsCompanion(
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
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (type.present) {
      map['type'] = Variable<String>(type.value);
    }
    if (status.present) {
      map['status'] = Variable<String>(status.value);
    }
    if (message.present) {
      map['message'] = Variable<String?>(message.value);
    }
    if (timestamp.present) {
      map['timestamp'] = Variable<DateTime>(timestamp.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('TestSyncLogsCompanion(')
          ..write('id: ${id}, ')
          ..write('type: ${type}, ')
          ..write('status: ${status}, ')
          ..write('message: ${message}, ')
          ..write('timestamp: ${timestamp}')
          ..write(')')
      ).toString();
  }
}

class \$TestSyncLogsTable extends TestSyncLogs
    with TableInfo<\$TestSyncLogsTable, TestSyncLog> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  \$TestSyncLogsTable(this.attachedDatabase, [this._alias]);

  static const VerificationMeta _idMeta = VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id =
      GeneratedColumn<int>(
          'id', aliasedName, false,
          hasAutoIncrement: true,
          type: DriftSqlType.int,
          requiredDuringInsert: false);

  static const VerificationMeta _typeMeta = VerificationMeta('type');
  @override
  late final GeneratedColumn<String> type =
      GeneratedColumn<String>(
          'type', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _statusMeta = VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status =
      GeneratedColumn<String>(
          'status', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _messageMeta = VerificationMeta('message');
  @override
  late final GeneratedColumn<String> message =
      GeneratedColumn<String>(
          'message', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _timestampMeta = VerificationMeta('timestamp');
  @override
  late final GeneratedColumn<DateTime> timestamp =
      GeneratedColumn<DateTime>(
          'timestamp', aliasedName, false,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: true);

  @override
  List<GeneratedColumn> get $columns => [id, type, status, message, timestamp];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String \$name = 'test_sync_logs';

  @override
  VerificationContext validateIntegrity(Insertable<TestSyncLog> instance,
      {{bool isInserting = false}}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta,
          id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('type')) {
      context.handle(_typeMeta,
          type.isAcceptableOrUnknown(data['type']!, _typeMeta));
    }
    else if (isInserting) {
      context.addError(_typeMeta,
          const VerificationError('type must be provided when inserting.'));
    }
    if (data.containsKey('status')) {
      context.handle(_statusMeta,
          status.isAcceptableOrUnknown(data['status']!, _statusMeta));
    }
    else if (isInserting) {
      context.addError(_statusMeta,
          const VerificationError('status must be provided when inserting.'));
    }
    if (data.containsKey('message')) {
      context.handle(_messageMeta,
          message.isAcceptableOrUnknown(data['message']!, _messageMeta));
    }
    if (data.containsKey('timestamp')) {
      context.handle(_timestampMeta,
          timestamp.isAcceptableOrUnknown(data['timestamp']!, _timestampMeta));
    }
    else if (isInserting) {
      context.addError(_timestampMeta,
          const VerificationError('timestamp must be provided when inserting.'));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};

  @override
  TestSyncLog map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '\$tablePrefix.' : '';
    return TestSyncLog(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['\${effectivePrefix}id'])!,
      type: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}type'])!,
      status: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}status'])!,
      message: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}message']),
      timestamp: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}timestamp'])!,
    );
  }

  @override
  \$TestSyncLogsTable createAlias(String alias) {
    return \$TestSyncLogsTable(attachedDatabase, alias);
  }
}

class TestSyncEvent extends DataClass implements Insertable<TestSyncEvent> {
  final int id;
  final String tenantId;
  final String type;
  final String? entityType;
  final String? entityId;
  final String message;
  final bool isRead;
  final DateTime createdAt;

  const TestSyncEvent({
    this.id,
    required this.tenantId,
    required this.type,
    this.entityType,
    this.entityId,
    required this.message,
    this.isRead,
    this.createdAt,
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

  factory TestSyncEvent.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return TestSyncEvent(
      id: serializer.fromJson<int>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenant_id']),
      type: serializer.fromJson<String>(json['type']),
      entityType: serializer.fromJson<String?>(json['entity_type']),
      entityId: serializer.fromJson<String?>(json['entity_id']),
      message: serializer.fromJson<String>(json['message']),
      isRead: serializer.fromJson<bool>(json['is_read']),
      createdAt: serializer.fromJson<DateTime>(json['created_at']),
    );
  }

  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'tenant_id': serializer.toJson<String>(tenantId),
      'type': serializer.toJson<String>(type),
      'entity_type': serializer.toJson<String?>(entityType),
      'entity_id': serializer.toJson<String?>(entityId),
      'message': serializer.toJson<String>(message),
      'is_read': serializer.toJson<bool>(isRead),
      'created_at': serializer.toJson<DateTime>(createdAt),
    };
  }

  TestSyncEvent copyWith({
    int? id,
    String? tenantId,
    String? type,
    Value<String> entityType = const Value.absent(),
    Value<String> entityId = const Value.absent(),
    String? message,
    bool? isRead,
    DateTime? createdAt,
  }) {
    return TestSyncEvent(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      type: type ?? this.type,
      entityType: entityType.present ? entityType.value : this.entityType,
      entityId: entityId.present ? entityId.value : this.entityId,
      message: message ?? this.message,
      isRead: isRead ?? this.isRead,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('TestSyncEvent(')
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('type: ${type}, ')
          ..write('entityType: ${entityType}, ')
          ..write('entityId: ${entityId}, ')
          ..write('message: ${message}, ')
          ..write('isRead: ${isRead}, ')
          ..write('createdAt: ${createdAt}')
          ..write(')')
      ).toString();
  }

  @override
  int get hashCode => Object.hash(id, tenantId, type, entityType, entityId, message, isRead, createdAt);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is TestSyncEvent &&
          other.id == this.id &&
          other.tenantId == this.tenantId &&
          other.type == this.type &&
          other.entityType == this.entityType &&
          other.entityId == this.entityId &&
          other.message == this.message &&
          other.isRead == this.isRead &&
          other.createdAt == this.createdAt)
  ;
}

class TestSyncEventsCompanion extends UpdateCompanion<TestSyncEvent> {
  final Value<int> id;
  final Value<String> tenantId;
  final Value<String> type;
  final Value<String?> entityType;
  final Value<String?> entityId;
  final Value<String> message;
  final Value<bool> isRead;
  final Value<DateTime> createdAt;

  const TestSyncEventsCompanion({
    this.id = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.type = const Value.absent(),
    this.entityType = const Value.absent(),
    this.entityId = const Value.absent(),
    this.message = const Value.absent(),
    this.isRead = const Value.absent(),
    this.createdAt = const Value.absent(),
  });

  TestSyncEventsCompanion.insert({
    this.id = const Value.absent(),
    required String tenantId,
    required String type,
    Value<String?> entityType = const Value.absent(),
    Value<String?> entityId = const Value.absent(),
    required String message,
    Value<bool> isRead = const Value.absent(),
    Value<DateTime> createdAt = const Value.absent(),
  })
      : tenantId = Value(tenantId),
        type = Value(type),
        message = Value(message);

  static Insertable<TestSyncEvent> custom({
    Expression<dynamic>? id,
    Expression<dynamic>? tenantId,
    Expression<dynamic>? type,
    Expression<dynamic>? entityType,
    Expression<dynamic>? entityId,
    Expression<dynamic>? message,
    Expression<dynamic>? isRead,
    Expression<dynamic>? createdAt,
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

  TestSyncEventsCompanion copyWith({
    Value<int>? id,
    Value<String>? tenantId,
    Value<String>? type,
    Value<String?>? entityType,
    Value<String?>? entityId,
    Value<String>? message,
    Value<bool>? isRead,
    Value<DateTime>? createdAt,
  }) {
    return TestSyncEventsCompanion(
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
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (tenantId.present) {
      map['tenant_id'] = Variable<String>(tenantId.value);
    }
    if (type.present) {
      map['type'] = Variable<String>(type.value);
    }
    if (entityType.present) {
      map['entity_type'] = Variable<String?>(entityType.value);
    }
    if (entityId.present) {
      map['entity_id'] = Variable<String?>(entityId.value);
    }
    if (message.present) {
      map['message'] = Variable<String>(message.value);
    }
    if (isRead.present) {
      map['is_read'] = Variable<bool>(isRead.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('TestSyncEventsCompanion(')
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('type: ${type}, ')
          ..write('entityType: ${entityType}, ')
          ..write('entityId: ${entityId}, ')
          ..write('message: ${message}, ')
          ..write('isRead: ${isRead}, ')
          ..write('createdAt: ${createdAt}')
          ..write(')')
      ).toString();
  }
}

class \$TestSyncEventsTable extends TestSyncEvents
    with TableInfo<\$TestSyncEventsTable, TestSyncEvent> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  \$TestSyncEventsTable(this.attachedDatabase, [this._alias]);

  static const VerificationMeta _idMeta = VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id =
      GeneratedColumn<int>(
          'id', aliasedName, false,
          hasAutoIncrement: true,
          type: DriftSqlType.int,
          requiredDuringInsert: false);

  static const VerificationMeta _tenantIdMeta = VerificationMeta('tenantId');
  @override
  late final GeneratedColumn<String> tenantId =
      GeneratedColumn<String>(
          'tenant_id', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _typeMeta = VerificationMeta('type');
  @override
  late final GeneratedColumn<String> type =
      GeneratedColumn<String>(
          'type', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _entityTypeMeta = VerificationMeta('entityType');
  @override
  late final GeneratedColumn<String> entityType =
      GeneratedColumn<String>(
          'entity_type', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _entityIdMeta = VerificationMeta('entityId');
  @override
  late final GeneratedColumn<String> entityId =
      GeneratedColumn<String>(
          'entity_id', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _messageMeta = VerificationMeta('message');
  @override
  late final GeneratedColumn<String> message =
      GeneratedColumn<String>(
          'message', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _isReadMeta = VerificationMeta('isRead');
  @override
  late final GeneratedColumn<bool> isRead =
      GeneratedColumn<bool>(
          'is_read', aliasedName, false,
          defaultValue: const Constant(false),
          type: DriftSqlType.bool,
          requiredDuringInsert: false);

  static const VerificationMeta _createdAtMeta = VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt =
      GeneratedColumn<DateTime>(
          'created_at', aliasedName, false,
          defaultValue: currentDateAndTime,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: false);

  @override
  List<GeneratedColumn> get $columns => [id, tenantId, type, entityType, entityId, message, isRead, createdAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String \$name = 'test_sync_events';

  @override
  VerificationContext validateIntegrity(Insertable<TestSyncEvent> instance,
      {{bool isInserting = false}}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta,
          id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('tenant_id')) {
      context.handle(_tenantIdMeta,
          tenantId.isAcceptableOrUnknown(data['tenant_id']!, _tenantIdMeta));
    }
    else if (isInserting) {
      context.addError(_tenantIdMeta,
          const VerificationError('tenantId must be provided when inserting.'));
    }
    if (data.containsKey('type')) {
      context.handle(_typeMeta,
          type.isAcceptableOrUnknown(data['type']!, _typeMeta));
    }
    else if (isInserting) {
      context.addError(_typeMeta,
          const VerificationError('type must be provided when inserting.'));
    }
    if (data.containsKey('entity_type')) {
      context.handle(_entityTypeMeta,
          entityType.isAcceptableOrUnknown(data['entity_type']!, _entityTypeMeta));
    }
    if (data.containsKey('entity_id')) {
      context.handle(_entityIdMeta,
          entityId.isAcceptableOrUnknown(data['entity_id']!, _entityIdMeta));
    }
    if (data.containsKey('message')) {
      context.handle(_messageMeta,
          message.isAcceptableOrUnknown(data['message']!, _messageMeta));
    }
    else if (isInserting) {
      context.addError(_messageMeta,
          const VerificationError('message must be provided when inserting.'));
    }
    if (data.containsKey('is_read')) {
      context.handle(_isReadMeta,
          isRead.isAcceptableOrUnknown(data['is_read']!, _isReadMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};

  @override
  TestSyncEvent map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '\$tablePrefix.' : '';
    return TestSyncEvent(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['\${effectivePrefix}id'])!,
      tenantId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}tenant_id'])!,
      type: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}type'])!,
      entityType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}entity_type']),
      entityId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}entity_id']),
      message: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}message'])!,
      isRead: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['\${effectivePrefix}is_read'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}created_at'])!,
    );
  }

  @override
  \$TestSyncEventsTable createAlias(String alias) {
    return \$TestSyncEventsTable(attachedDatabase, alias);
  }
}

abstract class _\$TestDatabase extends GeneratedDatabase {
  _\$TestDatabase(QueryExecutor e) : super(e);

  late final \$TestTasksTable testTasks = \$TestTasksTable(this);
  late final \$TestOutboxTable testOutbox = \$TestOutboxTable(this);
  late final \$TestFieldsTable testFields = \$TestFieldsTable(this);
  late final \$TestSyncLogsTable testSyncLogs = \$TestSyncLogsTable(this);
  late final \$TestSyncEventsTable testSyncEvents = \$TestSyncEventsTable(this);

  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
    testTasks,
    testOutbox,
    testFields,
    testSyncLogs,
    testSyncEvents,
  ];
}
