// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'weather_dao_test.dart';

// ignore_for_file: type=lint
class $WeatherCacheTable extends WeatherCache
    with TableInfo<$WeatherCacheTable, WeatherCacheData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $WeatherCacheTable(this.attachedDatabase, [this._alias]);
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
  static const VerificationMeta _locationIdMeta =
      const VerificationMeta('locationId');
  @override
  late final GeneratedColumn<String> locationId = GeneratedColumn<String>(
      'location_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _latitudeMeta =
      const VerificationMeta('latitude');
  @override
  late final GeneratedColumn<double> latitude = GeneratedColumn<double>(
      'latitude', aliasedName, false,
      type: DriftSqlType.double, requiredDuringInsert: true);
  static const VerificationMeta _longitudeMeta =
      const VerificationMeta('longitude');
  @override
  late final GeneratedColumn<double> longitude = GeneratedColumn<double>(
      'longitude', aliasedName, false,
      type: DriftSqlType.double, requiredDuringInsert: true);
  static const VerificationMeta _weatherTypeMeta =
      const VerificationMeta('weatherType');
  @override
  late final GeneratedColumn<String> weatherType = GeneratedColumn<String>(
      'weather_type', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _dataMeta = const VerificationMeta('data');
  @override
  late final GeneratedColumn<String> data = GeneratedColumn<String>(
      'data', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _fetchedAtMeta =
      const VerificationMeta('fetchedAt');
  @override
  late final GeneratedColumn<DateTime> fetchedAt = GeneratedColumn<DateTime>(
      'fetched_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  static const VerificationMeta _expiresAtMeta =
      const VerificationMeta('expiresAt');
  @override
  late final GeneratedColumn<DateTime> expiresAt = GeneratedColumn<DateTime>(
      'expires_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  static const VerificationMeta _forecastDateMeta =
      const VerificationMeta('forecastDate');
  @override
  late final GeneratedColumn<DateTime> forecastDate = GeneratedColumn<DateTime>(
      'forecast_date', aliasedName, true,
      type: DriftSqlType.dateTime, requiredDuringInsert: false);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        tenantId,
        locationId,
        latitude,
        longitude,
        weatherType,
        data,
        fetchedAt,
        expiresAt,
        forecastDate
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'weather_cache';
  @override
  VerificationContext validateIntegrity(Insertable<WeatherCacheData> instance,
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
    if (data.containsKey('location_id')) {
      context.handle(
          _locationIdMeta,
          locationId.isAcceptableOrUnknown(
              data['location_id']!, _locationIdMeta));
    } else if (isInserting) {
      context.missing(_locationIdMeta);
    }
    if (data.containsKey('latitude')) {
      context.handle(_latitudeMeta,
          latitude.isAcceptableOrUnknown(data['latitude']!, _latitudeMeta));
    } else if (isInserting) {
      context.missing(_latitudeMeta);
    }
    if (data.containsKey('longitude')) {
      context.handle(_longitudeMeta,
          longitude.isAcceptableOrUnknown(data['longitude']!, _longitudeMeta));
    } else if (isInserting) {
      context.missing(_longitudeMeta);
    }
    if (data.containsKey('weather_type')) {
      context.handle(
          _weatherTypeMeta,
          weatherType.isAcceptableOrUnknown(
              data['weather_type']!, _weatherTypeMeta));
    } else if (isInserting) {
      context.missing(_weatherTypeMeta);
    }
    if (data.containsKey('data')) {
      context.handle(
          _dataMeta, this.data.isAcceptableOrUnknown(data['data']!, _dataMeta));
    } else if (isInserting) {
      context.missing(_dataMeta);
    }
    if (data.containsKey('fetched_at')) {
      context.handle(_fetchedAtMeta,
          fetchedAt.isAcceptableOrUnknown(data['fetched_at']!, _fetchedAtMeta));
    } else if (isInserting) {
      context.missing(_fetchedAtMeta);
    }
    if (data.containsKey('expires_at')) {
      context.handle(_expiresAtMeta,
          expiresAt.isAcceptableOrUnknown(data['expires_at']!, _expiresAtMeta));
    } else if (isInserting) {
      context.missing(_expiresAtMeta);
    }
    if (data.containsKey('forecast_date')) {
      context.handle(
          _forecastDateMeta,
          forecastDate.isAcceptableOrUnknown(
              data['forecast_date']!, _forecastDateMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  WeatherCacheData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return WeatherCacheData(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      tenantId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}tenant_id'])!,
      locationId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}location_id'])!,
      latitude: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}latitude'])!,
      longitude: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}longitude'])!,
      weatherType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}weather_type'])!,
      data: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}data'])!,
      fetchedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}fetched_at'])!,
      expiresAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}expires_at'])!,
      forecastDate: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}forecast_date']),
    );
  }

  @override
  $WeatherCacheTable createAlias(String alias) {
    return $WeatherCacheTable(attachedDatabase, alias);
  }
}

class WeatherCacheData extends DataClass
    implements Insertable<WeatherCacheData> {
  final int id;
  final String tenantId;
  final String locationId;
  final double latitude;
  final double longitude;
  final String weatherType;
  final String data;
  final DateTime fetchedAt;
  final DateTime expiresAt;
  final DateTime? forecastDate;
  const WeatherCacheData(
      {required this.id,
      required this.tenantId,
      required this.locationId,
      required this.latitude,
      required this.longitude,
      required this.weatherType,
      required this.data,
      required this.fetchedAt,
      required this.expiresAt,
      this.forecastDate});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['tenant_id'] = Variable<String>(tenantId);
    map['location_id'] = Variable<String>(locationId);
    map['latitude'] = Variable<double>(latitude);
    map['longitude'] = Variable<double>(longitude);
    map['weather_type'] = Variable<String>(weatherType);
    map['data'] = Variable<String>(data);
    map['fetched_at'] = Variable<DateTime>(fetchedAt);
    map['expires_at'] = Variable<DateTime>(expiresAt);
    if (!nullToAbsent || forecastDate != null) {
      map['forecast_date'] = Variable<DateTime>(forecastDate);
    }
    return map;
  }

  WeatherCacheCompanion toCompanion(bool nullToAbsent) {
    return WeatherCacheCompanion(
      id: Value(id),
      tenantId: Value(tenantId),
      locationId: Value(locationId),
      latitude: Value(latitude),
      longitude: Value(longitude),
      weatherType: Value(weatherType),
      data: Value(data),
      fetchedAt: Value(fetchedAt),
      expiresAt: Value(expiresAt),
      forecastDate: forecastDate == null && nullToAbsent
          ? const Value.absent()
          : Value(forecastDate),
    );
  }

  factory WeatherCacheData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return WeatherCacheData(
      id: serializer.fromJson<int>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenantId']),
      locationId: serializer.fromJson<String>(json['locationId']),
      latitude: serializer.fromJson<double>(json['latitude']),
      longitude: serializer.fromJson<double>(json['longitude']),
      weatherType: serializer.fromJson<String>(json['weatherType']),
      data: serializer.fromJson<String>(json['data']),
      fetchedAt: serializer.fromJson<DateTime>(json['fetchedAt']),
      expiresAt: serializer.fromJson<DateTime>(json['expiresAt']),
      forecastDate: serializer.fromJson<DateTime?>(json['forecastDate']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'tenantId': serializer.toJson<String>(tenantId),
      'locationId': serializer.toJson<String>(locationId),
      'latitude': serializer.toJson<double>(latitude),
      'longitude': serializer.toJson<double>(longitude),
      'weatherType': serializer.toJson<String>(weatherType),
      'data': serializer.toJson<String>(data),
      'fetchedAt': serializer.toJson<DateTime>(fetchedAt),
      'expiresAt': serializer.toJson<DateTime>(expiresAt),
      'forecastDate': serializer.toJson<DateTime?>(forecastDate),
    };
  }

  WeatherCacheData copyWith(
          {int? id,
          String? tenantId,
          String? locationId,
          double? latitude,
          double? longitude,
          String? weatherType,
          String? data,
          DateTime? fetchedAt,
          DateTime? expiresAt,
          Value<DateTime?> forecastDate = const Value.absent()}) =>
      WeatherCacheData(
        id: id ?? this.id,
        tenantId: tenantId ?? this.tenantId,
        locationId: locationId ?? this.locationId,
        latitude: latitude ?? this.latitude,
        longitude: longitude ?? this.longitude,
        weatherType: weatherType ?? this.weatherType,
        data: data ?? this.data,
        fetchedAt: fetchedAt ?? this.fetchedAt,
        expiresAt: expiresAt ?? this.expiresAt,
        forecastDate:
            forecastDate.present ? forecastDate.value : this.forecastDate,
      );
  WeatherCacheData copyWithCompanion(WeatherCacheCompanion data) {
    return WeatherCacheData(
      id: data.id.present ? data.id.value : this.id,
      tenantId: data.tenantId.present ? data.tenantId.value : this.tenantId,
      locationId:
          data.locationId.present ? data.locationId.value : this.locationId,
      latitude: data.latitude.present ? data.latitude.value : this.latitude,
      longitude: data.longitude.present ? data.longitude.value : this.longitude,
      weatherType:
          data.weatherType.present ? data.weatherType.value : this.weatherType,
      data: data.data.present ? data.data.value : this.data,
      fetchedAt: data.fetchedAt.present ? data.fetchedAt.value : this.fetchedAt,
      expiresAt: data.expiresAt.present ? data.expiresAt.value : this.expiresAt,
      forecastDate: data.forecastDate.present
          ? data.forecastDate.value
          : this.forecastDate,
    );
  }

  @override
  String toString() {
    return (StringBuffer('WeatherCacheData(')
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('locationId: $locationId, ')
          ..write('latitude: $latitude, ')
          ..write('longitude: $longitude, ')
          ..write('weatherType: $weatherType, ')
          ..write('data: $data, ')
          ..write('fetchedAt: $fetchedAt, ')
          ..write('expiresAt: $expiresAt, ')
          ..write('forecastDate: $forecastDate')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, tenantId, locationId, latitude, longitude,
      weatherType, data, fetchedAt, expiresAt, forecastDate);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is WeatherCacheData &&
          other.id == this.id &&
          other.tenantId == this.tenantId &&
          other.locationId == this.locationId &&
          other.latitude == this.latitude &&
          other.longitude == this.longitude &&
          other.weatherType == this.weatherType &&
          other.data == this.data &&
          other.fetchedAt == this.fetchedAt &&
          other.expiresAt == this.expiresAt &&
          other.forecastDate == this.forecastDate);
}

class WeatherCacheCompanion extends UpdateCompanion<WeatherCacheData> {
  final Value<int> id;
  final Value<String> tenantId;
  final Value<String> locationId;
  final Value<double> latitude;
  final Value<double> longitude;
  final Value<String> weatherType;
  final Value<String> data;
  final Value<DateTime> fetchedAt;
  final Value<DateTime> expiresAt;
  final Value<DateTime?> forecastDate;
  const WeatherCacheCompanion({
    this.id = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.locationId = const Value.absent(),
    this.latitude = const Value.absent(),
    this.longitude = const Value.absent(),
    this.weatherType = const Value.absent(),
    this.data = const Value.absent(),
    this.fetchedAt = const Value.absent(),
    this.expiresAt = const Value.absent(),
    this.forecastDate = const Value.absent(),
  });
  WeatherCacheCompanion.insert({
    this.id = const Value.absent(),
    required String tenantId,
    required String locationId,
    required double latitude,
    required double longitude,
    required String weatherType,
    required String data,
    required DateTime fetchedAt,
    required DateTime expiresAt,
    this.forecastDate = const Value.absent(),
  })  : tenantId = Value(tenantId),
        locationId = Value(locationId),
        latitude = Value(latitude),
        longitude = Value(longitude),
        weatherType = Value(weatherType),
        data = Value(data),
        fetchedAt = Value(fetchedAt),
        expiresAt = Value(expiresAt);
  static Insertable<WeatherCacheData> custom({
    Expression<int>? id,
    Expression<String>? tenantId,
    Expression<String>? locationId,
    Expression<double>? latitude,
    Expression<double>? longitude,
    Expression<String>? weatherType,
    Expression<String>? data,
    Expression<DateTime>? fetchedAt,
    Expression<DateTime>? expiresAt,
    Expression<DateTime>? forecastDate,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (tenantId != null) 'tenant_id': tenantId,
      if (locationId != null) 'location_id': locationId,
      if (latitude != null) 'latitude': latitude,
      if (longitude != null) 'longitude': longitude,
      if (weatherType != null) 'weather_type': weatherType,
      if (data != null) 'data': data,
      if (fetchedAt != null) 'fetched_at': fetchedAt,
      if (expiresAt != null) 'expires_at': expiresAt,
      if (forecastDate != null) 'forecast_date': forecastDate,
    });
  }

  WeatherCacheCompanion copyWith(
      {Value<int>? id,
      Value<String>? tenantId,
      Value<String>? locationId,
      Value<double>? latitude,
      Value<double>? longitude,
      Value<String>? weatherType,
      Value<String>? data,
      Value<DateTime>? fetchedAt,
      Value<DateTime>? expiresAt,
      Value<DateTime?>? forecastDate}) {
    return WeatherCacheCompanion(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      locationId: locationId ?? this.locationId,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      weatherType: weatherType ?? this.weatherType,
      data: data ?? this.data,
      fetchedAt: fetchedAt ?? this.fetchedAt,
      expiresAt: expiresAt ?? this.expiresAt,
      forecastDate: forecastDate ?? this.forecastDate,
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
    if (locationId.present) {
      map['location_id'] = Variable<String>(locationId.value);
    }
    if (latitude.present) {
      map['latitude'] = Variable<double>(latitude.value);
    }
    if (longitude.present) {
      map['longitude'] = Variable<double>(longitude.value);
    }
    if (weatherType.present) {
      map['weather_type'] = Variable<String>(weatherType.value);
    }
    if (data.present) {
      map['data'] = Variable<String>(data.value);
    }
    if (fetchedAt.present) {
      map['fetched_at'] = Variable<DateTime>(fetchedAt.value);
    }
    if (expiresAt.present) {
      map['expires_at'] = Variable<DateTime>(expiresAt.value);
    }
    if (forecastDate.present) {
      map['forecast_date'] = Variable<DateTime>(forecastDate.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('WeatherCacheCompanion(')
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('locationId: $locationId, ')
          ..write('latitude: $latitude, ')
          ..write('longitude: $longitude, ')
          ..write('weatherType: $weatherType, ')
          ..write('data: $data, ')
          ..write('fetchedAt: $fetchedAt, ')
          ..write('expiresAt: $expiresAt, ')
          ..write('forecastDate: $forecastDate')
          ..write(')'))
        .toString();
  }
}

class $WeatherAlertsTable extends WeatherAlerts
    with TableInfo<$WeatherAlertsTable, WeatherAlert> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $WeatherAlertsTable(this.attachedDatabase, [this._alias]);
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
  static const VerificationMeta _alertIdMeta =
      const VerificationMeta('alertId');
  @override
  late final GeneratedColumn<String> alertId = GeneratedColumn<String>(
      'alert_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _alertTypeMeta =
      const VerificationMeta('alertType');
  @override
  late final GeneratedColumn<String> alertType = GeneratedColumn<String>(
      'alert_type', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _severityMeta =
      const VerificationMeta('severity');
  @override
  late final GeneratedColumn<String> severity = GeneratedColumn<String>(
      'severity', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _titleMeta = const VerificationMeta('title');
  @override
  late final GeneratedColumn<String> title = GeneratedColumn<String>(
      'title', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _titleArMeta =
      const VerificationMeta('titleAr');
  @override
  late final GeneratedColumn<String> titleAr = GeneratedColumn<String>(
      'title_ar', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _descriptionMeta =
      const VerificationMeta('description');
  @override
  late final GeneratedColumn<String> description = GeneratedColumn<String>(
      'description', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _descriptionArMeta =
      const VerificationMeta('descriptionAr');
  @override
  late final GeneratedColumn<String> descriptionAr = GeneratedColumn<String>(
      'description_ar', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _latitudeMeta =
      const VerificationMeta('latitude');
  @override
  late final GeneratedColumn<double> latitude = GeneratedColumn<double>(
      'latitude', aliasedName, true,
      type: DriftSqlType.double, requiredDuringInsert: false);
  static const VerificationMeta _longitudeMeta =
      const VerificationMeta('longitude');
  @override
  late final GeneratedColumn<double> longitude = GeneratedColumn<double>(
      'longitude', aliasedName, true,
      type: DriftSqlType.double, requiredDuringInsert: false);
  static const VerificationMeta _radiusMeta = const VerificationMeta('radius');
  @override
  late final GeneratedColumn<double> radius = GeneratedColumn<double>(
      'radius', aliasedName, true,
      type: DriftSqlType.double, requiredDuringInsert: false);
  static const VerificationMeta _startsAtMeta =
      const VerificationMeta('startsAt');
  @override
  late final GeneratedColumn<DateTime> startsAt = GeneratedColumn<DateTime>(
      'starts_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  static const VerificationMeta _expiresAtMeta =
      const VerificationMeta('expiresAt');
  @override
  late final GeneratedColumn<DateTime> expiresAt = GeneratedColumn<DateTime>(
      'expires_at', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  static const VerificationMeta _isReadMeta = const VerificationMeta('isRead');
  @override
  late final GeneratedColumn<bool> isRead = GeneratedColumn<bool>(
      'is_read', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("is_read" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _isActiveMeta =
      const VerificationMeta('isActive');
  @override
  late final GeneratedColumn<bool> isActive = GeneratedColumn<bool>(
      'is_active', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("is_active" IN (0, 1))'),
      defaultValue: const Constant(true));
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
        alertId,
        alertType,
        severity,
        title,
        titleAr,
        description,
        descriptionAr,
        latitude,
        longitude,
        radius,
        startsAt,
        expiresAt,
        isRead,
        isActive,
        createdAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'weather_alerts';
  @override
  VerificationContext validateIntegrity(Insertable<WeatherAlert> instance,
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
    if (data.containsKey('alert_id')) {
      context.handle(_alertIdMeta,
          alertId.isAcceptableOrUnknown(data['alert_id']!, _alertIdMeta));
    } else if (isInserting) {
      context.missing(_alertIdMeta);
    }
    if (data.containsKey('alert_type')) {
      context.handle(_alertTypeMeta,
          alertType.isAcceptableOrUnknown(data['alert_type']!, _alertTypeMeta));
    } else if (isInserting) {
      context.missing(_alertTypeMeta);
    }
    if (data.containsKey('severity')) {
      context.handle(_severityMeta,
          severity.isAcceptableOrUnknown(data['severity']!, _severityMeta));
    } else if (isInserting) {
      context.missing(_severityMeta);
    }
    if (data.containsKey('title')) {
      context.handle(
          _titleMeta, title.isAcceptableOrUnknown(data['title']!, _titleMeta));
    } else if (isInserting) {
      context.missing(_titleMeta);
    }
    if (data.containsKey('title_ar')) {
      context.handle(_titleArMeta,
          titleAr.isAcceptableOrUnknown(data['title_ar']!, _titleArMeta));
    }
    if (data.containsKey('description')) {
      context.handle(
          _descriptionMeta,
          description.isAcceptableOrUnknown(
              data['description']!, _descriptionMeta));
    } else if (isInserting) {
      context.missing(_descriptionMeta);
    }
    if (data.containsKey('description_ar')) {
      context.handle(
          _descriptionArMeta,
          descriptionAr.isAcceptableOrUnknown(
              data['description_ar']!, _descriptionArMeta));
    }
    if (data.containsKey('latitude')) {
      context.handle(_latitudeMeta,
          latitude.isAcceptableOrUnknown(data['latitude']!, _latitudeMeta));
    }
    if (data.containsKey('longitude')) {
      context.handle(_longitudeMeta,
          longitude.isAcceptableOrUnknown(data['longitude']!, _longitudeMeta));
    }
    if (data.containsKey('radius')) {
      context.handle(_radiusMeta,
          radius.isAcceptableOrUnknown(data['radius']!, _radiusMeta));
    }
    if (data.containsKey('starts_at')) {
      context.handle(_startsAtMeta,
          startsAt.isAcceptableOrUnknown(data['starts_at']!, _startsAtMeta));
    } else if (isInserting) {
      context.missing(_startsAtMeta);
    }
    if (data.containsKey('expires_at')) {
      context.handle(_expiresAtMeta,
          expiresAt.isAcceptableOrUnknown(data['expires_at']!, _expiresAtMeta));
    } else if (isInserting) {
      context.missing(_expiresAtMeta);
    }
    if (data.containsKey('is_read')) {
      context.handle(_isReadMeta,
          isRead.isAcceptableOrUnknown(data['is_read']!, _isReadMeta));
    }
    if (data.containsKey('is_active')) {
      context.handle(_isActiveMeta,
          isActive.isAcceptableOrUnknown(data['is_active']!, _isActiveMeta));
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
  WeatherAlert map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return WeatherAlert(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      tenantId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}tenant_id'])!,
      alertId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}alert_id'])!,
      alertType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}alert_type'])!,
      severity: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}severity'])!,
      title: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}title'])!,
      titleAr: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}title_ar']),
      description: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}description'])!,
      descriptionAr: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}description_ar']),
      latitude: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}latitude']),
      longitude: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}longitude']),
      radius: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}radius']),
      startsAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}starts_at'])!,
      expiresAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}expires_at'])!,
      isRead: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}is_read'])!,
      isActive: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}is_active'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $WeatherAlertsTable createAlias(String alias) {
    return $WeatherAlertsTable(attachedDatabase, alias);
  }
}

class WeatherAlert extends DataClass implements Insertable<WeatherAlert> {
  final int id;
  final String tenantId;
  final String alertId;
  final String alertType;
  final String severity;
  final String title;
  final String? titleAr;
  final String description;
  final String? descriptionAr;
  final double? latitude;
  final double? longitude;
  final double? radius;
  final DateTime startsAt;
  final DateTime expiresAt;
  final bool isRead;
  final bool isActive;
  final DateTime createdAt;
  const WeatherAlert(
      {required this.id,
      required this.tenantId,
      required this.alertId,
      required this.alertType,
      required this.severity,
      required this.title,
      this.titleAr,
      required this.description,
      this.descriptionAr,
      this.latitude,
      this.longitude,
      this.radius,
      required this.startsAt,
      required this.expiresAt,
      required this.isRead,
      required this.isActive,
      required this.createdAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['tenant_id'] = Variable<String>(tenantId);
    map['alert_id'] = Variable<String>(alertId);
    map['alert_type'] = Variable<String>(alertType);
    map['severity'] = Variable<String>(severity);
    map['title'] = Variable<String>(title);
    if (!nullToAbsent || titleAr != null) {
      map['title_ar'] = Variable<String>(titleAr);
    }
    map['description'] = Variable<String>(description);
    if (!nullToAbsent || descriptionAr != null) {
      map['description_ar'] = Variable<String>(descriptionAr);
    }
    if (!nullToAbsent || latitude != null) {
      map['latitude'] = Variable<double>(latitude);
    }
    if (!nullToAbsent || longitude != null) {
      map['longitude'] = Variable<double>(longitude);
    }
    if (!nullToAbsent || radius != null) {
      map['radius'] = Variable<double>(radius);
    }
    map['starts_at'] = Variable<DateTime>(startsAt);
    map['expires_at'] = Variable<DateTime>(expiresAt);
    map['is_read'] = Variable<bool>(isRead);
    map['is_active'] = Variable<bool>(isActive);
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  WeatherAlertsCompanion toCompanion(bool nullToAbsent) {
    return WeatherAlertsCompanion(
      id: Value(id),
      tenantId: Value(tenantId),
      alertId: Value(alertId),
      alertType: Value(alertType),
      severity: Value(severity),
      title: Value(title),
      titleAr: titleAr == null && nullToAbsent
          ? const Value.absent()
          : Value(titleAr),
      description: Value(description),
      descriptionAr: descriptionAr == null && nullToAbsent
          ? const Value.absent()
          : Value(descriptionAr),
      latitude: latitude == null && nullToAbsent
          ? const Value.absent()
          : Value(latitude),
      longitude: longitude == null && nullToAbsent
          ? const Value.absent()
          : Value(longitude),
      radius:
          radius == null && nullToAbsent ? const Value.absent() : Value(radius),
      startsAt: Value(startsAt),
      expiresAt: Value(expiresAt),
      isRead: Value(isRead),
      isActive: Value(isActive),
      createdAt: Value(createdAt),
    );
  }

  factory WeatherAlert.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return WeatherAlert(
      id: serializer.fromJson<int>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenantId']),
      alertId: serializer.fromJson<String>(json['alertId']),
      alertType: serializer.fromJson<String>(json['alertType']),
      severity: serializer.fromJson<String>(json['severity']),
      title: serializer.fromJson<String>(json['title']),
      titleAr: serializer.fromJson<String?>(json['titleAr']),
      description: serializer.fromJson<String>(json['description']),
      descriptionAr: serializer.fromJson<String?>(json['descriptionAr']),
      latitude: serializer.fromJson<double?>(json['latitude']),
      longitude: serializer.fromJson<double?>(json['longitude']),
      radius: serializer.fromJson<double?>(json['radius']),
      startsAt: serializer.fromJson<DateTime>(json['startsAt']),
      expiresAt: serializer.fromJson<DateTime>(json['expiresAt']),
      isRead: serializer.fromJson<bool>(json['isRead']),
      isActive: serializer.fromJson<bool>(json['isActive']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'tenantId': serializer.toJson<String>(tenantId),
      'alertId': serializer.toJson<String>(alertId),
      'alertType': serializer.toJson<String>(alertType),
      'severity': serializer.toJson<String>(severity),
      'title': serializer.toJson<String>(title),
      'titleAr': serializer.toJson<String?>(titleAr),
      'description': serializer.toJson<String>(description),
      'descriptionAr': serializer.toJson<String?>(descriptionAr),
      'latitude': serializer.toJson<double?>(latitude),
      'longitude': serializer.toJson<double?>(longitude),
      'radius': serializer.toJson<double?>(radius),
      'startsAt': serializer.toJson<DateTime>(startsAt),
      'expiresAt': serializer.toJson<DateTime>(expiresAt),
      'isRead': serializer.toJson<bool>(isRead),
      'isActive': serializer.toJson<bool>(isActive),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  WeatherAlert copyWith(
          {int? id,
          String? tenantId,
          String? alertId,
          String? alertType,
          String? severity,
          String? title,
          Value<String?> titleAr = const Value.absent(),
          String? description,
          Value<String?> descriptionAr = const Value.absent(),
          Value<double?> latitude = const Value.absent(),
          Value<double?> longitude = const Value.absent(),
          Value<double?> radius = const Value.absent(),
          DateTime? startsAt,
          DateTime? expiresAt,
          bool? isRead,
          bool? isActive,
          DateTime? createdAt}) =>
      WeatherAlert(
        id: id ?? this.id,
        tenantId: tenantId ?? this.tenantId,
        alertId: alertId ?? this.alertId,
        alertType: alertType ?? this.alertType,
        severity: severity ?? this.severity,
        title: title ?? this.title,
        titleAr: titleAr.present ? titleAr.value : this.titleAr,
        description: description ?? this.description,
        descriptionAr:
            descriptionAr.present ? descriptionAr.value : this.descriptionAr,
        latitude: latitude.present ? latitude.value : this.latitude,
        longitude: longitude.present ? longitude.value : this.longitude,
        radius: radius.present ? radius.value : this.radius,
        startsAt: startsAt ?? this.startsAt,
        expiresAt: expiresAt ?? this.expiresAt,
        isRead: isRead ?? this.isRead,
        isActive: isActive ?? this.isActive,
        createdAt: createdAt ?? this.createdAt,
      );
  WeatherAlert copyWithCompanion(WeatherAlertsCompanion data) {
    return WeatherAlert(
      id: data.id.present ? data.id.value : this.id,
      tenantId: data.tenantId.present ? data.tenantId.value : this.tenantId,
      alertId: data.alertId.present ? data.alertId.value : this.alertId,
      alertType: data.alertType.present ? data.alertType.value : this.alertType,
      severity: data.severity.present ? data.severity.value : this.severity,
      title: data.title.present ? data.title.value : this.title,
      titleAr: data.titleAr.present ? data.titleAr.value : this.titleAr,
      description:
          data.description.present ? data.description.value : this.description,
      descriptionAr: data.descriptionAr.present
          ? data.descriptionAr.value
          : this.descriptionAr,
      latitude: data.latitude.present ? data.latitude.value : this.latitude,
      longitude: data.longitude.present ? data.longitude.value : this.longitude,
      radius: data.radius.present ? data.radius.value : this.radius,
      startsAt: data.startsAt.present ? data.startsAt.value : this.startsAt,
      expiresAt: data.expiresAt.present ? data.expiresAt.value : this.expiresAt,
      isRead: data.isRead.present ? data.isRead.value : this.isRead,
      isActive: data.isActive.present ? data.isActive.value : this.isActive,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('WeatherAlert(')
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('alertId: $alertId, ')
          ..write('alertType: $alertType, ')
          ..write('severity: $severity, ')
          ..write('title: $title, ')
          ..write('titleAr: $titleAr, ')
          ..write('description: $description, ')
          ..write('descriptionAr: $descriptionAr, ')
          ..write('latitude: $latitude, ')
          ..write('longitude: $longitude, ')
          ..write('radius: $radius, ')
          ..write('startsAt: $startsAt, ')
          ..write('expiresAt: $expiresAt, ')
          ..write('isRead: $isRead, ')
          ..write('isActive: $isActive, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id,
      tenantId,
      alertId,
      alertType,
      severity,
      title,
      titleAr,
      description,
      descriptionAr,
      latitude,
      longitude,
      radius,
      startsAt,
      expiresAt,
      isRead,
      isActive,
      createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is WeatherAlert &&
          other.id == this.id &&
          other.tenantId == this.tenantId &&
          other.alertId == this.alertId &&
          other.alertType == this.alertType &&
          other.severity == this.severity &&
          other.title == this.title &&
          other.titleAr == this.titleAr &&
          other.description == this.description &&
          other.descriptionAr == this.descriptionAr &&
          other.latitude == this.latitude &&
          other.longitude == this.longitude &&
          other.radius == this.radius &&
          other.startsAt == this.startsAt &&
          other.expiresAt == this.expiresAt &&
          other.isRead == this.isRead &&
          other.isActive == this.isActive &&
          other.createdAt == this.createdAt);
}

class WeatherAlertsCompanion extends UpdateCompanion<WeatherAlert> {
  final Value<int> id;
  final Value<String> tenantId;
  final Value<String> alertId;
  final Value<String> alertType;
  final Value<String> severity;
  final Value<String> title;
  final Value<String?> titleAr;
  final Value<String> description;
  final Value<String?> descriptionAr;
  final Value<double?> latitude;
  final Value<double?> longitude;
  final Value<double?> radius;
  final Value<DateTime> startsAt;
  final Value<DateTime> expiresAt;
  final Value<bool> isRead;
  final Value<bool> isActive;
  final Value<DateTime> createdAt;
  const WeatherAlertsCompanion({
    this.id = const Value.absent(),
    this.tenantId = const Value.absent(),
    this.alertId = const Value.absent(),
    this.alertType = const Value.absent(),
    this.severity = const Value.absent(),
    this.title = const Value.absent(),
    this.titleAr = const Value.absent(),
    this.description = const Value.absent(),
    this.descriptionAr = const Value.absent(),
    this.latitude = const Value.absent(),
    this.longitude = const Value.absent(),
    this.radius = const Value.absent(),
    this.startsAt = const Value.absent(),
    this.expiresAt = const Value.absent(),
    this.isRead = const Value.absent(),
    this.isActive = const Value.absent(),
    this.createdAt = const Value.absent(),
  });
  WeatherAlertsCompanion.insert({
    this.id = const Value.absent(),
    required String tenantId,
    required String alertId,
    required String alertType,
    required String severity,
    required String title,
    this.titleAr = const Value.absent(),
    required String description,
    this.descriptionAr = const Value.absent(),
    this.latitude = const Value.absent(),
    this.longitude = const Value.absent(),
    this.radius = const Value.absent(),
    required DateTime startsAt,
    required DateTime expiresAt,
    this.isRead = const Value.absent(),
    this.isActive = const Value.absent(),
    this.createdAt = const Value.absent(),
  })  : tenantId = Value(tenantId),
        alertId = Value(alertId),
        alertType = Value(alertType),
        severity = Value(severity),
        title = Value(title),
        description = Value(description),
        startsAt = Value(startsAt),
        expiresAt = Value(expiresAt);
  static Insertable<WeatherAlert> custom({
    Expression<int>? id,
    Expression<String>? tenantId,
    Expression<String>? alertId,
    Expression<String>? alertType,
    Expression<String>? severity,
    Expression<String>? title,
    Expression<String>? titleAr,
    Expression<String>? description,
    Expression<String>? descriptionAr,
    Expression<double>? latitude,
    Expression<double>? longitude,
    Expression<double>? radius,
    Expression<DateTime>? startsAt,
    Expression<DateTime>? expiresAt,
    Expression<bool>? isRead,
    Expression<bool>? isActive,
    Expression<DateTime>? createdAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (tenantId != null) 'tenant_id': tenantId,
      if (alertId != null) 'alert_id': alertId,
      if (alertType != null) 'alert_type': alertType,
      if (severity != null) 'severity': severity,
      if (title != null) 'title': title,
      if (titleAr != null) 'title_ar': titleAr,
      if (description != null) 'description': description,
      if (descriptionAr != null) 'description_ar': descriptionAr,
      if (latitude != null) 'latitude': latitude,
      if (longitude != null) 'longitude': longitude,
      if (radius != null) 'radius': radius,
      if (startsAt != null) 'starts_at': startsAt,
      if (expiresAt != null) 'expires_at': expiresAt,
      if (isRead != null) 'is_read': isRead,
      if (isActive != null) 'is_active': isActive,
      if (createdAt != null) 'created_at': createdAt,
    });
  }

  WeatherAlertsCompanion copyWith(
      {Value<int>? id,
      Value<String>? tenantId,
      Value<String>? alertId,
      Value<String>? alertType,
      Value<String>? severity,
      Value<String>? title,
      Value<String?>? titleAr,
      Value<String>? description,
      Value<String?>? descriptionAr,
      Value<double?>? latitude,
      Value<double?>? longitude,
      Value<double?>? radius,
      Value<DateTime>? startsAt,
      Value<DateTime>? expiresAt,
      Value<bool>? isRead,
      Value<bool>? isActive,
      Value<DateTime>? createdAt}) {
    return WeatherAlertsCompanion(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      alertId: alertId ?? this.alertId,
      alertType: alertType ?? this.alertType,
      severity: severity ?? this.severity,
      title: title ?? this.title,
      titleAr: titleAr ?? this.titleAr,
      description: description ?? this.description,
      descriptionAr: descriptionAr ?? this.descriptionAr,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      radius: radius ?? this.radius,
      startsAt: startsAt ?? this.startsAt,
      expiresAt: expiresAt ?? this.expiresAt,
      isRead: isRead ?? this.isRead,
      isActive: isActive ?? this.isActive,
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
    if (alertId.present) {
      map['alert_id'] = Variable<String>(alertId.value);
    }
    if (alertType.present) {
      map['alert_type'] = Variable<String>(alertType.value);
    }
    if (severity.present) {
      map['severity'] = Variable<String>(severity.value);
    }
    if (title.present) {
      map['title'] = Variable<String>(title.value);
    }
    if (titleAr.present) {
      map['title_ar'] = Variable<String>(titleAr.value);
    }
    if (description.present) {
      map['description'] = Variable<String>(description.value);
    }
    if (descriptionAr.present) {
      map['description_ar'] = Variable<String>(descriptionAr.value);
    }
    if (latitude.present) {
      map['latitude'] = Variable<double>(latitude.value);
    }
    if (longitude.present) {
      map['longitude'] = Variable<double>(longitude.value);
    }
    if (radius.present) {
      map['radius'] = Variable<double>(radius.value);
    }
    if (startsAt.present) {
      map['starts_at'] = Variable<DateTime>(startsAt.value);
    }
    if (expiresAt.present) {
      map['expires_at'] = Variable<DateTime>(expiresAt.value);
    }
    if (isRead.present) {
      map['is_read'] = Variable<bool>(isRead.value);
    }
    if (isActive.present) {
      map['is_active'] = Variable<bool>(isActive.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('WeatherAlertsCompanion(')
          ..write('id: $id, ')
          ..write('tenantId: $tenantId, ')
          ..write('alertId: $alertId, ')
          ..write('alertType: $alertType, ')
          ..write('severity: $severity, ')
          ..write('title: $title, ')
          ..write('titleAr: $titleAr, ')
          ..write('description: $description, ')
          ..write('descriptionAr: $descriptionAr, ')
          ..write('latitude: $latitude, ')
          ..write('longitude: $longitude, ')
          ..write('radius: $radius, ')
          ..write('startsAt: $startsAt, ')
          ..write('expiresAt: $expiresAt, ')
          ..write('isRead: $isRead, ')
          ..write('isActive: $isActive, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }
}

class $WeatherStatisticsTable extends WeatherStatistics
    with TableInfo<$WeatherStatisticsTable, WeatherStatistic> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $WeatherStatisticsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _fieldIdMeta =
      const VerificationMeta('fieldId');
  @override
  late final GeneratedColumn<String> fieldId = GeneratedColumn<String>(
      'field_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _dateMeta = const VerificationMeta('date');
  @override
  late final GeneratedColumn<DateTime> date = GeneratedColumn<DateTime>(
      'date', aliasedName, false,
      type: DriftSqlType.dateTime, requiredDuringInsert: true);
  static const VerificationMeta _tempMinMeta =
      const VerificationMeta('tempMin');
  @override
  late final GeneratedColumn<double> tempMin = GeneratedColumn<double>(
      'temp_min', aliasedName, true,
      type: DriftSqlType.double, requiredDuringInsert: false);
  static const VerificationMeta _tempMaxMeta =
      const VerificationMeta('tempMax');
  @override
  late final GeneratedColumn<double> tempMax = GeneratedColumn<double>(
      'temp_max', aliasedName, true,
      type: DriftSqlType.double, requiredDuringInsert: false);
  static const VerificationMeta _tempAvgMeta =
      const VerificationMeta('tempAvg');
  @override
  late final GeneratedColumn<double> tempAvg = GeneratedColumn<double>(
      'temp_avg', aliasedName, true,
      type: DriftSqlType.double, requiredDuringInsert: false);
  static const VerificationMeta _humidityMeta =
      const VerificationMeta('humidity');
  @override
  late final GeneratedColumn<double> humidity = GeneratedColumn<double>(
      'humidity', aliasedName, true,
      type: DriftSqlType.double, requiredDuringInsert: false);
  static const VerificationMeta _precipitationMeta =
      const VerificationMeta('precipitation');
  @override
  late final GeneratedColumn<double> precipitation = GeneratedColumn<double>(
      'precipitation', aliasedName, true,
      type: DriftSqlType.double, requiredDuringInsert: false);
  static const VerificationMeta _windSpeedMeta =
      const VerificationMeta('windSpeed');
  @override
  late final GeneratedColumn<double> windSpeed = GeneratedColumn<double>(
      'wind_speed', aliasedName, true,
      type: DriftSqlType.double, requiredDuringInsert: false);
  static const VerificationMeta _solarRadiationMeta =
      const VerificationMeta('solarRadiation');
  @override
  late final GeneratedColumn<double> solarRadiation = GeneratedColumn<double>(
      'solar_radiation', aliasedName, true,
      type: DriftSqlType.double, requiredDuringInsert: false);
  static const VerificationMeta _evapotranspirationMeta =
      const VerificationMeta('evapotranspiration');
  @override
  late final GeneratedColumn<double> evapotranspiration =
      GeneratedColumn<double>('evapotranspiration', aliasedName, true,
          type: DriftSqlType.double, requiredDuringInsert: false);
  static const VerificationMeta _growingDegreeDaysMeta =
      const VerificationMeta('growingDegreeDays');
  @override
  late final GeneratedColumn<int> growingDegreeDays = GeneratedColumn<int>(
      'growing_degree_days', aliasedName, true,
      type: DriftSqlType.int, requiredDuringInsert: false);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        fieldId,
        date,
        tempMin,
        tempMax,
        tempAvg,
        humidity,
        precipitation,
        windSpeed,
        solarRadiation,
        evapotranspiration,
        growingDegreeDays
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'weather_statistics';
  @override
  VerificationContext validateIntegrity(Insertable<WeatherStatistic> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('field_id')) {
      context.handle(_fieldIdMeta,
          fieldId.isAcceptableOrUnknown(data['field_id']!, _fieldIdMeta));
    } else if (isInserting) {
      context.missing(_fieldIdMeta);
    }
    if (data.containsKey('date')) {
      context.handle(
          _dateMeta, date.isAcceptableOrUnknown(data['date']!, _dateMeta));
    } else if (isInserting) {
      context.missing(_dateMeta);
    }
    if (data.containsKey('temp_min')) {
      context.handle(_tempMinMeta,
          tempMin.isAcceptableOrUnknown(data['temp_min']!, _tempMinMeta));
    }
    if (data.containsKey('temp_max')) {
      context.handle(_tempMaxMeta,
          tempMax.isAcceptableOrUnknown(data['temp_max']!, _tempMaxMeta));
    }
    if (data.containsKey('temp_avg')) {
      context.handle(_tempAvgMeta,
          tempAvg.isAcceptableOrUnknown(data['temp_avg']!, _tempAvgMeta));
    }
    if (data.containsKey('humidity')) {
      context.handle(_humidityMeta,
          humidity.isAcceptableOrUnknown(data['humidity']!, _humidityMeta));
    }
    if (data.containsKey('precipitation')) {
      context.handle(
          _precipitationMeta,
          precipitation.isAcceptableOrUnknown(
              data['precipitation']!, _precipitationMeta));
    }
    if (data.containsKey('wind_speed')) {
      context.handle(_windSpeedMeta,
          windSpeed.isAcceptableOrUnknown(data['wind_speed']!, _windSpeedMeta));
    }
    if (data.containsKey('solar_radiation')) {
      context.handle(
          _solarRadiationMeta,
          solarRadiation.isAcceptableOrUnknown(
              data['solar_radiation']!, _solarRadiationMeta));
    }
    if (data.containsKey('evapotranspiration')) {
      context.handle(
          _evapotranspirationMeta,
          evapotranspiration.isAcceptableOrUnknown(
              data['evapotranspiration']!, _evapotranspirationMeta));
    }
    if (data.containsKey('growing_degree_days')) {
      context.handle(
          _growingDegreeDaysMeta,
          growingDegreeDays.isAcceptableOrUnknown(
              data['growing_degree_days']!, _growingDegreeDaysMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  WeatherStatistic map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return WeatherStatistic(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      fieldId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}field_id'])!,
      date: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}date'])!,
      tempMin: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}temp_min']),
      tempMax: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}temp_max']),
      tempAvg: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}temp_avg']),
      humidity: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}humidity']),
      precipitation: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}precipitation']),
      windSpeed: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}wind_speed']),
      solarRadiation: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['${effectivePrefix}solar_radiation']),
      evapotranspiration: attachedDatabase.typeMapping.read(
          DriftSqlType.double, data['${effectivePrefix}evapotranspiration']),
      growingDegreeDays: attachedDatabase.typeMapping.read(
          DriftSqlType.int, data['${effectivePrefix}growing_degree_days']),
    );
  }

  @override
  $WeatherStatisticsTable createAlias(String alias) {
    return $WeatherStatisticsTable(attachedDatabase, alias);
  }
}

class WeatherStatistic extends DataClass
    implements Insertable<WeatherStatistic> {
  final int id;
  final String fieldId;
  final DateTime date;
  final double? tempMin;
  final double? tempMax;
  final double? tempAvg;
  final double? humidity;
  final double? precipitation;
  final double? windSpeed;
  final double? solarRadiation;
  final double? evapotranspiration;
  final int? growingDegreeDays;
  const WeatherStatistic(
      {required this.id,
      required this.fieldId,
      required this.date,
      this.tempMin,
      this.tempMax,
      this.tempAvg,
      this.humidity,
      this.precipitation,
      this.windSpeed,
      this.solarRadiation,
      this.evapotranspiration,
      this.growingDegreeDays});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['field_id'] = Variable<String>(fieldId);
    map['date'] = Variable<DateTime>(date);
    if (!nullToAbsent || tempMin != null) {
      map['temp_min'] = Variable<double>(tempMin);
    }
    if (!nullToAbsent || tempMax != null) {
      map['temp_max'] = Variable<double>(tempMax);
    }
    if (!nullToAbsent || tempAvg != null) {
      map['temp_avg'] = Variable<double>(tempAvg);
    }
    if (!nullToAbsent || humidity != null) {
      map['humidity'] = Variable<double>(humidity);
    }
    if (!nullToAbsent || precipitation != null) {
      map['precipitation'] = Variable<double>(precipitation);
    }
    if (!nullToAbsent || windSpeed != null) {
      map['wind_speed'] = Variable<double>(windSpeed);
    }
    if (!nullToAbsent || solarRadiation != null) {
      map['solar_radiation'] = Variable<double>(solarRadiation);
    }
    if (!nullToAbsent || evapotranspiration != null) {
      map['evapotranspiration'] = Variable<double>(evapotranspiration);
    }
    if (!nullToAbsent || growingDegreeDays != null) {
      map['growing_degree_days'] = Variable<int>(growingDegreeDays);
    }
    return map;
  }

  WeatherStatisticsCompanion toCompanion(bool nullToAbsent) {
    return WeatherStatisticsCompanion(
      id: Value(id),
      fieldId: Value(fieldId),
      date: Value(date),
      tempMin: tempMin == null && nullToAbsent
          ? const Value.absent()
          : Value(tempMin),
      tempMax: tempMax == null && nullToAbsent
          ? const Value.absent()
          : Value(tempMax),
      tempAvg: tempAvg == null && nullToAbsent
          ? const Value.absent()
          : Value(tempAvg),
      humidity: humidity == null && nullToAbsent
          ? const Value.absent()
          : Value(humidity),
      precipitation: precipitation == null && nullToAbsent
          ? const Value.absent()
          : Value(precipitation),
      windSpeed: windSpeed == null && nullToAbsent
          ? const Value.absent()
          : Value(windSpeed),
      solarRadiation: solarRadiation == null && nullToAbsent
          ? const Value.absent()
          : Value(solarRadiation),
      evapotranspiration: evapotranspiration == null && nullToAbsent
          ? const Value.absent()
          : Value(evapotranspiration),
      growingDegreeDays: growingDegreeDays == null && nullToAbsent
          ? const Value.absent()
          : Value(growingDegreeDays),
    );
  }

  factory WeatherStatistic.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return WeatherStatistic(
      id: serializer.fromJson<int>(json['id']),
      fieldId: serializer.fromJson<String>(json['fieldId']),
      date: serializer.fromJson<DateTime>(json['date']),
      tempMin: serializer.fromJson<double?>(json['tempMin']),
      tempMax: serializer.fromJson<double?>(json['tempMax']),
      tempAvg: serializer.fromJson<double?>(json['tempAvg']),
      humidity: serializer.fromJson<double?>(json['humidity']),
      precipitation: serializer.fromJson<double?>(json['precipitation']),
      windSpeed: serializer.fromJson<double?>(json['windSpeed']),
      solarRadiation: serializer.fromJson<double?>(json['solarRadiation']),
      evapotranspiration:
          serializer.fromJson<double?>(json['evapotranspiration']),
      growingDegreeDays: serializer.fromJson<int?>(json['growingDegreeDays']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'fieldId': serializer.toJson<String>(fieldId),
      'date': serializer.toJson<DateTime>(date),
      'tempMin': serializer.toJson<double?>(tempMin),
      'tempMax': serializer.toJson<double?>(tempMax),
      'tempAvg': serializer.toJson<double?>(tempAvg),
      'humidity': serializer.toJson<double?>(humidity),
      'precipitation': serializer.toJson<double?>(precipitation),
      'windSpeed': serializer.toJson<double?>(windSpeed),
      'solarRadiation': serializer.toJson<double?>(solarRadiation),
      'evapotranspiration': serializer.toJson<double?>(evapotranspiration),
      'growingDegreeDays': serializer.toJson<int?>(growingDegreeDays),
    };
  }

  WeatherStatistic copyWith(
          {int? id,
          String? fieldId,
          DateTime? date,
          Value<double?> tempMin = const Value.absent(),
          Value<double?> tempMax = const Value.absent(),
          Value<double?> tempAvg = const Value.absent(),
          Value<double?> humidity = const Value.absent(),
          Value<double?> precipitation = const Value.absent(),
          Value<double?> windSpeed = const Value.absent(),
          Value<double?> solarRadiation = const Value.absent(),
          Value<double?> evapotranspiration = const Value.absent(),
          Value<int?> growingDegreeDays = const Value.absent()}) =>
      WeatherStatistic(
        id: id ?? this.id,
        fieldId: fieldId ?? this.fieldId,
        date: date ?? this.date,
        tempMin: tempMin.present ? tempMin.value : this.tempMin,
        tempMax: tempMax.present ? tempMax.value : this.tempMax,
        tempAvg: tempAvg.present ? tempAvg.value : this.tempAvg,
        humidity: humidity.present ? humidity.value : this.humidity,
        precipitation:
            precipitation.present ? precipitation.value : this.precipitation,
        windSpeed: windSpeed.present ? windSpeed.value : this.windSpeed,
        solarRadiation:
            solarRadiation.present ? solarRadiation.value : this.solarRadiation,
        evapotranspiration: evapotranspiration.present
            ? evapotranspiration.value
            : this.evapotranspiration,
        growingDegreeDays: growingDegreeDays.present
            ? growingDegreeDays.value
            : this.growingDegreeDays,
      );
  WeatherStatistic copyWithCompanion(WeatherStatisticsCompanion data) {
    return WeatherStatistic(
      id: data.id.present ? data.id.value : this.id,
      fieldId: data.fieldId.present ? data.fieldId.value : this.fieldId,
      date: data.date.present ? data.date.value : this.date,
      tempMin: data.tempMin.present ? data.tempMin.value : this.tempMin,
      tempMax: data.tempMax.present ? data.tempMax.value : this.tempMax,
      tempAvg: data.tempAvg.present ? data.tempAvg.value : this.tempAvg,
      humidity: data.humidity.present ? data.humidity.value : this.humidity,
      precipitation: data.precipitation.present
          ? data.precipitation.value
          : this.precipitation,
      windSpeed: data.windSpeed.present ? data.windSpeed.value : this.windSpeed,
      solarRadiation: data.solarRadiation.present
          ? data.solarRadiation.value
          : this.solarRadiation,
      evapotranspiration: data.evapotranspiration.present
          ? data.evapotranspiration.value
          : this.evapotranspiration,
      growingDegreeDays: data.growingDegreeDays.present
          ? data.growingDegreeDays.value
          : this.growingDegreeDays,
    );
  }

  @override
  String toString() {
    return (StringBuffer('WeatherStatistic(')
          ..write('id: $id, ')
          ..write('fieldId: $fieldId, ')
          ..write('date: $date, ')
          ..write('tempMin: $tempMin, ')
          ..write('tempMax: $tempMax, ')
          ..write('tempAvg: $tempAvg, ')
          ..write('humidity: $humidity, ')
          ..write('precipitation: $precipitation, ')
          ..write('windSpeed: $windSpeed, ')
          ..write('solarRadiation: $solarRadiation, ')
          ..write('evapotranspiration: $evapotranspiration, ')
          ..write('growingDegreeDays: $growingDegreeDays')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id,
      fieldId,
      date,
      tempMin,
      tempMax,
      tempAvg,
      humidity,
      precipitation,
      windSpeed,
      solarRadiation,
      evapotranspiration,
      growingDegreeDays);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is WeatherStatistic &&
          other.id == this.id &&
          other.fieldId == this.fieldId &&
          other.date == this.date &&
          other.tempMin == this.tempMin &&
          other.tempMax == this.tempMax &&
          other.tempAvg == this.tempAvg &&
          other.humidity == this.humidity &&
          other.precipitation == this.precipitation &&
          other.windSpeed == this.windSpeed &&
          other.solarRadiation == this.solarRadiation &&
          other.evapotranspiration == this.evapotranspiration &&
          other.growingDegreeDays == this.growingDegreeDays);
}

class WeatherStatisticsCompanion extends UpdateCompanion<WeatherStatistic> {
  final Value<int> id;
  final Value<String> fieldId;
  final Value<DateTime> date;
  final Value<double?> tempMin;
  final Value<double?> tempMax;
  final Value<double?> tempAvg;
  final Value<double?> humidity;
  final Value<double?> precipitation;
  final Value<double?> windSpeed;
  final Value<double?> solarRadiation;
  final Value<double?> evapotranspiration;
  final Value<int?> growingDegreeDays;
  const WeatherStatisticsCompanion({
    this.id = const Value.absent(),
    this.fieldId = const Value.absent(),
    this.date = const Value.absent(),
    this.tempMin = const Value.absent(),
    this.tempMax = const Value.absent(),
    this.tempAvg = const Value.absent(),
    this.humidity = const Value.absent(),
    this.precipitation = const Value.absent(),
    this.windSpeed = const Value.absent(),
    this.solarRadiation = const Value.absent(),
    this.evapotranspiration = const Value.absent(),
    this.growingDegreeDays = const Value.absent(),
  });
  WeatherStatisticsCompanion.insert({
    this.id = const Value.absent(),
    required String fieldId,
    required DateTime date,
    this.tempMin = const Value.absent(),
    this.tempMax = const Value.absent(),
    this.tempAvg = const Value.absent(),
    this.humidity = const Value.absent(),
    this.precipitation = const Value.absent(),
    this.windSpeed = const Value.absent(),
    this.solarRadiation = const Value.absent(),
    this.evapotranspiration = const Value.absent(),
    this.growingDegreeDays = const Value.absent(),
  })  : fieldId = Value(fieldId),
        date = Value(date);
  static Insertable<WeatherStatistic> custom({
    Expression<int>? id,
    Expression<String>? fieldId,
    Expression<DateTime>? date,
    Expression<double>? tempMin,
    Expression<double>? tempMax,
    Expression<double>? tempAvg,
    Expression<double>? humidity,
    Expression<double>? precipitation,
    Expression<double>? windSpeed,
    Expression<double>? solarRadiation,
    Expression<double>? evapotranspiration,
    Expression<int>? growingDegreeDays,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (fieldId != null) 'field_id': fieldId,
      if (date != null) 'date': date,
      if (tempMin != null) 'temp_min': tempMin,
      if (tempMax != null) 'temp_max': tempMax,
      if (tempAvg != null) 'temp_avg': tempAvg,
      if (humidity != null) 'humidity': humidity,
      if (precipitation != null) 'precipitation': precipitation,
      if (windSpeed != null) 'wind_speed': windSpeed,
      if (solarRadiation != null) 'solar_radiation': solarRadiation,
      if (evapotranspiration != null) 'evapotranspiration': evapotranspiration,
      if (growingDegreeDays != null) 'growing_degree_days': growingDegreeDays,
    });
  }

  WeatherStatisticsCompanion copyWith(
      {Value<int>? id,
      Value<String>? fieldId,
      Value<DateTime>? date,
      Value<double?>? tempMin,
      Value<double?>? tempMax,
      Value<double?>? tempAvg,
      Value<double?>? humidity,
      Value<double?>? precipitation,
      Value<double?>? windSpeed,
      Value<double?>? solarRadiation,
      Value<double?>? evapotranspiration,
      Value<int?>? growingDegreeDays}) {
    return WeatherStatisticsCompanion(
      id: id ?? this.id,
      fieldId: fieldId ?? this.fieldId,
      date: date ?? this.date,
      tempMin: tempMin ?? this.tempMin,
      tempMax: tempMax ?? this.tempMax,
      tempAvg: tempAvg ?? this.tempAvg,
      humidity: humidity ?? this.humidity,
      precipitation: precipitation ?? this.precipitation,
      windSpeed: windSpeed ?? this.windSpeed,
      solarRadiation: solarRadiation ?? this.solarRadiation,
      evapotranspiration: evapotranspiration ?? this.evapotranspiration,
      growingDegreeDays: growingDegreeDays ?? this.growingDegreeDays,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (fieldId.present) {
      map['field_id'] = Variable<String>(fieldId.value);
    }
    if (date.present) {
      map['date'] = Variable<DateTime>(date.value);
    }
    if (tempMin.present) {
      map['temp_min'] = Variable<double>(tempMin.value);
    }
    if (tempMax.present) {
      map['temp_max'] = Variable<double>(tempMax.value);
    }
    if (tempAvg.present) {
      map['temp_avg'] = Variable<double>(tempAvg.value);
    }
    if (humidity.present) {
      map['humidity'] = Variable<double>(humidity.value);
    }
    if (precipitation.present) {
      map['precipitation'] = Variable<double>(precipitation.value);
    }
    if (windSpeed.present) {
      map['wind_speed'] = Variable<double>(windSpeed.value);
    }
    if (solarRadiation.present) {
      map['solar_radiation'] = Variable<double>(solarRadiation.value);
    }
    if (evapotranspiration.present) {
      map['evapotranspiration'] = Variable<double>(evapotranspiration.value);
    }
    if (growingDegreeDays.present) {
      map['growing_degree_days'] = Variable<int>(growingDegreeDays.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('WeatherStatisticsCompanion(')
          ..write('id: $id, ')
          ..write('fieldId: $fieldId, ')
          ..write('date: $date, ')
          ..write('tempMin: $tempMin, ')
          ..write('tempMax: $tempMax, ')
          ..write('tempAvg: $tempAvg, ')
          ..write('humidity: $humidity, ')
          ..write('precipitation: $precipitation, ')
          ..write('windSpeed: $windSpeed, ')
          ..write('solarRadiation: $solarRadiation, ')
          ..write('evapotranspiration: $evapotranspiration, ')
          ..write('growingDegreeDays: $growingDegreeDays')
          ..write(')'))
        .toString();
  }
}

abstract class _$WeatherDaoTestDatabase extends GeneratedDatabase {
  _$WeatherDaoTestDatabase(QueryExecutor e) : super(e);
  $WeatherDaoTestDatabaseManager get managers =>
      $WeatherDaoTestDatabaseManager(this);
  late final $WeatherCacheTable weatherCache = $WeatherCacheTable(this);
  late final $WeatherAlertsTable weatherAlerts = $WeatherAlertsTable(this);
  late final $WeatherStatisticsTable weatherStatistics =
      $WeatherStatisticsTable(this);
  late final Index weatherCacheTenantIdx = Index('weather_cache_tenant_idx',
      'CREATE INDEX weather_cache_tenant_idx ON weather_cache (tenant_id)');
  late final Index weatherCacheLocationIdx = Index('weather_cache_location_idx',
      'CREATE INDEX weather_cache_location_idx ON weather_cache (location_id)');
  late final Index weatherCacheExpiryIdx = Index('weather_cache_expiry_idx',
      'CREATE INDEX weather_cache_expiry_idx ON weather_cache (expires_at)');
  late final Index weatherAlertsTenantIdx = Index('weather_alerts_tenant_idx',
      'CREATE INDEX weather_alerts_tenant_idx ON weather_alerts (tenant_id)');
  late final Index weatherAlertsReadIdx = Index('weather_alerts_read_idx',
      'CREATE INDEX weather_alerts_read_idx ON weather_alerts (is_read)');
  late final Index weatherAlertsActiveIdx = Index('weather_alerts_active_idx',
      'CREATE INDEX weather_alerts_active_idx ON weather_alerts (is_active)');
  late final Index weatherStatsFieldIdx = Index('weather_stats_field_idx',
      'CREATE INDEX weather_stats_field_idx ON weather_statistics (field_id)');
  late final Index weatherStatsDateIdx = Index('weather_stats_date_idx',
      'CREATE INDEX weather_stats_date_idx ON weather_statistics (date)');
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
        weatherCache,
        weatherAlerts,
        weatherStatistics,
        weatherCacheTenantIdx,
        weatherCacheLocationIdx,
        weatherCacheExpiryIdx,
        weatherAlertsTenantIdx,
        weatherAlertsReadIdx,
        weatherAlertsActiveIdx,
        weatherStatsFieldIdx,
        weatherStatsDateIdx
      ];
  @override
  DriftDatabaseOptions get options =>
      const DriftDatabaseOptions(storeDateTimeAsText: true);
}

typedef $$WeatherCacheTableCreateCompanionBuilder = WeatherCacheCompanion
    Function({
  Value<int> id,
  required String tenantId,
  required String locationId,
  required double latitude,
  required double longitude,
  required String weatherType,
  required String data,
  required DateTime fetchedAt,
  required DateTime expiresAt,
  Value<DateTime?> forecastDate,
});
typedef $$WeatherCacheTableUpdateCompanionBuilder = WeatherCacheCompanion
    Function({
  Value<int> id,
  Value<String> tenantId,
  Value<String> locationId,
  Value<double> latitude,
  Value<double> longitude,
  Value<String> weatherType,
  Value<String> data,
  Value<DateTime> fetchedAt,
  Value<DateTime> expiresAt,
  Value<DateTime?> forecastDate,
});

class $$WeatherCacheTableFilterComposer
    extends Composer<_$WeatherDaoTestDatabase, $WeatherCacheTable> {
  $$WeatherCacheTableFilterComposer({
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

  ColumnFilters<String> get locationId => $composableBuilder(
      column: $table.locationId, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get latitude => $composableBuilder(
      column: $table.latitude, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get longitude => $composableBuilder(
      column: $table.longitude, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get weatherType => $composableBuilder(
      column: $table.weatherType, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get data => $composableBuilder(
      column: $table.data, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get fetchedAt => $composableBuilder(
      column: $table.fetchedAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get expiresAt => $composableBuilder(
      column: $table.expiresAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get forecastDate => $composableBuilder(
      column: $table.forecastDate, builder: (column) => ColumnFilters(column));
}

class $$WeatherCacheTableOrderingComposer
    extends Composer<_$WeatherDaoTestDatabase, $WeatherCacheTable> {
  $$WeatherCacheTableOrderingComposer({
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

  ColumnOrderings<String> get locationId => $composableBuilder(
      column: $table.locationId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get latitude => $composableBuilder(
      column: $table.latitude, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get longitude => $composableBuilder(
      column: $table.longitude, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get weatherType => $composableBuilder(
      column: $table.weatherType, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get data => $composableBuilder(
      column: $table.data, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get fetchedAt => $composableBuilder(
      column: $table.fetchedAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get expiresAt => $composableBuilder(
      column: $table.expiresAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get forecastDate => $composableBuilder(
      column: $table.forecastDate,
      builder: (column) => ColumnOrderings(column));
}

class $$WeatherCacheTableAnnotationComposer
    extends Composer<_$WeatherDaoTestDatabase, $WeatherCacheTable> {
  $$WeatherCacheTableAnnotationComposer({
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

  GeneratedColumn<String> get locationId => $composableBuilder(
      column: $table.locationId, builder: (column) => column);

  GeneratedColumn<double> get latitude =>
      $composableBuilder(column: $table.latitude, builder: (column) => column);

  GeneratedColumn<double> get longitude =>
      $composableBuilder(column: $table.longitude, builder: (column) => column);

  GeneratedColumn<String> get weatherType => $composableBuilder(
      column: $table.weatherType, builder: (column) => column);

  GeneratedColumn<String> get data =>
      $composableBuilder(column: $table.data, builder: (column) => column);

  GeneratedColumn<DateTime> get fetchedAt =>
      $composableBuilder(column: $table.fetchedAt, builder: (column) => column);

  GeneratedColumn<DateTime> get expiresAt =>
      $composableBuilder(column: $table.expiresAt, builder: (column) => column);

  GeneratedColumn<DateTime> get forecastDate => $composableBuilder(
      column: $table.forecastDate, builder: (column) => column);
}

class $$WeatherCacheTableTableManager extends RootTableManager<
    _$WeatherDaoTestDatabase,
    $WeatherCacheTable,
    WeatherCacheData,
    $$WeatherCacheTableFilterComposer,
    $$WeatherCacheTableOrderingComposer,
    $$WeatherCacheTableAnnotationComposer,
    $$WeatherCacheTableCreateCompanionBuilder,
    $$WeatherCacheTableUpdateCompanionBuilder,
    (
      WeatherCacheData,
      BaseReferences<_$WeatherDaoTestDatabase, $WeatherCacheTable,
          WeatherCacheData>
    ),
    WeatherCacheData,
    PrefetchHooks Function()> {
  $$WeatherCacheTableTableManager(
      _$WeatherDaoTestDatabase db, $WeatherCacheTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$WeatherCacheTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$WeatherCacheTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$WeatherCacheTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> tenantId = const Value.absent(),
            Value<String> locationId = const Value.absent(),
            Value<double> latitude = const Value.absent(),
            Value<double> longitude = const Value.absent(),
            Value<String> weatherType = const Value.absent(),
            Value<String> data = const Value.absent(),
            Value<DateTime> fetchedAt = const Value.absent(),
            Value<DateTime> expiresAt = const Value.absent(),
            Value<DateTime?> forecastDate = const Value.absent(),
          }) =>
              WeatherCacheCompanion(
            id: id,
            tenantId: tenantId,
            locationId: locationId,
            latitude: latitude,
            longitude: longitude,
            weatherType: weatherType,
            data: data,
            fetchedAt: fetchedAt,
            expiresAt: expiresAt,
            forecastDate: forecastDate,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String tenantId,
            required String locationId,
            required double latitude,
            required double longitude,
            required String weatherType,
            required String data,
            required DateTime fetchedAt,
            required DateTime expiresAt,
            Value<DateTime?> forecastDate = const Value.absent(),
          }) =>
              WeatherCacheCompanion.insert(
            id: id,
            tenantId: tenantId,
            locationId: locationId,
            latitude: latitude,
            longitude: longitude,
            weatherType: weatherType,
            data: data,
            fetchedAt: fetchedAt,
            expiresAt: expiresAt,
            forecastDate: forecastDate,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$WeatherCacheTableProcessedTableManager = ProcessedTableManager<
    _$WeatherDaoTestDatabase,
    $WeatherCacheTable,
    WeatherCacheData,
    $$WeatherCacheTableFilterComposer,
    $$WeatherCacheTableOrderingComposer,
    $$WeatherCacheTableAnnotationComposer,
    $$WeatherCacheTableCreateCompanionBuilder,
    $$WeatherCacheTableUpdateCompanionBuilder,
    (
      WeatherCacheData,
      BaseReferences<_$WeatherDaoTestDatabase, $WeatherCacheTable,
          WeatherCacheData>
    ),
    WeatherCacheData,
    PrefetchHooks Function()>;
typedef $$WeatherAlertsTableCreateCompanionBuilder = WeatherAlertsCompanion
    Function({
  Value<int> id,
  required String tenantId,
  required String alertId,
  required String alertType,
  required String severity,
  required String title,
  Value<String?> titleAr,
  required String description,
  Value<String?> descriptionAr,
  Value<double?> latitude,
  Value<double?> longitude,
  Value<double?> radius,
  required DateTime startsAt,
  required DateTime expiresAt,
  Value<bool> isRead,
  Value<bool> isActive,
  Value<DateTime> createdAt,
});
typedef $$WeatherAlertsTableUpdateCompanionBuilder = WeatherAlertsCompanion
    Function({
  Value<int> id,
  Value<String> tenantId,
  Value<String> alertId,
  Value<String> alertType,
  Value<String> severity,
  Value<String> title,
  Value<String?> titleAr,
  Value<String> description,
  Value<String?> descriptionAr,
  Value<double?> latitude,
  Value<double?> longitude,
  Value<double?> radius,
  Value<DateTime> startsAt,
  Value<DateTime> expiresAt,
  Value<bool> isRead,
  Value<bool> isActive,
  Value<DateTime> createdAt,
});

class $$WeatherAlertsTableFilterComposer
    extends Composer<_$WeatherDaoTestDatabase, $WeatherAlertsTable> {
  $$WeatherAlertsTableFilterComposer({
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

  ColumnFilters<String> get alertId => $composableBuilder(
      column: $table.alertId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get alertType => $composableBuilder(
      column: $table.alertType, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get severity => $composableBuilder(
      column: $table.severity, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get title => $composableBuilder(
      column: $table.title, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get titleAr => $composableBuilder(
      column: $table.titleAr, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get description => $composableBuilder(
      column: $table.description, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get descriptionAr => $composableBuilder(
      column: $table.descriptionAr, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get latitude => $composableBuilder(
      column: $table.latitude, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get longitude => $composableBuilder(
      column: $table.longitude, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get radius => $composableBuilder(
      column: $table.radius, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get startsAt => $composableBuilder(
      column: $table.startsAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get expiresAt => $composableBuilder(
      column: $table.expiresAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get isRead => $composableBuilder(
      column: $table.isRead, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get isActive => $composableBuilder(
      column: $table.isActive, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));
}

class $$WeatherAlertsTableOrderingComposer
    extends Composer<_$WeatherDaoTestDatabase, $WeatherAlertsTable> {
  $$WeatherAlertsTableOrderingComposer({
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

  ColumnOrderings<String> get alertId => $composableBuilder(
      column: $table.alertId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get alertType => $composableBuilder(
      column: $table.alertType, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get severity => $composableBuilder(
      column: $table.severity, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get title => $composableBuilder(
      column: $table.title, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get titleAr => $composableBuilder(
      column: $table.titleAr, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get description => $composableBuilder(
      column: $table.description, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get descriptionAr => $composableBuilder(
      column: $table.descriptionAr,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get latitude => $composableBuilder(
      column: $table.latitude, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get longitude => $composableBuilder(
      column: $table.longitude, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get radius => $composableBuilder(
      column: $table.radius, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get startsAt => $composableBuilder(
      column: $table.startsAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get expiresAt => $composableBuilder(
      column: $table.expiresAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get isRead => $composableBuilder(
      column: $table.isRead, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get isActive => $composableBuilder(
      column: $table.isActive, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));
}

class $$WeatherAlertsTableAnnotationComposer
    extends Composer<_$WeatherDaoTestDatabase, $WeatherAlertsTable> {
  $$WeatherAlertsTableAnnotationComposer({
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

  GeneratedColumn<String> get alertId =>
      $composableBuilder(column: $table.alertId, builder: (column) => column);

  GeneratedColumn<String> get alertType =>
      $composableBuilder(column: $table.alertType, builder: (column) => column);

  GeneratedColumn<String> get severity =>
      $composableBuilder(column: $table.severity, builder: (column) => column);

  GeneratedColumn<String> get title =>
      $composableBuilder(column: $table.title, builder: (column) => column);

  GeneratedColumn<String> get titleAr =>
      $composableBuilder(column: $table.titleAr, builder: (column) => column);

  GeneratedColumn<String> get description => $composableBuilder(
      column: $table.description, builder: (column) => column);

  GeneratedColumn<String> get descriptionAr => $composableBuilder(
      column: $table.descriptionAr, builder: (column) => column);

  GeneratedColumn<double> get latitude =>
      $composableBuilder(column: $table.latitude, builder: (column) => column);

  GeneratedColumn<double> get longitude =>
      $composableBuilder(column: $table.longitude, builder: (column) => column);

  GeneratedColumn<double> get radius =>
      $composableBuilder(column: $table.radius, builder: (column) => column);

  GeneratedColumn<DateTime> get startsAt =>
      $composableBuilder(column: $table.startsAt, builder: (column) => column);

  GeneratedColumn<DateTime> get expiresAt =>
      $composableBuilder(column: $table.expiresAt, builder: (column) => column);

  GeneratedColumn<bool> get isRead =>
      $composableBuilder(column: $table.isRead, builder: (column) => column);

  GeneratedColumn<bool> get isActive =>
      $composableBuilder(column: $table.isActive, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$WeatherAlertsTableTableManager extends RootTableManager<
    _$WeatherDaoTestDatabase,
    $WeatherAlertsTable,
    WeatherAlert,
    $$WeatherAlertsTableFilterComposer,
    $$WeatherAlertsTableOrderingComposer,
    $$WeatherAlertsTableAnnotationComposer,
    $$WeatherAlertsTableCreateCompanionBuilder,
    $$WeatherAlertsTableUpdateCompanionBuilder,
    (
      WeatherAlert,
      BaseReferences<_$WeatherDaoTestDatabase, $WeatherAlertsTable,
          WeatherAlert>
    ),
    WeatherAlert,
    PrefetchHooks Function()> {
  $$WeatherAlertsTableTableManager(
      _$WeatherDaoTestDatabase db, $WeatherAlertsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$WeatherAlertsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$WeatherAlertsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$WeatherAlertsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> tenantId = const Value.absent(),
            Value<String> alertId = const Value.absent(),
            Value<String> alertType = const Value.absent(),
            Value<String> severity = const Value.absent(),
            Value<String> title = const Value.absent(),
            Value<String?> titleAr = const Value.absent(),
            Value<String> description = const Value.absent(),
            Value<String?> descriptionAr = const Value.absent(),
            Value<double?> latitude = const Value.absent(),
            Value<double?> longitude = const Value.absent(),
            Value<double?> radius = const Value.absent(),
            Value<DateTime> startsAt = const Value.absent(),
            Value<DateTime> expiresAt = const Value.absent(),
            Value<bool> isRead = const Value.absent(),
            Value<bool> isActive = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
          }) =>
              WeatherAlertsCompanion(
            id: id,
            tenantId: tenantId,
            alertId: alertId,
            alertType: alertType,
            severity: severity,
            title: title,
            titleAr: titleAr,
            description: description,
            descriptionAr: descriptionAr,
            latitude: latitude,
            longitude: longitude,
            radius: radius,
            startsAt: startsAt,
            expiresAt: expiresAt,
            isRead: isRead,
            isActive: isActive,
            createdAt: createdAt,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String tenantId,
            required String alertId,
            required String alertType,
            required String severity,
            required String title,
            Value<String?> titleAr = const Value.absent(),
            required String description,
            Value<String?> descriptionAr = const Value.absent(),
            Value<double?> latitude = const Value.absent(),
            Value<double?> longitude = const Value.absent(),
            Value<double?> radius = const Value.absent(),
            required DateTime startsAt,
            required DateTime expiresAt,
            Value<bool> isRead = const Value.absent(),
            Value<bool> isActive = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
          }) =>
              WeatherAlertsCompanion.insert(
            id: id,
            tenantId: tenantId,
            alertId: alertId,
            alertType: alertType,
            severity: severity,
            title: title,
            titleAr: titleAr,
            description: description,
            descriptionAr: descriptionAr,
            latitude: latitude,
            longitude: longitude,
            radius: radius,
            startsAt: startsAt,
            expiresAt: expiresAt,
            isRead: isRead,
            isActive: isActive,
            createdAt: createdAt,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$WeatherAlertsTableProcessedTableManager = ProcessedTableManager<
    _$WeatherDaoTestDatabase,
    $WeatherAlertsTable,
    WeatherAlert,
    $$WeatherAlertsTableFilterComposer,
    $$WeatherAlertsTableOrderingComposer,
    $$WeatherAlertsTableAnnotationComposer,
    $$WeatherAlertsTableCreateCompanionBuilder,
    $$WeatherAlertsTableUpdateCompanionBuilder,
    (
      WeatherAlert,
      BaseReferences<_$WeatherDaoTestDatabase, $WeatherAlertsTable,
          WeatherAlert>
    ),
    WeatherAlert,
    PrefetchHooks Function()>;
typedef $$WeatherStatisticsTableCreateCompanionBuilder
    = WeatherStatisticsCompanion Function({
  Value<int> id,
  required String fieldId,
  required DateTime date,
  Value<double?> tempMin,
  Value<double?> tempMax,
  Value<double?> tempAvg,
  Value<double?> humidity,
  Value<double?> precipitation,
  Value<double?> windSpeed,
  Value<double?> solarRadiation,
  Value<double?> evapotranspiration,
  Value<int?> growingDegreeDays,
});
typedef $$WeatherStatisticsTableUpdateCompanionBuilder
    = WeatherStatisticsCompanion Function({
  Value<int> id,
  Value<String> fieldId,
  Value<DateTime> date,
  Value<double?> tempMin,
  Value<double?> tempMax,
  Value<double?> tempAvg,
  Value<double?> humidity,
  Value<double?> precipitation,
  Value<double?> windSpeed,
  Value<double?> solarRadiation,
  Value<double?> evapotranspiration,
  Value<int?> growingDegreeDays,
});

class $$WeatherStatisticsTableFilterComposer
    extends Composer<_$WeatherDaoTestDatabase, $WeatherStatisticsTable> {
  $$WeatherStatisticsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get fieldId => $composableBuilder(
      column: $table.fieldId, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get date => $composableBuilder(
      column: $table.date, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get tempMin => $composableBuilder(
      column: $table.tempMin, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get tempMax => $composableBuilder(
      column: $table.tempMax, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get tempAvg => $composableBuilder(
      column: $table.tempAvg, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get humidity => $composableBuilder(
      column: $table.humidity, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get precipitation => $composableBuilder(
      column: $table.precipitation, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get windSpeed => $composableBuilder(
      column: $table.windSpeed, builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get solarRadiation => $composableBuilder(
      column: $table.solarRadiation,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<double> get evapotranspiration => $composableBuilder(
      column: $table.evapotranspiration,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get growingDegreeDays => $composableBuilder(
      column: $table.growingDegreeDays,
      builder: (column) => ColumnFilters(column));
}

class $$WeatherStatisticsTableOrderingComposer
    extends Composer<_$WeatherDaoTestDatabase, $WeatherStatisticsTable> {
  $$WeatherStatisticsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get fieldId => $composableBuilder(
      column: $table.fieldId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get date => $composableBuilder(
      column: $table.date, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get tempMin => $composableBuilder(
      column: $table.tempMin, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get tempMax => $composableBuilder(
      column: $table.tempMax, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get tempAvg => $composableBuilder(
      column: $table.tempAvg, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get humidity => $composableBuilder(
      column: $table.humidity, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get precipitation => $composableBuilder(
      column: $table.precipitation,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get windSpeed => $composableBuilder(
      column: $table.windSpeed, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get solarRadiation => $composableBuilder(
      column: $table.solarRadiation,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<double> get evapotranspiration => $composableBuilder(
      column: $table.evapotranspiration,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get growingDegreeDays => $composableBuilder(
      column: $table.growingDegreeDays,
      builder: (column) => ColumnOrderings(column));
}

class $$WeatherStatisticsTableAnnotationComposer
    extends Composer<_$WeatherDaoTestDatabase, $WeatherStatisticsTable> {
  $$WeatherStatisticsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get fieldId =>
      $composableBuilder(column: $table.fieldId, builder: (column) => column);

  GeneratedColumn<DateTime> get date =>
      $composableBuilder(column: $table.date, builder: (column) => column);

  GeneratedColumn<double> get tempMin =>
      $composableBuilder(column: $table.tempMin, builder: (column) => column);

  GeneratedColumn<double> get tempMax =>
      $composableBuilder(column: $table.tempMax, builder: (column) => column);

  GeneratedColumn<double> get tempAvg =>
      $composableBuilder(column: $table.tempAvg, builder: (column) => column);

  GeneratedColumn<double> get humidity =>
      $composableBuilder(column: $table.humidity, builder: (column) => column);

  GeneratedColumn<double> get precipitation => $composableBuilder(
      column: $table.precipitation, builder: (column) => column);

  GeneratedColumn<double> get windSpeed =>
      $composableBuilder(column: $table.windSpeed, builder: (column) => column);

  GeneratedColumn<double> get solarRadiation => $composableBuilder(
      column: $table.solarRadiation, builder: (column) => column);

  GeneratedColumn<double> get evapotranspiration => $composableBuilder(
      column: $table.evapotranspiration, builder: (column) => column);

  GeneratedColumn<int> get growingDegreeDays => $composableBuilder(
      column: $table.growingDegreeDays, builder: (column) => column);
}

class $$WeatherStatisticsTableTableManager extends RootTableManager<
    _$WeatherDaoTestDatabase,
    $WeatherStatisticsTable,
    WeatherStatistic,
    $$WeatherStatisticsTableFilterComposer,
    $$WeatherStatisticsTableOrderingComposer,
    $$WeatherStatisticsTableAnnotationComposer,
    $$WeatherStatisticsTableCreateCompanionBuilder,
    $$WeatherStatisticsTableUpdateCompanionBuilder,
    (
      WeatherStatistic,
      BaseReferences<_$WeatherDaoTestDatabase, $WeatherStatisticsTable,
          WeatherStatistic>
    ),
    WeatherStatistic,
    PrefetchHooks Function()> {
  $$WeatherStatisticsTableTableManager(
      _$WeatherDaoTestDatabase db, $WeatherStatisticsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$WeatherStatisticsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$WeatherStatisticsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$WeatherStatisticsTableAnnotationComposer(
                  $db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> fieldId = const Value.absent(),
            Value<DateTime> date = const Value.absent(),
            Value<double?> tempMin = const Value.absent(),
            Value<double?> tempMax = const Value.absent(),
            Value<double?> tempAvg = const Value.absent(),
            Value<double?> humidity = const Value.absent(),
            Value<double?> precipitation = const Value.absent(),
            Value<double?> windSpeed = const Value.absent(),
            Value<double?> solarRadiation = const Value.absent(),
            Value<double?> evapotranspiration = const Value.absent(),
            Value<int?> growingDegreeDays = const Value.absent(),
          }) =>
              WeatherStatisticsCompanion(
            id: id,
            fieldId: fieldId,
            date: date,
            tempMin: tempMin,
            tempMax: tempMax,
            tempAvg: tempAvg,
            humidity: humidity,
            precipitation: precipitation,
            windSpeed: windSpeed,
            solarRadiation: solarRadiation,
            evapotranspiration: evapotranspiration,
            growingDegreeDays: growingDegreeDays,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String fieldId,
            required DateTime date,
            Value<double?> tempMin = const Value.absent(),
            Value<double?> tempMax = const Value.absent(),
            Value<double?> tempAvg = const Value.absent(),
            Value<double?> humidity = const Value.absent(),
            Value<double?> precipitation = const Value.absent(),
            Value<double?> windSpeed = const Value.absent(),
            Value<double?> solarRadiation = const Value.absent(),
            Value<double?> evapotranspiration = const Value.absent(),
            Value<int?> growingDegreeDays = const Value.absent(),
          }) =>
              WeatherStatisticsCompanion.insert(
            id: id,
            fieldId: fieldId,
            date: date,
            tempMin: tempMin,
            tempMax: tempMax,
            tempAvg: tempAvg,
            humidity: humidity,
            precipitation: precipitation,
            windSpeed: windSpeed,
            solarRadiation: solarRadiation,
            evapotranspiration: evapotranspiration,
            growingDegreeDays: growingDegreeDays,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$WeatherStatisticsTableProcessedTableManager = ProcessedTableManager<
    _$WeatherDaoTestDatabase,
    $WeatherStatisticsTable,
    WeatherStatistic,
    $$WeatherStatisticsTableFilterComposer,
    $$WeatherStatisticsTableOrderingComposer,
    $$WeatherStatisticsTableAnnotationComposer,
    $$WeatherStatisticsTableCreateCompanionBuilder,
    $$WeatherStatisticsTableUpdateCompanionBuilder,
    (
      WeatherStatistic,
      BaseReferences<_$WeatherDaoTestDatabase, $WeatherStatisticsTable,
          WeatherStatistic>
    ),
    WeatherStatistic,
    PrefetchHooks Function()>;

class $WeatherDaoTestDatabaseManager {
  final _$WeatherDaoTestDatabase _db;
  $WeatherDaoTestDatabaseManager(this._db);
  $$WeatherCacheTableTableManager get weatherCache =>
      $$WeatherCacheTableTableManager(_db, _db.weatherCache);
  $$WeatherAlertsTableTableManager get weatherAlerts =>
      $$WeatherAlertsTableTableManager(_db, _db.weatherAlerts);
  $$WeatherStatisticsTableTableManager get weatherStatistics =>
      $$WeatherStatisticsTableTableManager(_db, _db.weatherStatistics);
}
