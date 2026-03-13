// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'weather_dao_test.dart';

// ignore_for_file: type=lint

// **************************************************************************
// DriftDatabaseGenerator
// **************************************************************************

class WeatherCacheData extends DataClass implements Insertable<WeatherCacheData> {
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

  const WeatherCacheData({
    this.id,
    required this.tenantId,
    required this.locationId,
    required this.latitude,
    required this.longitude,
    required this.weatherType,
    required this.data,
    required this.fetchedAt,
    required this.expiresAt,
    this.forecastDate,
  });

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

  factory WeatherCacheData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return WeatherCacheData(
      id: serializer.fromJson<int>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenant_id']),
      locationId: serializer.fromJson<String>(json['location_id']),
      latitude: serializer.fromJson<double>(json['latitude']),
      longitude: serializer.fromJson<double>(json['longitude']),
      weatherType: serializer.fromJson<String>(json['weather_type']),
      data: serializer.fromJson<String>(json['data']),
      fetchedAt: serializer.fromJson<DateTime>(json['fetched_at']),
      expiresAt: serializer.fromJson<DateTime>(json['expires_at']),
      forecastDate: serializer.fromJson<DateTime?>(json['forecast_date']),
    );
  }

  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'tenant_id': serializer.toJson<String>(tenantId),
      'location_id': serializer.toJson<String>(locationId),
      'latitude': serializer.toJson<double>(latitude),
      'longitude': serializer.toJson<double>(longitude),
      'weather_type': serializer.toJson<String>(weatherType),
      'data': serializer.toJson<String>(data),
      'fetched_at': serializer.toJson<DateTime>(fetchedAt),
      'expires_at': serializer.toJson<DateTime>(expiresAt),
      'forecast_date': serializer.toJson<DateTime?>(forecastDate),
    };
  }

  WeatherCacheData copyWith({
    int? id,
    String? tenantId,
    String? locationId,
    double? latitude,
    double? longitude,
    String? weatherType,
    String? data,
    DateTime? fetchedAt,
    DateTime? expiresAt,
    Value<DateTime> forecastDate = const Value.absent(),
  }) {
    return WeatherCacheData(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      locationId: locationId ?? this.locationId,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      weatherType: weatherType ?? this.weatherType,
      data: data ?? this.data,
      fetchedAt: fetchedAt ?? this.fetchedAt,
      expiresAt: expiresAt ?? this.expiresAt,
      forecastDate: forecastDate.present ? forecastDate.value : this.forecastDate,
    );
  }

  @override
  String toString() {
    return (StringBuffer('WeatherCacheData(')
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('locationId: ${locationId}, ')
          ..write('latitude: ${latitude}, ')
          ..write('longitude: ${longitude}, ')
          ..write('weatherType: ${weatherType}, ')
          ..write('data: ${data}, ')
          ..write('fetchedAt: ${fetchedAt}, ')
          ..write('expiresAt: ${expiresAt}, ')
          ..write('forecastDate: ${forecastDate}')
          ..write(')')
      ).toString();
  }

  @override
  int get hashCode => Object.hash(id, tenantId, locationId, latitude, longitude, weatherType, data, fetchedAt, expiresAt, forecastDate);

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
          other.forecastDate == this.forecastDate)
  ;
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
    Value<DateTime?> forecastDate = const Value.absent(),
  })
      : tenantId = Value(tenantId),
        locationId = Value(locationId),
        latitude = Value(latitude),
        longitude = Value(longitude),
        weatherType = Value(weatherType),
        data = Value(data),
        fetchedAt = Value(fetchedAt),
        expiresAt = Value(expiresAt);

  static Insertable<WeatherCacheData> custom({
    Expression<dynamic>? id,
    Expression<dynamic>? tenantId,
    Expression<dynamic>? locationId,
    Expression<dynamic>? latitude,
    Expression<dynamic>? longitude,
    Expression<dynamic>? weatherType,
    Expression<dynamic>? data,
    Expression<dynamic>? fetchedAt,
    Expression<dynamic>? expiresAt,
    Expression<dynamic>? forecastDate,
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

  WeatherCacheCompanion copyWith({
    Value<int>? id,
    Value<String>? tenantId,
    Value<String>? locationId,
    Value<double>? latitude,
    Value<double>? longitude,
    Value<String>? weatherType,
    Value<String>? data,
    Value<DateTime>? fetchedAt,
    Value<DateTime>? expiresAt,
    Value<DateTime?>? forecastDate,
  }) {
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
      map['forecast_date'] = Variable<DateTime?>(forecastDate.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('WeatherCacheCompanion(')
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('locationId: ${locationId}, ')
          ..write('latitude: ${latitude}, ')
          ..write('longitude: ${longitude}, ')
          ..write('weatherType: ${weatherType}, ')
          ..write('data: ${data}, ')
          ..write('fetchedAt: ${fetchedAt}, ')
          ..write('expiresAt: ${expiresAt}, ')
          ..write('forecastDate: ${forecastDate}')
          ..write(')')
      ).toString();
  }
}

class \$WeatherCacheTable extends WeatherCache
    with TableInfo<\$WeatherCacheTable, WeatherCacheData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  \$WeatherCacheTable(this.attachedDatabase, [this._alias]);

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

  static const VerificationMeta _locationIdMeta = VerificationMeta('locationId');
  @override
  late final GeneratedColumn<String> locationId =
      GeneratedColumn<String>(
          'location_id', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _latitudeMeta = VerificationMeta('latitude');
  @override
  late final GeneratedColumn<double> latitude =
      GeneratedColumn<double>(
          'latitude', aliasedName, false,
          type: DriftSqlType.double,
          requiredDuringInsert: true);

  static const VerificationMeta _longitudeMeta = VerificationMeta('longitude');
  @override
  late final GeneratedColumn<double> longitude =
      GeneratedColumn<double>(
          'longitude', aliasedName, false,
          type: DriftSqlType.double,
          requiredDuringInsert: true);

  static const VerificationMeta _weatherTypeMeta = VerificationMeta('weatherType');
  @override
  late final GeneratedColumn<String> weatherType =
      GeneratedColumn<String>(
          'weather_type', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _dataMeta = VerificationMeta('data');
  @override
  late final GeneratedColumn<String> data =
      GeneratedColumn<String>(
          'data', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _fetchedAtMeta = VerificationMeta('fetchedAt');
  @override
  late final GeneratedColumn<DateTime> fetchedAt =
      GeneratedColumn<DateTime>(
          'fetched_at', aliasedName, false,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: true);

  static const VerificationMeta _expiresAtMeta = VerificationMeta('expiresAt');
  @override
  late final GeneratedColumn<DateTime> expiresAt =
      GeneratedColumn<DateTime>(
          'expires_at', aliasedName, false,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: true);

  static const VerificationMeta _forecastDateMeta = VerificationMeta('forecastDate');
  @override
  late final GeneratedColumn<DateTime> forecastDate =
      GeneratedColumn<DateTime>(
          'forecast_date', aliasedName, true,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: false);

  @override
  List<GeneratedColumn> get $columns => [id, tenantId, locationId, latitude, longitude, weatherType, data, fetchedAt, expiresAt, forecastDate];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String \$name = 'weather_cache';

  @override
  VerificationContext validateIntegrity(Insertable<WeatherCacheData> instance,
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
    if (data.containsKey('location_id')) {
      context.handle(_locationIdMeta,
          locationId.isAcceptableOrUnknown(data['location_id']!, _locationIdMeta));
    }
    else if (isInserting) {
      context.addError(_locationIdMeta,
          const VerificationError('locationId must be provided when inserting.'));
    }
    if (data.containsKey('latitude')) {
      context.handle(_latitudeMeta,
          latitude.isAcceptableOrUnknown(data['latitude']!, _latitudeMeta));
    }
    else if (isInserting) {
      context.addError(_latitudeMeta,
          const VerificationError('latitude must be provided when inserting.'));
    }
    if (data.containsKey('longitude')) {
      context.handle(_longitudeMeta,
          longitude.isAcceptableOrUnknown(data['longitude']!, _longitudeMeta));
    }
    else if (isInserting) {
      context.addError(_longitudeMeta,
          const VerificationError('longitude must be provided when inserting.'));
    }
    if (data.containsKey('weather_type')) {
      context.handle(_weatherTypeMeta,
          weatherType.isAcceptableOrUnknown(data['weather_type']!, _weatherTypeMeta));
    }
    else if (isInserting) {
      context.addError(_weatherTypeMeta,
          const VerificationError('weatherType must be provided when inserting.'));
    }
    if (data.containsKey('data')) {
      context.handle(_dataMeta,
          data.isAcceptableOrUnknown(data['data']!, _dataMeta));
    }
    else if (isInserting) {
      context.addError(_dataMeta,
          const VerificationError('data must be provided when inserting.'));
    }
    if (data.containsKey('fetched_at')) {
      context.handle(_fetchedAtMeta,
          fetchedAt.isAcceptableOrUnknown(data['fetched_at']!, _fetchedAtMeta));
    }
    else if (isInserting) {
      context.addError(_fetchedAtMeta,
          const VerificationError('fetchedAt must be provided when inserting.'));
    }
    if (data.containsKey('expires_at')) {
      context.handle(_expiresAtMeta,
          expiresAt.isAcceptableOrUnknown(data['expires_at']!, _expiresAtMeta));
    }
    else if (isInserting) {
      context.addError(_expiresAtMeta,
          const VerificationError('expiresAt must be provided when inserting.'));
    }
    if (data.containsKey('forecast_date')) {
      context.handle(_forecastDateMeta,
          forecastDate.isAcceptableOrUnknown(data['forecast_date']!, _forecastDateMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};

  @override
  WeatherCacheData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '\$tablePrefix.' : '';
    return WeatherCacheData(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['\${effectivePrefix}id'])!,
      tenantId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}tenant_id'])!,
      locationId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}location_id'])!,
      latitude: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}latitude'])!,
      longitude: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}longitude'])!,
      weatherType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}weather_type'])!,
      data: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}data'])!,
      fetchedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}fetched_at'])!,
      expiresAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}expires_at'])!,
      forecastDate: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}forecast_date']),
    );
  }

  @override
  \$WeatherCacheTable createAlias(String alias) {
    return \$WeatherCacheTable(attachedDatabase, alias);
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

  const WeatherAlert({
    this.id,
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
    this.isRead,
    this.isActive,
    this.createdAt,
  });

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

  factory WeatherAlert.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return WeatherAlert(
      id: serializer.fromJson<int>(json['id']),
      tenantId: serializer.fromJson<String>(json['tenant_id']),
      alertId: serializer.fromJson<String>(json['alert_id']),
      alertType: serializer.fromJson<String>(json['alert_type']),
      severity: serializer.fromJson<String>(json['severity']),
      title: serializer.fromJson<String>(json['title']),
      titleAr: serializer.fromJson<String?>(json['title_ar']),
      description: serializer.fromJson<String>(json['description']),
      descriptionAr: serializer.fromJson<String?>(json['description_ar']),
      latitude: serializer.fromJson<double?>(json['latitude']),
      longitude: serializer.fromJson<double?>(json['longitude']),
      radius: serializer.fromJson<double?>(json['radius']),
      startsAt: serializer.fromJson<DateTime>(json['starts_at']),
      expiresAt: serializer.fromJson<DateTime>(json['expires_at']),
      isRead: serializer.fromJson<bool>(json['is_read']),
      isActive: serializer.fromJson<bool>(json['is_active']),
      createdAt: serializer.fromJson<DateTime>(json['created_at']),
    );
  }

  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'tenant_id': serializer.toJson<String>(tenantId),
      'alert_id': serializer.toJson<String>(alertId),
      'alert_type': serializer.toJson<String>(alertType),
      'severity': serializer.toJson<String>(severity),
      'title': serializer.toJson<String>(title),
      'title_ar': serializer.toJson<String?>(titleAr),
      'description': serializer.toJson<String>(description),
      'description_ar': serializer.toJson<String?>(descriptionAr),
      'latitude': serializer.toJson<double?>(latitude),
      'longitude': serializer.toJson<double?>(longitude),
      'radius': serializer.toJson<double?>(radius),
      'starts_at': serializer.toJson<DateTime>(startsAt),
      'expires_at': serializer.toJson<DateTime>(expiresAt),
      'is_read': serializer.toJson<bool>(isRead),
      'is_active': serializer.toJson<bool>(isActive),
      'created_at': serializer.toJson<DateTime>(createdAt),
    };
  }

  WeatherAlert copyWith({
    int? id,
    String? tenantId,
    String? alertId,
    String? alertType,
    String? severity,
    String? title,
    Value<String> titleAr = const Value.absent(),
    String? description,
    Value<String> descriptionAr = const Value.absent(),
    Value<double> latitude = const Value.absent(),
    Value<double> longitude = const Value.absent(),
    Value<double> radius = const Value.absent(),
    DateTime? startsAt,
    DateTime? expiresAt,
    bool? isRead,
    bool? isActive,
    DateTime? createdAt,
  }) {
    return WeatherAlert(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      alertId: alertId ?? this.alertId,
      alertType: alertType ?? this.alertType,
      severity: severity ?? this.severity,
      title: title ?? this.title,
      titleAr: titleAr.present ? titleAr.value : this.titleAr,
      description: description ?? this.description,
      descriptionAr: descriptionAr.present ? descriptionAr.value : this.descriptionAr,
      latitude: latitude.present ? latitude.value : this.latitude,
      longitude: longitude.present ? longitude.value : this.longitude,
      radius: radius.present ? radius.value : this.radius,
      startsAt: startsAt ?? this.startsAt,
      expiresAt: expiresAt ?? this.expiresAt,
      isRead: isRead ?? this.isRead,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('WeatherAlert(')
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('alertId: ${alertId}, ')
          ..write('alertType: ${alertType}, ')
          ..write('severity: ${severity}, ')
          ..write('title: ${title}, ')
          ..write('titleAr: ${titleAr}, ')
          ..write('description: ${description}, ')
          ..write('descriptionAr: ${descriptionAr}, ')
          ..write('latitude: ${latitude}, ')
          ..write('longitude: ${longitude}, ')
          ..write('radius: ${radius}, ')
          ..write('startsAt: ${startsAt}, ')
          ..write('expiresAt: ${expiresAt}, ')
          ..write('isRead: ${isRead}, ')
          ..write('isActive: ${isActive}, ')
          ..write('createdAt: ${createdAt}')
          ..write(')')
      ).toString();
  }

  @override
  int get hashCode => Object.hash(id, tenantId, alertId, alertType, severity, title, titleAr, description, descriptionAr, latitude, longitude, radius, startsAt, expiresAt, isRead, isActive, createdAt);

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
          other.createdAt == this.createdAt)
  ;
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
  })
      : tenantId = Value(tenantId),
        alertId = Value(alertId),
        alertType = Value(alertType),
        severity = Value(severity),
        title = Value(title),
        description = Value(description),
        startsAt = Value(startsAt),
        expiresAt = Value(expiresAt);

  static Insertable<WeatherAlert> custom({
    Expression<dynamic>? id,
    Expression<dynamic>? tenantId,
    Expression<dynamic>? alertId,
    Expression<dynamic>? alertType,
    Expression<dynamic>? severity,
    Expression<dynamic>? title,
    Expression<dynamic>? titleAr,
    Expression<dynamic>? description,
    Expression<dynamic>? descriptionAr,
    Expression<dynamic>? latitude,
    Expression<dynamic>? longitude,
    Expression<dynamic>? radius,
    Expression<dynamic>? startsAt,
    Expression<dynamic>? expiresAt,
    Expression<dynamic>? isRead,
    Expression<dynamic>? isActive,
    Expression<dynamic>? createdAt,
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

  WeatherAlertsCompanion copyWith({
    Value<int>? id,
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
    Value<DateTime>? createdAt,
  }) {
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
      map['title_ar'] = Variable<String?>(titleAr.value);
    }
    if (description.present) {
      map['description'] = Variable<String>(description.value);
    }
    if (descriptionAr.present) {
      map['description_ar'] = Variable<String?>(descriptionAr.value);
    }
    if (latitude.present) {
      map['latitude'] = Variable<double?>(latitude.value);
    }
    if (longitude.present) {
      map['longitude'] = Variable<double?>(longitude.value);
    }
    if (radius.present) {
      map['radius'] = Variable<double?>(radius.value);
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
          ..write('id: ${id}, ')
          ..write('tenantId: ${tenantId}, ')
          ..write('alertId: ${alertId}, ')
          ..write('alertType: ${alertType}, ')
          ..write('severity: ${severity}, ')
          ..write('title: ${title}, ')
          ..write('titleAr: ${titleAr}, ')
          ..write('description: ${description}, ')
          ..write('descriptionAr: ${descriptionAr}, ')
          ..write('latitude: ${latitude}, ')
          ..write('longitude: ${longitude}, ')
          ..write('radius: ${radius}, ')
          ..write('startsAt: ${startsAt}, ')
          ..write('expiresAt: ${expiresAt}, ')
          ..write('isRead: ${isRead}, ')
          ..write('isActive: ${isActive}, ')
          ..write('createdAt: ${createdAt}')
          ..write(')')
      ).toString();
  }
}

class \$WeatherAlertsTable extends WeatherAlerts
    with TableInfo<\$WeatherAlertsTable, WeatherAlert> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  \$WeatherAlertsTable(this.attachedDatabase, [this._alias]);

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

  static const VerificationMeta _alertIdMeta = VerificationMeta('alertId');
  @override
  late final GeneratedColumn<String> alertId =
      GeneratedColumn<String>(
          'alert_id', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _alertTypeMeta = VerificationMeta('alertType');
  @override
  late final GeneratedColumn<String> alertType =
      GeneratedColumn<String>(
          'alert_type', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _severityMeta = VerificationMeta('severity');
  @override
  late final GeneratedColumn<String> severity =
      GeneratedColumn<String>(
          'severity', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _titleMeta = VerificationMeta('title');
  @override
  late final GeneratedColumn<String> title =
      GeneratedColumn<String>(
          'title', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _titleArMeta = VerificationMeta('titleAr');
  @override
  late final GeneratedColumn<String> titleAr =
      GeneratedColumn<String>(
          'title_ar', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _descriptionMeta = VerificationMeta('description');
  @override
  late final GeneratedColumn<String> description =
      GeneratedColumn<String>(
          'description', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _descriptionArMeta = VerificationMeta('descriptionAr');
  @override
  late final GeneratedColumn<String> descriptionAr =
      GeneratedColumn<String>(
          'description_ar', aliasedName, true,
          type: DriftSqlType.string,
          requiredDuringInsert: false);

  static const VerificationMeta _latitudeMeta = VerificationMeta('latitude');
  @override
  late final GeneratedColumn<double> latitude =
      GeneratedColumn<double>(
          'latitude', aliasedName, true,
          type: DriftSqlType.double,
          requiredDuringInsert: false);

  static const VerificationMeta _longitudeMeta = VerificationMeta('longitude');
  @override
  late final GeneratedColumn<double> longitude =
      GeneratedColumn<double>(
          'longitude', aliasedName, true,
          type: DriftSqlType.double,
          requiredDuringInsert: false);

  static const VerificationMeta _radiusMeta = VerificationMeta('radius');
  @override
  late final GeneratedColumn<double> radius =
      GeneratedColumn<double>(
          'radius', aliasedName, true,
          type: DriftSqlType.double,
          requiredDuringInsert: false);

  static const VerificationMeta _startsAtMeta = VerificationMeta('startsAt');
  @override
  late final GeneratedColumn<DateTime> startsAt =
      GeneratedColumn<DateTime>(
          'starts_at', aliasedName, false,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: true);

  static const VerificationMeta _expiresAtMeta = VerificationMeta('expiresAt');
  @override
  late final GeneratedColumn<DateTime> expiresAt =
      GeneratedColumn<DateTime>(
          'expires_at', aliasedName, false,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: true);

  static const VerificationMeta _isReadMeta = VerificationMeta('isRead');
  @override
  late final GeneratedColumn<bool> isRead =
      GeneratedColumn<bool>(
          'is_read', aliasedName, false,
          defaultValue: const Constant(false),
          type: DriftSqlType.bool,
          requiredDuringInsert: false);

  static const VerificationMeta _isActiveMeta = VerificationMeta('isActive');
  @override
  late final GeneratedColumn<bool> isActive =
      GeneratedColumn<bool>(
          'is_active', aliasedName, false,
          defaultValue: const Constant(true),
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
  List<GeneratedColumn> get $columns => [id, tenantId, alertId, alertType, severity, title, titleAr, description, descriptionAr, latitude, longitude, radius, startsAt, expiresAt, isRead, isActive, createdAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String \$name = 'weather_alerts';

  @override
  VerificationContext validateIntegrity(Insertable<WeatherAlert> instance,
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
    if (data.containsKey('alert_id')) {
      context.handle(_alertIdMeta,
          alertId.isAcceptableOrUnknown(data['alert_id']!, _alertIdMeta));
    }
    else if (isInserting) {
      context.addError(_alertIdMeta,
          const VerificationError('alertId must be provided when inserting.'));
    }
    if (data.containsKey('alert_type')) {
      context.handle(_alertTypeMeta,
          alertType.isAcceptableOrUnknown(data['alert_type']!, _alertTypeMeta));
    }
    else if (isInserting) {
      context.addError(_alertTypeMeta,
          const VerificationError('alertType must be provided when inserting.'));
    }
    if (data.containsKey('severity')) {
      context.handle(_severityMeta,
          severity.isAcceptableOrUnknown(data['severity']!, _severityMeta));
    }
    else if (isInserting) {
      context.addError(_severityMeta,
          const VerificationError('severity must be provided when inserting.'));
    }
    if (data.containsKey('title')) {
      context.handle(_titleMeta,
          title.isAcceptableOrUnknown(data['title']!, _titleMeta));
    }
    else if (isInserting) {
      context.addError(_titleMeta,
          const VerificationError('title must be provided when inserting.'));
    }
    if (data.containsKey('title_ar')) {
      context.handle(_titleArMeta,
          titleAr.isAcceptableOrUnknown(data['title_ar']!, _titleArMeta));
    }
    if (data.containsKey('description')) {
      context.handle(_descriptionMeta,
          description.isAcceptableOrUnknown(data['description']!, _descriptionMeta));
    }
    else if (isInserting) {
      context.addError(_descriptionMeta,
          const VerificationError('description must be provided when inserting.'));
    }
    if (data.containsKey('description_ar')) {
      context.handle(_descriptionArMeta,
          descriptionAr.isAcceptableOrUnknown(data['description_ar']!, _descriptionArMeta));
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
    }
    else if (isInserting) {
      context.addError(_startsAtMeta,
          const VerificationError('startsAt must be provided when inserting.'));
    }
    if (data.containsKey('expires_at')) {
      context.handle(_expiresAtMeta,
          expiresAt.isAcceptableOrUnknown(data['expires_at']!, _expiresAtMeta));
    }
    else if (isInserting) {
      context.addError(_expiresAtMeta,
          const VerificationError('expiresAt must be provided when inserting.'));
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
    final effectivePrefix = tablePrefix != null ? '\$tablePrefix.' : '';
    return WeatherAlert(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['\${effectivePrefix}id'])!,
      tenantId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}tenant_id'])!,
      alertId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}alert_id'])!,
      alertType: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}alert_type'])!,
      severity: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}severity'])!,
      title: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}title'])!,
      titleAr: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}title_ar']),
      description: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}description'])!,
      descriptionAr: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}description_ar']),
      latitude: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}latitude']),
      longitude: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}longitude']),
      radius: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}radius']),
      startsAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}starts_at'])!,
      expiresAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}expires_at'])!,
      isRead: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['\${effectivePrefix}is_read'])!,
      isActive: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['\${effectivePrefix}is_active'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}created_at'])!,
    );
  }

  @override
  \$WeatherAlertsTable createAlias(String alias) {
    return \$WeatherAlertsTable(attachedDatabase, alias);
  }
}

class WeatherStatistic extends DataClass implements Insertable<WeatherStatistic> {
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

  const WeatherStatistic({
    this.id,
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
    this.growingDegreeDays,
  });

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

  factory WeatherStatistic.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return WeatherStatistic(
      id: serializer.fromJson<int>(json['id']),
      fieldId: serializer.fromJson<String>(json['field_id']),
      date: serializer.fromJson<DateTime>(json['date']),
      tempMin: serializer.fromJson<double?>(json['temp_min']),
      tempMax: serializer.fromJson<double?>(json['temp_max']),
      tempAvg: serializer.fromJson<double?>(json['temp_avg']),
      humidity: serializer.fromJson<double?>(json['humidity']),
      precipitation: serializer.fromJson<double?>(json['precipitation']),
      windSpeed: serializer.fromJson<double?>(json['wind_speed']),
      solarRadiation: serializer.fromJson<double?>(json['solar_radiation']),
      evapotranspiration: serializer.fromJson<double?>(json['evapotranspiration']),
      growingDegreeDays: serializer.fromJson<int?>(json['growing_degree_days']),
    );
  }

  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'field_id': serializer.toJson<String>(fieldId),
      'date': serializer.toJson<DateTime>(date),
      'temp_min': serializer.toJson<double?>(tempMin),
      'temp_max': serializer.toJson<double?>(tempMax),
      'temp_avg': serializer.toJson<double?>(tempAvg),
      'humidity': serializer.toJson<double?>(humidity),
      'precipitation': serializer.toJson<double?>(precipitation),
      'wind_speed': serializer.toJson<double?>(windSpeed),
      'solar_radiation': serializer.toJson<double?>(solarRadiation),
      'evapotranspiration': serializer.toJson<double?>(evapotranspiration),
      'growing_degree_days': serializer.toJson<int?>(growingDegreeDays),
    };
  }

  WeatherStatistic copyWith({
    int? id,
    String? fieldId,
    DateTime? date,
    Value<double> tempMin = const Value.absent(),
    Value<double> tempMax = const Value.absent(),
    Value<double> tempAvg = const Value.absent(),
    Value<double> humidity = const Value.absent(),
    Value<double> precipitation = const Value.absent(),
    Value<double> windSpeed = const Value.absent(),
    Value<double> solarRadiation = const Value.absent(),
    Value<double> evapotranspiration = const Value.absent(),
    Value<int> growingDegreeDays = const Value.absent(),
  }) {
    return WeatherStatistic(
      id: id ?? this.id,
      fieldId: fieldId ?? this.fieldId,
      date: date ?? this.date,
      tempMin: tempMin.present ? tempMin.value : this.tempMin,
      tempMax: tempMax.present ? tempMax.value : this.tempMax,
      tempAvg: tempAvg.present ? tempAvg.value : this.tempAvg,
      humidity: humidity.present ? humidity.value : this.humidity,
      precipitation: precipitation.present ? precipitation.value : this.precipitation,
      windSpeed: windSpeed.present ? windSpeed.value : this.windSpeed,
      solarRadiation: solarRadiation.present ? solarRadiation.value : this.solarRadiation,
      evapotranspiration: evapotranspiration.present ? evapotranspiration.value : this.evapotranspiration,
      growingDegreeDays: growingDegreeDays.present ? growingDegreeDays.value : this.growingDegreeDays,
    );
  }

  @override
  String toString() {
    return (StringBuffer('WeatherStatistic(')
          ..write('id: ${id}, ')
          ..write('fieldId: ${fieldId}, ')
          ..write('date: ${date}, ')
          ..write('tempMin: ${tempMin}, ')
          ..write('tempMax: ${tempMax}, ')
          ..write('tempAvg: ${tempAvg}, ')
          ..write('humidity: ${humidity}, ')
          ..write('precipitation: ${precipitation}, ')
          ..write('windSpeed: ${windSpeed}, ')
          ..write('solarRadiation: ${solarRadiation}, ')
          ..write('evapotranspiration: ${evapotranspiration}, ')
          ..write('growingDegreeDays: ${growingDegreeDays}')
          ..write(')')
      ).toString();
  }

  @override
  int get hashCode => Object.hash(id, fieldId, date, tempMin, tempMax, tempAvg, humidity, precipitation, windSpeed, solarRadiation, evapotranspiration, growingDegreeDays);

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
          other.growingDegreeDays == this.growingDegreeDays)
  ;
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
    Value<double?> tempMin = const Value.absent(),
    Value<double?> tempMax = const Value.absent(),
    Value<double?> tempAvg = const Value.absent(),
    Value<double?> humidity = const Value.absent(),
    Value<double?> precipitation = const Value.absent(),
    Value<double?> windSpeed = const Value.absent(),
    Value<double?> solarRadiation = const Value.absent(),
    Value<double?> evapotranspiration = const Value.absent(),
    Value<int?> growingDegreeDays = const Value.absent(),
  })
      : fieldId = Value(fieldId),
        date = Value(date);

  static Insertable<WeatherStatistic> custom({
    Expression<dynamic>? id,
    Expression<dynamic>? fieldId,
    Expression<dynamic>? date,
    Expression<dynamic>? tempMin,
    Expression<dynamic>? tempMax,
    Expression<dynamic>? tempAvg,
    Expression<dynamic>? humidity,
    Expression<dynamic>? precipitation,
    Expression<dynamic>? windSpeed,
    Expression<dynamic>? solarRadiation,
    Expression<dynamic>? evapotranspiration,
    Expression<dynamic>? growingDegreeDays,
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

  WeatherStatisticsCompanion copyWith({
    Value<int>? id,
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
    Value<int?>? growingDegreeDays,
  }) {
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
      map['temp_min'] = Variable<double?>(tempMin.value);
    }
    if (tempMax.present) {
      map['temp_max'] = Variable<double?>(tempMax.value);
    }
    if (tempAvg.present) {
      map['temp_avg'] = Variable<double?>(tempAvg.value);
    }
    if (humidity.present) {
      map['humidity'] = Variable<double?>(humidity.value);
    }
    if (precipitation.present) {
      map['precipitation'] = Variable<double?>(precipitation.value);
    }
    if (windSpeed.present) {
      map['wind_speed'] = Variable<double?>(windSpeed.value);
    }
    if (solarRadiation.present) {
      map['solar_radiation'] = Variable<double?>(solarRadiation.value);
    }
    if (evapotranspiration.present) {
      map['evapotranspiration'] = Variable<double?>(evapotranspiration.value);
    }
    if (growingDegreeDays.present) {
      map['growing_degree_days'] = Variable<int?>(growingDegreeDays.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('WeatherStatisticsCompanion(')
          ..write('id: ${id}, ')
          ..write('fieldId: ${fieldId}, ')
          ..write('date: ${date}, ')
          ..write('tempMin: ${tempMin}, ')
          ..write('tempMax: ${tempMax}, ')
          ..write('tempAvg: ${tempAvg}, ')
          ..write('humidity: ${humidity}, ')
          ..write('precipitation: ${precipitation}, ')
          ..write('windSpeed: ${windSpeed}, ')
          ..write('solarRadiation: ${solarRadiation}, ')
          ..write('evapotranspiration: ${evapotranspiration}, ')
          ..write('growingDegreeDays: ${growingDegreeDays}')
          ..write(')')
      ).toString();
  }
}

class \$WeatherStatisticsTable extends WeatherStatistics
    with TableInfo<\$WeatherStatisticsTable, WeatherStatistic> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  \$WeatherStatisticsTable(this.attachedDatabase, [this._alias]);

  static const VerificationMeta _idMeta = VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id =
      GeneratedColumn<int>(
          'id', aliasedName, false,
          hasAutoIncrement: true,
          type: DriftSqlType.int,
          requiredDuringInsert: false);

  static const VerificationMeta _fieldIdMeta = VerificationMeta('fieldId');
  @override
  late final GeneratedColumn<String> fieldId =
      GeneratedColumn<String>(
          'field_id', aliasedName, false,
          type: DriftSqlType.string,
          requiredDuringInsert: true);

  static const VerificationMeta _dateMeta = VerificationMeta('date');
  @override
  late final GeneratedColumn<DateTime> date =
      GeneratedColumn<DateTime>(
          'date', aliasedName, false,
          type: DriftSqlType.dateTime,
          requiredDuringInsert: true);

  static const VerificationMeta _tempMinMeta = VerificationMeta('tempMin');
  @override
  late final GeneratedColumn<double> tempMin =
      GeneratedColumn<double>(
          'temp_min', aliasedName, true,
          type: DriftSqlType.double,
          requiredDuringInsert: false);

  static const VerificationMeta _tempMaxMeta = VerificationMeta('tempMax');
  @override
  late final GeneratedColumn<double> tempMax =
      GeneratedColumn<double>(
          'temp_max', aliasedName, true,
          type: DriftSqlType.double,
          requiredDuringInsert: false);

  static const VerificationMeta _tempAvgMeta = VerificationMeta('tempAvg');
  @override
  late final GeneratedColumn<double> tempAvg =
      GeneratedColumn<double>(
          'temp_avg', aliasedName, true,
          type: DriftSqlType.double,
          requiredDuringInsert: false);

  static const VerificationMeta _humidityMeta = VerificationMeta('humidity');
  @override
  late final GeneratedColumn<double> humidity =
      GeneratedColumn<double>(
          'humidity', aliasedName, true,
          type: DriftSqlType.double,
          requiredDuringInsert: false);

  static const VerificationMeta _precipitationMeta = VerificationMeta('precipitation');
  @override
  late final GeneratedColumn<double> precipitation =
      GeneratedColumn<double>(
          'precipitation', aliasedName, true,
          type: DriftSqlType.double,
          requiredDuringInsert: false);

  static const VerificationMeta _windSpeedMeta = VerificationMeta('windSpeed');
  @override
  late final GeneratedColumn<double> windSpeed =
      GeneratedColumn<double>(
          'wind_speed', aliasedName, true,
          type: DriftSqlType.double,
          requiredDuringInsert: false);

  static const VerificationMeta _solarRadiationMeta = VerificationMeta('solarRadiation');
  @override
  late final GeneratedColumn<double> solarRadiation =
      GeneratedColumn<double>(
          'solar_radiation', aliasedName, true,
          type: DriftSqlType.double,
          requiredDuringInsert: false);

  static const VerificationMeta _evapotranspirationMeta = VerificationMeta('evapotranspiration');
  @override
  late final GeneratedColumn<double> evapotranspiration =
      GeneratedColumn<double>(
          'evapotranspiration', aliasedName, true,
          type: DriftSqlType.double,
          requiredDuringInsert: false);

  static const VerificationMeta _growingDegreeDaysMeta = VerificationMeta('growingDegreeDays');
  @override
  late final GeneratedColumn<int> growingDegreeDays =
      GeneratedColumn<int>(
          'growing_degree_days', aliasedName, true,
          type: DriftSqlType.int,
          requiredDuringInsert: false);

  @override
  List<GeneratedColumn> get $columns => [id, fieldId, date, tempMin, tempMax, tempAvg, humidity, precipitation, windSpeed, solarRadiation, evapotranspiration, growingDegreeDays];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String \$name = 'weather_statistics';

  @override
  VerificationContext validateIntegrity(Insertable<WeatherStatistic> instance,
      {{bool isInserting = false}}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta,
          id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('field_id')) {
      context.handle(_fieldIdMeta,
          fieldId.isAcceptableOrUnknown(data['field_id']!, _fieldIdMeta));
    }
    else if (isInserting) {
      context.addError(_fieldIdMeta,
          const VerificationError('fieldId must be provided when inserting.'));
    }
    if (data.containsKey('date')) {
      context.handle(_dateMeta,
          date.isAcceptableOrUnknown(data['date']!, _dateMeta));
    }
    else if (isInserting) {
      context.addError(_dateMeta,
          const VerificationError('date must be provided when inserting.'));
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
      context.handle(_precipitationMeta,
          precipitation.isAcceptableOrUnknown(data['precipitation']!, _precipitationMeta));
    }
    if (data.containsKey('wind_speed')) {
      context.handle(_windSpeedMeta,
          windSpeed.isAcceptableOrUnknown(data['wind_speed']!, _windSpeedMeta));
    }
    if (data.containsKey('solar_radiation')) {
      context.handle(_solarRadiationMeta,
          solarRadiation.isAcceptableOrUnknown(data['solar_radiation']!, _solarRadiationMeta));
    }
    if (data.containsKey('evapotranspiration')) {
      context.handle(_evapotranspirationMeta,
          evapotranspiration.isAcceptableOrUnknown(data['evapotranspiration']!, _evapotranspirationMeta));
    }
    if (data.containsKey('growing_degree_days')) {
      context.handle(_growingDegreeDaysMeta,
          growingDegreeDays.isAcceptableOrUnknown(data['growing_degree_days']!, _growingDegreeDaysMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};

  @override
  WeatherStatistic map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '\$tablePrefix.' : '';
    return WeatherStatistic(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['\${effectivePrefix}id'])!,
      fieldId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['\${effectivePrefix}field_id'])!,
      date: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['\${effectivePrefix}date'])!,
      tempMin: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}temp_min']),
      tempMax: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}temp_max']),
      tempAvg: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}temp_avg']),
      humidity: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}humidity']),
      precipitation: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}precipitation']),
      windSpeed: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}wind_speed']),
      solarRadiation: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}solar_radiation']),
      evapotranspiration: attachedDatabase.typeMapping
          .read(DriftSqlType.double, data['\${effectivePrefix}evapotranspiration']),
      growingDegreeDays: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['\${effectivePrefix}growing_degree_days']),
    );
  }

  @override
  \$WeatherStatisticsTable createAlias(String alias) {
    return \$WeatherStatisticsTable(attachedDatabase, alias);
  }
}

abstract class _\$WeatherDaoTestDatabase extends GeneratedDatabase {
  _\$WeatherDaoTestDatabase(QueryExecutor e) : super(e);

  late final \$WeatherCacheTable weatherCache = \$WeatherCacheTable(this);
  late final \$WeatherAlertsTable weatherAlerts = \$WeatherAlertsTable(this);
  late final \$WeatherStatisticsTable weatherStatistics = \$WeatherStatisticsTable(this);

  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
    weatherCache,
    weatherAlerts,
    weatherStatistics,
  ];
}
