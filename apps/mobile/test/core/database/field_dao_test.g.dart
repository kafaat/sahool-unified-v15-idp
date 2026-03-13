// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'field_dao_test.dart';

// ignore_for_file: type=lint

// **************************************************************************
// DriftDatabaseGenerator
// **************************************************************************

class DaoField extends DataClass implements Insertable<DaoField> {
  final String id;
  final String? remoteId;
  final String tenantId;
  final String? farmId;
  final String name;
  final String? nameAr;
  final String? cropType;
  final List<Map<String, double>> boundary;
  final Map<String, double>? centroid;
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

  const DaoField({
    required this.id,
    this.remoteId,
    required this.tenantId,
    this.farmId,
    required this.name,
    this.nameAr,
    this.cropType,
    required this.boundary,
    this.centroid,
    required this.areaHectares,
    this.status,
    this.ndviCurrent,
    this.ndviUpdatedAt,
    required this.synced,
    required this.isDeleted,
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
    if (!nullToAbsent || nameAr != null) {
      map['name_ar'] = Variable<String>(nameAr);
    }
    if (!nullToAbsent || cropType != null) {
      map['crop_type'] = Variable<String>(cropType);
    }
    map['boundary'] = Variable<String>(const GeoPolygonConverter().toSql(boundary));
    if (!nullToAbsent || centroid != null) {
      map['centroid'] = Variable<String>(const GeoPointConverter().toSql(centroid));
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

  factory DaoField.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return DaoField(
      id: serializer.fromJson<String>(json['id']),
      remoteId: serializer.fromJson<String?>(json['remote_id']),
      tenantId: serializer.fromJson<String>(json['tenant_id']),
      farmId: serializer.fromJson<String?>(json['farm_id']),
      name: serializer.fromJson<String>(json['name']),
      nameAr: serializer.fromJson<String?>(json['name_ar']),
      cropType: serializer.fromJson<String?>(json['crop_type']),
      boundary: const GeoPolygonConverter().fromSql(serializer.fromJson<String>(json['boundary'])),
      centroid: const GeoPointConverter().fromSql(serializer.fromJson<String?>(json['centroid'])),
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
      'name_ar': serializer.toJson<String?>(nameAr),
      'crop_type': serializer.toJson<String?>(cropType),
      'boundary': serializer.toJson<String>(const GeoPolygonConverter().toSql(boundary)),
      'centroid': serializer.toJson<String?>(const GeoPointConverter().toSql(centroid)),
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

  DaoField copyWith({
    String? id,
    Value<String> remoteId = const Value.absent(),
    String? tenantId,
    Value<String> farmId = const Value.absent(),
    String? name,
    Value<String> nameAr = const Value.absent(),
    Value<String> cropType = const Value.absent(),
    List<Map<String, double>>? boundary,
    Value<Map<String, double>> centroid = const Value.absent(),
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
    return DaoField(
      id: id ?? this.id,
      remoteId: remoteId.present ? remoteId.value : this.remoteId,
      tenantId: tenantId ?? this.tenantId,
      farmId: farmId.present ? farmId.value : this.farmId,
      name: name ?? this.name,
      nameAr: nameAr.present ? nameAr.value : this.nameAr,
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
  String toString() => 'DaoField(id: $id, tenantId: $tenantId, name: $name)';

  @override
  int get hashCode => Object.hash(id, tenantId, name, boundary, areaHectares);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is DaoField && other.id == id && other.tenantId == tenantId);
}

class DaoFieldsCompanion extends UpdateCompanion<DaoField> {
  final Value<String> id;
  final Value<String?> remoteId;
  final Value<String> tenantId;
  final Value<String?> farmId;
  final Value<String> name;
  final Value<String?> nameAr;
  final Value<String?> cropType;
  final Value<List<Map<String, double>>> boundary;
  final Value<Map<String, double>?> centroid;
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

  const DaoFieldsCompanion({
    this.id = const Value.absent(),
    this.remoteId = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.farmId = const Value.absent(),
    this.name = const Value.absent(),
    this.nameAr = const Value.absent(),
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

  DaoFieldsCompanion.insert({
    required String id,
    this.remoteId = const Value.absent(),
    required String tenantId,
    this.farmId = const Value.absent(),
    required String name,
    this.nameAr = const Value.absent(),
    this.cropType = const Value.absent(),
    required List<Map<String, double>> boundary,
    this.centroid = const Value.absent(),
    required double areaHectares,
    this.status = const Value.absent(),
    this.ndviCurrent = const Value.absent(),
    this.ndviUpdatedAt = const Value.absent(),
    this.synced = const Value.absent(),
    this.isDeleted = const Value.absent(),
    required DateTime createdAt,
    required DateTime updatedAt,
    this.etag = const Value.absent(),
    this.serverUpdatedAt = const Value.absent(),
  })  : id = Value(id),
        tenantId = Value(tenantId),
        name = Value(name),
        boundary = Value(boundary),
        areaHectares = Value(areaHectares),
        createdAt = Value(createdAt),
        updatedAt = Value(updatedAt);

  static Insertable<DaoField> custom({
    Expression<dynamic>? id,
    Expression<dynamic>? tenantId,
    Expression<dynamic>? name,
    Expression<dynamic>? boundary,
    Expression<dynamic>? areaHectares,
    Expression<dynamic>? createdAt,
    Expression<dynamic>? updatedAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (tenantId != null) 'tenant_id': tenantId,
      if (name != null) 'name': name,
      if (boundary != null) 'boundary': boundary,
      if (areaHectares != null) 'area_hectares': areaHectares,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
    });
  }

  DaoFieldsCompanion copyWith({
    Value<String>? id,
    Value<String?>? remoteId,
    Value<String>? tenantId,
    Value<String?>? farmId,
    Value<String>? name,
    Value<String?>? nameAr,
    Value<String?>? cropType,
    Value<List<Map<String, double>>>? boundary,
    Value<Map<String, double>?>? centroid,
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
    return DaoFieldsCompanion(
      id: id ?? this.id,
      remoteId: remoteId ?? this.remoteId,
      tenantId: tenantId ?? this.tenantId,
      farmId: farmId ?? this.farmId,
      name: name ?? this.name,
      nameAr: nameAr ?? this.nameAr,
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
    if (id.present) { map['id'] = Variable<String>(id.value); }
    if (remoteId.present) { map['remote_id'] = Variable<String?>(remoteId.value); }
    if (tenantId.present) { map['tenant_id'] = Variable<String>(tenantId.value); }
    if (farmId.present) { map['farm_id'] = Variable<String?>(farmId.value); }
    if (name.present) { map['name'] = Variable<String>(name.value); }
    if (nameAr.present) { map['name_ar'] = Variable<String?>(nameAr.value); }
    if (cropType.present) { map['crop_type'] = Variable<String?>(cropType.value); }
    if (boundary.present) { map['boundary'] = Variable<String>(const GeoPolygonConverter().toSql(boundary.value)); }
    if (centroid.present) { map['centroid'] = Variable<String?>(const GeoPointConverter().toSql(centroid.value)); }
    if (areaHectares.present) { map['area_hectares'] = Variable<double>(areaHectares.value); }
    if (status.present) { map['status'] = Variable<String?>(status.value); }
    if (ndviCurrent.present) { map['ndvi_current'] = Variable<double?>(ndviCurrent.value); }
    if (ndviUpdatedAt.present) { map['ndvi_updated_at'] = Variable<DateTime?>(ndviUpdatedAt.value); }
    if (synced.present) { map['synced'] = Variable<bool>(synced.value); }
    if (isDeleted.present) { map['is_deleted'] = Variable<bool>(isDeleted.value); }
    if (createdAt.present) { map['created_at'] = Variable<DateTime>(createdAt.value); }
    if (updatedAt.present) { map['updated_at'] = Variable<DateTime>(updatedAt.value); }
    if (etag.present) { map['etag'] = Variable<String?>(etag.value); }
    if (serverUpdatedAt.present) { map['server_updated_at'] = Variable<DateTime?>(serverUpdatedAt.value); }
    return map;
  }

  @override
  String toString() => 'DaoFieldsCompanion(id: $id, tenantId: $tenantId)';
}

class $DaoFieldsTable extends DaoFields
    with TableInfo<$DaoFieldsTable, DaoField> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $DaoFieldsTable(this.attachedDatabase, [this._alias]);

  static const VerificationMeta _idMeta = VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>('id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _remoteIdMeta = VerificationMeta('remoteId');
  @override
  late final GeneratedColumn<String> remoteId = GeneratedColumn<String>('remote_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _tenantIdMeta = VerificationMeta('tenantId');
  @override
  late final GeneratedColumn<String> tenantId = GeneratedColumn<String>('tenant_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _farmIdMeta = VerificationMeta('farmId');
  @override
  late final GeneratedColumn<String> farmId = GeneratedColumn<String>('farm_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _nameMeta = VerificationMeta('name');
  @override
  late final GeneratedColumn<String> name = GeneratedColumn<String>('name', aliasedName, false,
      additionalChecks: GeneratedColumn.checkTextLength(minTextLength: 1, maxTextLength: 100),
      type: DriftSqlType.string, requiredDuringInsert: true);

  static const VerificationMeta _nameArMeta = VerificationMeta('nameAr');
  @override
  late final GeneratedColumn<String> nameAr = GeneratedColumn<String>('name_ar', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _cropTypeMeta = VerificationMeta('cropType');
  @override
  late final GeneratedColumn<String> cropType = GeneratedColumn<String>('crop_type', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _boundaryMeta = VerificationMeta('boundary');
  @override
  late final GeneratedColumnWithTypeConverter<List<Map<String, double>>, String> boundary =
      GeneratedColumnWithTypeConverter<List<Map<String, double>>, String>(
          'boundary', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true,
          converter: const GeoPolygonConverter());

  static const VerificationMeta _centroidMeta = VerificationMeta('centroid');
  @override
  late final GeneratedColumnWithTypeConverter<Map<String, double>?, String?> centroid =
      GeneratedColumnWithTypeConverter<Map<String, double>?, String?>(
          'centroid', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false,
          converter: const GeoPointConverter());

  static const VerificationMeta _areaHectaresMeta = VerificationMeta('areaHectares');
  @override
  late final GeneratedColumn<double> areaHectares = GeneratedColumn<double>('area_hectares', aliasedName, false,
      type: DriftSqlType.double, requiredDuringInsert: true);

  static const VerificationMeta _statusMeta = VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status = GeneratedColumn<String>('status', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _ndviCurrentMeta = VerificationMeta('ndviCurrent');
  @override
  late final GeneratedColumn<double> ndviCurrent = GeneratedColumn<double>('ndvi_current', aliasedName, true,
      type: DriftSqlType.double, requiredDuringInsert: false);

  static const VerificationMeta _ndviUpdatedAtMeta = VerificationMeta('ndviUpdatedAt');
  @override
  late final GeneratedColumn<DateTime> ndviUpdatedAt = GeneratedColumn<DateTime>('ndvi_updated_at', aliasedName, true,
      type: DriftSqlType.dateTime, requiredDuringInsert: false);

  static const VerificationMeta _syncedMeta = VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>('synced', aliasedName, false,
      defaultValue: const Constant(false), type: DriftSqlType.bool, requiredDuringInsert: false);

  static const VerificationMeta _isDeletedMeta = VerificationMeta('isDeleted');
  @override
  late final GeneratedColumn<bool> isDeleted = GeneratedColumn<bool>('is_deleted', aliasedName, false,
      defaultValue: const Constant(false), type: DriftSqlType.bool, requiredDuringInsert: false);

  static const VerificationMeta _createdAtMeta = VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>('created_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);

  static const VerificationMeta _updatedAtMeta = VerificationMeta('updatedAt');
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>('updated_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);

  static const VerificationMeta _etagMeta = VerificationMeta('etag');
  @override
  late final GeneratedColumn<String> etag = GeneratedColumn<String>('etag', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);

  static const VerificationMeta _serverUpdatedAtMeta = VerificationMeta('serverUpdatedAt');
  @override
  late final GeneratedColumn<DateTime> serverUpdatedAt = GeneratedColumn<DateTime>('server_updated_at', aliasedName, true,
      type: DriftSqlType.dateTime, requiredDuringInsert: false);

  @override
  List<GeneratedColumn> get $columns => [
    id, remoteId, tenantId, farmId, name, nameAr, cropType, boundary, centroid,
    areaHectares, status, ndviCurrent, ndviUpdatedAt, synced, isDeleted,
    createdAt, updatedAt, etag, serverUpdatedAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'dao_fields';

  @override
  VerificationContext validateIntegrity(Insertable<DaoField> instance,
      {bool isInserting = false}) {
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
  DaoField map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '\$tablePrefix.' : '';
    return DaoField(
      id: attachedDatabase.typeMapping.read(DriftSqlType.string, data['\${effectivePrefix}id'])!,
      remoteId: attachedDatabase.typeMapping.read(DriftSqlType.string, data['\${effectivePrefix}remote_id']),
      tenantId: attachedDatabase.typeMapping.read(DriftSqlType.string, data['\${effectivePrefix}tenant_id'])!,
      farmId: attachedDatabase.typeMapping.read(DriftSqlType.string, data['\${effectivePrefix}farm_id']),
      name: attachedDatabase.typeMapping.read(DriftSqlType.string, data['\${effectivePrefix}name'])!,
      nameAr: attachedDatabase.typeMapping.read(DriftSqlType.string, data['\${effectivePrefix}name_ar']),
      cropType: attachedDatabase.typeMapping.read(DriftSqlType.string, data['\${effectivePrefix}crop_type']),
      boundary: const GeoPolygonConverter().fromSql(
          attachedDatabase.typeMapping.read(DriftSqlType.string, data['\${effectivePrefix}boundary'])!),
      centroid: const GeoPointConverter().fromSql(
          attachedDatabase.typeMapping.read(DriftSqlType.string, data['\${effectivePrefix}centroid'])),
      areaHectares: attachedDatabase.typeMapping.read(DriftSqlType.double, data['\${effectivePrefix}area_hectares'])!,
      status: attachedDatabase.typeMapping.read(DriftSqlType.string, data['\${effectivePrefix}status']),
      ndviCurrent: attachedDatabase.typeMapping.read(DriftSqlType.double, data['\${effectivePrefix}ndvi_current']),
      ndviUpdatedAt: attachedDatabase.typeMapping.read(DriftSqlType.dateTime, data['\${effectivePrefix}ndvi_updated_at']),
      synced: attachedDatabase.typeMapping.read(DriftSqlType.bool, data['\${effectivePrefix}synced'])!,
      isDeleted: attachedDatabase.typeMapping.read(DriftSqlType.bool, data['\${effectivePrefix}is_deleted'])!,
      createdAt: attachedDatabase.typeMapping.read(DriftSqlType.dateTime, data['\${effectivePrefix}created_at'])!,
      updatedAt: attachedDatabase.typeMapping.read(DriftSqlType.dateTime, data['\${effectivePrefix}updated_at'])!,
      etag: attachedDatabase.typeMapping.read(DriftSqlType.string, data['\${effectivePrefix}etag']),
      serverUpdatedAt: attachedDatabase.typeMapping.read(DriftSqlType.dateTime, data['\${effectivePrefix}server_updated_at']),
    );
  }

  @override
  $DaoFieldsTable createAlias(String alias) {
    return $DaoFieldsTable(attachedDatabase, alias);
  }
}

abstract class _$FieldDaoTestDatabase extends GeneratedDatabase {
  _$FieldDaoTestDatabase(QueryExecutor e) : super(e);

  late final $DaoFieldsTable daoFields = $DaoFieldsTable(this);

  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [daoFields];
}
