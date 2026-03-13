// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'migration_integration_test.dart';

// ignore_for_file: type=lint

// **************************************************************************
// DriftDatabaseGenerator
// **************************************************************************

class TestTask extends DataClass implements Insertable<TestTask> {
  final String id;
  final String tenantId;
  final String fieldId;
  final String title;
  final String status;
  final DateTime createdAt;
  final DateTime updatedAt;
  final bool synced;

  const TestTask({
    required this.id,
    required this.tenantId,
    required this.fieldId,
    required this.title,
    this.status,
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
    map['title'] = Variable<String>(title);
    map['status'] = Variable<String>(status);
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
      title: serializer.fromJson<String>(json['title']),
      status: serializer.fromJson<String>(json['status']),
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
      'title': serializer.toJson<String>(title),
      'status': serializer.toJson<String>(status),
      'created_at': serializer.toJson<DateTime>(createdAt),
      'updated_at': serializer.toJson<DateTime>(updatedAt),
      'synced': serializer.toJson<bool>(synced),
    };
  }

  TestTask copyWith({
    String? id,
    String? tenantId,
    String? fieldId,
    String? title,
    String? status,
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? synced,
  }) {
    return TestTask(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      fieldId: fieldId ?? this.fieldId,
      title: title ?? this.title,
      status: status ?? this.status,
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
          ..write('title: ${title}, ')
          ..write('status: ${status}, ')
          ..write('createdAt: ${createdAt}, ')
          ..write('updatedAt: ${updatedAt}, ')
          ..write('synced: ${synced}')
          ..write(')')
      ).toString();
  }

  @override
  int get hashCode => Object.hash(id, tenantId, fieldId, title, status, createdAt, updatedAt, synced);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is TestTask &&
          other.id == this.id &&
          other.tenantId == this.tenantId &&
          other.fieldId == this.fieldId &&
          other.title == this.title &&
          other.status == this.status &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt &&
          other.synced == this.synced)
  ;
}

class TestTasksCompanion extends UpdateCompanion<TestTask> {
  final Value<String> id;
  final Value<String> tenantId;
  final Value<String> fieldId;
  final Value<String> title;
  final Value<String> status;
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;
  final Value<bool> synced;

  const TestTasksCompanion({
    this.id = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.fieldId = const Value.absent(),
    this.title = const Value.absent(),
    this.status = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.synced = const Value.absent(),
  });

  TestTasksCompanion.insert({
    required String id,
    required String tenantId,
    required String fieldId,
    required String title,
    Value<String> status = const Value.absent(),
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
    Expression<dynamic>? title,
    Expression<dynamic>? status,
    Expression<dynamic>? createdAt,
    Expression<dynamic>? updatedAt,
    Expression<dynamic>? synced,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (tenantId != null) 'tenant_id': tenantId,
      if (fieldId != null) 'field_id': fieldId,
      if (title != null) 'title': title,
      if (status != null) 'status': status,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (synced != null) 'synced': synced,
    });
  }

  TestTasksCompanion copyWith({
    Value<String>? id,
    Value<String>? tenantId,
    Value<String>? fieldId,
    Value<String>? title,
    Value<String>? status,
    Value<DateTime>? createdAt,
    Value<DateTime>? updatedAt,
    Value<bool>? synced,
  }) {
    return TestTasksCompanion(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      fieldId: fieldId ?? this.fieldId,
      title: title ?? this.title,
      status: status ?? this.status,
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
    if (title.present) {
      map['title'] = Variable<String>(title.value);
    }
    if (status.present) {
      map['status'] = Variable<String>(status.value);
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
          ..write('title: ${title}, ')
          ..write('status: ${status}, ')
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

  static const VerificationMeta _titleMeta = VerificationMeta('title');
  @override
  late final GeneratedColumn<String> title =
      GeneratedColumn<String>(
          'title', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _statusMeta = VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status =
      GeneratedColumn<String>(
          'status', aliasedName, false,
          defaultValue: const Constant('open'),
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
  List<GeneratedColumn> get $columns => [id, tenantId, fieldId, title, status, createdAt, updatedAt, synced];
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
    if (data.containsKey('title')) {
      context.handle(_titleMeta,
          title.isAcceptableOrUnknown(data['title']!, _titleMeta));
    }
    else if (isInserting) {
      context.addError(_titleMeta,
          const VerificationError('title must be provided when inserting.'));
    }
    if (data.containsKey('status')) {
      context.handle(_statusMeta,
          status.isAcceptableOrUnknown(data['status']!, _statusMeta));
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
      title: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}title'])!,
      status: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}status'])!,
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
          ..write('isSynced: ${isSynced}, ')
          ..write('createdAt: ${createdAt}')
          ..write(')')
      ).toString();
  }

  @override
  int get hashCode => Object.hash(id, tenantId, entityType, entityId, apiEndpoint, method, payload, isSynced, createdAt);

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
  List<GeneratedColumn> get $columns => [id, tenantId, entityType, entityId, apiEndpoint, method, payload, isSynced, createdAt];
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
  final String tenantId;
  final String name;
  final String boundary;
  final double areaHectares;
  final bool synced;
  final DateTime createdAt;
  final DateTime updatedAt;

  const TestField({
    required this.id,
    required this.tenantId,
    required this.name,
    required this.boundary,
    required this.areaHectares,
    this.synced,
    required this.createdAt,
    required this.updatedAt,
  });

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['tenant_id'] = Variable<String>(tenantId);
    map['name'] = Variable<String>(name);
    map['boundary'] = Variable<String>(boundary);
    map['area_hectares'] = Variable<double>(areaHectares);
    map['synced'] = Variable<bool>(synced);
    map['created_at'] = Variable<DateTime>(createdAt);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    return map;
  }

  factory TestField.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return TestField(
      id: serializer.fromJson<String>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenant_id']),
      name: serializer.fromJson<String>(json['name']),
      boundary: serializer.fromJson<String>(json['boundary']),
      areaHectares: serializer.fromJson<double>(json['area_hectares']),
      synced: serializer.fromJson<bool>(json['synced']),
      createdAt: serializer.fromJson<DateTime>(json['created_at']),
      updatedAt: serializer.fromJson<DateTime>(json['updated_at']),
    );
  }

  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'tenant_id': serializer.toJson<String>(tenantId),
      'name': serializer.toJson<String>(name),
      'boundary': serializer.toJson<String>(boundary),
      'area_hectares': serializer.toJson<double>(areaHectares),
      'synced': serializer.toJson<bool>(synced),
      'created_at': serializer.toJson<DateTime>(createdAt),
      'updated_at': serializer.toJson<DateTime>(updatedAt),
    };
  }

  TestField copyWith({
    String? id,
    String? tenantId,
    String? name,
    String? boundary,
    double? areaHectares,
    bool? synced,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return TestField(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      name: name ?? this.name,
      boundary: boundary ?? this.boundary,
      areaHectares: areaHectares ?? this.areaHectares,
      synced: synced ?? this.synced,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('TestField(')
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('name: ${name}, ')
          ..write('boundary: ${boundary}, ')
          ..write('areaHectares: ${areaHectares}, ')
          ..write('synced: ${synced}, ')
          ..write('createdAt: ${createdAt}, ')
          ..write('updatedAt: ${updatedAt}')
          ..write(')')
      ).toString();
  }

  @override
  int get hashCode => Object.hash(id, tenantId, name, boundary, areaHectares, synced, createdAt, updatedAt);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is TestField &&
          other.id == this.id &&
          other.tenantId == this.tenantId &&
          other.name == this.name &&
          other.boundary == this.boundary &&
          other.areaHectares == this.areaHectares &&
          other.synced == this.synced &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt)
  ;
}

class TestFieldsCompanion extends UpdateCompanion<TestField> {
  final Value<String> id;
  final Value<String> tenantId;
  final Value<String> name;
  final Value<String> boundary;
  final Value<double> areaHectares;
  final Value<bool> synced;
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;

  const TestFieldsCompanion({
    this.id = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.name = const Value.absent(),
    this.boundary = const Value.absent(),
    this.areaHectares = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
  });

  TestFieldsCompanion.insert({
    required String id,
    required String tenantId,
    required String name,
    required String boundary,
    required double areaHectares,
    Value<bool> synced = const Value.absent(),
    required DateTime createdAt,
    required DateTime updatedAt,
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
    Expression<dynamic>? tenantId,
    Expression<dynamic>? name,
    Expression<dynamic>? boundary,
    Expression<dynamic>? areaHectares,
    Expression<dynamic>? synced,
    Expression<dynamic>? createdAt,
    Expression<dynamic>? updatedAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (tenantId != null) 'tenant_id': tenantId,
      if (name != null) 'name': name,
      if (boundary != null) 'boundary': boundary,
      if (areaHectares != null) 'area_hectares': areaHectares,
      if (synced != null) 'synced': synced,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
    });
  }

  TestFieldsCompanion copyWith({
    Value<String>? id,
    Value<String>? tenantId,
    Value<String>? name,
    Value<String>? boundary,
    Value<double>? areaHectares,
    Value<bool>? synced,
    Value<DateTime>? createdAt,
    Value<DateTime>? updatedAt,
  }) {
    return TestFieldsCompanion(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      name: name ?? this.name,
      boundary: boundary ?? this.boundary,
      areaHectares: areaHectares ?? this.areaHectares,
      synced: synced ?? this.synced,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
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
    if (name.present) {
      map['name'] = Variable<String>(name.value);
    }
    if (boundary.present) {
      map['boundary'] = Variable<String>(boundary.value);
    }
    if (areaHectares.present) {
      map['area_hectares'] = Variable<double>(areaHectares.value);
    }
    if (synced.present) {
      map['synced'] = Variable<bool>(synced.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('TestFieldsCompanion(')
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('name: ${name}, ')
          ..write('boundary: ${boundary}, ')
          ..write('areaHectares: ${areaHectares}, ')
          ..write('synced: ${synced}, ')
          ..write('createdAt: ${createdAt}, ')
          ..write('updatedAt: ${updatedAt}')
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

  static const VerificationMeta _tenantIdMeta = VerificationMeta('tenantId');
  @override
  late final GeneratedColumn<String> tenantId =
      GeneratedColumn<String>(
          'tenant_id', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _nameMeta = VerificationMeta('name');
  @override
  late final GeneratedColumn<String> name =
      GeneratedColumn<String>(
          'name', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _boundaryMeta = VerificationMeta('boundary');
  @override
  late final GeneratedColumn<String> boundary =
      GeneratedColumn<String>(
          'boundary', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _areaHectaresMeta = VerificationMeta('areaHectares');
  @override
  late final GeneratedColumn<double> areaHectares =
      GeneratedColumn<double>(
          'area_hectares', aliasedName, false,
          type: DriftSqlType.double,
          requiredDuringInsert: true);

  static const VerificationMeta _syncedMeta = VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced =
      GeneratedColumn<bool>(
          'synced', aliasedName, false,
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

  @override
  List<GeneratedColumn> get $columns => [id, tenantId, name, boundary, areaHectares, synced, createdAt, updatedAt];
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
    if (data.containsKey('tenant_id')) {
      context.handle(_tenantIdMeta,
          tenantId.isAcceptableOrUnknown(data['tenant_id']!, _tenantIdMeta));
    }
    else if (isInserting) {
      context.addError(_tenantIdMeta,
          const VerificationError('tenantId must be provided when inserting.'));
    }
    if (data.containsKey('name')) {
      context.handle(_nameMeta,
          name.isAcceptableOrUnknown(data['name']!, _nameMeta));
    }
    else if (isInserting) {
      context.addError(_nameMeta,
          const VerificationError('name must be provided when inserting.'));
    }
    if (data.containsKey('boundary')) {
      context.handle(_boundaryMeta,
          boundary.isAcceptableOrUnknown(data['boundary']!, _boundaryMeta));
    }
    else if (isInserting) {
      context.addError(_boundaryMeta,
          const VerificationError('boundary must be provided when inserting.'));
    }
    if (data.containsKey('area_hectares')) {
      context.handle(_areaHectaresMeta,
          areaHectares.isAcceptableOrUnknown(data['area_hectares']!, _areaHectaresMeta));
    }
    else if (isInserting) {
      context.addError(_areaHectaresMeta,
          const VerificationError('areaHectares must be provided when inserting.'));
    }
    if (data.containsKey('synced')) {
      context.handle(_syncedMeta,
          synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta));
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
      tenantId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}tenant_id'])!,
      name: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}name'])!,
      boundary: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}boundary'])!,
      areaHectares: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}area_hectares'])!,
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['\${effectivePrefix}synced'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}created_at'])!,
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}updated_at'])!,
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
  final String message;
  final bool isRead;
  final DateTime createdAt;

  const TestSyncEvent({
    this.id,
    required this.tenantId,
    required this.type,
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
      'message': serializer.toJson<String>(message),
      'is_read': serializer.toJson<bool>(isRead),
      'created_at': serializer.toJson<DateTime>(createdAt),
    };
  }

  TestSyncEvent copyWith({
    int? id,
    String? tenantId,
    String? type,
    String? message,
    bool? isRead,
    DateTime? createdAt,
  }) {
    return TestSyncEvent(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      type: type ?? this.type,
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
          ..write('message: ${message}, ')
          ..write('isRead: ${isRead}, ')
          ..write('createdAt: ${createdAt}')
          ..write(')')
      ).toString();
  }

  @override
  int get hashCode => Object.hash(id, tenantId, type, message, isRead, createdAt);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is TestSyncEvent &&
          other.id == this.id &&
          other.tenantId == this.tenantId &&
          other.type == this.type &&
          other.message == this.message &&
          other.isRead == this.isRead &&
          other.createdAt == this.createdAt)
  ;
}

class TestSyncEventsCompanion extends UpdateCompanion<TestSyncEvent> {
  final Value<int> id;
  final Value<String> tenantId;
  final Value<String> type;
  final Value<String> message;
  final Value<bool> isRead;
  final Value<DateTime> createdAt;

  const TestSyncEventsCompanion({
    this.id = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.type = const Value.absent(),
    this.message = const Value.absent(),
    this.isRead = const Value.absent(),
    this.createdAt = const Value.absent(),
  });

  TestSyncEventsCompanion.insert({
    this.id = const Value.absent(),
    required String tenantId,
    required String type,
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
    Expression<dynamic>? message,
    Expression<dynamic>? isRead,
    Expression<dynamic>? createdAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (tenantId != null) 'tenant_id': tenantId,
      if (type != null) 'type': type,
      if (message != null) 'message': message,
      if (isRead != null) 'is_read': isRead,
      if (createdAt != null) 'created_at': createdAt,
    });
  }

  TestSyncEventsCompanion copyWith({
    Value<int>? id,
    Value<String>? tenantId,
    Value<String>? type,
    Value<String>? message,
    Value<bool>? isRead,
    Value<DateTime>? createdAt,
  }) {
    return TestSyncEventsCompanion(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      type: type ?? this.type,
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
  List<GeneratedColumn> get $columns => [id, tenantId, type, message, isRead, createdAt];
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
