// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'sync_queue_dao_test.dart';

// ignore_for_file: type=lint

// **************************************************************************
// DriftDatabaseGenerator
// **************************************************************************

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

  const SyncOutboxData({
    this.id,
    required this.tenantId,
    required this.entityType,
    required this.entityId,
    required this.apiEndpoint,
    this.method,
    required this.payload,
    this.ifMatch,
    this.retryCount,
    this.maxRetries,
    this.priority,
    this.isSynced,
    this.errorMessage,
    this.lastAttempt,
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

  factory SyncOutboxData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SyncOutboxData(
      id: serializer.fromJson<int>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenant_id']),
      entityType: serializer.fromJson<String>(json['entity_type']),
      entityId: serializer.fromJson<String>(json['entity_id']),
      apiEndpoint: serializer.fromJson<String>(json['api_endpoint']),
      method: serializer.fromJson<String>(json['method']),
      payload: serializer.fromJson<String>(json['payload']),
      ifMatch: serializer.fromJson<String?>(json['if_match']),
      retryCount: serializer.fromJson<int>(json['retry_count']),
      maxRetries: serializer.fromJson<int>(json['max_retries']),
      priority: serializer.fromJson<int>(json['priority']),
      isSynced: serializer.fromJson<bool>(json['is_synced']),
      errorMessage: serializer.fromJson<String?>(json['error_message']),
      lastAttempt: serializer.fromJson<DateTime?>(json['last_attempt']),
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
      'max_retries': serializer.toJson<int>(maxRetries),
      'priority': serializer.toJson<int>(priority),
      'is_synced': serializer.toJson<bool>(isSynced),
      'error_message': serializer.toJson<String?>(errorMessage),
      'last_attempt': serializer.toJson<DateTime?>(lastAttempt),
      'created_at': serializer.toJson<DateTime>(createdAt),
    };
  }

  SyncOutboxData copyWith({
    int? id,
    String? tenantId,
    String? entityType,
    String? entityId,
    String? apiEndpoint,
    String? method,
    String? payload,
    Value<String> ifMatch = const Value.absent(),
    int? retryCount,
    int? maxRetries,
    int? priority,
    bool? isSynced,
    Value<String> errorMessage = const Value.absent(),
    Value<DateTime> lastAttempt = const Value.absent(),
    DateTime? createdAt,
  }) {
    return SyncOutboxData(
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
      errorMessage: errorMessage.present ? errorMessage.value : this.errorMessage,
      lastAttempt: lastAttempt.present ? lastAttempt.value : this.lastAttempt,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('SyncOutboxData(')
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('entityType: ${entityType}, ')
          ..write('entityId: ${entityId}, ')
          ..write('apiEndpoint: ${apiEndpoint}, ')
          ..write('method: ${method}, ')
          ..write('payload: ${payload}, ')
          ..write('ifMatch: ${ifMatch}, ')
          ..write('retryCount: ${retryCount}, ')
          ..write('maxRetries: ${maxRetries}, ')
          ..write('priority: ${priority}, ')
          ..write('isSynced: ${isSynced}, ')
          ..write('errorMessage: ${errorMessage}, ')
          ..write('lastAttempt: ${lastAttempt}, ')
          ..write('createdAt: ${createdAt}')
          ..write(')')
      ).toString();
  }

  @override
  int get hashCode => Object.hash(id, tenantId, entityType, entityId, apiEndpoint, method, payload, ifMatch, retryCount, maxRetries, priority, isSynced, errorMessage, lastAttempt, createdAt);

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
          other.createdAt == this.createdAt)
  ;
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
  })
      : tenantId = Value(tenantId),
        entityType = Value(entityType),
        entityId = Value(entityId),
        apiEndpoint = Value(apiEndpoint),
        payload = Value(payload);

  static Insertable<SyncOutboxData> custom({
    Expression<dynamic>? id,
    Expression<dynamic>? tenantId,
    Expression<dynamic>? entityType,
    Expression<dynamic>? entityId,
    Expression<dynamic>? apiEndpoint,
    Expression<dynamic>? method,
    Expression<dynamic>? payload,
    Expression<dynamic>? ifMatch,
    Expression<dynamic>? retryCount,
    Expression<dynamic>? maxRetries,
    Expression<dynamic>? priority,
    Expression<dynamic>? isSynced,
    Expression<dynamic>? errorMessage,
    Expression<dynamic>? lastAttempt,
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
      if (maxRetries != null) 'max_retries': maxRetries,
      if (priority != null) 'priority': priority,
      if (isSynced != null) 'is_synced': isSynced,
      if (errorMessage != null) 'error_message': errorMessage,
      if (lastAttempt != null) 'last_attempt': lastAttempt,
      if (createdAt != null) 'created_at': createdAt,
    });
  }

  SyncOutboxCompanion copyWith({
    Value<int>? id,
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
    Value<DateTime>? createdAt,
  }) {
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
      map['if_match'] = Variable<String?>(ifMatch.value);
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
      map['error_message'] = Variable<String?>(errorMessage.value);
    }
    if (lastAttempt.present) {
      map['last_attempt'] = Variable<DateTime?>(lastAttempt.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('SyncOutboxCompanion(')
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('entityType: ${entityType}, ')
          ..write('entityId: ${entityId}, ')
          ..write('apiEndpoint: ${apiEndpoint}, ')
          ..write('method: ${method}, ')
          ..write('payload: ${payload}, ')
          ..write('ifMatch: ${ifMatch}, ')
          ..write('retryCount: ${retryCount}, ')
          ..write('maxRetries: ${maxRetries}, ')
          ..write('priority: ${priority}, ')
          ..write('isSynced: ${isSynced}, ')
          ..write('errorMessage: ${errorMessage}, ')
          ..write('lastAttempt: ${lastAttempt}, ')
          ..write('createdAt: ${createdAt}')
          ..write(')')
      ).toString();
  }
}

class \$SyncOutboxTable extends SyncOutbox
    with TableInfo<\$SyncOutboxTable, SyncOutboxData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  \$SyncOutboxTable(this.attachedDatabase, [this._alias]);

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

  static const VerificationMeta _maxRetriesMeta = VerificationMeta('maxRetries');
  @override
  late final GeneratedColumn<int> maxRetries =
      GeneratedColumn<int>(
          'max_retries', aliasedName, false,
          defaultValue: const Constant(5),
          type: DriftSqlType.int,
          requiredDuringInsert: false);

  static const VerificationMeta _priorityMeta = VerificationMeta('priority');
  @override
  late final GeneratedColumn<int> priority =
      GeneratedColumn<int>(
          'priority', aliasedName, false,
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

  static const VerificationMeta _errorMessageMeta = VerificationMeta('errorMessage');
  @override
  late final GeneratedColumn<String> errorMessage =
      GeneratedColumn<String>(
          'error_message', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _lastAttemptMeta = VerificationMeta('lastAttempt');
  @override
  late final GeneratedColumn<DateTime> lastAttempt =
      GeneratedColumn<DateTime>(
          'last_attempt', aliasedName, true,
          type: DriftSqlType.dateTime,
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
  List<GeneratedColumn> get $columns => [id, tenantId, entityType, entityId, apiEndpoint, method, payload, ifMatch, retryCount, maxRetries, priority, isSynced, errorMessage, lastAttempt, createdAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String \$name = 'sync_outbox';

  @override
  VerificationContext validateIntegrity(Insertable<SyncOutboxData> instance,
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
    if (data.containsKey('max_retries')) {
      context.handle(_maxRetriesMeta,
          maxRetries.isAcceptableOrUnknown(data['max_retries']!, _maxRetriesMeta));
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
      context.handle(_errorMessageMeta,
          errorMessage.isAcceptableOrUnknown(data['error_message']!, _errorMessageMeta));
    }
    if (data.containsKey('last_attempt')) {
      context.handle(_lastAttemptMeta,
          lastAttempt.isAcceptableOrUnknown(data['last_attempt']!, _lastAttemptMeta));
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
    final effectivePrefix = tablePrefix != null ? '\$tablePrefix.' : '';
    return SyncOutboxData(
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
      maxRetries: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['\${effectivePrefix}max_retries'])!,
      priority: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['\${effectivePrefix}priority'])!,
      isSynced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['\${effectivePrefix}is_synced'])!,
      errorMessage: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}error_message']),
      lastAttempt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}last_attempt']),
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}created_at'])!,
    );
  }

  @override
  \$SyncOutboxTable createAlias(String alias) {
    return \$SyncOutboxTable(attachedDatabase, alias);
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

  const SyncLog({
    this.id,
    required this.type,
    required this.status,
    this.message,
    this.itemsSynced,
    this.itemsFailed,
    this.durationMs,
    this.details,
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

  factory SyncLog.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SyncLog(
      id: serializer.fromJson<int>(json['id']),
      type: serializer.fromJson<String>(json['type']),
      status: serializer.fromJson<String>(json['status']),
      message: serializer.fromJson<String?>(json['message']),
      itemsSynced: serializer.fromJson<int?>(json['items_synced']),
      itemsFailed: serializer.fromJson<int?>(json['items_failed']),
      durationMs: serializer.fromJson<int?>(json['duration_ms']),
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
      'items_synced': serializer.toJson<int?>(itemsSynced),
      'items_failed': serializer.toJson<int?>(itemsFailed),
      'duration_ms': serializer.toJson<int?>(durationMs),
      'details': serializer.toJson<String?>(details),
      'timestamp': serializer.toJson<DateTime>(timestamp),
    };
  }

  SyncLog copyWith({
    int? id,
    String? type,
    String? status,
    Value<String> message = const Value.absent(),
    Value<int> itemsSynced = const Value.absent(),
    Value<int> itemsFailed = const Value.absent(),
    Value<int> durationMs = const Value.absent(),
    Value<String> details = const Value.absent(),
    DateTime? timestamp,
  }) {
    return SyncLog(
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
  }

  @override
  String toString() {
    return (StringBuffer('SyncLog(')
          ..write('id: ${id}, ')
          ..write('type: ${type}, ')
          ..write('status: ${status}, ')
          ..write('message: ${message}, ')
          ..write('itemsSynced: ${itemsSynced}, ')
          ..write('itemsFailed: ${itemsFailed}, ')
          ..write('durationMs: ${durationMs}, ')
          ..write('details: ${details}, ')
          ..write('timestamp: ${timestamp}')
          ..write(')')
      ).toString();
  }

  @override
  int get hashCode => Object.hash(id, type, status, message, itemsSynced, itemsFailed, durationMs, details, timestamp);

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
          other.timestamp == this.timestamp)
  ;
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
    Value<String?> message = const Value.absent(),
    Value<int?> itemsSynced = const Value.absent(),
    Value<int?> itemsFailed = const Value.absent(),
    Value<int?> durationMs = const Value.absent(),
    Value<String?> details = const Value.absent(),
    required DateTime timestamp,
  })
      : type = Value(type),
        status = Value(status),
        timestamp = Value(timestamp);

  static Insertable<SyncLog> custom({
    Expression<dynamic>? id,
    Expression<dynamic>? type,
    Expression<dynamic>? status,
    Expression<dynamic>? message,
    Expression<dynamic>? itemsSynced,
    Expression<dynamic>? itemsFailed,
    Expression<dynamic>? durationMs,
    Expression<dynamic>? details,
    Expression<dynamic>? timestamp,
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

  SyncLogsCompanion copyWith({
    Value<int>? id,
    Value<String>? type,
    Value<String>? status,
    Value<String?>? message,
    Value<int?>? itemsSynced,
    Value<int?>? itemsFailed,
    Value<int?>? durationMs,
    Value<String?>? details,
    Value<DateTime>? timestamp,
  }) {
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
      map['message'] = Variable<String?>(message.value);
    }
    if (itemsSynced.present) {
      map['items_synced'] = Variable<int?>(itemsSynced.value);
    }
    if (itemsFailed.present) {
      map['items_failed'] = Variable<int?>(itemsFailed.value);
    }
    if (durationMs.present) {
      map['duration_ms'] = Variable<int?>(durationMs.value);
    }
    if (details.present) {
      map['details'] = Variable<String?>(details.value);
    }
    if (timestamp.present) {
      map['timestamp'] = Variable<DateTime>(timestamp.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('SyncLogsCompanion(')
          ..write('id: ${id}, ')
          ..write('type: ${type}, ')
          ..write('status: ${status}, ')
          ..write('message: ${message}, ')
          ..write('itemsSynced: ${itemsSynced}, ')
          ..write('itemsFailed: ${itemsFailed}, ')
          ..write('durationMs: ${durationMs}, ')
          ..write('details: ${details}, ')
          ..write('timestamp: ${timestamp}')
          ..write(')')
      ).toString();
  }
}

class \$SyncLogsTable extends SyncLogs
    with TableInfo<\$SyncLogsTable, SyncLog> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  \$SyncLogsTable(this.attachedDatabase, [this._alias]);

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

  static const VerificationMeta _itemsSyncedMeta = VerificationMeta('itemsSynced');
  @override
  late final GeneratedColumn<int> itemsSynced =
      GeneratedColumn<int>(
          'items_synced', aliasedName, true,
          type: DriftSqlType.int,
          requiredDuringInsert: false);

  static const VerificationMeta _itemsFailedMeta = VerificationMeta('itemsFailed');
  @override
  late final GeneratedColumn<int> itemsFailed =
      GeneratedColumn<int>(
          'items_failed', aliasedName, true,
          type: DriftSqlType.int,
          requiredDuringInsert: false);

  static const VerificationMeta _durationMsMeta = VerificationMeta('durationMs');
  @override
  late final GeneratedColumn<int> durationMs =
      GeneratedColumn<int>(
          'duration_ms', aliasedName, true,
          type: DriftSqlType.int,
          requiredDuringInsert: false);

  static const VerificationMeta _detailsMeta = VerificationMeta('details');
  @override
  late final GeneratedColumn<String> details =
      GeneratedColumn<String>(
          'details', aliasedName, true,
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
  List<GeneratedColumn> get $columns => [id, type, status, message, itemsSynced, itemsFailed, durationMs, details, timestamp];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String \$name = 'sync_logs';

  @override
  VerificationContext validateIntegrity(Insertable<SyncLog> instance,
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
    if (data.containsKey('items_synced')) {
      context.handle(_itemsSyncedMeta,
          itemsSynced.isAcceptableOrUnknown(data['items_synced']!, _itemsSyncedMeta));
    }
    if (data.containsKey('items_failed')) {
      context.handle(_itemsFailedMeta,
          itemsFailed.isAcceptableOrUnknown(data['items_failed']!, _itemsFailedMeta));
    }
    if (data.containsKey('duration_ms')) {
      context.handle(_durationMsMeta,
          durationMs.isAcceptableOrUnknown(data['duration_ms']!, _durationMsMeta));
    }
    if (data.containsKey('details')) {
      context.handle(_detailsMeta,
          details.isAcceptableOrUnknown(data['details']!, _detailsMeta));
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
  SyncLog map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '\$tablePrefix.' : '';
    return SyncLog(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['\${effectivePrefix}id'])!,
      type: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}type'])!,
      status: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}status'])!,
      message: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}message']),
      itemsSynced: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['\${effectivePrefix}items_synced']),
      itemsFailed: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['\${effectivePrefix}items_failed']),
      durationMs: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['\${effectivePrefix}duration_ms']),
      details: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}details']),
      timestamp: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}timestamp'])!,
    );
  }

  @override
  \$SyncLogsTable createAlias(String alias) {
    return \$SyncLogsTable(attachedDatabase, alias);
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

  const SyncEvent({
    this.id,
    required this.tenantId,
    required this.type,
    this.entityType,
    this.entityId,
    required this.message,
    this.messageAr,
    this.details,
    this.resolution,
    this.isRead,
    this.isResolved,
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

  factory SyncEvent.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SyncEvent(
      id: serializer.fromJson<int>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenant_id']),
      type: serializer.fromJson<String>(json['type']),
      entityType: serializer.fromJson<String?>(json['entity_type']),
      entityId: serializer.fromJson<String?>(json['entity_id']),
      message: serializer.fromJson<String>(json['message']),
      messageAr: serializer.fromJson<String?>(json['message_ar']),
      details: serializer.fromJson<String?>(json['details']),
      resolution: serializer.fromJson<String?>(json['resolution']),
      isRead: serializer.fromJson<bool>(json['is_read']),
      isResolved: serializer.fromJson<bool>(json['is_resolved']),
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
      'message_ar': serializer.toJson<String?>(messageAr),
      'details': serializer.toJson<String?>(details),
      'resolution': serializer.toJson<String?>(resolution),
      'is_read': serializer.toJson<bool>(isRead),
      'is_resolved': serializer.toJson<bool>(isResolved),
      'created_at': serializer.toJson<DateTime>(createdAt),
    };
  }

  SyncEvent copyWith({
    int? id,
    String? tenantId,
    String? type,
    Value<String> entityType = const Value.absent(),
    Value<String> entityId = const Value.absent(),
    String? message,
    Value<String> messageAr = const Value.absent(),
    Value<String> details = const Value.absent(),
    Value<String> resolution = const Value.absent(),
    bool? isRead,
    bool? isResolved,
    DateTime? createdAt,
  }) {
    return SyncEvent(
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
  }

  @override
  String toString() {
    return (StringBuffer('SyncEvent(')
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('type: ${type}, ')
          ..write('entityType: ${entityType}, ')
          ..write('entityId: ${entityId}, ')
          ..write('message: ${message}, ')
          ..write('messageAr: ${messageAr}, ')
          ..write('details: ${details}, ')
          ..write('resolution: ${resolution}, ')
          ..write('isRead: ${isRead}, ')
          ..write('isResolved: ${isResolved}, ')
          ..write('createdAt: ${createdAt}')
          ..write(')')
      ).toString();
  }

  @override
  int get hashCode => Object.hash(id, tenantId, type, entityType, entityId, message, messageAr, details, resolution, isRead, isResolved, createdAt);

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
          other.createdAt == this.createdAt)
  ;
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
    Value<String?> entityType = const Value.absent(),
    Value<String?> entityId = const Value.absent(),
    required String message,
    Value<String?> messageAr = const Value.absent(),
    Value<String?> details = const Value.absent(),
    Value<String?> resolution = const Value.absent(),
    Value<bool> isRead = const Value.absent(),
    Value<bool> isResolved = const Value.absent(),
    Value<DateTime> createdAt = const Value.absent(),
  })
      : tenantId = Value(tenantId),
        type = Value(type),
        message = Value(message);

  static Insertable<SyncEvent> custom({
    Expression<dynamic>? id,
    Expression<dynamic>? tenantId,
    Expression<dynamic>? type,
    Expression<dynamic>? entityType,
    Expression<dynamic>? entityId,
    Expression<dynamic>? message,
    Expression<dynamic>? messageAr,
    Expression<dynamic>? details,
    Expression<dynamic>? resolution,
    Expression<dynamic>? isRead,
    Expression<dynamic>? isResolved,
    Expression<dynamic>? createdAt,
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

  SyncEventsCompanion copyWith({
    Value<int>? id,
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
    Value<DateTime>? createdAt,
  }) {
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
      map['entity_type'] = Variable<String?>(entityType.value);
    }
    if (entityId.present) {
      map['entity_id'] = Variable<String?>(entityId.value);
    }
    if (message.present) {
      map['message'] = Variable<String>(message.value);
    }
    if (messageAr.present) {
      map['message_ar'] = Variable<String?>(messageAr.value);
    }
    if (details.present) {
      map['details'] = Variable<String?>(details.value);
    }
    if (resolution.present) {
      map['resolution'] = Variable<String?>(resolution.value);
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
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('type: ${type}, ')
          ..write('entityType: ${entityType}, ')
          ..write('entityId: ${entityId}, ')
          ..write('message: ${message}, ')
          ..write('messageAr: ${messageAr}, ')
          ..write('details: ${details}, ')
          ..write('resolution: ${resolution}, ')
          ..write('isRead: ${isRead}, ')
          ..write('isResolved: ${isResolved}, ')
          ..write('createdAt: ${createdAt}')
          ..write(')')
      ).toString();
  }
}

class \$SyncEventsTable extends SyncEvents
    with TableInfo<\$SyncEventsTable, SyncEvent> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  \$SyncEventsTable(this.attachedDatabase, [this._alias]);

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

  static const VerificationMeta _messageArMeta = VerificationMeta('messageAr');
  @override
  late final GeneratedColumn<String> messageAr =
      GeneratedColumn<String>(
          'message_ar', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _detailsMeta = VerificationMeta('details');
  @override
  late final GeneratedColumn<String> details =
      GeneratedColumn<String>(
          'details', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _resolutionMeta = VerificationMeta('resolution');
  @override
  late final GeneratedColumn<String> resolution =
      GeneratedColumn<String>(
          'resolution', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _isReadMeta = VerificationMeta('isRead');
  @override
  late final GeneratedColumn<bool> isRead =
      GeneratedColumn<bool>(
          'is_read', aliasedName, false,
          defaultValue: const Constant(false),
          type: DriftSqlType.bool,
          requiredDuringInsert: false);

  static const VerificationMeta _isResolvedMeta = VerificationMeta('isResolved');
  @override
  late final GeneratedColumn<bool> isResolved =
      GeneratedColumn<bool>(
          'is_resolved', aliasedName, false,
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
  List<GeneratedColumn> get $columns => [id, tenantId, type, entityType, entityId, message, messageAr, details, resolution, isRead, isResolved, createdAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String \$name = 'sync_events';

  @override
  VerificationContext validateIntegrity(Insertable<SyncEvent> instance,
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
    if (data.containsKey('message_ar')) {
      context.handle(_messageArMeta,
          messageAr.isAcceptableOrUnknown(data['message_ar']!, _messageArMeta));
    }
    if (data.containsKey('details')) {
      context.handle(_detailsMeta,
          details.isAcceptableOrUnknown(data['details']!, _detailsMeta));
    }
    if (data.containsKey('resolution')) {
      context.handle(_resolutionMeta,
          resolution.isAcceptableOrUnknown(data['resolution']!, _resolutionMeta));
    }
    if (data.containsKey('is_read')) {
      context.handle(_isReadMeta,
          isRead.isAcceptableOrUnknown(data['is_read']!, _isReadMeta));
    }
    if (data.containsKey('is_resolved')) {
      context.handle(_isResolvedMeta,
          isResolved.isAcceptableOrUnknown(data['is_resolved']!, _isResolvedMeta));
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
    final effectivePrefix = tablePrefix != null ? '\$tablePrefix.' : '';
    return SyncEvent(
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
      messageAr: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}message_ar']),
      details: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}details']),
      resolution: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}resolution']),
      isRead: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['\${effectivePrefix}is_read'])!,
      isResolved: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['\${effectivePrefix}is_resolved'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}created_at'])!,
    );
  }

  @override
  \$SyncEventsTable createAlias(String alias) {
    return \$SyncEventsTable(attachedDatabase, alias);
  }
}

abstract class _\$SyncDaoTestDatabase extends GeneratedDatabase {
  _\$SyncDaoTestDatabase(QueryExecutor e) : super(e);

  late final \$SyncOutboxTable syncOutbox = \$SyncOutboxTable(this);
  late final \$SyncLogsTable syncLogs = \$SyncLogsTable(this);
  late final \$SyncEventsTable syncEvents = \$SyncEventsTable(this);

  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
    syncOutbox,
    syncLogs,
    syncEvents,
  ];
}
