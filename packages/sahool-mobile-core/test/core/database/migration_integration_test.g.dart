// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'migration_integration_test.dart';

// ignore_for_file: type=lint
class $TestTasksTable extends TestTasks
    with TableInfo<$TestTasksTable, TestTask> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $TestTasksTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _tenantIdMeta =
      const VerificationMeta('tenantId');
  @override
  late final GeneratedColumn<String> tenantId = GeneratedColumn<String>(
      'tenant_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _fieldIdMeta =
      const VerificationMeta('fieldId');
  @override
  late final GeneratedColumn<String> fieldId = GeneratedColumn<String>(
      'field_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _titleMeta = const VerificationMeta('title');
  @override
  late final GeneratedColumn<String> title = GeneratedColumn<String>(
      'title', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _statusMeta = const VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status = GeneratedColumn<String>(
      'status', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('open'));
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  static const VerificationMeta _updatedAtMeta =
      const VerificationMeta('updatedAt');
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
      'updated_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  static const VerificationMeta _syncedMeta = const VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>(
      'synced', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("synced" IN (0, 1))'),
      defaultValue: const Constant(false));
  @override
  List<GeneratedColumn> get $columns =>
      [id, tenantId, fieldId, title, status, createdAt, updatedAt, synced];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'test_tasks';
  @override
  VerificationContext validateIntegrity(Insertable<TestTask> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('tenant_id')) {
      context.handle(_tenantIdMeta,
          tenantId.isAcceptableOrUnknown(data['tenant_id']!, _tenantIdMeta));
    } else if (isInserting) {
      context.missing(_tenantIdMeta);
    }
    if (data.containsKey('field_id')) {
      context.handle(_fieldIdMeta,
          fieldId.isAcceptableOrUnknown(data['field_id']!, _fieldIdMeta));
    } else if (isInserting) {
      context.missing(_fieldIdMeta);
    }
    if (data.containsKey('title')) {
      context.handle(
          _titleMeta, title.isAcceptableOrUnknown(data['title']!, _titleMeta));
    } else if (isInserting) {
      context.missing(_titleMeta);
    }
    if (data.containsKey('status')) {
      context.handle(_statusMeta,
          status.isAcceptableOrUnknown(data['status']!, _statusMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    } else if (isInserting) {
      context.missing(_createdAtMeta);
    }
    if (data.containsKey('updated_at')) {
      context.handle(_updatedAtMeta,
          updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta));
    } else if (isInserting) {
      context.missing(_updatedAtMeta);
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
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return TestTask(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      tenantId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}tenant_id'])!,
      fieldId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}field_id'])!,
      title: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}title'])!,
      status: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}status'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}updated_at'])!,
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
    );
  }

  @override
  $TestTasksTable createAlias(String alias) {
    return $TestTasksTable(attachedDatabase, alias);
  }
}

class TestTask extends DataClass implements Insertable<TestTask> {
  final String id;
  final String tenantId;
  final String fieldId;
  final String title;
  final String status;
  final DateTime createdAt;
  final DateTime updatedAt;
  final bool synced;
  const TestTask(
      {required this.id,
      required this.tenantId,
      required this.fieldId,
      required this.title,
      required this.status,
      required this.createdAt,
      required this.updatedAt,
      required this.synced});
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

  TestTasksCompanion toCompanion(bool nullToAbsent) {
    return TestTasksCompanion(
      id: Value(id),
      tenantId: Value(tenantId),
      fieldId: Value(fieldId),
      title: Value(title),
      status: Value(status),
      createdAt: Value(createdAt),
      updatedAt: Value(updatedAt),
      synced: Value(synced),
    );
  }

  factory TestTask.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return TestTask(
      id: serializer.fromJson<String>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenantId']),
      fieldId: serializer.fromJson<String>(json['fieldId']),
      title: serializer.fromJson<String>(json['title']),
      status: serializer.fromJson<String>(json['status']),
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
      'title': serializer.toJson<String>(title),
      'status': serializer.toJson<String>(status),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
      'synced': serializer.toJson<bool>(synced),
    };
  }

  TestTask copyWith(
          {String? id,
          String? tenantId,
          String? fieldId,
          String? title,
          String? status,
          DateTime? createdAt,
          DateTime? updatedAt,
          bool? synced}) =>
      TestTask(
        id: id ?? this.id,
        tenantId: tenantId ?? this.tenantId,
        fieldId: fieldId ?? this.fieldId,
        title: title ?? this.title,
        status: status ?? this.status,
        createdAt: createdAt ?? this.createdAt,
        updatedAt: updatedAt ?? this.updatedAt,
        synced: synced ?? this.synced,
      );
  TestTask copyWithCompanion(TestTasksCompanion data) {
    return TestTask(
      id: data.id.present ? data.id.value : this.id,
      tenantId: data.tenantId.present ? data.tenantId.value : this.tenantId,
      fieldId: data.fieldId.present ? data.fieldId.value : this.fieldId,
      title: data.title.present ? data.title.value : this.title,
      status: data.status.present ? data.status.value : this.status,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
      synced: data.synced.present ? data.synced.value : this.synced,
    );
  }

  @override
  String toString() {
    return (StringBuffer('TestTask(')
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('fieldId: $fieldId, ')
          ..write('title: $title, ')
          ..write('status: $status, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('synced: $synced')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id, tenantId, fieldId, title, status, createdAt, updatedAt, synced);
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
          other.synced == this.synced);
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
  final Value<int> rowid;
  const TestTasksCompanion({
    this.id = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.fieldId = const Value.absent(),
    this.title = const Value.absent(),
    this.status = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.synced = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  TestTasksCompanion.insert({
    required String id,
    required String tenantId,
    required String fieldId,
    required String title,
    this.status = const Value.absent(),
    required DateTime createdAt,
    required DateTime updatedAt,
    this.synced = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        tenantId = Value(tenantId),
        fieldId = Value(fieldId),
        title = Value(title),
        createdAt = Value(createdAt),
        updatedAt = Value(updatedAt);
  static Insertable<TestTask> custom({
    Expression<String>? id,
    Expression<String>? tenantId,
    Expression<String>? fieldId,
    Expression<String>? title,
    Expression<String>? status,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<bool>? synced,
    Expression<int>? rowid,
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
      if (rowid != null) 'rowid': rowid,
    });
  }

  TestTasksCompanion copyWith(
      {Value<String>? id,
      Value<String>? tenantId,
      Value<String>? fieldId,
      Value<String>? title,
      Value<String>? status,
      Value<DateTime>? createdAt,
      Value<DateTime>? updatedAt,
      Value<bool>? synced,
      Value<int>? rowid}) {
    return TestTasksCompanion(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      fieldId: fieldId ?? this.fieldId,
      title: title ?? this.title,
      status: status ?? this.status,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      synced: synced ?? this.synced,
      rowid: rowid ?? this.rowid,
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
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('TestTasksCompanion(')
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('fieldId: $fieldId, ')
          ..write('title: $title, ')
          ..write('status: $status, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('synced: $synced, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $TestOutboxTable extends TestOutbox
    with TableInfo<$TestOutboxTable, TestOutboxData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $TestOutboxTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _tenantIdMeta =
      const VerificationMeta('tenantId');
  @override
  late final GeneratedColumn<String> tenantId = GeneratedColumn<String>(
      'tenant_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _entityTypeMeta =
      const VerificationMeta('entityType');
  @override
  late final GeneratedColumn<String> entityType = GeneratedColumn<String>(
      'entity_type', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _entityIdMeta =
      const VerificationMeta('entityId');
  @override
  late final GeneratedColumn<String> entityId = GeneratedColumn<String>(
      'entity_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _apiEndpointMeta =
      const VerificationMeta('apiEndpoint');
  @override
  late final GeneratedColumn<String> apiEndpoint = GeneratedColumn<String>(
      'api_endpoint', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _methodMeta = const VerificationMeta('method');
  @override
  late final GeneratedColumn<String> method = GeneratedColumn<String>(
      'method', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('POST'));
  static const VerificationMeta _payloadMeta =
      const VerificationMeta('payload');
  @override
  late final GeneratedColumn<String> payload = GeneratedColumn<String>(
      'payload', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _isSyncedMeta =
      const VerificationMeta('isSynced');
  @override
  late final GeneratedColumn<bool> isSynced = GeneratedColumn<bool>(
      'is_synced', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("is_synced" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        tenantId,
        entityType,
        entityId,
        apiEndpoint,
        method,
        payload,
        isSynced,
        createdAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'test_outbox';
  @override
  VerificationContext validateIntegrity(Insertable<TestOutboxData> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('tenant_id')) {
      context.handle(_tenantIdMeta,
          tenantId.isAcceptableOrUnknown(data['tenant_id']!, _tenantIdMeta));
    } else if (isInserting) {
      context.missing(_tenantIdMeta);
    }
    if (data.containsKey('entity_type')) {
      context.handle(
          _entityTypeMeta,
          entityType.isAcceptableOrUnknown(
              data['entity_type']!, _entityTypeMeta));
    } else if (isInserting) {
      context.missing(_entityTypeMeta);
    }
    if (data.containsKey('entity_id')) {
      context.handle(_entityIdMeta,
          entityId.isAcceptableOrUnknown(data['entity_id']!, _entityIdMeta));
    } else if (isInserting) {
      context.missing(_entityIdMeta);
    }
    if (data.containsKey('api_endpoint')) {
      context.handle(
          _apiEndpointMeta,
          apiEndpoint.isAcceptableOrUnknown(
              data['api_endpoint']!, _apiEndpointMeta));
    } else if (isInserting) {
      context.missing(_apiEndpointMeta);
    }
    if (data.containsKey('method')) {
      context.handle(_methodMeta,
          method.isAcceptableOrUnknown(data['method']!, _methodMeta));
    }
    if (data.containsKey('payload')) {
      context.handle(_payloadMeta,
          payload.isAcceptableOrUnknown(data['payload']!, _payloadMeta));
    } else if (isInserting) {
      context.missing(_payloadMeta);
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
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return TestOutboxData(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      tenantId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}tenant_id'])!,
      entityType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}entity_type'])!,
      entityId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}entity_id'])!,
      apiEndpoint: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}api_endpoint'])!,
      method: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}method'])!,
      payload: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}payload'])!,
      isSynced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}is_synced'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $TestOutboxTable createAlias(String alias) {
    return $TestOutboxTable(attachedDatabase, alias);
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
  const TestOutboxData(
      {required this.id,
      required this.tenantId,
      required this.entityType,
      required this.entityId,
      required this.apiEndpoint,
      required this.method,
      required this.payload,
      required this.isSynced,
      required this.createdAt});
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

  TestOutboxCompanion toCompanion(bool nullToAbsent) {
    return TestOutboxCompanion(
      id: Value(id),
      tenantId: Value(tenantId),
      entityType: Value(entityType),
      entityId: Value(entityId),
      apiEndpoint: Value(apiEndpoint),
      method: Value(method),
      payload: Value(payload),
      isSynced: Value(isSynced),
      createdAt: Value(createdAt),
    );
  }

  factory TestOutboxData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return TestOutboxData(
      id: serializer.fromJson<int>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenantId']),
      entityType: serializer.fromJson<String>(json['entityType']),
      entityId: serializer.fromJson<String>(json['entityId']),
      apiEndpoint: serializer.fromJson<String>(json['apiEndpoint']),
      method: serializer.fromJson<String>(json['method']),
      payload: serializer.fromJson<String>(json['payload']),
      isSynced: serializer.fromJson<bool>(json['isSynced']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'tenantId': serializer.toJson<String>(tenantId),
      'entityType': serializer.toJson<String>(entityType),
      'entityId': serializer.toJson<String>(entityId),
      'apiEndpoint': serializer.toJson<String>(apiEndpoint),
      'method': serializer.toJson<String>(method),
      'payload': serializer.toJson<String>(payload),
      'isSynced': serializer.toJson<bool>(isSynced),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  TestOutboxData copyWith(
          {int? id,
          String? tenantId,
          String? entityType,
          String? entityId,
          String? apiEndpoint,
          String? method,
          String? payload,
          bool? isSynced,
          DateTime? createdAt}) =>
      TestOutboxData(
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
  TestOutboxData copyWithCompanion(TestOutboxCompanion data) {
    return TestOutboxData(
      id: data.id.present ? data.id.value : this.id,
      tenantId: data.tenantId.present ? data.tenantId.value : this.tenantId,
      entityType:
          data.entityType.present ? data.entityType.value : this.entityType,
      entityId: data.entityId.present ? data.entityId.value : this.entityId,
      apiEndpoint:
          data.apiEndpoint.present ? data.apiEndpoint.value : this.apiEndpoint,
      method: data.method.present ? data.method.value : this.method,
      payload: data.payload.present ? data.payload.value : this.payload,
      isSynced: data.isSynced.present ? data.isSynced.value : this.isSynced,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('TestOutboxData(')
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('entityType: $entityType, ')
          ..write('entityId: $entityId, ')
          ..write('apiEndpoint: $apiEndpoint, ')
          ..write('method: $method, ')
          ..write('payload: $payload, ')
          ..write('isSynced: $isSynced, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, tenantId, entityType, entityId,
      apiEndpoint, method, payload, isSynced, createdAt);
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
          other.createdAt == this.createdAt);
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
    this.method = const Value.absent(),
    required String payload,
    this.isSynced = const Value.absent(),
    this.createdAt = const Value.absent(),
  })  : tenantId = Value(tenantId),
        entityType = Value(entityType),
        entityId = Value(entityId),
        apiEndpoint = Value(apiEndpoint),
        payload = Value(payload);
  static Insertable<TestOutboxData> custom({
    Expression<int>? id,
    Expression<String>? tenantId,
    Expression<String>? entityType,
    Expression<String>? entityId,
    Expression<String>? apiEndpoint,
    Expression<String>? method,
    Expression<String>? payload,
    Expression<bool>? isSynced,
    Expression<DateTime>? createdAt,
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

  TestOutboxCompanion copyWith(
      {Value<int>? id,
      Value<String>? tenantId,
      Value<String>? entityType,
      Value<String>? entityId,
      Value<String>? apiEndpoint,
      Value<String>? method,
      Value<String>? payload,
      Value<bool>? isSynced,
      Value<DateTime>? createdAt}) {
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
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('entityType: $entityType, ')
          ..write('entityId: $entityId, ')
          ..write('apiEndpoint: $apiEndpoint, ')
          ..write('method: $method, ')
          ..write('payload: $payload, ')
          ..write('isSynced: $isSynced, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }
}

class $TestFieldsTable extends TestFields
    with TableInfo<$TestFieldsTable, TestField> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $TestFieldsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _tenantIdMeta =
      const VerificationMeta('tenantId');
  @override
  late final GeneratedColumn<String> tenantId = GeneratedColumn<String>(
      'tenant_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _nameMeta = const VerificationMeta('name');
  @override
  late final GeneratedColumn<String> name = GeneratedColumn<String>(
      'name', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _boundaryMeta =
      const VerificationMeta('boundary');
  @override
  late final GeneratedColumn<String> boundary = GeneratedColumn<String>(
      'boundary', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _areaHectaresMeta =
      const VerificationMeta('areaHectares');
  @override
  late final GeneratedColumn<double> areaHectares = GeneratedColumn<double>(
      'area_hectares', aliasedName, false,
      type: DriftSqlType.double, requiredDuringInsert: true);
  static const VerificationMeta _syncedMeta = const VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>(
      'synced', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("synced" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  static const VerificationMeta _updatedAtMeta =
      const VerificationMeta('updatedAt');
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
      'updated_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        tenantId,
        name,
        boundary,
        areaHectares,
        synced,
        createdAt,
        updatedAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'test_fields';
  @override
  VerificationContext validateIntegrity(Insertable<TestField> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('tenant_id')) {
      context.handle(_tenantIdMeta,
          tenantId.isAcceptableOrUnknown(data['tenant_id']!, _tenantIdMeta));
    } else if (isInserting) {
      context.missing(_tenantIdMeta);
    }
    if (data.containsKey('name')) {
      context.handle(
          _nameMeta, name.isAcceptableOrUnknown(data['name']!, _nameMeta));
    } else if (isInserting) {
      context.missing(_nameMeta);
    }
    if (data.containsKey('boundary')) {
      context.handle(_boundaryMeta,
          boundary.isAcceptableOrUnknown(data['boundary']!, _boundaryMeta));
    } else if (isInserting) {
      context.missing(_boundaryMeta);
    }
    if (data.containsKey('area_hectares')) {
      context.handle(
          _areaHectaresMeta,
          areaHectares.isAcceptableOrUnknown(
              data['area_hectares']!, _areaHectaresMeta));
    } else if (isInserting) {
      context.missing(_areaHectaresMeta);
    }
    if (data.containsKey('synced')) {
      context.handle(_syncedMeta,
          synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    } else if (isInserting) {
      context.missing(_createdAtMeta);
    }
    if (data.containsKey('updated_at')) {
      context.handle(_updatedAtMeta,
          updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta));
    } else if (isInserting) {
      context.missing(_updatedAtMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  TestField map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return TestField(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      tenantId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}tenant_id'])!,
      name: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}name'])!,
      boundary: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boundary'])!,
      areaHectares: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}area_hectares'])!,
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}updated_at'])!,
    );
  }

  @override
  $TestFieldsTable createAlias(String alias) {
    return $TestFieldsTable(attachedDatabase, alias);
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
  const TestField(
      {required this.id,
      required this.tenantId,
      required this.name,
      required this.boundary,
      required this.areaHectares,
      required this.synced,
      required this.createdAt,
      required this.updatedAt});
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

  TestFieldsCompanion toCompanion(bool nullToAbsent) {
    return TestFieldsCompanion(
      id: Value(id),
      tenantId: Value(tenantId),
      name: Value(name),
      boundary: Value(boundary),
      areaHectares: Value(areaHectares),
      synced: Value(synced),
      createdAt: Value(createdAt),
      updatedAt: Value(updatedAt),
    );
  }

  factory TestField.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return TestField(
      id: serializer.fromJson<String>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenantId']),
      name: serializer.fromJson<String>(json['name']),
      boundary: serializer.fromJson<String>(json['boundary']),
      areaHectares: serializer.fromJson<double>(json['areaHectares']),
      synced: serializer.fromJson<bool>(json['synced']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'tenantId': serializer.toJson<String>(tenantId),
      'name': serializer.toJson<String>(name),
      'boundary': serializer.toJson<String>(boundary),
      'areaHectares': serializer.toJson<double>(areaHectares),
      'synced': serializer.toJson<bool>(synced),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
    };
  }

  TestField copyWith(
          {String? id,
          String? tenantId,
          String? name,
          String? boundary,
          double? areaHectares,
          bool? synced,
          DateTime? createdAt,
          DateTime? updatedAt}) =>
      TestField(
        id: id ?? this.id,
        tenantId: tenantId ?? this.tenantId,
        name: name ?? this.name,
        boundary: boundary ?? this.boundary,
        areaHectares: areaHectares ?? this.areaHectares,
        synced: synced ?? this.synced,
        createdAt: createdAt ?? this.createdAt,
        updatedAt: updatedAt ?? this.updatedAt,
      );
  TestField copyWithCompanion(TestFieldsCompanion data) {
    return TestField(
      id: data.id.present ? data.id.value : this.id,
      tenantId: data.tenantId.present ? data.tenantId.value : this.tenantId,
      name: data.name.present ? data.name.value : this.name,
      boundary: data.boundary.present ? data.boundary.value : this.boundary,
      areaHectares: data.areaHectares.present
          ? data.areaHectares.value
          : this.areaHectares,
      synced: data.synced.present ? data.synced.value : this.synced,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('TestField(')
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('name: $name, ')
          ..write('boundary: $boundary, ')
          ..write('areaHectares: $areaHectares, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id, tenantId, name, boundary, areaHectares, synced, createdAt, updatedAt);
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
          other.updatedAt == this.updatedAt);
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
  final Value<int> rowid;
  const TestFieldsCompanion({
    this.id = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.name = const Value.absent(),
    this.boundary = const Value.absent(),
    this.areaHectares = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  TestFieldsCompanion.insert({
    required String id,
    required String tenantId,
    required String name,
    required String boundary,
    required double areaHectares,
    this.synced = const Value.absent(),
    required DateTime createdAt,
    required DateTime updatedAt,
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        tenantId = Value(tenantId),
        name = Value(name),
        boundary = Value(boundary),
        areaHectares = Value(areaHectares),
        createdAt = Value(createdAt),
        updatedAt = Value(updatedAt);
  static Insertable<TestField> custom({
    Expression<String>? id,
    Expression<String>? tenantId,
    Expression<String>? name,
    Expression<String>? boundary,
    Expression<double>? areaHectares,
    Expression<bool>? synced,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<int>? rowid,
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
      if (rowid != null) 'rowid': rowid,
    });
  }

  TestFieldsCompanion copyWith(
      {Value<String>? id,
      Value<String>? tenantId,
      Value<String>? name,
      Value<String>? boundary,
      Value<double>? areaHectares,
      Value<bool>? synced,
      Value<DateTime>? createdAt,
      Value<DateTime>? updatedAt,
      Value<int>? rowid}) {
    return TestFieldsCompanion(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      name: name ?? this.name,
      boundary: boundary ?? this.boundary,
      areaHectares: areaHectares ?? this.areaHectares,
      synced: synced ?? this.synced,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      rowid: rowid ?? this.rowid,
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
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('TestFieldsCompanion(')
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('name: $name, ')
          ..write('boundary: $boundary, ')
          ..write('areaHectares: $areaHectares, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $TestSyncLogsTable extends TestSyncLogs
    with TableInfo<$TestSyncLogsTable, TestSyncLog> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $TestSyncLogsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _typeMeta = const VerificationMeta('type');
  @override
  late final GeneratedColumn<String> type = GeneratedColumn<String>(
      'type', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _statusMeta = const VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status = GeneratedColumn<String>(
      'status', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _messageMeta =
      const VerificationMeta('message');
  @override
  late final GeneratedColumn<String> message = GeneratedColumn<String>(
      'message', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _timestampMeta =
      const VerificationMeta('timestamp');
  @override
  late final GeneratedColumn<DateTime> timestamp = GeneratedColumn<DateTime>(
      'timestamp', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  @override
  List<GeneratedColumn> get $columns => [id, type, status, message, timestamp];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'test_sync_logs';
  @override
  VerificationContext validateIntegrity(Insertable<TestSyncLog> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('type')) {
      context.handle(
          _typeMeta, type.isAcceptableOrUnknown(data['type']!, _typeMeta));
    } else if (isInserting) {
      context.missing(_typeMeta);
    }
    if (data.containsKey('status')) {
      context.handle(_statusMeta,
          status.isAcceptableOrUnknown(data['status']!, _statusMeta));
    } else if (isInserting) {
      context.missing(_statusMeta);
    }
    if (data.containsKey('message')) {
      context.handle(_messageMeta,
          message.isAcceptableOrUnknown(data['message']!, _messageMeta));
    }
    if (data.containsKey('timestamp')) {
      context.handle(_timestampMeta,
          timestamp.isAcceptableOrUnknown(data['timestamp']!, _timestampMeta));
    } else if (isInserting) {
      context.missing(_timestampMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  TestSyncLog map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return TestSyncLog(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      type: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}type'])!,
      status: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}status'])!,
      message: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}message']),
      timestamp: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}timestamp'])!,
    );
  }

  @override
  $TestSyncLogsTable createAlias(String alias) {
    return $TestSyncLogsTable(attachedDatabase, alias);
  }
}

class TestSyncLog extends DataClass implements Insertable<TestSyncLog> {
  final int id;
  final String type;
  final String status;
  final String? message;
  final DateTime timestamp;
  const TestSyncLog(
      {required this.id,
      required this.type,
      required this.status,
      this.message,
      required this.timestamp});
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

  TestSyncLogsCompanion toCompanion(bool nullToAbsent) {
    return TestSyncLogsCompanion(
      id: Value(id),
      type: Value(type),
      status: Value(status),
      message: message == null && nullToAbsent
          ? const Value.absent()
          : Value(message),
      timestamp: Value(timestamp),
    );
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

  TestSyncLog copyWith(
          {int? id,
          String? type,
          String? status,
          Value<String?> message = const Value.absent(),
          DateTime? timestamp}) =>
      TestSyncLog(
        id: id ?? this.id,
        type: type ?? this.type,
        status: status ?? this.status,
        message: message.present ? message.value : this.message,
        timestamp: timestamp ?? this.timestamp,
      );
  TestSyncLog copyWithCompanion(TestSyncLogsCompanion data) {
    return TestSyncLog(
      id: data.id.present ? data.id.value : this.id,
      type: data.type.present ? data.type.value : this.type,
      status: data.status.present ? data.status.value : this.status,
      message: data.message.present ? data.message.value : this.message,
      timestamp: data.timestamp.present ? data.timestamp.value : this.timestamp,
    );
  }

  @override
  String toString() {
    return (StringBuffer('TestSyncLog(')
          ..write('id: $id, ')
          ..write('type: $type, ')
          ..write('status: $status, ')
          ..write('message: $message, ')
          ..write('timestamp: $timestamp')
          ..write(')'))
        .toString();
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
          other.timestamp == this.timestamp);
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
    this.message = const Value.absent(),
    required DateTime timestamp,
  })  : type = Value(type),
        status = Value(status),
        timestamp = Value(timestamp);
  static Insertable<TestSyncLog> custom({
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

  TestSyncLogsCompanion copyWith(
      {Value<int>? id,
      Value<String>? type,
      Value<String>? status,
      Value<String?>? message,
      Value<DateTime>? timestamp}) {
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
      map['message'] = Variable<String>(message.value);
    }
    if (timestamp.present) {
      map['timestamp'] = Variable<DateTime>(timestamp.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('TestSyncLogsCompanion(')
          ..write('id: $id, ')
          ..write('type: $type, ')
          ..write('status: $status, ')
          ..write('message: $message, ')
          ..write('timestamp: $timestamp')
          ..write(')'))
        .toString();
  }
}

class $TestSyncEventsTable extends TestSyncEvents
    with TableInfo<$TestSyncEventsTable, TestSyncEvent> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $TestSyncEventsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _tenantIdMeta =
      const VerificationMeta('tenantId');
  @override
  late final GeneratedColumn<String> tenantId = GeneratedColumn<String>(
      'tenant_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _typeMeta = const VerificationMeta('type');
  @override
  late final GeneratedColumn<String> type = GeneratedColumn<String>(
      'type', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _messageMeta =
      const VerificationMeta('message');
  @override
  late final GeneratedColumn<String> message = GeneratedColumn<String>(
      'message', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _isReadMeta = const VerificationMeta('isRead');
  @override
  late final GeneratedColumn<bool> isRead = GeneratedColumn<bool>(
      'is_read', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("is_read" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  @override
  List<GeneratedColumn> get $columns =>
      [id, tenantId, type, message, isRead, createdAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'test_sync_events';
  @override
  VerificationContext validateIntegrity(Insertable<TestSyncEvent> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('tenant_id')) {
      context.handle(_tenantIdMeta,
          tenantId.isAcceptableOrUnknown(data['tenant_id']!, _tenantIdMeta));
    } else if (isInserting) {
      context.missing(_tenantIdMeta);
    }
    if (data.containsKey('type')) {
      context.handle(
          _typeMeta, type.isAcceptableOrUnknown(data['type']!, _typeMeta));
    } else if (isInserting) {
      context.missing(_typeMeta);
    }
    if (data.containsKey('message')) {
      context.handle(_messageMeta,
          message.isAcceptableOrUnknown(data['message']!, _messageMeta));
    } else if (isInserting) {
      context.missing(_messageMeta);
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
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return TestSyncEvent(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      tenantId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}tenant_id'])!,
      type: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}type'])!,
      message: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}message'])!,
      isRead: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}is_read'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $TestSyncEventsTable createAlias(String alias) {
    return $TestSyncEventsTable(attachedDatabase, alias);
  }
}

class TestSyncEvent extends DataClass implements Insertable<TestSyncEvent> {
  final int id;
  final String tenantId;
  final String type;
  final String message;
  final bool isRead;
  final DateTime createdAt;
  const TestSyncEvent(
      {required this.id,
      required this.tenantId,
      required this.type,
      required this.message,
      required this.isRead,
      required this.createdAt});
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

  TestSyncEventsCompanion toCompanion(bool nullToAbsent) {
    return TestSyncEventsCompanion(
      id: Value(id),
      tenantId: Value(tenantId),
      type: Value(type),
      message: Value(message),
      isRead: Value(isRead),
      createdAt: Value(createdAt),
    );
  }

  factory TestSyncEvent.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return TestSyncEvent(
      id: serializer.fromJson<int>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenantId']),
      type: serializer.fromJson<String>(json['type']),
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
      'message': serializer.toJson<String>(message),
      'isRead': serializer.toJson<bool>(isRead),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  TestSyncEvent copyWith(
          {int? id,
          String? tenantId,
          String? type,
          String? message,
          bool? isRead,
          DateTime? createdAt}) =>
      TestSyncEvent(
        id: id ?? this.id,
        tenantId: tenantId ?? this.tenantId,
        type: type ?? this.type,
        message: message ?? this.message,
        isRead: isRead ?? this.isRead,
        createdAt: createdAt ?? this.createdAt,
      );
  TestSyncEvent copyWithCompanion(TestSyncEventsCompanion data) {
    return TestSyncEvent(
      id: data.id.present ? data.id.value : this.id,
      tenantId: data.tenantId.present ? data.tenantId.value : this.tenantId,
      type: data.type.present ? data.type.value : this.type,
      message: data.message.present ? data.message.value : this.message,
      isRead: data.isRead.present ? data.isRead.value : this.isRead,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('TestSyncEvent(')
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('type: $type, ')
          ..write('message: $message, ')
          ..write('isRead: $isRead, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode =>
      Object.hash(id, tenantId, type, message, isRead, createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is TestSyncEvent &&
          other.id == this.id &&
          other.tenantId == this.tenantId &&
          other.type == this.type &&
          other.message == this.message &&
          other.isRead == this.isRead &&
          other.createdAt == this.createdAt);
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
    this.isRead = const Value.absent(),
    this.createdAt = const Value.absent(),
  })  : tenantId = Value(tenantId),
        type = Value(type),
        message = Value(message);
  static Insertable<TestSyncEvent> custom({
    Expression<int>? id,
    Expression<String>? tenantId,
    Expression<String>? type,
    Expression<String>? message,
    Expression<bool>? isRead,
    Expression<DateTime>? createdAt,
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

  TestSyncEventsCompanion copyWith(
      {Value<int>? id,
      Value<String>? tenantId,
      Value<String>? type,
      Value<String>? message,
      Value<bool>? isRead,
      Value<DateTime>? createdAt}) {
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
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('type: $type, ')
          ..write('message: $message, ')
          ..write('isRead: $isRead, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }
}

abstract class _$TestDatabase extends GeneratedDatabase {
  _$TestDatabase(QueryExecutor e) : super(e);
  $TestDatabaseManager get managers => $TestDatabaseManager(this);
  late final $TestTasksTable testTasks = $TestTasksTable(this);
  late final $TestOutboxTable testOutbox = $TestOutboxTable(this);
  late final $TestFieldsTable testFields = $TestFieldsTable(this);
  late final $TestSyncLogsTable testSyncLogs = $TestSyncLogsTable(this);
  late final $TestSyncEventsTable testSyncEvents = $TestSyncEventsTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities =>
      [testTasks, testOutbox, testFields, testSyncLogs, testSyncEvents];
  @override
  DriftDatabaseOptions get options =>
      const DriftDatabaseOptions(storeDateTimeAsText: true);
}

typedef $$TestTasksTableCreateCompanionBuilder = TestTasksCompanion Function({
  required String id,
  required String tenantId,
  required String fieldId,
  required String title,
  Value<String> status,
  required DateTime createdAt,
  required DateTime updatedAt,
  Value<bool> synced,
  Value<int> rowid,
});
typedef $$TestTasksTableUpdateCompanionBuilder = TestTasksCompanion Function({
  Value<String> id,
  Value<String> tenantId,
  Value<String> fieldId,
  Value<String> title,
  Value<String> status,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<bool> synced,
  Value<int> rowid,
});

class $$TestTasksTableFilterComposer
    extends Composer<_$TestDatabase, $TestTasksTable> {
  $$TestTasksTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get tenantId => $composableBuilder(
      column: $table.tenantId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get fieldId => $composableBuilder(
      column: $table.fieldId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get title => $composableBuilder(
      column: $table.title, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get status => $composableBuilder(
      column: $table.status, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnFilters(column));
}

class $$TestTasksTableOrderingComposer
    extends Composer<_$TestDatabase, $TestTasksTable> {
  $$TestTasksTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get tenantId => $composableBuilder(
      column: $table.tenantId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get fieldId => $composableBuilder(
      column: $table.fieldId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get title => $composableBuilder(
      column: $table.title, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get status => $composableBuilder(
      column: $table.status, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnOrderings(column));
}

class $$TestTasksTableAnnotationComposer
    extends Composer<_$TestDatabase, $TestTasksTable> {
  $$TestTasksTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get tenantId =>
      $composableBuilder(column: $table.tenantId, builder: (column) => column);

  GeneratedColumn<String> get fieldId =>
      $composableBuilder(column: $table.fieldId, builder: (column) => column);

  GeneratedColumn<String> get title =>
      $composableBuilder(column: $table.title, builder: (column) => column);

  GeneratedColumn<String> get status =>
      $composableBuilder(column: $table.status, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);
}

class $$TestTasksTableTableManager extends RootTableManager<
    _$TestDatabase,
    $TestTasksTable,
    TestTask,
    $$TestTasksTableFilterComposer,
    $$TestTasksTableOrderingComposer,
    $$TestTasksTableAnnotationComposer,
    $$TestTasksTableCreateCompanionBuilder,
    $$TestTasksTableUpdateCompanionBuilder,
    (TestTask, BaseReferences<_$TestDatabase, $TestTasksTable, TestTask>),
    TestTask,
    PrefetchHooks Function()> {
  $$TestTasksTableTableManager(_$TestDatabase db, $TestTasksTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$TestTasksTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$TestTasksTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$TestTasksTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> tenantId = const Value.absent(),
            Value<String> fieldId = const Value.absent(),
            Value<String> title = const Value.absent(),
            Value<String> status = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              TestTasksCompanion(
            id: id,
            tenantId: tenantId,
            fieldId: fieldId,
            title: title,
            status: status,
            createdAt: createdAt,
            updatedAt: updatedAt,
            synced: synced,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String tenantId,
            required String fieldId,
            required String title,
            Value<String> status = const Value.absent(),
            required DateTime createdAt,
            required DateTime updatedAt,
            Value<bool> synced = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              TestTasksCompanion.insert(
            id: id,
            tenantId: tenantId,
            fieldId: fieldId,
            title: title,
            status: status,
            createdAt: createdAt,
            updatedAt: updatedAt,
            synced: synced,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$TestTasksTableProcessedTableManager = ProcessedTableManager<
    _$TestDatabase,
    $TestTasksTable,
    TestTask,
    $$TestTasksTableFilterComposer,
    $$TestTasksTableOrderingComposer,
    $$TestTasksTableAnnotationComposer,
    $$TestTasksTableCreateCompanionBuilder,
    $$TestTasksTableUpdateCompanionBuilder,
    (TestTask, BaseReferences<_$TestDatabase, $TestTasksTable, TestTask>),
    TestTask,
    PrefetchHooks Function()>;
typedef $$TestOutboxTableCreateCompanionBuilder = TestOutboxCompanion Function({
  Value<int> id,
  required String tenantId,
  required String entityType,
  required String entityId,
  required String apiEndpoint,
  Value<String> method,
  required String payload,
  Value<bool> isSynced,
  Value<DateTime> createdAt,
});
typedef $$TestOutboxTableUpdateCompanionBuilder = TestOutboxCompanion Function({
  Value<int> id,
  Value<String> tenantId,
  Value<String> entityType,
  Value<String> entityId,
  Value<String> apiEndpoint,
  Value<String> method,
  Value<String> payload,
  Value<bool> isSynced,
  Value<DateTime> createdAt,
});

class $$TestOutboxTableFilterComposer
    extends Composer<_$TestDatabase, $TestOutboxTable> {
  $$TestOutboxTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get tenantId => $composableBuilder(
      column: $table.tenantId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get entityType => $composableBuilder(
      column: $table.entityType, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get entityId => $composableBuilder(
      column: $table.entityId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get apiEndpoint => $composableBuilder(
      column: $table.apiEndpoint, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get method => $composableBuilder(
      column: $table.method, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get payload => $composableBuilder(
      column: $table.payload, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get isSynced => $composableBuilder(
      column: $table.isSynced, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));
}

class $$TestOutboxTableOrderingComposer
    extends Composer<_$TestDatabase, $TestOutboxTable> {
  $$TestOutboxTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get tenantId => $composableBuilder(
      column: $table.tenantId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get entityType => $composableBuilder(
      column: $table.entityType, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get entityId => $composableBuilder(
      column: $table.entityId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get apiEndpoint => $composableBuilder(
      column: $table.apiEndpoint, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get method => $composableBuilder(
      column: $table.method, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get payload => $composableBuilder(
      column: $table.payload, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get isSynced => $composableBuilder(
      column: $table.isSynced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));
}

class $$TestOutboxTableAnnotationComposer
    extends Composer<_$TestDatabase, $TestOutboxTable> {
  $$TestOutboxTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get tenantId =>
      $composableBuilder(column: $table.tenantId, builder: (column) => column);

  GeneratedColumn<String> get entityType => $composableBuilder(
      column: $table.entityType, builder: (column) => column);

  GeneratedColumn<String> get entityId =>
      $composableBuilder(column: $table.entityId, builder: (column) => column);

  GeneratedColumn<String> get apiEndpoint => $composableBuilder(
      column: $table.apiEndpoint, builder: (column) => column);

  GeneratedColumn<String> get method =>
      $composableBuilder(column: $table.method, builder: (column) => column);

  GeneratedColumn<String> get payload =>
      $composableBuilder(column: $table.payload, builder: (column) => column);

  GeneratedColumn<bool> get isSynced =>
      $composableBuilder(column: $table.isSynced, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$TestOutboxTableTableManager extends RootTableManager<
    _$TestDatabase,
    $TestOutboxTable,
    TestOutboxData,
    $$TestOutboxTableFilterComposer,
    $$TestOutboxTableOrderingComposer,
    $$TestOutboxTableAnnotationComposer,
    $$TestOutboxTableCreateCompanionBuilder,
    $$TestOutboxTableUpdateCompanionBuilder,
    (
      TestOutboxData,
      BaseReferences<_$TestDatabase, $TestOutboxTable, TestOutboxData>
    ),
    TestOutboxData,
    PrefetchHooks Function()> {
  $$TestOutboxTableTableManager(_$TestDatabase db, $TestOutboxTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$TestOutboxTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$TestOutboxTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$TestOutboxTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> tenantId = const Value.absent(),
            Value<String> entityType = const Value.absent(),
            Value<String> entityId = const Value.absent(),
            Value<String> apiEndpoint = const Value.absent(),
            Value<String> method = const Value.absent(),
            Value<String> payload = const Value.absent(),
            Value<bool> isSynced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
          }) =>
              TestOutboxCompanion(
            id: id,
            tenantId: tenantId,
            entityType: entityType,
            entityId: entityId,
            apiEndpoint: apiEndpoint,
            method: method,
            payload: payload,
            isSynced: isSynced,
            createdAt: createdAt,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String tenantId,
            required String entityType,
            required String entityId,
            required String apiEndpoint,
            Value<String> method = const Value.absent(),
            required String payload,
            Value<bool> isSynced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
          }) =>
              TestOutboxCompanion.insert(
            id: id,
            tenantId: tenantId,
            entityType: entityType,
            entityId: entityId,
            apiEndpoint: apiEndpoint,
            method: method,
            payload: payload,
            isSynced: isSynced,
            createdAt: createdAt,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$TestOutboxTableProcessedTableManager = ProcessedTableManager<
    _$TestDatabase,
    $TestOutboxTable,
    TestOutboxData,
    $$TestOutboxTableFilterComposer,
    $$TestOutboxTableOrderingComposer,
    $$TestOutboxTableAnnotationComposer,
    $$TestOutboxTableCreateCompanionBuilder,
    $$TestOutboxTableUpdateCompanionBuilder,
    (
      TestOutboxData,
      BaseReferences<_$TestDatabase, $TestOutboxTable, TestOutboxData>
    ),
    TestOutboxData,
    PrefetchHooks Function()>;
typedef $$TestFieldsTableCreateCompanionBuilder = TestFieldsCompanion Function({
  required String id,
  required String tenantId,
  required String name,
  required String boundary,
  required double areaHectares,
  Value<bool> synced,
  required DateTime createdAt,
  required DateTime updatedAt,
  Value<int> rowid,
});
typedef $$TestFieldsTableUpdateCompanionBuilder = TestFieldsCompanion Function({
  Value<String> id,
  Value<String> tenantId,
  Value<String> name,
  Value<String> boundary,
  Value<double> areaHectares,
  Value<bool> synced,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});

class $$TestFieldsTableFilterComposer
    extends Composer<_$TestDatabase, $TestFieldsTable> {
  $$TestFieldsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get tenantId => $composableBuilder(
      column: $table.tenantId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get name => $composableBuilder(
      column: $table.name, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get boundary => $composableBuilder(
      column: $table.boundary, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get areaHectares => $composableBuilder(
      column: $table.areaHectares, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnFilters(column));
}

class $$TestFieldsTableOrderingComposer
    extends Composer<_$TestDatabase, $TestFieldsTable> {
  $$TestFieldsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get tenantId => $composableBuilder(
      column: $table.tenantId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get name => $composableBuilder(
      column: $table.name, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get boundary => $composableBuilder(
      column: $table.boundary, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get areaHectares => $composableBuilder(
      column: $table.areaHectares,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnOrderings(column));
}

class $$TestFieldsTableAnnotationComposer
    extends Composer<_$TestDatabase, $TestFieldsTable> {
  $$TestFieldsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get tenantId =>
      $composableBuilder(column: $table.tenantId, builder: (column) => column);

  GeneratedColumn<String> get name =>
      $composableBuilder(column: $table.name, builder: (column) => column);

  GeneratedColumn<String> get boundary =>
      $composableBuilder(column: $table.boundary, builder: (column) => column);

  GeneratedColumn<double> get areaHectares => $composableBuilder(
      column: $table.areaHectares, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);
}

class $$TestFieldsTableTableManager extends RootTableManager<
    _$TestDatabase,
    $TestFieldsTable,
    TestField,
    $$TestFieldsTableFilterComposer,
    $$TestFieldsTableOrderingComposer,
    $$TestFieldsTableAnnotationComposer,
    $$TestFieldsTableCreateCompanionBuilder,
    $$TestFieldsTableUpdateCompanionBuilder,
    (TestField, BaseReferences<_$TestDatabase, $TestFieldsTable, TestField>),
    TestField,
    PrefetchHooks Function()> {
  $$TestFieldsTableTableManager(_$TestDatabase db, $TestFieldsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$TestFieldsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$TestFieldsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$TestFieldsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> tenantId = const Value.absent(),
            Value<String> name = const Value.absent(),
            Value<String> boundary = const Value.absent(),
            Value<double> areaHectares = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              TestFieldsCompanion(
            id: id,
            tenantId: tenantId,
            name: name,
            boundary: boundary,
            areaHectares: areaHectares,
            synced: synced,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String tenantId,
            required String name,
            required String boundary,
            required double areaHectares,
            Value<bool> synced = const Value.absent(),
            required DateTime createdAt,
            required DateTime updatedAt,
            Value<int> rowid = const Value.absent(),
          }) =>
              TestFieldsCompanion.insert(
            id: id,
            tenantId: tenantId,
            name: name,
            boundary: boundary,
            areaHectares: areaHectares,
            synced: synced,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$TestFieldsTableProcessedTableManager = ProcessedTableManager<
    _$TestDatabase,
    $TestFieldsTable,
    TestField,
    $$TestFieldsTableFilterComposer,
    $$TestFieldsTableOrderingComposer,
    $$TestFieldsTableAnnotationComposer,
    $$TestFieldsTableCreateCompanionBuilder,
    $$TestFieldsTableUpdateCompanionBuilder,
    (TestField, BaseReferences<_$TestDatabase, $TestFieldsTable, TestField>),
    TestField,
    PrefetchHooks Function()>;
typedef $$TestSyncLogsTableCreateCompanionBuilder = TestSyncLogsCompanion
    Function({
  Value<int> id,
  required String type,
  required String status,
  Value<String?> message,
  required DateTime timestamp,
});
typedef $$TestSyncLogsTableUpdateCompanionBuilder = TestSyncLogsCompanion
    Function({
  Value<int> id,
  Value<String> type,
  Value<String> status,
  Value<String?> message,
  Value<DateTime> timestamp,
});

class $$TestSyncLogsTableFilterComposer
    extends Composer<_$TestDatabase, $TestSyncLogsTable> {
  $$TestSyncLogsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get type => $composableBuilder(
      column: $table.type, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get status => $composableBuilder(
      column: $table.status, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get message => $composableBuilder(
      column: $table.message, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get timestamp => $composableBuilder(
      column: $table.timestamp, builder: (column) => ColumnFilters(column));
}

class $$TestSyncLogsTableOrderingComposer
    extends Composer<_$TestDatabase, $TestSyncLogsTable> {
  $$TestSyncLogsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get type => $composableBuilder(
      column: $table.type, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get status => $composableBuilder(
      column: $table.status, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get message => $composableBuilder(
      column: $table.message, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get timestamp => $composableBuilder(
      column: $table.timestamp, builder: (column) => ColumnOrderings(column));
}

class $$TestSyncLogsTableAnnotationComposer
    extends Composer<_$TestDatabase, $TestSyncLogsTable> {
  $$TestSyncLogsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get type =>
      $composableBuilder(column: $table.type, builder: (column) => column);

  GeneratedColumn<String> get status =>
      $composableBuilder(column: $table.status, builder: (column) => column);

  GeneratedColumn<String> get message =>
      $composableBuilder(column: $table.message, builder: (column) => column);

  GeneratedColumn<DateTime> get timestamp =>
      $composableBuilder(column: $table.timestamp, builder: (column) => column);
}

class $$TestSyncLogsTableTableManager extends RootTableManager<
    _$TestDatabase,
    $TestSyncLogsTable,
    TestSyncLog,
    $$TestSyncLogsTableFilterComposer,
    $$TestSyncLogsTableOrderingComposer,
    $$TestSyncLogsTableAnnotationComposer,
    $$TestSyncLogsTableCreateCompanionBuilder,
    $$TestSyncLogsTableUpdateCompanionBuilder,
    (
      TestSyncLog,
      BaseReferences<_$TestDatabase, $TestSyncLogsTable, TestSyncLog>
    ),
    TestSyncLog,
    PrefetchHooks Function()> {
  $$TestSyncLogsTableTableManager(_$TestDatabase db, $TestSyncLogsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$TestSyncLogsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$TestSyncLogsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$TestSyncLogsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> type = const Value.absent(),
            Value<String> status = const Value.absent(),
            Value<String?> message = const Value.absent(),
            Value<DateTime> timestamp = const Value.absent(),
          }) =>
              TestSyncLogsCompanion(
            id: id,
            type: type,
            status: status,
            message: message,
            timestamp: timestamp,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String type,
            required String status,
            Value<String?> message = const Value.absent(),
            required DateTime timestamp,
          }) =>
              TestSyncLogsCompanion.insert(
            id: id,
            type: type,
            status: status,
            message: message,
            timestamp: timestamp,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$TestSyncLogsTableProcessedTableManager = ProcessedTableManager<
    _$TestDatabase,
    $TestSyncLogsTable,
    TestSyncLog,
    $$TestSyncLogsTableFilterComposer,
    $$TestSyncLogsTableOrderingComposer,
    $$TestSyncLogsTableAnnotationComposer,
    $$TestSyncLogsTableCreateCompanionBuilder,
    $$TestSyncLogsTableUpdateCompanionBuilder,
    (
      TestSyncLog,
      BaseReferences<_$TestDatabase, $TestSyncLogsTable, TestSyncLog>
    ),
    TestSyncLog,
    PrefetchHooks Function()>;
typedef $$TestSyncEventsTableCreateCompanionBuilder = TestSyncEventsCompanion
    Function({
  Value<int> id,
  required String tenantId,
  required String type,
  required String message,
  Value<bool> isRead,
  Value<DateTime> createdAt,
});
typedef $$TestSyncEventsTableUpdateCompanionBuilder = TestSyncEventsCompanion
    Function({
  Value<int> id,
  Value<String> tenantId,
  Value<String> type,
  Value<String> message,
  Value<bool> isRead,
  Value<DateTime> createdAt,
});

class $$TestSyncEventsTableFilterComposer
    extends Composer<_$TestDatabase, $TestSyncEventsTable> {
  $$TestSyncEventsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get tenantId => $composableBuilder(
      column: $table.tenantId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get type => $composableBuilder(
      column: $table.type, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get message => $composableBuilder(
      column: $table.message, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get isRead => $composableBuilder(
      column: $table.isRead, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));
}

class $$TestSyncEventsTableOrderingComposer
    extends Composer<_$TestDatabase, $TestSyncEventsTable> {
  $$TestSyncEventsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get tenantId => $composableBuilder(
      column: $table.tenantId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get type => $composableBuilder(
      column: $table.type, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get message => $composableBuilder(
      column: $table.message, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get isRead => $composableBuilder(
      column: $table.isRead, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));
}

class $$TestSyncEventsTableAnnotationComposer
    extends Composer<_$TestDatabase, $TestSyncEventsTable> {
  $$TestSyncEventsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get tenantId =>
      $composableBuilder(column: $table.tenantId, builder: (column) => column);

  GeneratedColumn<String> get type =>
      $composableBuilder(column: $table.type, builder: (column) => column);

  GeneratedColumn<String> get message =>
      $composableBuilder(column: $table.message, builder: (column) => column);

  GeneratedColumn<bool> get isRead =>
      $composableBuilder(column: $table.isRead, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$TestSyncEventsTableTableManager extends RootTableManager<
    _$TestDatabase,
    $TestSyncEventsTable,
    TestSyncEvent,
    $$TestSyncEventsTableFilterComposer,
    $$TestSyncEventsTableOrderingComposer,
    $$TestSyncEventsTableAnnotationComposer,
    $$TestSyncEventsTableCreateCompanionBuilder,
    $$TestSyncEventsTableUpdateCompanionBuilder,
    (
      TestSyncEvent,
      BaseReferences<_$TestDatabase, $TestSyncEventsTable, TestSyncEvent>
    ),
    TestSyncEvent,
    PrefetchHooks Function()> {
  $$TestSyncEventsTableTableManager(
      _$TestDatabase db, $TestSyncEventsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$TestSyncEventsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$TestSyncEventsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$TestSyncEventsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> tenantId = const Value.absent(),
            Value<String> type = const Value.absent(),
            Value<String> message = const Value.absent(),
            Value<bool> isRead = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
          }) =>
              TestSyncEventsCompanion(
            id: id,
            tenantId: tenantId,
            type: type,
            message: message,
            isRead: isRead,
            createdAt: createdAt,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String tenantId,
            required String type,
            required String message,
            Value<bool> isRead = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
          }) =>
              TestSyncEventsCompanion.insert(
            id: id,
            tenantId: tenantId,
            type: type,
            message: message,
            isRead: isRead,
            createdAt: createdAt,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$TestSyncEventsTableProcessedTableManager = ProcessedTableManager<
    _$TestDatabase,
    $TestSyncEventsTable,
    TestSyncEvent,
    $$TestSyncEventsTableFilterComposer,
    $$TestSyncEventsTableOrderingComposer,
    $$TestSyncEventsTableAnnotationComposer,
    $$TestSyncEventsTableCreateCompanionBuilder,
    $$TestSyncEventsTableUpdateCompanionBuilder,
    (
      TestSyncEvent,
      BaseReferences<_$TestDatabase, $TestSyncEventsTable, TestSyncEvent>
    ),
    TestSyncEvent,
    PrefetchHooks Function()>;

class $TestDatabaseManager {
  final _$TestDatabase _db;
  $TestDatabaseManager(this._db);
  $$TestTasksTableTableManager get testTasks =>
      $$TestTasksTableTableManager(_db, _db.testTasks);
  $$TestOutboxTableTableManager get testOutbox =>
      $$TestOutboxTableTableManager(_db, _db.testOutbox);
  $$TestFieldsTableTableManager get testFields =>
      $$TestFieldsTableTableManager(_db, _db.testFields);
  $$TestSyncLogsTableTableManager get testSyncLogs =>
      $$TestSyncLogsTableTableManager(_db, _db.testSyncLogs);
  $$TestSyncEventsTableTableManager get testSyncEvents =>
      $$TestSyncEventsTableTableManager(_db, _db.testSyncEvents);
}
