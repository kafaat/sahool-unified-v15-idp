// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'sync_queue_dao_test.dart';

// ignore_for_file: type=lint
class $SyncOutboxTable extends SyncOutbox
    with TableInfo<$SyncOutboxTable, SyncOutboxData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $SyncOutboxTable(this.attachedDatabase, [this._alias]);
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
  static const VerificationMeta _ifMatchMeta =
      const VerificationMeta('ifMatch');
  @override
  late final GeneratedColumn<String> ifMatch = GeneratedColumn<String>(
      'if_match', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _retryCountMeta =
      const VerificationMeta('retryCount');
  @override
  late final GeneratedColumn<int> retryCount = GeneratedColumn<int>(
      'retry_count', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _maxRetriesMeta =
      const VerificationMeta('maxRetries');
  @override
  late final GeneratedColumn<int> maxRetries = GeneratedColumn<int>(
      'max_retries', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(5));
  static const VerificationMeta _priorityMeta =
      const VerificationMeta('priority');
  @override
  late final GeneratedColumn<int> priority = GeneratedColumn<int>(
      'priority', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
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
  static const VerificationMeta _errorMessageMeta =
      const VerificationMeta('errorMessage');
  @override
  late final GeneratedColumn<String> errorMessage = GeneratedColumn<String>(
      'error_message', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _lastAttemptMeta =
      const VerificationMeta('lastAttempt');
  @override
  late final GeneratedColumn<DateTime> lastAttempt = GeneratedColumn<DateTime>(
      'last_attempt', aliasedName, true,
      type: DriftSqlType.dateTime, requiredDuringInsert: false);
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
        ifMatch,
        retryCount,
        maxRetries,
        priority,
        isSynced,
        errorMessage,
        lastAttempt,
        createdAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'sync_outbox';
  @override
  VerificationContext validateIntegrity(Insertable<SyncOutboxData> instance,
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
    if (data.containsKey('if_match')) {
      context.handle(_ifMatchMeta,
          ifMatch.isAcceptableOrUnknown(data['if_match']!, _ifMatchMeta));
    }
    if (data.containsKey('retry_count')) {
      context.handle(
          _retryCountMeta,
          retryCount.isAcceptableOrUnknown(
              data['retry_count']!, _retryCountMeta));
    }
    if (data.containsKey('max_retries')) {
      context.handle(
          _maxRetriesMeta,
          maxRetries.isAcceptableOrUnknown(
              data['max_retries']!, _maxRetriesMeta));
    }
    if (data.containsKey('priority')) {
      context.handle(_priorityMeta,
          priority.isAcceptableOrUnknown(data['priority']!, _priorityMeta));
    }
    if (data.containsKey('is_synced')) {
      context.handle(_isSyncedMeta,
          isSynced.isAcceptableOrUnknown(data['is_synced']!, _isSyncedMeta));
    }
    if (data.containsKey('error_message')) {
      context.handle(
          _errorMessageMeta,
          errorMessage.isAcceptableOrUnknown(
              data['error_message']!, _errorMessageMeta));
    }
    if (data.containsKey('last_attempt')) {
      context.handle(
          _lastAttemptMeta,
          lastAttempt.isAcceptableOrUnknown(
              data['last_attempt']!, _lastAttemptMeta));
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
  SyncOutboxData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return SyncOutboxData(
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
      ifMatch: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}if_match']),
      retryCount: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}retry_count'])!,
      maxRetries: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}max_retries'])!,
      priority: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}priority'])!,
      isSynced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}is_synced'])!,
      errorMessage: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}error_message']),
      lastAttempt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}last_attempt']),
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $SyncOutboxTable createAlias(String alias) {
    return $SyncOutboxTable(attachedDatabase, alias);
  }
}

class SyncOutboxData extends DataClass implements Insertable<SyncOutboxData> {
  final int id;
  final String tenantId;
  final String entityType;
  final String entityId;
  final String apiEndpoint;
  final String method;
  final String payload;
  final String? ifMatch;
  final int retryCount;
  final int maxRetries;
  final int priority;
  final bool isSynced;
  final String? errorMessage;
  final DateTime? lastAttempt;
  final DateTime createdAt;
  const SyncOutboxData(
      {required this.id,
      required this.tenantId,
      required this.entityType,
      required this.entityId,
      required this.apiEndpoint,
      required this.method,
      required this.payload,
      this.ifMatch,
      required this.retryCount,
      required this.maxRetries,
      required this.priority,
      required this.isSynced,
      this.errorMessage,
      this.lastAttempt,
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
    if (!nullToAbsent || ifMatch != null) {
      map['if_match'] = Variable<String>(ifMatch);
    }
    map['retry_count'] = Variable<int>(retryCount);
    map['max_retries'] = Variable<int>(maxRetries);
    map['priority'] = Variable<int>(priority);
    map['is_synced'] = Variable<bool>(isSynced);
    if (!nullToAbsent || errorMessage != null) {
      map['error_message'] = Variable<String>(errorMessage);
    }
    if (!nullToAbsent || lastAttempt != null) {
      map['last_attempt'] = Variable<DateTime>(lastAttempt);
    }
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  SyncOutboxCompanion toCompanion(bool nullToAbsent) {
    return SyncOutboxCompanion(
      id: Value(id),
      tenantId: Value(tenantId),
      entityType: Value(entityType),
      entityId: Value(entityId),
      apiEndpoint: Value(apiEndpoint),
      method: Value(method),
      payload: Value(payload),
      ifMatch: ifMatch == null && nullToAbsent
          ? const Value.absent()
          : Value(ifMatch),
      retryCount: Value(retryCount),
      maxRetries: Value(maxRetries),
      priority: Value(priority),
      isSynced: Value(isSynced),
      errorMessage: errorMessage == null && nullToAbsent
          ? const Value.absent()
          : Value(errorMessage),
      lastAttempt: lastAttempt == null && nullToAbsent
          ? const Value.absent()
          : Value(lastAttempt),
      createdAt: Value(createdAt),
    );
  }

  factory SyncOutboxData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SyncOutboxData(
      id: serializer.fromJson<int>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenantId']),
      entityType: serializer.fromJson<String>(json['entityType']),
      entityId: serializer.fromJson<String>(json['entityId']),
      apiEndpoint: serializer.fromJson<String>(json['apiEndpoint']),
      method: serializer.fromJson<String>(json['method']),
      payload: serializer.fromJson<String>(json['payload']),
      ifMatch: serializer.fromJson<String?>(json['ifMatch']),
      retryCount: serializer.fromJson<int>(json['retryCount']),
      maxRetries: serializer.fromJson<int>(json['maxRetries']),
      priority: serializer.fromJson<int>(json['priority']),
      isSynced: serializer.fromJson<bool>(json['isSynced']),
      errorMessage: serializer.fromJson<String?>(json['errorMessage']),
      lastAttempt: serializer.fromJson<DateTime?>(json['lastAttempt']),
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
      'ifMatch': serializer.toJson<String?>(ifMatch),
      'retryCount': serializer.toJson<int>(retryCount),
      'maxRetries': serializer.toJson<int>(maxRetries),
      'priority': serializer.toJson<int>(priority),
      'isSynced': serializer.toJson<bool>(isSynced),
      'errorMessage': serializer.toJson<String?>(errorMessage),
      'lastAttempt': serializer.toJson<DateTime?>(lastAttempt),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  SyncOutboxData copyWith(
          {int? id,
          String? tenantId,
          String? entityType,
          String? entityId,
          String? apiEndpoint,
          String? method,
          String? payload,
          Value<String?> ifMatch = const Value.absent(),
          int? retryCount,
          int? maxRetries,
          int? priority,
          bool? isSynced,
          Value<String?> errorMessage = const Value.absent(),
          Value<DateTime?> lastAttempt = const Value.absent(),
          DateTime? createdAt}) =>
      SyncOutboxData(
        id: id ?? this.id,
        tenantId: tenantId ?? this.tenantId,
        entityType: entityType ?? this.entityType,
        entityId: entityId ?? this.entityId,
        apiEndpoint: apiEndpoint ?? this.apiEndpoint,
        method: method ?? this.method,
        payload: payload ?? this.payload,
        ifMatch: ifMatch.present ? ifMatch.value : this.ifMatch,
        retryCount: retryCount ?? this.retryCount,
        maxRetries: maxRetries ?? this.maxRetries,
        priority: priority ?? this.priority,
        isSynced: isSynced ?? this.isSynced,
        errorMessage:
            errorMessage.present ? errorMessage.value : this.errorMessage,
        lastAttempt: lastAttempt.present ? lastAttempt.value : this.lastAttempt,
        createdAt: createdAt ?? this.createdAt,
      );
  SyncOutboxData copyWithCompanion(SyncOutboxCompanion data) {
    return SyncOutboxData(
      id: data.id.present ? data.id.value : this.id,
      tenantId: data.tenantId.present ? data.tenantId.value : this.tenantId,
      entityType:
          data.entityType.present ? data.entityType.value : this.entityType,
      entityId: data.entityId.present ? data.entityId.value : this.entityId,
      apiEndpoint:
          data.apiEndpoint.present ? data.apiEndpoint.value : this.apiEndpoint,
      method: data.method.present ? data.method.value : this.method,
      payload: data.payload.present ? data.payload.value : this.payload,
      ifMatch: data.ifMatch.present ? data.ifMatch.value : this.ifMatch,
      retryCount:
          data.retryCount.present ? data.retryCount.value : this.retryCount,
      maxRetries:
          data.maxRetries.present ? data.maxRetries.value : this.maxRetries,
      priority: data.priority.present ? data.priority.value : this.priority,
      isSynced: data.isSynced.present ? data.isSynced.value : this.isSynced,
      errorMessage: data.errorMessage.present
          ? data.errorMessage.value
          : this.errorMessage,
      lastAttempt:
          data.lastAttempt.present ? data.lastAttempt.value : this.lastAttempt,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('SyncOutboxData(')
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('entityType: $entityType, ')
          ..write('entityId: $entityId, ')
          ..write('apiEndpoint: $apiEndpoint, ')
          ..write('method: $method, ')
          ..write('payload: $payload, ')
          ..write('ifMatch: $ifMatch, ')
          ..write('retryCount: $retryCount, ')
          ..write('maxRetries: $maxRetries, ')
          ..write('priority: $priority, ')
          ..write('isSynced: $isSynced, ')
          ..write('errorMessage: $errorMessage, ')
          ..write('lastAttempt: $lastAttempt, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id,
      tenantId,
      entityType,
      entityId,
      apiEndpoint,
      method,
      payload,
      ifMatch,
      retryCount,
      maxRetries,
      priority,
      isSynced,
      errorMessage,
      lastAttempt,
      createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is SyncOutboxData &&
          other.id == this.id &&
          other.tenantId == this.tenantId &&
          other.entityType == this.entityType &&
          other.entityId == this.entityId &&
          other.apiEndpoint == this.apiEndpoint &&
          other.method == this.method &&
          other.payload == this.payload &&
          other.ifMatch == this.ifMatch &&
          other.retryCount == this.retryCount &&
          other.maxRetries == this.maxRetries &&
          other.priority == this.priority &&
          other.isSynced == this.isSynced &&
          other.errorMessage == this.errorMessage &&
          other.lastAttempt == this.lastAttempt &&
          other.createdAt == this.createdAt);
}

class SyncOutboxCompanion extends UpdateCompanion<SyncOutboxData> {
  final Value<int> id;
  final Value<String> tenantId;
  final Value<String> entityType;
  final Value<String> entityId;
  final Value<String> apiEndpoint;
  final Value<String> method;
  final Value<String> payload;
  final Value<String?> ifMatch;
  final Value<int> retryCount;
  final Value<int> maxRetries;
  final Value<int> priority;
  final Value<bool> isSynced;
  final Value<String?> errorMessage;
  final Value<DateTime?> lastAttempt;
  final Value<DateTime> createdAt;
  const SyncOutboxCompanion({
    this.id = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.entityType = const Value.absent(),
    this.entityId = const Value.absent(),
    this.apiEndpoint = const Value.absent(),
    this.method = const Value.absent(),
    this.payload = const Value.absent(),
    this.ifMatch = const Value.absent(),
    this.retryCount = const Value.absent(),
    this.maxRetries = const Value.absent(),
    this.priority = const Value.absent(),
    this.isSynced = const Value.absent(),
    this.errorMessage = const Value.absent(),
    this.lastAttempt = const Value.absent(),
    this.createdAt = const Value.absent(),
  });
  SyncOutboxCompanion.insert({
    this.id = const Value.absent(),
    required String tenantId,
    required String entityType,
    required String entityId,
    required String apiEndpoint,
    this.method = const Value.absent(),
    required String payload,
    this.ifMatch = const Value.absent(),
    this.retryCount = const Value.absent(),
    this.maxRetries = const Value.absent(),
    this.priority = const Value.absent(),
    this.isSynced = const Value.absent(),
    this.errorMessage = const Value.absent(),
    this.lastAttempt = const Value.absent(),
    this.createdAt = const Value.absent(),
  })  : tenantId = Value(tenantId),
        entityType = Value(entityType),
        entityId = Value(entityId),
        apiEndpoint = Value(apiEndpoint),
        payload = Value(payload);
  static Insertable<SyncOutboxData> custom({
    Expression<int>? id,
    Expression<String>? tenantId,
    Expression<String>? entityType,
    Expression<String>? entityId,
    Expression<String>? apiEndpoint,
    Expression<String>? method,
    Expression<String>? payload,
    Expression<String>? ifMatch,
    Expression<int>? retryCount,
    Expression<int>? maxRetries,
    Expression<int>? priority,
    Expression<bool>? isSynced,
    Expression<String>? errorMessage,
    Expression<DateTime>? lastAttempt,
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
      if (ifMatch != null) 'if_match': ifMatch,
      if (retryCount != null) 'retry_count': retryCount,
      if (maxRetries != null) 'max_retries': maxRetries,
      if (priority != null) 'priority': priority,
      if (isSynced != null) 'is_synced': isSynced,
      if (errorMessage != null) 'error_message': errorMessage,
      if (lastAttempt != null) 'last_attempt': lastAttempt,
      if (createdAt != null) 'created_at': createdAt,
    });
  }

  SyncOutboxCompanion copyWith(
      {Value<int>? id,
      Value<String>? tenantId,
      Value<String>? entityType,
      Value<String>? entityId,
      Value<String>? apiEndpoint,
      Value<String>? method,
      Value<String>? payload,
      Value<String?>? ifMatch,
      Value<int>? retryCount,
      Value<int>? maxRetries,
      Value<int>? priority,
      Value<bool>? isSynced,
      Value<String?>? errorMessage,
      Value<DateTime?>? lastAttempt,
      Value<DateTime>? createdAt}) {
    return SyncOutboxCompanion(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      entityType: entityType ?? this.entityType,
      entityId: entityId ?? this.entityId,
      apiEndpoint: apiEndpoint ?? this.apiEndpoint,
      method: method ?? this.method,
      payload: payload ?? this.payload,
      ifMatch: ifMatch ?? this.ifMatch,
      retryCount: retryCount ?? this.retryCount,
      maxRetries: maxRetries ?? this.maxRetries,
      priority: priority ?? this.priority,
      isSynced: isSynced ?? this.isSynced,
      errorMessage: errorMessage ?? this.errorMessage,
      lastAttempt: lastAttempt ?? this.lastAttempt,
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
      map['if_match'] = Variable<String>(ifMatch.value);
    }
    if (retryCount.present) {
      map['retry_count'] = Variable<int>(retryCount.value);
    }
    if (maxRetries.present) {
      map['max_retries'] = Variable<int>(maxRetries.value);
    }
    if (priority.present) {
      map['priority'] = Variable<int>(priority.value);
    }
    if (isSynced.present) {
      map['is_synced'] = Variable<bool>(isSynced.value);
    }
    if (errorMessage.present) {
      map['error_message'] = Variable<String>(errorMessage.value);
    }
    if (lastAttempt.present) {
      map['last_attempt'] = Variable<DateTime>(lastAttempt.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('SyncOutboxCompanion(')
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('entityType: $entityType, ')
          ..write('entityId: $entityId, ')
          ..write('apiEndpoint: $apiEndpoint, ')
          ..write('method: $method, ')
          ..write('payload: $payload, ')
          ..write('ifMatch: $ifMatch, ')
          ..write('retryCount: $retryCount, ')
          ..write('maxRetries: $maxRetries, ')
          ..write('priority: $priority, ')
          ..write('isSynced: $isSynced, ')
          ..write('errorMessage: $errorMessage, ')
          ..write('lastAttempt: $lastAttempt, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }
}

class $SyncLogsTable extends SyncLogs with TableInfo<$SyncLogsTable, SyncLog> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $SyncLogsTable(this.attachedDatabase, [this._alias]);
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
  static const VerificationMeta _itemsSyncedMeta =
      const VerificationMeta('itemsSynced');
  @override
  late final GeneratedColumn<int> itemsSynced = GeneratedColumn<int>(
      'items_synced', aliasedName, true,
      type: DriftSqlType.int, requiredDuringInsert: false);
  static const VerificationMeta _itemsFailedMeta =
      const VerificationMeta('itemsFailed');
  @override
  late final GeneratedColumn<int> itemsFailed = GeneratedColumn<int>(
      'items_failed', aliasedName, true,
      type: DriftSqlType.int, requiredDuringInsert: false);
  static const VerificationMeta _durationMsMeta =
      const VerificationMeta('durationMs');
  @override
  late final GeneratedColumn<int> durationMs = GeneratedColumn<int>(
      'duration_ms', aliasedName, true,
      type: DriftSqlType.int, requiredDuringInsert: false);
  static const VerificationMeta _detailsMeta =
      const VerificationMeta('details');
  @override
  late final GeneratedColumn<String> details = GeneratedColumn<String>(
      'details', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _timestampMeta =
      const VerificationMeta('timestamp');
  @override
  late final GeneratedColumn<DateTime> timestamp = GeneratedColumn<DateTime>(
      'timestamp', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        type,
        status,
        message,
        itemsSynced,
        itemsFailed,
        durationMs,
        details,
        timestamp
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'sync_logs';
  @override
  VerificationContext validateIntegrity(Insertable<SyncLog> instance,
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
    if (data.containsKey('items_synced')) {
      context.handle(
          _itemsSyncedMeta,
          itemsSynced.isAcceptableOrUnknown(
              data['items_synced']!, _itemsSyncedMeta));
    }
    if (data.containsKey('items_failed')) {
      context.handle(
          _itemsFailedMeta,
          itemsFailed.isAcceptableOrUnknown(
              data['items_failed']!, _itemsFailedMeta));
    }
    if (data.containsKey('duration_ms')) {
      context.handle(
          _durationMsMeta,
          durationMs.isAcceptableOrUnknown(
              data['duration_ms']!, _durationMsMeta));
    }
    if (data.containsKey('details')) {
      context.handle(_detailsMeta,
          details.isAcceptableOrUnknown(data['details']!, _detailsMeta));
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
  SyncLog map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return SyncLog(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      type: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}type'])!,
      status: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}status'])!,
      message: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}message']),
      itemsSynced: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}items_synced']),
      itemsFailed: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}items_failed']),
      durationMs: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}duration_ms']),
      details: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}details']),
      timestamp: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}timestamp'])!,
    );
  }

  @override
  $SyncLogsTable createAlias(String alias) {
    return $SyncLogsTable(attachedDatabase, alias);
  }
}

class SyncLog extends DataClass implements Insertable<SyncLog> {
  final int id;
  final String type;
  final String status;
  final String? message;
  final int? itemsSynced;
  final int? itemsFailed;
  final int? durationMs;
  final String? details;
  final DateTime timestamp;
  const SyncLog(
      {required this.id,
      required this.type,
      required this.status,
      this.message,
      this.itemsSynced,
      this.itemsFailed,
      this.durationMs,
      this.details,
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
    if (!nullToAbsent || itemsSynced != null) {
      map['items_synced'] = Variable<int>(itemsSynced);
    }
    if (!nullToAbsent || itemsFailed != null) {
      map['items_failed'] = Variable<int>(itemsFailed);
    }
    if (!nullToAbsent || durationMs != null) {
      map['duration_ms'] = Variable<int>(durationMs);
    }
    if (!nullToAbsent || details != null) {
      map['details'] = Variable<String>(details);
    }
    map['timestamp'] = Variable<DateTime>(timestamp);
    return map;
  }

  SyncLogsCompanion toCompanion(bool nullToAbsent) {
    return SyncLogsCompanion(
      id: Value(id),
      type: Value(type),
      status: Value(status),
      message: message == null && nullToAbsent
          ? const Value.absent()
          : Value(message),
      itemsSynced: itemsSynced == null && nullToAbsent
          ? const Value.absent()
          : Value(itemsSynced),
      itemsFailed: itemsFailed == null && nullToAbsent
          ? const Value.absent()
          : Value(itemsFailed),
      durationMs: durationMs == null && nullToAbsent
          ? const Value.absent()
          : Value(durationMs),
      details: details == null && nullToAbsent
          ? const Value.absent()
          : Value(details),
      timestamp: Value(timestamp),
    );
  }

  factory SyncLog.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SyncLog(
      id: serializer.fromJson<int>(json['id']),
      type: serializer.fromJson<String>(json['type']),
      status: serializer.fromJson<String>(json['status']),
      message: serializer.fromJson<String?>(json['message']),
      itemsSynced: serializer.fromJson<int?>(json['itemsSynced']),
      itemsFailed: serializer.fromJson<int?>(json['itemsFailed']),
      durationMs: serializer.fromJson<int?>(json['durationMs']),
      details: serializer.fromJson<String?>(json['details']),
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
      'itemsSynced': serializer.toJson<int?>(itemsSynced),
      'itemsFailed': serializer.toJson<int?>(itemsFailed),
      'durationMs': serializer.toJson<int?>(durationMs),
      'details': serializer.toJson<String?>(details),
      'timestamp': serializer.toJson<DateTime>(timestamp),
    };
  }

  SyncLog copyWith(
          {int? id,
          String? type,
          String? status,
          Value<String?> message = const Value.absent(),
          Value<int?> itemsSynced = const Value.absent(),
          Value<int?> itemsFailed = const Value.absent(),
          Value<int?> durationMs = const Value.absent(),
          Value<String?> details = const Value.absent(),
          DateTime? timestamp}) =>
      SyncLog(
        id: id ?? this.id,
        type: type ?? this.type,
        status: status ?? this.status,
        message: message.present ? message.value : this.message,
        itemsSynced: itemsSynced.present ? itemsSynced.value : this.itemsSynced,
        itemsFailed: itemsFailed.present ? itemsFailed.value : this.itemsFailed,
        durationMs: durationMs.present ? durationMs.value : this.durationMs,
        details: details.present ? details.value : this.details,
        timestamp: timestamp ?? this.timestamp,
      );
  SyncLog copyWithCompanion(SyncLogsCompanion data) {
    return SyncLog(
      id: data.id.present ? data.id.value : this.id,
      type: data.type.present ? data.type.value : this.type,
      status: data.status.present ? data.status.value : this.status,
      message: data.message.present ? data.message.value : this.message,
      itemsSynced:
          data.itemsSynced.present ? data.itemsSynced.value : this.itemsSynced,
      itemsFailed:
          data.itemsFailed.present ? data.itemsFailed.value : this.itemsFailed,
      durationMs:
          data.durationMs.present ? data.durationMs.value : this.durationMs,
      details: data.details.present ? data.details.value : this.details,
      timestamp: data.timestamp.present ? data.timestamp.value : this.timestamp,
    );
  }

  @override
  String toString() {
    return (StringBuffer('SyncLog(')
          ..write('id: $id, ')
          ..write('type: $type, ')
          ..write('status: $status, ')
          ..write('message: $message, ')
          ..write('itemsSynced: $itemsSynced, ')
          ..write('itemsFailed: $itemsFailed, ')
          ..write('durationMs: $durationMs, ')
          ..write('details: $details, ')
          ..write('timestamp: $timestamp')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, type, status, message, itemsSynced,
      itemsFailed, durationMs, details, timestamp);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is SyncLog &&
          other.id == this.id &&
          other.type == this.type &&
          other.status == this.status &&
          other.message == this.message &&
          other.itemsSynced == this.itemsSynced &&
          other.itemsFailed == this.itemsFailed &&
          other.durationMs == this.durationMs &&
          other.details == this.details &&
          other.timestamp == this.timestamp);
}

class SyncLogsCompanion extends UpdateCompanion<SyncLog> {
  final Value<int> id;
  final Value<String> type;
  final Value<String> status;
  final Value<String?> message;
  final Value<int?> itemsSynced;
  final Value<int?> itemsFailed;
  final Value<int?> durationMs;
  final Value<String?> details;
  final Value<DateTime> timestamp;
  const SyncLogsCompanion({
    this.id = const Value.absent(),
    this.type = const Value.absent(),
    this.status = const Value.absent(),
    this.message = const Value.absent(),
    this.itemsSynced = const Value.absent(),
    this.itemsFailed = const Value.absent(),
    this.durationMs = const Value.absent(),
    this.details = const Value.absent(),
    this.timestamp = const Value.absent(),
  });
  SyncLogsCompanion.insert({
    this.id = const Value.absent(),
    required String type,
    required String status,
    this.message = const Value.absent(),
    this.itemsSynced = const Value.absent(),
    this.itemsFailed = const Value.absent(),
    this.durationMs = const Value.absent(),
    this.details = const Value.absent(),
    required DateTime timestamp,
  })  : type = Value(type),
        status = Value(status),
        timestamp = Value(timestamp);
  static Insertable<SyncLog> custom({
    Expression<int>? id,
    Expression<String>? type,
    Expression<String>? status,
    Expression<String>? message,
    Expression<int>? itemsSynced,
    Expression<int>? itemsFailed,
    Expression<int>? durationMs,
    Expression<String>? details,
    Expression<DateTime>? timestamp,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (type != null) 'type': type,
      if (status != null) 'status': status,
      if (message != null) 'message': message,
      if (itemsSynced != null) 'items_synced': itemsSynced,
      if (itemsFailed != null) 'items_failed': itemsFailed,
      if (durationMs != null) 'duration_ms': durationMs,
      if (details != null) 'details': details,
      if (timestamp != null) 'timestamp': timestamp,
    });
  }

  SyncLogsCompanion copyWith(
      {Value<int>? id,
      Value<String>? type,
      Value<String>? status,
      Value<String?>? message,
      Value<int?>? itemsSynced,
      Value<int?>? itemsFailed,
      Value<int?>? durationMs,
      Value<String?>? details,
      Value<DateTime>? timestamp}) {
    return SyncLogsCompanion(
      id: id ?? this.id,
      type: type ?? this.type,
      status: status ?? this.status,
      message: message ?? this.message,
      itemsSynced: itemsSynced ?? this.itemsSynced,
      itemsFailed: itemsFailed ?? this.itemsFailed,
      durationMs: durationMs ?? this.durationMs,
      details: details ?? this.details,
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
    if (itemsSynced.present) {
      map['items_synced'] = Variable<int>(itemsSynced.value);
    }
    if (itemsFailed.present) {
      map['items_failed'] = Variable<int>(itemsFailed.value);
    }
    if (durationMs.present) {
      map['duration_ms'] = Variable<int>(durationMs.value);
    }
    if (details.present) {
      map['details'] = Variable<String>(details.value);
    }
    if (timestamp.present) {
      map['timestamp'] = Variable<DateTime>(timestamp.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('SyncLogsCompanion(')
          ..write('id: $id, ')
          ..write('type: $type, ')
          ..write('status: $status, ')
          ..write('message: $message, ')
          ..write('itemsSynced: $itemsSynced, ')
          ..write('itemsFailed: $itemsFailed, ')
          ..write('durationMs: $durationMs, ')
          ..write('details: $details, ')
          ..write('timestamp: $timestamp')
          ..write(')'))
        .toString();
  }
}

class $SyncEventsTable extends SyncEvents
    with TableInfo<$SyncEventsTable, SyncEvent> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $SyncEventsTable(this.attachedDatabase, [this._alias]);
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
  static const VerificationMeta _entityTypeMeta =
      const VerificationMeta('entityType');
  @override
  late final GeneratedColumn<String> entityType = GeneratedColumn<String>(
      'entity_type', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _entityIdMeta =
      const VerificationMeta('entityId');
  @override
  late final GeneratedColumn<String> entityId = GeneratedColumn<String>(
      'entity_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _messageMeta =
      const VerificationMeta('message');
  @override
  late final GeneratedColumn<String> message = GeneratedColumn<String>(
      'message', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _messageArMeta =
      const VerificationMeta('messageAr');
  @override
  late final GeneratedColumn<String> messageAr = GeneratedColumn<String>(
      'message_ar', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _detailsMeta =
      const VerificationMeta('details');
  @override
  late final GeneratedColumn<String> details = GeneratedColumn<String>(
      'details', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _resolutionMeta =
      const VerificationMeta('resolution');
  @override
  late final GeneratedColumn<String> resolution = GeneratedColumn<String>(
      'resolution', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _isReadMeta = const VerificationMeta('isRead');
  @override
  late final GeneratedColumn<bool> isRead = GeneratedColumn<bool>(
      'is_read', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("is_read" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _isResolvedMeta =
      const VerificationMeta('isResolved');
  @override
  late final GeneratedColumn<bool> isResolved = GeneratedColumn<bool>(
      'is_resolved', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("is_resolved" IN (0, 1))'),
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
        type,
        entityType,
        entityId,
        message,
        messageAr,
        details,
        resolution,
        isRead,
        isResolved,
        createdAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'sync_events';
  @override
  VerificationContext validateIntegrity(Insertable<SyncEvent> instance,
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
    if (data.containsKey('entity_type')) {
      context.handle(
          _entityTypeMeta,
          entityType.isAcceptableOrUnknown(
              data['entity_type']!, _entityTypeMeta));
    }
    if (data.containsKey('entity_id')) {
      context.handle(_entityIdMeta,
          entityId.isAcceptableOrUnknown(data['entity_id']!, _entityIdMeta));
    }
    if (data.containsKey('message')) {
      context.handle(_messageMeta,
          message.isAcceptableOrUnknown(data['message']!, _messageMeta));
    } else if (isInserting) {
      context.missing(_messageMeta);
    }
    if (data.containsKey('message_ar')) {
      context.handle(_messageArMeta,
          messageAr.isAcceptableOrUnknown(data['message_ar']!, _messageArMeta));
    }
    if (data.containsKey('details')) {
      context.handle(_detailsMeta,
          details.isAcceptableOrUnknown(data['details']!, _detailsMeta));
    }
    if (data.containsKey('resolution')) {
      context.handle(
          _resolutionMeta,
          resolution.isAcceptableOrUnknown(
              data['resolution']!, _resolutionMeta));
    }
    if (data.containsKey('is_read')) {
      context.handle(_isReadMeta,
          isRead.isAcceptableOrUnknown(data['is_read']!, _isReadMeta));
    }
    if (data.containsKey('is_resolved')) {
      context.handle(
          _isResolvedMeta,
          isResolved.isAcceptableOrUnknown(
              data['is_resolved']!, _isResolvedMeta));
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
  SyncEvent map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return SyncEvent(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      tenantId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}tenant_id'])!,
      type: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}type'])!,
      entityType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}entity_type']),
      entityId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}entity_id']),
      message: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}message'])!,
      messageAr: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}message_ar']),
      details: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}details']),
      resolution: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}resolution']),
      isRead: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}is_read'])!,
      isResolved: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}is_resolved'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $SyncEventsTable createAlias(String alias) {
    return $SyncEventsTable(attachedDatabase, alias);
  }
}

class SyncEvent extends DataClass implements Insertable<SyncEvent> {
  final int id;
  final String tenantId;
  final String type;
  final String? entityType;
  final String? entityId;
  final String message;
  final String? messageAr;
  final String? details;
  final String? resolution;
  final bool isRead;
  final bool isResolved;
  final DateTime createdAt;
  const SyncEvent(
      {required this.id,
      required this.tenantId,
      required this.type,
      this.entityType,
      this.entityId,
      required this.message,
      this.messageAr,
      this.details,
      this.resolution,
      required this.isRead,
      required this.isResolved,
      required this.createdAt});
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
    if (!nullToAbsent || messageAr != null) {
      map['message_ar'] = Variable<String>(messageAr);
    }
    if (!nullToAbsent || details != null) {
      map['details'] = Variable<String>(details);
    }
    if (!nullToAbsent || resolution != null) {
      map['resolution'] = Variable<String>(resolution);
    }
    map['is_read'] = Variable<bool>(isRead);
    map['is_resolved'] = Variable<bool>(isResolved);
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  SyncEventsCompanion toCompanion(bool nullToAbsent) {
    return SyncEventsCompanion(
      id: Value(id),
      tenantId: Value(tenantId),
      type: Value(type),
      entityType: entityType == null && nullToAbsent
          ? const Value.absent()
          : Value(entityType),
      entityId: entityId == null && nullToAbsent
          ? const Value.absent()
          : Value(entityId),
      message: Value(message),
      messageAr: messageAr == null && nullToAbsent
          ? const Value.absent()
          : Value(messageAr),
      details: details == null && nullToAbsent
          ? const Value.absent()
          : Value(details),
      resolution: resolution == null && nullToAbsent
          ? const Value.absent()
          : Value(resolution),
      isRead: Value(isRead),
      isResolved: Value(isResolved),
      createdAt: Value(createdAt),
    );
  }

  factory SyncEvent.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SyncEvent(
      id: serializer.fromJson<int>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenantId']),
      type: serializer.fromJson<String>(json['type']),
      entityType: serializer.fromJson<String?>(json['entityType']),
      entityId: serializer.fromJson<String?>(json['entityId']),
      message: serializer.fromJson<String>(json['message']),
      messageAr: serializer.fromJson<String?>(json['messageAr']),
      details: serializer.fromJson<String?>(json['details']),
      resolution: serializer.fromJson<String?>(json['resolution']),
      isRead: serializer.fromJson<bool>(json['isRead']),
      isResolved: serializer.fromJson<bool>(json['isResolved']),
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
      'messageAr': serializer.toJson<String?>(messageAr),
      'details': serializer.toJson<String?>(details),
      'resolution': serializer.toJson<String?>(resolution),
      'isRead': serializer.toJson<bool>(isRead),
      'isResolved': serializer.toJson<bool>(isResolved),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  SyncEvent copyWith(
          {int? id,
          String? tenantId,
          String? type,
          Value<String?> entityType = const Value.absent(),
          Value<String?> entityId = const Value.absent(),
          String? message,
          Value<String?> messageAr = const Value.absent(),
          Value<String?> details = const Value.absent(),
          Value<String?> resolution = const Value.absent(),
          bool? isRead,
          bool? isResolved,
          DateTime? createdAt}) =>
      SyncEvent(
        id: id ?? this.id,
        tenantId: tenantId ?? this.tenantId,
        type: type ?? this.type,
        entityType: entityType.present ? entityType.value : this.entityType,
        entityId: entityId.present ? entityId.value : this.entityId,
        message: message ?? this.message,
        messageAr: messageAr.present ? messageAr.value : this.messageAr,
        details: details.present ? details.value : this.details,
        resolution: resolution.present ? resolution.value : this.resolution,
        isRead: isRead ?? this.isRead,
        isResolved: isResolved ?? this.isResolved,
        createdAt: createdAt ?? this.createdAt,
      );
  SyncEvent copyWithCompanion(SyncEventsCompanion data) {
    return SyncEvent(
      id: data.id.present ? data.id.value : this.id,
      tenantId: data.tenantId.present ? data.tenantId.value : this.tenantId,
      type: data.type.present ? data.type.value : this.type,
      entityType:
          data.entityType.present ? data.entityType.value : this.entityType,
      entityId: data.entityId.present ? data.entityId.value : this.entityId,
      message: data.message.present ? data.message.value : this.message,
      messageAr: data.messageAr.present ? data.messageAr.value : this.messageAr,
      details: data.details.present ? data.details.value : this.details,
      resolution:
          data.resolution.present ? data.resolution.value : this.resolution,
      isRead: data.isRead.present ? data.isRead.value : this.isRead,
      isResolved:
          data.isResolved.present ? data.isResolved.value : this.isResolved,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('SyncEvent(')
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('type: $type, ')
          ..write('entityType: $entityType, ')
          ..write('entityId: $entityId, ')
          ..write('message: $message, ')
          ..write('messageAr: $messageAr, ')
          ..write('details: $details, ')
          ..write('resolution: $resolution, ')
          ..write('isRead: $isRead, ')
          ..write('isResolved: $isResolved, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, tenantId, type, entityType, entityId,
      message, messageAr, details, resolution, isRead, isResolved, createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is SyncEvent &&
          other.id == this.id &&
          other.tenantId == this.tenantId &&
          other.type == this.type &&
          other.entityType == this.entityType &&
          other.entityId == this.entityId &&
          other.message == this.message &&
          other.messageAr == this.messageAr &&
          other.details == this.details &&
          other.resolution == this.resolution &&
          other.isRead == this.isRead &&
          other.isResolved == this.isResolved &&
          other.createdAt == this.createdAt);
}

class SyncEventsCompanion extends UpdateCompanion<SyncEvent> {
  final Value<int> id;
  final Value<String> tenantId;
  final Value<String> type;
  final Value<String?> entityType;
  final Value<String?> entityId;
  final Value<String> message;
  final Value<String?> messageAr;
  final Value<String?> details;
  final Value<String?> resolution;
  final Value<bool> isRead;
  final Value<bool> isResolved;
  final Value<DateTime> createdAt;
  const SyncEventsCompanion({
    this.id = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.type = const Value.absent(),
    this.entityType = const Value.absent(),
    this.entityId = const Value.absent(),
    this.message = const Value.absent(),
    this.messageAr = const Value.absent(),
    this.details = const Value.absent(),
    this.resolution = const Value.absent(),
    this.isRead = const Value.absent(),
    this.isResolved = const Value.absent(),
    this.createdAt = const Value.absent(),
  });
  SyncEventsCompanion.insert({
    this.id = const Value.absent(),
    required String tenantId,
    required String type,
    this.entityType = const Value.absent(),
    this.entityId = const Value.absent(),
    required String message,
    this.messageAr = const Value.absent(),
    this.details = const Value.absent(),
    this.resolution = const Value.absent(),
    this.isRead = const Value.absent(),
    this.isResolved = const Value.absent(),
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
    Expression<String>? messageAr,
    Expression<String>? details,
    Expression<String>? resolution,
    Expression<bool>? isRead,
    Expression<bool>? isResolved,
    Expression<DateTime>? createdAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (tenantId != null) 'tenant_id': tenantId,
      if (type != null) 'type': type,
      if (entityType != null) 'entity_type': entityType,
      if (entityId != null) 'entity_id': entityId,
      if (message != null) 'message': message,
      if (messageAr != null) 'message_ar': messageAr,
      if (details != null) 'details': details,
      if (resolution != null) 'resolution': resolution,
      if (isRead != null) 'is_read': isRead,
      if (isResolved != null) 'is_resolved': isResolved,
      if (createdAt != null) 'created_at': createdAt,
    });
  }

  SyncEventsCompanion copyWith(
      {Value<int>? id,
      Value<String>? tenantId,
      Value<String>? type,
      Value<String?>? entityType,
      Value<String?>? entityId,
      Value<String>? message,
      Value<String?>? messageAr,
      Value<String?>? details,
      Value<String?>? resolution,
      Value<bool>? isRead,
      Value<bool>? isResolved,
      Value<DateTime>? createdAt}) {
    return SyncEventsCompanion(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      type: type ?? this.type,
      entityType: entityType ?? this.entityType,
      entityId: entityId ?? this.entityId,
      message: message ?? this.message,
      messageAr: messageAr ?? this.messageAr,
      details: details ?? this.details,
      resolution: resolution ?? this.resolution,
      isRead: isRead ?? this.isRead,
      isResolved: isResolved ?? this.isResolved,
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
      map['entity_type'] = Variable<String>(entityType.value);
    }
    if (entityId.present) {
      map['entity_id'] = Variable<String>(entityId.value);
    }
    if (message.present) {
      map['message'] = Variable<String>(message.value);
    }
    if (messageAr.present) {
      map['message_ar'] = Variable<String>(messageAr.value);
    }
    if (details.present) {
      map['details'] = Variable<String>(details.value);
    }
    if (resolution.present) {
      map['resolution'] = Variable<String>(resolution.value);
    }
    if (isRead.present) {
      map['is_read'] = Variable<bool>(isRead.value);
    }
    if (isResolved.present) {
      map['is_resolved'] = Variable<bool>(isResolved.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('SyncEventsCompanion(')
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('type: $type, ')
          ..write('entityType: $entityType, ')
          ..write('entityId: $entityId, ')
          ..write('message: $message, ')
          ..write('messageAr: $messageAr, ')
          ..write('details: $details, ')
          ..write('resolution: $resolution, ')
          ..write('isRead: $isRead, ')
          ..write('isResolved: $isResolved, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }
}

abstract class _$SyncDaoTestDatabase extends GeneratedDatabase {
  _$SyncDaoTestDatabase(QueryExecutor e) : super(e);
  $SyncDaoTestDatabaseManager get managers => $SyncDaoTestDatabaseManager(this);
  late final $SyncOutboxTable syncOutbox = $SyncOutboxTable(this);
  late final $SyncLogsTable syncLogs = $SyncLogsTable(this);
  late final $SyncEventsTable syncEvents = $SyncEventsTable(this);
  late final Index syncOutboxTenantIdx = Index('sync_outbox_tenant_idx',
      'CREATE INDEX sync_outbox_tenant_idx ON sync_outbox (tenant_id)');
  late final Index syncOutboxSyncedIdx = Index('sync_outbox_synced_idx',
      'CREATE INDEX sync_outbox_synced_idx ON sync_outbox (is_synced)');
  late final Index syncOutboxEntityIdx = Index('sync_outbox_entity_idx',
      'CREATE INDEX sync_outbox_entity_idx ON sync_outbox (entity_type, entity_id)');
  late final Index syncOutboxCreatedIdx = Index('sync_outbox_created_idx',
      'CREATE INDEX sync_outbox_created_idx ON sync_outbox (created_at)');
  late final Index syncOutboxPriorityIdx = Index('sync_outbox_priority_idx',
      'CREATE INDEX sync_outbox_priority_idx ON sync_outbox (priority)');
  late final Index syncLogsTypeIdx = Index('sync_logs_type_idx',
      'CREATE INDEX sync_logs_type_idx ON sync_logs (type)');
  late final Index syncLogsStatusIdx = Index('sync_logs_status_idx',
      'CREATE INDEX sync_logs_status_idx ON sync_logs (status)');
  late final Index syncLogsTimestampIdx = Index('sync_logs_timestamp_idx',
      'CREATE INDEX sync_logs_timestamp_idx ON sync_logs (timestamp)');
  late final Index syncEventsTenantIdx = Index('sync_events_tenant_idx',
      'CREATE INDEX sync_events_tenant_idx ON sync_events (tenant_id)');
  late final Index syncEventsReadIdx = Index('sync_events_read_idx',
      'CREATE INDEX sync_events_read_idx ON sync_events (is_read)');
  late final Index syncEventsTypeIdx = Index('sync_events_type_idx',
      'CREATE INDEX sync_events_type_idx ON sync_events (type)');
  late final Index syncEventsCreatedIdx = Index('sync_events_created_idx',
      'CREATE INDEX sync_events_created_idx ON sync_events (created_at)');
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
        syncOutbox,
        syncLogs,
        syncEvents,
        syncOutboxTenantIdx,
        syncOutboxSyncedIdx,
        syncOutboxEntityIdx,
        syncOutboxCreatedIdx,
        syncOutboxPriorityIdx,
        syncLogsTypeIdx,
        syncLogsStatusIdx,
        syncLogsTimestampIdx,
        syncEventsTenantIdx,
        syncEventsReadIdx,
        syncEventsTypeIdx,
        syncEventsCreatedIdx
      ];
  @override
  DriftDatabaseOptions get options =>
      const DriftDatabaseOptions(storeDateTimeAsText: true);
}

typedef $$SyncOutboxTableCreateCompanionBuilder = SyncOutboxCompanion Function({
  Value<int> id,
  required String tenantId,
  required String entityType,
  required String entityId,
  required String apiEndpoint,
  Value<String> method,
  required String payload,
  Value<String?> ifMatch,
  Value<int> retryCount,
  Value<int> maxRetries,
  Value<int> priority,
  Value<bool> isSynced,
  Value<String?> errorMessage,
  Value<DateTime?> lastAttempt,
  Value<DateTime> createdAt,
});
typedef $$SyncOutboxTableUpdateCompanionBuilder = SyncOutboxCompanion Function({
  Value<int> id,
  Value<String> tenantId,
  Value<String> entityType,
  Value<String> entityId,
  Value<String> apiEndpoint,
  Value<String> method,
  Value<String> payload,
  Value<String?> ifMatch,
  Value<int> retryCount,
  Value<int> maxRetries,
  Value<int> priority,
  Value<bool> isSynced,
  Value<String?> errorMessage,
  Value<DateTime?> lastAttempt,
  Value<DateTime> createdAt,
});

class $$SyncOutboxTableFilterComposer
    extends Composer<_$SyncDaoTestDatabase, $SyncOutboxTable> {
  $$SyncOutboxTableFilterComposer({
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

  ColumnFilters<String> get ifMatch => $composableBuilder(
      column: $table.ifMatch, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get retryCount => $composableBuilder(
      column: $table.retryCount, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get maxRetries => $composableBuilder(
      column: $table.maxRetries, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get priority => $composableBuilder(
      column: $table.priority, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get isSynced => $composableBuilder(
      column: $table.isSynced, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get errorMessage => $composableBuilder(
      column: $table.errorMessage, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get lastAttempt => $composableBuilder(
      column: $table.lastAttempt, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));
}

class $$SyncOutboxTableOrderingComposer
    extends Composer<_$SyncDaoTestDatabase, $SyncOutboxTable> {
  $$SyncOutboxTableOrderingComposer({
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

  ColumnOrderings<String> get ifMatch => $composableBuilder(
      column: $table.ifMatch, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get retryCount => $composableBuilder(
      column: $table.retryCount, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get maxRetries => $composableBuilder(
      column: $table.maxRetries, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get priority => $composableBuilder(
      column: $table.priority, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get isSynced => $composableBuilder(
      column: $table.isSynced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get errorMessage => $composableBuilder(
      column: $table.errorMessage,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get lastAttempt => $composableBuilder(
      column: $table.lastAttempt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));
}

class $$SyncOutboxTableAnnotationComposer
    extends Composer<_$SyncDaoTestDatabase, $SyncOutboxTable> {
  $$SyncOutboxTableAnnotationComposer({
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

  GeneratedColumn<String> get ifMatch =>
      $composableBuilder(column: $table.ifMatch, builder: (column) => column);

  GeneratedColumn<int> get retryCount => $composableBuilder(
      column: $table.retryCount, builder: (column) => column);

  GeneratedColumn<int> get maxRetries => $composableBuilder(
      column: $table.maxRetries, builder: (column) => column);

  GeneratedColumn<int> get priority =>
      $composableBuilder(column: $table.priority, builder: (column) => column);

  GeneratedColumn<bool> get isSynced =>
      $composableBuilder(column: $table.isSynced, builder: (column) => column);

  GeneratedColumn<String> get errorMessage => $composableBuilder(
      column: $table.errorMessage, builder: (column) => column);

  GeneratedColumn<DateTime> get lastAttempt => $composableBuilder(
      column: $table.lastAttempt, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$SyncOutboxTableTableManager extends RootTableManager<
    _$SyncDaoTestDatabase,
    $SyncOutboxTable,
    SyncOutboxData,
    $$SyncOutboxTableFilterComposer,
    $$SyncOutboxTableOrderingComposer,
    $$SyncOutboxTableAnnotationComposer,
    $$SyncOutboxTableCreateCompanionBuilder,
    $$SyncOutboxTableUpdateCompanionBuilder,
    (
      SyncOutboxData,
      BaseReferences<_$SyncDaoTestDatabase, $SyncOutboxTable, SyncOutboxData>
    ),
    SyncOutboxData,
    PrefetchHooks Function()> {
  $$SyncOutboxTableTableManager(
      _$SyncDaoTestDatabase db, $SyncOutboxTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$SyncOutboxTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$SyncOutboxTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$SyncOutboxTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> tenantId = const Value.absent(),
            Value<String> entityType = const Value.absent(),
            Value<String> entityId = const Value.absent(),
            Value<String> apiEndpoint = const Value.absent(),
            Value<String> method = const Value.absent(),
            Value<String> payload = const Value.absent(),
            Value<String?> ifMatch = const Value.absent(),
            Value<int> retryCount = const Value.absent(),
            Value<int> maxRetries = const Value.absent(),
            Value<int> priority = const Value.absent(),
            Value<bool> isSynced = const Value.absent(),
            Value<String?> errorMessage = const Value.absent(),
            Value<DateTime?> lastAttempt = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
          }) =>
              SyncOutboxCompanion(
            id: id,
            tenantId: tenantId,
            entityType: entityType,
            entityId: entityId,
            apiEndpoint: apiEndpoint,
            method: method,
            payload: payload,
            ifMatch: ifMatch,
            retryCount: retryCount,
            maxRetries: maxRetries,
            priority: priority,
            isSynced: isSynced,
            errorMessage: errorMessage,
            lastAttempt: lastAttempt,
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
            Value<String?> ifMatch = const Value.absent(),
            Value<int> retryCount = const Value.absent(),
            Value<int> maxRetries = const Value.absent(),
            Value<int> priority = const Value.absent(),
            Value<bool> isSynced = const Value.absent(),
            Value<String?> errorMessage = const Value.absent(),
            Value<DateTime?> lastAttempt = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
          }) =>
              SyncOutboxCompanion.insert(
            id: id,
            tenantId: tenantId,
            entityType: entityType,
            entityId: entityId,
            apiEndpoint: apiEndpoint,
            method: method,
            payload: payload,
            ifMatch: ifMatch,
            retryCount: retryCount,
            maxRetries: maxRetries,
            priority: priority,
            isSynced: isSynced,
            errorMessage: errorMessage,
            lastAttempt: lastAttempt,
            createdAt: createdAt,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$SyncOutboxTableProcessedTableManager = ProcessedTableManager<
    _$SyncDaoTestDatabase,
    $SyncOutboxTable,
    SyncOutboxData,
    $$SyncOutboxTableFilterComposer,
    $$SyncOutboxTableOrderingComposer,
    $$SyncOutboxTableAnnotationComposer,
    $$SyncOutboxTableCreateCompanionBuilder,
    $$SyncOutboxTableUpdateCompanionBuilder,
    (
      SyncOutboxData,
      BaseReferences<_$SyncDaoTestDatabase, $SyncOutboxTable, SyncOutboxData>
    ),
    SyncOutboxData,
    PrefetchHooks Function()>;
typedef $$SyncLogsTableCreateCompanionBuilder = SyncLogsCompanion Function({
  Value<int> id,
  required String type,
  required String status,
  Value<String?> message,
  Value<int?> itemsSynced,
  Value<int?> itemsFailed,
  Value<int?> durationMs,
  Value<String?> details,
  required DateTime timestamp,
});
typedef $$SyncLogsTableUpdateCompanionBuilder = SyncLogsCompanion Function({
  Value<int> id,
  Value<String> type,
  Value<String> status,
  Value<String?> message,
  Value<int?> itemsSynced,
  Value<int?> itemsFailed,
  Value<int?> durationMs,
  Value<String?> details,
  Value<DateTime> timestamp,
});

class $$SyncLogsTableFilterComposer
    extends Composer<_$SyncDaoTestDatabase, $SyncLogsTable> {
  $$SyncLogsTableFilterComposer({
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

  ColumnFilters<int> get itemsSynced => $composableBuilder(
      column: $table.itemsSynced, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get itemsFailed => $composableBuilder(
      column: $table.itemsFailed, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get durationMs => $composableBuilder(
      column: $table.durationMs, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get details => $composableBuilder(
      column: $table.details, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get timestamp => $composableBuilder(
      column: $table.timestamp, builder: (column) => ColumnFilters(column));
}

class $$SyncLogsTableOrderingComposer
    extends Composer<_$SyncDaoTestDatabase, $SyncLogsTable> {
  $$SyncLogsTableOrderingComposer({
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

  ColumnOrderings<int> get itemsSynced => $composableBuilder(
      column: $table.itemsSynced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get itemsFailed => $composableBuilder(
      column: $table.itemsFailed, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get durationMs => $composableBuilder(
      column: $table.durationMs, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get details => $composableBuilder(
      column: $table.details, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get timestamp => $composableBuilder(
      column: $table.timestamp, builder: (column) => ColumnOrderings(column));
}

class $$SyncLogsTableAnnotationComposer
    extends Composer<_$SyncDaoTestDatabase, $SyncLogsTable> {
  $$SyncLogsTableAnnotationComposer({
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

  GeneratedColumn<int> get itemsSynced => $composableBuilder(
      column: $table.itemsSynced, builder: (column) => column);

  GeneratedColumn<int> get itemsFailed => $composableBuilder(
      column: $table.itemsFailed, builder: (column) => column);

  GeneratedColumn<int> get durationMs => $composableBuilder(
      column: $table.durationMs, builder: (column) => column);

  GeneratedColumn<String> get details =>
      $composableBuilder(column: $table.details, builder: (column) => column);

  GeneratedColumn<DateTime> get timestamp =>
      $composableBuilder(column: $table.timestamp, builder: (column) => column);
}

class $$SyncLogsTableTableManager extends RootTableManager<
    _$SyncDaoTestDatabase,
    $SyncLogsTable,
    SyncLog,
    $$SyncLogsTableFilterComposer,
    $$SyncLogsTableOrderingComposer,
    $$SyncLogsTableAnnotationComposer,
    $$SyncLogsTableCreateCompanionBuilder,
    $$SyncLogsTableUpdateCompanionBuilder,
    (SyncLog, BaseReferences<_$SyncDaoTestDatabase, $SyncLogsTable, SyncLog>),
    SyncLog,
    PrefetchHooks Function()> {
  $$SyncLogsTableTableManager(_$SyncDaoTestDatabase db, $SyncLogsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$SyncLogsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$SyncLogsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$SyncLogsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> type = const Value.absent(),
            Value<String> status = const Value.absent(),
            Value<String?> message = const Value.absent(),
            Value<int?> itemsSynced = const Value.absent(),
            Value<int?> itemsFailed = const Value.absent(),
            Value<int?> durationMs = const Value.absent(),
            Value<String?> details = const Value.absent(),
            Value<DateTime> timestamp = const Value.absent(),
          }) =>
              SyncLogsCompanion(
            id: id,
            type: type,
            status: status,
            message: message,
            itemsSynced: itemsSynced,
            itemsFailed: itemsFailed,
            durationMs: durationMs,
            details: details,
            timestamp: timestamp,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String type,
            required String status,
            Value<String?> message = const Value.absent(),
            Value<int?> itemsSynced = const Value.absent(),
            Value<int?> itemsFailed = const Value.absent(),
            Value<int?> durationMs = const Value.absent(),
            Value<String?> details = const Value.absent(),
            required DateTime timestamp,
          }) =>
              SyncLogsCompanion.insert(
            id: id,
            type: type,
            status: status,
            message: message,
            itemsSynced: itemsSynced,
            itemsFailed: itemsFailed,
            durationMs: durationMs,
            details: details,
            timestamp: timestamp,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$SyncLogsTableProcessedTableManager = ProcessedTableManager<
    _$SyncDaoTestDatabase,
    $SyncLogsTable,
    SyncLog,
    $$SyncLogsTableFilterComposer,
    $$SyncLogsTableOrderingComposer,
    $$SyncLogsTableAnnotationComposer,
    $$SyncLogsTableCreateCompanionBuilder,
    $$SyncLogsTableUpdateCompanionBuilder,
    (SyncLog, BaseReferences<_$SyncDaoTestDatabase, $SyncLogsTable, SyncLog>),
    SyncLog,
    PrefetchHooks Function()>;
typedef $$SyncEventsTableCreateCompanionBuilder = SyncEventsCompanion Function({
  Value<int> id,
  required String tenantId,
  required String type,
  Value<String?> entityType,
  Value<String?> entityId,
  required String message,
  Value<String?> messageAr,
  Value<String?> details,
  Value<String?> resolution,
  Value<bool> isRead,
  Value<bool> isResolved,
  Value<DateTime> createdAt,
});
typedef $$SyncEventsTableUpdateCompanionBuilder = SyncEventsCompanion Function({
  Value<int> id,
  Value<String> tenantId,
  Value<String> type,
  Value<String?> entityType,
  Value<String?> entityId,
  Value<String> message,
  Value<String?> messageAr,
  Value<String?> details,
  Value<String?> resolution,
  Value<bool> isRead,
  Value<bool> isResolved,
  Value<DateTime> createdAt,
});

class $$SyncEventsTableFilterComposer
    extends Composer<_$SyncDaoTestDatabase, $SyncEventsTable> {
  $$SyncEventsTableFilterComposer({
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

  ColumnFilters<String> get entityType => $composableBuilder(
      column: $table.entityType, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get entityId => $composableBuilder(
      column: $table.entityId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get message => $composableBuilder(
      column: $table.message, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get messageAr => $composableBuilder(
      column: $table.messageAr, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get details => $composableBuilder(
      column: $table.details, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get resolution => $composableBuilder(
      column: $table.resolution, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get isRead => $composableBuilder(
      column: $table.isRead, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get isResolved => $composableBuilder(
      column: $table.isResolved, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));
}

class $$SyncEventsTableOrderingComposer
    extends Composer<_$SyncDaoTestDatabase, $SyncEventsTable> {
  $$SyncEventsTableOrderingComposer({
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

  ColumnOrderings<String> get entityType => $composableBuilder(
      column: $table.entityType, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get entityId => $composableBuilder(
      column: $table.entityId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get message => $composableBuilder(
      column: $table.message, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get messageAr => $composableBuilder(
      column: $table.messageAr, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get details => $composableBuilder(
      column: $table.details, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get resolution => $composableBuilder(
      column: $table.resolution, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get isRead => $composableBuilder(
      column: $table.isRead, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get isResolved => $composableBuilder(
      column: $table.isResolved, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));
}

class $$SyncEventsTableAnnotationComposer
    extends Composer<_$SyncDaoTestDatabase, $SyncEventsTable> {
  $$SyncEventsTableAnnotationComposer({
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

  GeneratedColumn<String> get entityType => $composableBuilder(
      column: $table.entityType, builder: (column) => column);

  GeneratedColumn<String> get entityId =>
      $composableBuilder(column: $table.entityId, builder: (column) => column);

  GeneratedColumn<String> get message =>
      $composableBuilder(column: $table.message, builder: (column) => column);

  GeneratedColumn<String> get messageAr =>
      $composableBuilder(column: $table.messageAr, builder: (column) => column);

  GeneratedColumn<String> get details =>
      $composableBuilder(column: $table.details, builder: (column) => column);

  GeneratedColumn<String> get resolution => $composableBuilder(
      column: $table.resolution, builder: (column) => column);

  GeneratedColumn<bool> get isRead =>
      $composableBuilder(column: $table.isRead, builder: (column) => column);

  GeneratedColumn<bool> get isResolved => $composableBuilder(
      column: $table.isResolved, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$SyncEventsTableTableManager extends RootTableManager<
    _$SyncDaoTestDatabase,
    $SyncEventsTable,
    SyncEvent,
    $$SyncEventsTableFilterComposer,
    $$SyncEventsTableOrderingComposer,
    $$SyncEventsTableAnnotationComposer,
    $$SyncEventsTableCreateCompanionBuilder,
    $$SyncEventsTableUpdateCompanionBuilder,
    (
      SyncEvent,
      BaseReferences<_$SyncDaoTestDatabase, $SyncEventsTable, SyncEvent>
    ),
    SyncEvent,
    PrefetchHooks Function()> {
  $$SyncEventsTableTableManager(
      _$SyncDaoTestDatabase db, $SyncEventsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$SyncEventsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$SyncEventsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$SyncEventsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> tenantId = const Value.absent(),
            Value<String> type = const Value.absent(),
            Value<String?> entityType = const Value.absent(),
            Value<String?> entityId = const Value.absent(),
            Value<String> message = const Value.absent(),
            Value<String?> messageAr = const Value.absent(),
            Value<String?> details = const Value.absent(),
            Value<String?> resolution = const Value.absent(),
            Value<bool> isRead = const Value.absent(),
            Value<bool> isResolved = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
          }) =>
              SyncEventsCompanion(
            id: id,
            tenantId: tenantId,
            type: type,
            entityType: entityType,
            entityId: entityId,
            message: message,
            messageAr: messageAr,
            details: details,
            resolution: resolution,
            isRead: isRead,
            isResolved: isResolved,
            createdAt: createdAt,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String tenantId,
            required String type,
            Value<String?> entityType = const Value.absent(),
            Value<String?> entityId = const Value.absent(),
            required String message,
            Value<String?> messageAr = const Value.absent(),
            Value<String?> details = const Value.absent(),
            Value<String?> resolution = const Value.absent(),
            Value<bool> isRead = const Value.absent(),
            Value<bool> isResolved = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
          }) =>
              SyncEventsCompanion.insert(
            id: id,
            tenantId: tenantId,
            type: type,
            entityType: entityType,
            entityId: entityId,
            message: message,
            messageAr: messageAr,
            details: details,
            resolution: resolution,
            isRead: isRead,
            isResolved: isResolved,
            createdAt: createdAt,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$SyncEventsTableProcessedTableManager = ProcessedTableManager<
    _$SyncDaoTestDatabase,
    $SyncEventsTable,
    SyncEvent,
    $$SyncEventsTableFilterComposer,
    $$SyncEventsTableOrderingComposer,
    $$SyncEventsTableAnnotationComposer,
    $$SyncEventsTableCreateCompanionBuilder,
    $$SyncEventsTableUpdateCompanionBuilder,
    (
      SyncEvent,
      BaseReferences<_$SyncDaoTestDatabase, $SyncEventsTable, SyncEvent>
    ),
    SyncEvent,
    PrefetchHooks Function()>;

class $SyncDaoTestDatabaseManager {
  final _$SyncDaoTestDatabase _db;
  $SyncDaoTestDatabaseManager(this._db);
  $$SyncOutboxTableTableManager get syncOutbox =>
      $$SyncOutboxTableTableManager(_db, _db.syncOutbox);
  $$SyncLogsTableTableManager get syncLogs =>
      $$SyncLogsTableTableManager(_db, _db.syncLogs);
  $$SyncEventsTableTableManager get syncEvents =>
      $$SyncEventsTableTableManager(_db, _db.syncEvents);
}
