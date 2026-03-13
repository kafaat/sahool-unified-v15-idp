// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'field_dao_test.dart';

// ignore_for_file: type=lint
class $DaoFieldsTable extends DaoFields
    with TableInfo<$DaoFieldsTable, DaoField> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $DaoFieldsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _remoteIdMeta =
      const VerificationMeta('remoteId');
  @override
  late final GeneratedColumn<String> remoteId = GeneratedColumn<String>(
      'remote_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _tenantIdMeta =
      const VerificationMeta('tenantId');
  @override
  late final GeneratedColumn<String> tenantId = GeneratedColumn<String>(
      'tenant_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _farmIdMeta = const VerificationMeta('farmId');
  @override
  late final GeneratedColumn<String> farmId = GeneratedColumn<String>(
      'farm_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _nameMeta = const VerificationMeta('name');
  @override
  late final GeneratedColumn<String> name = GeneratedColumn<String>(
      'name', aliasedName, false,
      additionalChecks:
          GeneratedColumn.checkTextLength(minTextLength: 1, maxTextLength: 100),
      type: DriftSqlType.string,
      requiredDuringInsert: true);
  static const VerificationMeta _nameArMeta = const VerificationMeta('nameAr');
  @override
  late final GeneratedColumn<String> nameAr = GeneratedColumn<String>(
      'name_ar', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _cropTypeMeta =
      const VerificationMeta('cropType');
  @override
  late final GeneratedColumn<String> cropType = GeneratedColumn<String>(
      'crop_type', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  @override
  late final GeneratedColumnWithTypeConverter<List<Map<String, double>>, String>
      boundary = GeneratedColumn<String>('boundary', aliasedName, false,
              type: DriftSqlType.string, requiredDuringInsert: true)
          .withConverter<List<Map<String, double>>>(
              $DaoFieldsTable.$converterboundary);
  @override
  late final GeneratedColumnWithTypeConverter<Map<String, double>?, String>
      centroid = GeneratedColumn<String>('centroid', aliasedName, true,
              type: DriftSqlType.string, requiredDuringInsert: false)
          .withConverter<Map<String, double>?>(
              $DaoFieldsTable.$convertercentroid);
  static const VerificationMeta _areaHectaresMeta =
      const VerificationMeta('areaHectares');
  @override
  late final GeneratedColumn<double> areaHectares = GeneratedColumn<double>(
      'area_hectares', aliasedName, false,
      type: DriftSqlType.double, requiredDuringInsert: true);
  static const VerificationMeta _statusMeta = const VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status = GeneratedColumn<String>(
      'status', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _ndviCurrentMeta =
      const VerificationMeta('ndviCurrent');
  @override
  late final GeneratedColumn<double> ndviCurrent = GeneratedColumn<double>(
      'ndvi_current', aliasedName, true,
      type: DriftSqlType.double, requiredDuringInsert: false);
  static const VerificationMeta _ndviUpdatedAtMeta =
      const VerificationMeta('ndviUpdatedAt');
  @override
  late final GeneratedColumn<DateTime> ndviUpdatedAt =
      GeneratedColumn<DateTime>('ndvi_updated_at', aliasedName, true,
          type: DriftSqlType.dateTime, requiredDuringInsert: false);
  static const VerificationMeta _syncedMeta = const VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>(
      'synced', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("synced" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _isDeletedMeta =
      const VerificationMeta('isDeleted');
  @override
  late final GeneratedColumn<bool> isDeleted = GeneratedColumn<bool>(
      'is_deleted', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("is_deleted" IN (0, 1))'),
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
  static const VerificationMeta _etagMeta = const VerificationMeta('etag');
  @override
  late final GeneratedColumn<String> etag = GeneratedColumn<String>(
      'etag', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _serverUpdatedAtMeta =
      const VerificationMeta('serverUpdatedAt');
  @override
  late final GeneratedColumn<DateTime> serverUpdatedAt =
      GeneratedColumn<DateTime>('server_updated_at', aliasedName, true,
          type: DriftSqlType.dateTime, requiredDuringInsert: false);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        remoteId,
        tenantId,
        farmId,
        name,
        nameAr,
        cropType,
        boundary,
        centroid,
        areaHectares,
        status,
        ndviCurrent,
        ndviUpdatedAt,
        synced,
        isDeleted,
        createdAt,
        updatedAt,
        etag,
        serverUpdatedAt
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
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('remote_id')) {
      context.handle(_remoteIdMeta,
          remoteId.isAcceptableOrUnknown(data['remote_id']!, _remoteIdMeta));
    }
    if (data.containsKey('tenant_id')) {
      context.handle(_tenantIdMeta,
          tenantId.isAcceptableOrUnknown(data['tenant_id']!, _tenantIdMeta));
    } else if (isInserting) {
      context.missing(_tenantIdMeta);
    }
    if (data.containsKey('farm_id')) {
      context.handle(_farmIdMeta,
          farmId.isAcceptableOrUnknown(data['farm_id']!, _farmIdMeta));
    }
    if (data.containsKey('name')) {
      context.handle(
          _nameMeta, name.isAcceptableOrUnknown(data['name']!, _nameMeta));
    } else if (isInserting) {
      context.missing(_nameMeta);
    }
    if (data.containsKey('name_ar')) {
      context.handle(_nameArMeta,
          nameAr.isAcceptableOrUnknown(data['name_ar']!, _nameArMeta));
    }
    if (data.containsKey('crop_type')) {
      context.handle(_cropTypeMeta,
          cropType.isAcceptableOrUnknown(data['crop_type']!, _cropTypeMeta));
    }
    if (data.containsKey('area_hectares')) {
      context.handle(
          _areaHectaresMeta,
          areaHectares.isAcceptableOrUnknown(
              data['area_hectares']!, _areaHectaresMeta));
    } else if (isInserting) {
      context.missing(_areaHectaresMeta);
    }
    if (data.containsKey('status')) {
      context.handle(_statusMeta,
          status.isAcceptableOrUnknown(data['status']!, _statusMeta));
    }
    if (data.containsKey('ndvi_current')) {
      context.handle(
          _ndviCurrentMeta,
          ndviCurrent.isAcceptableOrUnknown(
              data['ndvi_current']!, _ndviCurrentMeta));
    }
    if (data.containsKey('ndvi_updated_at')) {
      context.handle(
          _ndviUpdatedAtMeta,
          ndviUpdatedAt.isAcceptableOrUnknown(
              data['ndvi_updated_at']!, _ndviUpdatedAtMeta));
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
    } else if (isInserting) {
      context.missing(_createdAtMeta);
    }
    if (data.containsKey('updated_at')) {
      context.handle(_updatedAtMeta,
          updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta));
    } else if (isInserting) {
      context.missing(_updatedAtMeta);
    }
    if (data.containsKey('etag')) {
      context.handle(
          _etagMeta, etag.isAcceptableOrUnknown(data['etag']!, _etagMeta));
    }
    if (data.containsKey('server_updated_at')) {
      context.handle(
          _serverUpdatedAtMeta,
          serverUpdatedAt.isAcceptableOrUnknown(
              data['server_updated_at']!, _serverUpdatedAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  DaoField map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return DaoField(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      remoteId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}remote_id']),
      tenantId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}tenant_id'])!,
      farmId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}farm_id']),
      name: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}name'])!,
      nameAr: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}name_ar']),
      cropType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}crop_type']),
      boundary: $DaoFieldsTable.$converterboundary.fromSql(attachedDatabase
          .typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boundary'])!),
      centroid: $DaoFieldsTable.$convertercentroid.fromSql(attachedDatabase
          .typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}centroid'])),
      areaHectares: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}area_hectares'])!,
      status: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}status']),
      ndviCurrent: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}ndvi_current']),
      ndviUpdatedAt: attachedDatabase.typeMapping.read(
          DriftSqlType.dateTime, data['${effectivePrefix}ndvi_updated_at']),
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
      isDeleted: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}is_deleted'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}updated_at'])!,
      etag: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}etag']),
      serverUpdatedAt: attachedDatabase.typeMapping.read(
          DriftSqlType.dateTime, data['${effectivePrefix}server_updated_at']),
    );
  }

  @override
  $DaoFieldsTable createAlias(String alias) {
    return $DaoFieldsTable(attachedDatabase, alias);
  }

  static TypeConverter<List<Map<String, double>>, String> $converterboundary =
      const GeoPolygonConverter();
  static TypeConverter<Map<String, double>?, String?> $convertercentroid =
      const GeoPointConverter();
}

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
  const DaoField(
      {required this.id,
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
      this.serverUpdatedAt});
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
    {
      map['boundary'] =
          Variable<String>($DaoFieldsTable.$converterboundary.toSql(boundary));
    }
    if (!nullToAbsent || centroid != null) {
      map['centroid'] =
          Variable<String>($DaoFieldsTable.$convertercentroid.toSql(centroid));
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

  DaoFieldsCompanion toCompanion(bool nullToAbsent) {
    return DaoFieldsCompanion(
      id: Value(id),
      remoteId: remoteId == null && nullToAbsent
          ? const Value.absent()
          : Value(remoteId),
      tenantId: Value(tenantId),
      farmId:
          farmId == null && nullToAbsent ? const Value.absent() : Value(farmId),
      name: Value(name),
      nameAr:
          nameAr == null && nullToAbsent ? const Value.absent() : Value(nameAr),
      cropType: cropType == null && nullToAbsent
          ? const Value.absent()
          : Value(cropType),
      boundary: Value(boundary),
      centroid: centroid == null && nullToAbsent
          ? const Value.absent()
          : Value(centroid),
      areaHectares: Value(areaHectares),
      status:
          status == null && nullToAbsent ? const Value.absent() : Value(status),
      ndviCurrent: ndviCurrent == null && nullToAbsent
          ? const Value.absent()
          : Value(ndviCurrent),
      ndviUpdatedAt: ndviUpdatedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(ndviUpdatedAt),
      synced: Value(synced),
      isDeleted: Value(isDeleted),
      createdAt: Value(createdAt),
      updatedAt: Value(updatedAt),
      etag: etag == null && nullToAbsent ? const Value.absent() : Value(etag),
      serverUpdatedAt: serverUpdatedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(serverUpdatedAt),
    );
  }

  factory DaoField.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return DaoField(
      id: serializer.fromJson<String>(json['id']),
      remoteId: serializer.fromJson<String?>(json['remoteId']),
      tenantId: serializer.fromJson<String>(json['tenantId']),
      farmId: serializer.fromJson<String?>(json['farmId']),
      name: serializer.fromJson<String>(json['name']),
      nameAr: serializer.fromJson<String?>(json['nameAr']),
      cropType: serializer.fromJson<String?>(json['cropType']),
      boundary:
          serializer.fromJson<List<Map<String, double>>>(json['boundary']),
      centroid: serializer.fromJson<Map<String, double>?>(json['centroid']),
      areaHectares: serializer.fromJson<double>(json['areaHectares']),
      status: serializer.fromJson<String?>(json['status']),
      ndviCurrent: serializer.fromJson<double?>(json['ndviCurrent']),
      ndviUpdatedAt: serializer.fromJson<DateTime?>(json['ndviUpdatedAt']),
      synced: serializer.fromJson<bool>(json['synced']),
      isDeleted: serializer.fromJson<bool>(json['isDeleted']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
      etag: serializer.fromJson<String?>(json['etag']),
      serverUpdatedAt: serializer.fromJson<DateTime?>(json['serverUpdatedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'remoteId': serializer.toJson<String?>(remoteId),
      'tenantId': serializer.toJson<String>(tenantId),
      'farmId': serializer.toJson<String?>(farmId),
      'name': serializer.toJson<String>(name),
      'nameAr': serializer.toJson<String?>(nameAr),
      'cropType': serializer.toJson<String?>(cropType),
      'boundary': serializer.toJson<List<Map<String, double>>>(boundary),
      'centroid': serializer.toJson<Map<String, double>?>(centroid),
      'areaHectares': serializer.toJson<double>(areaHectares),
      'status': serializer.toJson<String?>(status),
      'ndviCurrent': serializer.toJson<double?>(ndviCurrent),
      'ndviUpdatedAt': serializer.toJson<DateTime?>(ndviUpdatedAt),
      'synced': serializer.toJson<bool>(synced),
      'isDeleted': serializer.toJson<bool>(isDeleted),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
      'etag': serializer.toJson<String?>(etag),
      'serverUpdatedAt': serializer.toJson<DateTime?>(serverUpdatedAt),
    };
  }

  DaoField copyWith(
          {String? id,
          Value<String?> remoteId = const Value.absent(),
          String? tenantId,
          Value<String?> farmId = const Value.absent(),
          String? name,
          Value<String?> nameAr = const Value.absent(),
          Value<String?> cropType = const Value.absent(),
          List<Map<String, double>>? boundary,
          Value<Map<String, double>?> centroid = const Value.absent(),
          double? areaHectares,
          Value<String?> status = const Value.absent(),
          Value<double?> ndviCurrent = const Value.absent(),
          Value<DateTime?> ndviUpdatedAt = const Value.absent(),
          bool? synced,
          bool? isDeleted,
          DateTime? createdAt,
          DateTime? updatedAt,
          Value<String?> etag = const Value.absent(),
          Value<DateTime?> serverUpdatedAt = const Value.absent()}) =>
      DaoField(
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
        ndviUpdatedAt:
            ndviUpdatedAt.present ? ndviUpdatedAt.value : this.ndviUpdatedAt,
        synced: synced ?? this.synced,
        isDeleted: isDeleted ?? this.isDeleted,
        createdAt: createdAt ?? this.createdAt,
        updatedAt: updatedAt ?? this.updatedAt,
        etag: etag.present ? etag.value : this.etag,
        serverUpdatedAt: serverUpdatedAt.present
            ? serverUpdatedAt.value
            : this.serverUpdatedAt,
      );
  DaoField copyWithCompanion(DaoFieldsCompanion data) {
    return DaoField(
      id: data.id.present ? data.id.value : this.id,
      remoteId: data.remoteId.present ? data.remoteId.value : this.remoteId,
      tenantId: data.tenantId.present ? data.tenantId.value : this.tenantId,
      farmId: data.farmId.present ? data.farmId.value : this.farmId,
      name: data.name.present ? data.name.value : this.name,
      nameAr: data.nameAr.present ? data.nameAr.value : this.nameAr,
      cropType: data.cropType.present ? data.cropType.value : this.cropType,
      boundary: data.boundary.present ? data.boundary.value : this.boundary,
      centroid: data.centroid.present ? data.centroid.value : this.centroid,
      areaHectares: data.areaHectares.present
          ? data.areaHectares.value
          : this.areaHectares,
      status: data.status.present ? data.status.value : this.status,
      ndviCurrent:
          data.ndviCurrent.present ? data.ndviCurrent.value : this.ndviCurrent,
      ndviUpdatedAt: data.ndviUpdatedAt.present
          ? data.ndviUpdatedAt.value
          : this.ndviUpdatedAt,
      synced: data.synced.present ? data.synced.value : this.synced,
      isDeleted: data.isDeleted.present ? data.isDeleted.value : this.isDeleted,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
      etag: data.etag.present ? data.etag.value : this.etag,
      serverUpdatedAt: data.serverUpdatedAt.present
          ? data.serverUpdatedAt.value
          : this.serverUpdatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('DaoField(')
          ..write('id: $id, ')
          ..write('remoteId: $remoteId, ')
          ..write('tenantId: $tenantId, ')
          ..write('farmId: $farmId, ')
          ..write('name: $name, ')
          ..write('nameAr: $nameAr, ')
          ..write('cropType: $cropType, ')
          ..write('boundary: $boundary, ')
          ..write('centroid: $centroid, ')
          ..write('areaHectares: $areaHectares, ')
          ..write('status: $status, ')
          ..write('ndviCurrent: $ndviCurrent, ')
          ..write('ndviUpdatedAt: $ndviUpdatedAt, ')
          ..write('synced: $synced, ')
          ..write('isDeleted: $isDeleted, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('etag: $etag, ')
          ..write('serverUpdatedAt: $serverUpdatedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id,
      remoteId,
      tenantId,
      farmId,
      name,
      nameAr,
      cropType,
      boundary,
      centroid,
      areaHectares,
      status,
      ndviCurrent,
      ndviUpdatedAt,
      synced,
      isDeleted,
      createdAt,
      updatedAt,
      etag,
      serverUpdatedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is DaoField &&
          other.id == this.id &&
          other.remoteId == this.remoteId &&
          other.tenantId == this.tenantId &&
          other.farmId == this.farmId &&
          other.name == this.name &&
          other.nameAr == this.nameAr &&
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
          other.serverUpdatedAt == this.serverUpdatedAt);
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
  final Value<int> rowid;
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
    this.rowid = const Value.absent(),
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
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        tenantId = Value(tenantId),
        name = Value(name),
        boundary = Value(boundary),
        areaHectares = Value(areaHectares),
        createdAt = Value(createdAt),
        updatedAt = Value(updatedAt);
  static Insertable<DaoField> custom({
    Expression<String>? id,
    Expression<String>? remoteId,
    Expression<String>? tenantId,
    Expression<String>? farmId,
    Expression<String>? name,
    Expression<String>? nameAr,
    Expression<String>? cropType,
    Expression<String>? boundary,
    Expression<String>? centroid,
    Expression<double>? areaHectares,
    Expression<String>? status,
    Expression<double>? ndviCurrent,
    Expression<DateTime>? ndviUpdatedAt,
    Expression<bool>? synced,
    Expression<bool>? isDeleted,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<String>? etag,
    Expression<DateTime>? serverUpdatedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (remoteId != null) 'remote_id': remoteId,
      if (tenantId != null) 'tenant_id': tenantId,
      if (farmId != null) 'farm_id': farmId,
      if (name != null) 'name': name,
      if (nameAr != null) 'name_ar': nameAr,
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
      if (rowid != null) 'rowid': rowid,
    });
  }

  DaoFieldsCompanion copyWith(
      {Value<String>? id,
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
      Value<int>? rowid}) {
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
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (remoteId.present) {
      map['remote_id'] = Variable<String>(remoteId.value);
    }
    if (tenantId.present) {
      map['tenant_id'] = Variable<String>(tenantId.value);
    }
    if (farmId.present) {
      map['farm_id'] = Variable<String>(farmId.value);
    }
    if (name.present) {
      map['name'] = Variable<String>(name.value);
    }
    if (nameAr.present) {
      map['name_ar'] = Variable<String>(nameAr.value);
    }
    if (cropType.present) {
      map['crop_type'] = Variable<String>(cropType.value);
    }
    if (boundary.present) {
      map['boundary'] = Variable<String>(
          $DaoFieldsTable.$converterboundary.toSql(boundary.value));
    }
    if (centroid.present) {
      map['centroid'] = Variable<String>(
          $DaoFieldsTable.$convertercentroid.toSql(centroid.value));
    }
    if (areaHectares.present) {
      map['area_hectares'] = Variable<double>(areaHectares.value);
    }
    if (status.present) {
      map['status'] = Variable<String>(status.value);
    }
    if (ndviCurrent.present) {
      map['ndvi_current'] = Variable<double>(ndviCurrent.value);
    }
    if (ndviUpdatedAt.present) {
      map['ndvi_updated_at'] = Variable<DateTime>(ndviUpdatedAt.value);
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
      map['etag'] = Variable<String>(etag.value);
    }
    if (serverUpdatedAt.present) {
      map['server_updated_at'] = Variable<DateTime>(serverUpdatedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('DaoFieldsCompanion(')
          ..write('id: $id, ')
          ..write('remoteId: $remoteId, ')
          ..write('tenantId: $tenantId, ')
          ..write('farmId: $farmId, ')
          ..write('name: $name, ')
          ..write('nameAr: $nameAr, ')
          ..write('cropType: $cropType, ')
          ..write('boundary: $boundary, ')
          ..write('centroid: $centroid, ')
          ..write('areaHectares: $areaHectares, ')
          ..write('status: $status, ')
          ..write('ndviCurrent: $ndviCurrent, ')
          ..write('ndviUpdatedAt: $ndviUpdatedAt, ')
          ..write('synced: $synced, ')
          ..write('isDeleted: $isDeleted, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('etag: $etag, ')
          ..write('serverUpdatedAt: $serverUpdatedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

abstract class _$FieldDaoTestDatabase extends GeneratedDatabase {
  _$FieldDaoTestDatabase(QueryExecutor e) : super(e);
  $FieldDaoTestDatabaseManager get managers =>
      $FieldDaoTestDatabaseManager(this);
  late final $DaoFieldsTable daoFields = $DaoFieldsTable(this);
  late final Index daoFieldsTenantIdx = Index('dao_fields_tenant_idx',
      'CREATE INDEX dao_fields_tenant_idx ON dao_fields (tenant_id)');
  late final Index daoFieldsFarmIdx = Index('dao_fields_farm_idx',
      'CREATE INDEX dao_fields_farm_idx ON dao_fields (farm_id)');
  late final Index daoFieldsSyncedIdx = Index('dao_fields_synced_idx',
      'CREATE INDEX dao_fields_synced_idx ON dao_fields (synced)');
  late final Index daoFieldsDeletedIdx = Index('dao_fields_deleted_idx',
      'CREATE INDEX dao_fields_deleted_idx ON dao_fields (is_deleted)');
  late final Index daoFieldsTenantDeletedIdx = Index(
      'dao_fields_tenant_deleted_idx',
      'CREATE INDEX dao_fields_tenant_deleted_idx ON dao_fields (tenant_id, is_deleted)');
  late final Index daoFieldsUpdatedIdx = Index('dao_fields_updated_idx',
      'CREATE INDEX dao_fields_updated_idx ON dao_fields (updated_at)');
  late final Index daoFieldsRemoteIdx = Index('dao_fields_remote_idx',
      'CREATE INDEX dao_fields_remote_idx ON dao_fields (remote_id)');
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
        daoFields,
        daoFieldsTenantIdx,
        daoFieldsFarmIdx,
        daoFieldsSyncedIdx,
        daoFieldsDeletedIdx,
        daoFieldsTenantDeletedIdx,
        daoFieldsUpdatedIdx,
        daoFieldsRemoteIdx
      ];
  @override
  DriftDatabaseOptions get options =>
      const DriftDatabaseOptions(storeDateTimeAsText: true);
}

typedef $$DaoFieldsTableCreateCompanionBuilder = DaoFieldsCompanion Function({
  required String id,
  Value<String?> remoteId,
  required String tenantId,
  Value<String?> farmId,
  required String name,
  Value<String?> nameAr,
  Value<String?> cropType,
  required List<Map<String, double>> boundary,
  Value<Map<String, double>?> centroid,
  required double areaHectares,
  Value<String?> status,
  Value<double?> ndviCurrent,
  Value<DateTime?> ndviUpdatedAt,
  Value<bool> synced,
  Value<bool> isDeleted,
  required DateTime createdAt,
  required DateTime updatedAt,
  Value<String?> etag,
  Value<DateTime?> serverUpdatedAt,
  Value<int> rowid,
});
typedef $$DaoFieldsTableUpdateCompanionBuilder = DaoFieldsCompanion Function({
  Value<String> id,
  Value<String?> remoteId,
  Value<String> tenantId,
  Value<String?> farmId,
  Value<String> name,
  Value<String?> nameAr,
  Value<String?> cropType,
  Value<List<Map<String, double>>> boundary,
  Value<Map<String, double>?> centroid,
  Value<double> areaHectares,
  Value<String?> status,
  Value<double?> ndviCurrent,
  Value<DateTime?> ndviUpdatedAt,
  Value<bool> synced,
  Value<bool> isDeleted,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<String?> etag,
  Value<DateTime?> serverUpdatedAt,
  Value<int> rowid,
});

class $$DaoFieldsTableFilterComposer
    extends Composer<_$FieldDaoTestDatabase, $DaoFieldsTable> {
  $$DaoFieldsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get remoteId => $composableBuilder(
      column: $table.remoteId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get tenantId => $composableBuilder(
      column: $table.tenantId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get farmId => $composableBuilder(
      column: $table.farmId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get name => $composableBuilder(
      column: $table.name, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get nameAr => $composableBuilder(
      column: $table.nameAr, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get cropType => $composableBuilder(
      column: $table.cropType, builder: (column) => ColumnFilters(column));

  ColumnWithTypeConverterFilters<List<Map<String, double>>,
          List<Map<String, double>>, String>
      get boundary => $composableBuilder(
          column: $table.boundary,
          builder: (column) => ColumnWithTypeConverterFilters(column));

  ColumnWithTypeConverterFilters<Map<String, double>?, Map<String, double>,
          String>
      get centroid => $composableBuilder(
          column: $table.centroid,
          builder: (column) => ColumnWithTypeConverterFilters(column));

  ColumnFilters<double> get areaHectares => $composableBuilder(
      column: $table.areaHectares, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get status => $composableBuilder(
      column: $table.status, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get ndviCurrent => $composableBuilder(
      column: $table.ndviCurrent, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get ndviUpdatedAt => $composableBuilder(
      column: $table.ndviUpdatedAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get isDeleted => $composableBuilder(
      column: $table.isDeleted, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get etag => $composableBuilder(
      column: $table.etag, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get serverUpdatedAt => $composableBuilder(
      column: $table.serverUpdatedAt,
      builder: (column) => ColumnFilters(column));
}

class $$DaoFieldsTableOrderingComposer
    extends Composer<_$FieldDaoTestDatabase, $DaoFieldsTable> {
  $$DaoFieldsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get remoteId => $composableBuilder(
      column: $table.remoteId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get tenantId => $composableBuilder(
      column: $table.tenantId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get farmId => $composableBuilder(
      column: $table.farmId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get name => $composableBuilder(
      column: $table.name, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get nameAr => $composableBuilder(
      column: $table.nameAr, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get cropType => $composableBuilder(
      column: $table.cropType, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get boundary => $composableBuilder(
      column: $table.boundary, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get centroid => $composableBuilder(
      column: $table.centroid, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get areaHectares => $composableBuilder(
      column: $table.areaHectares,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get status => $composableBuilder(
      column: $table.status, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get ndviCurrent => $composableBuilder(
      column: $table.ndviCurrent, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get ndviUpdatedAt => $composableBuilder(
      column: $table.ndviUpdatedAt,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get isDeleted => $composableBuilder(
      column: $table.isDeleted, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get etag => $composableBuilder(
      column: $table.etag, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get serverUpdatedAt => $composableBuilder(
      column: $table.serverUpdatedAt,
      builder: (column) => ColumnOrderings(column));
}

class $$DaoFieldsTableAnnotationComposer
    extends Composer<_$FieldDaoTestDatabase, $DaoFieldsTable> {
  $$DaoFieldsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get remoteId =>
      $composableBuilder(column: $table.remoteId, builder: (column) => column);

  GeneratedColumn<String> get tenantId =>
      $composableBuilder(column: $table.tenantId, builder: (column) => column);

  GeneratedColumn<String> get farmId =>
      $composableBuilder(column: $table.farmId, builder: (column) => column);

  GeneratedColumn<String> get name =>
      $composableBuilder(column: $table.name, builder: (column) => column);

  GeneratedColumn<String> get nameAr =>
      $composableBuilder(column: $table.nameAr, builder: (column) => column);

  GeneratedColumn<String> get cropType =>
      $composableBuilder(column: $table.cropType, builder: (column) => column);

  GeneratedColumnWithTypeConverter<List<Map<String, double>>, String>
      get boundary => $composableBuilder(
          column: $table.boundary, builder: (column) => column);

  GeneratedColumnWithTypeConverter<Map<String, double>?, String> get centroid =>
      $composableBuilder(column: $table.centroid, builder: (column) => column);

  GeneratedColumn<double> get areaHectares => $composableBuilder(
      column: $table.areaHectares, builder: (column) => column);

  GeneratedColumn<String> get status =>
      $composableBuilder(column: $table.status, builder: (column) => column);

  GeneratedColumn<double> get ndviCurrent => $composableBuilder(
      column: $table.ndviCurrent, builder: (column) => column);

  GeneratedColumn<DateTime> get ndviUpdatedAt => $composableBuilder(
      column: $table.ndviUpdatedAt, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  GeneratedColumn<bool> get isDeleted =>
      $composableBuilder(column: $table.isDeleted, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  GeneratedColumn<String> get etag =>
      $composableBuilder(column: $table.etag, builder: (column) => column);

  GeneratedColumn<DateTime> get serverUpdatedAt => $composableBuilder(
      column: $table.serverUpdatedAt, builder: (column) => column);
}

class $$DaoFieldsTableTableManager extends RootTableManager<
    _$FieldDaoTestDatabase,
    $DaoFieldsTable,
    DaoField,
    $$DaoFieldsTableFilterComposer,
    $$DaoFieldsTableOrderingComposer,
    $$DaoFieldsTableAnnotationComposer,
    $$DaoFieldsTableCreateCompanionBuilder,
    $$DaoFieldsTableUpdateCompanionBuilder,
    (
      DaoField,
      BaseReferences<_$FieldDaoTestDatabase, $DaoFieldsTable, DaoField>
    ),
    DaoField,
    PrefetchHooks Function()> {
  $$DaoFieldsTableTableManager(_$FieldDaoTestDatabase db, $DaoFieldsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$DaoFieldsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$DaoFieldsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$DaoFieldsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String?> remoteId = const Value.absent(),
            Value<String> tenantId = const Value.absent(),
            Value<String?> farmId = const Value.absent(),
            Value<String> name = const Value.absent(),
            Value<String?> nameAr = const Value.absent(),
            Value<String?> cropType = const Value.absent(),
            Value<List<Map<String, double>>> boundary = const Value.absent(),
            Value<Map<String, double>?> centroid = const Value.absent(),
            Value<double> areaHectares = const Value.absent(),
            Value<String?> status = const Value.absent(),
            Value<double?> ndviCurrent = const Value.absent(),
            Value<DateTime?> ndviUpdatedAt = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<bool> isDeleted = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<String?> etag = const Value.absent(),
            Value<DateTime?> serverUpdatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              DaoFieldsCompanion(
            id: id,
            remoteId: remoteId,
            tenantId: tenantId,
            farmId: farmId,
            name: name,
            nameAr: nameAr,
            cropType: cropType,
            boundary: boundary,
            centroid: centroid,
            areaHectares: areaHectares,
            status: status,
            ndviCurrent: ndviCurrent,
            ndviUpdatedAt: ndviUpdatedAt,
            synced: synced,
            isDeleted: isDeleted,
            createdAt: createdAt,
            updatedAt: updatedAt,
            etag: etag,
            serverUpdatedAt: serverUpdatedAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            Value<String?> remoteId = const Value.absent(),
            required String tenantId,
            Value<String?> farmId = const Value.absent(),
            required String name,
            Value<String?> nameAr = const Value.absent(),
            Value<String?> cropType = const Value.absent(),
            required List<Map<String, double>> boundary,
            Value<Map<String, double>?> centroid = const Value.absent(),
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
            Value<int> rowid = const Value.absent(),
          }) =>
              DaoFieldsCompanion.insert(
            id: id,
            remoteId: remoteId,
            tenantId: tenantId,
            farmId: farmId,
            name: name,
            nameAr: nameAr,
            cropType: cropType,
            boundary: boundary,
            centroid: centroid,
            areaHectares: areaHectares,
            status: status,
            ndviCurrent: ndviCurrent,
            ndviUpdatedAt: ndviUpdatedAt,
            synced: synced,
            isDeleted: isDeleted,
            createdAt: createdAt,
            updatedAt: updatedAt,
            etag: etag,
            serverUpdatedAt: serverUpdatedAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$DaoFieldsTableProcessedTableManager = ProcessedTableManager<
    _$FieldDaoTestDatabase,
    $DaoFieldsTable,
    DaoField,
    $$DaoFieldsTableFilterComposer,
    $$DaoFieldsTableOrderingComposer,
    $$DaoFieldsTableAnnotationComposer,
    $$DaoFieldsTableCreateCompanionBuilder,
    $$DaoFieldsTableUpdateCompanionBuilder,
    (
      DaoField,
      BaseReferences<_$FieldDaoTestDatabase, $DaoFieldsTable, DaoField>
    ),
    DaoField,
    PrefetchHooks Function()>;

class $FieldDaoTestDatabaseManager {
  final _$FieldDaoTestDatabase _db;
  $FieldDaoTestDatabaseManager(this._db);
  $$DaoFieldsTableTableManager get daoFields =>
      $$DaoFieldsTableTableManager(_db, _db.daoFields);
}
