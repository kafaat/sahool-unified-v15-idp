// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'local_log.dart';

// **************************************************************************
// IsarCollectionGenerator
// **************************************************************************

// coverage:ignore-file
// ignore_for_file: duplicate_ignore, non_constant_identifier_names, constant_identifier_names, invalid_use_of_protected_member, unnecessary_cast, prefer_const_constructors, lines_longer_than_80_chars, require_trailing_commas, inference_failure_on_function_invocation, unnecessary_parenthesis, unnecessary_raw_strings, unnecessary_null_checks, join_return_with_assignment, prefer_final_locals, avoid_js_rounded_ints, avoid_positional_boolean_parameters, always_specify_types

extension GetLocalResearchLogCollection on Isar {
  IsarCollection<LocalResearchLog> get localResearchLogs => this.collection();
}

const LocalResearchLogSchema = CollectionSchema(
  name: r'LocalResearchLog',
  id: -3670137861275249217,
  properties: {
    r'category': PropertySchema(
      id: 0,
      name: r'category',
      type: IsarType.string,
    ),
    r'createdAt': PropertySchema(
      id: 1,
      name: r'createdAt',
      type: IsarType.dateTime,
    ),
    r'deviceId': PropertySchema(
      id: 2,
      name: r'deviceId',
      type: IsarType.string,
    ),
    r'experimentId': PropertySchema(
      id: 3,
      name: r'experimentId',
      type: IsarType.string,
    ),
    r'hash': PropertySchema(
      id: 4,
      name: r'hash',
      type: IsarType.string,
    ),
    r'lastSyncAttempt': PropertySchema(
      id: 5,
      name: r'lastSyncAttempt',
      type: IsarType.dateTime,
    ),
    r'latitude': PropertySchema(
      id: 6,
      name: r'latitude',
      type: IsarType.double,
    ),
    r'localAttachmentPaths': PropertySchema(
      id: 7,
      name: r'localAttachmentPaths',
      type: IsarType.stringList,
    ),
    r'localPhotoPaths': PropertySchema(
      id: 8,
      name: r'localPhotoPaths',
      type: IsarType.stringList,
    ),
    r'logDate': PropertySchema(
      id: 9,
      name: r'logDate',
      type: IsarType.dateTime,
    ),
    r'logTime': PropertySchema(
      id: 10,
      name: r'logTime',
      type: IsarType.string,
    ),
    r'longitude': PropertySchema(
      id: 11,
      name: r'longitude',
      type: IsarType.double,
    ),
    r'measurementsJson': PropertySchema(
      id: 12,
      name: r'measurementsJson',
      type: IsarType.string,
    ),
    r'notes': PropertySchema(
      id: 13,
      name: r'notes',
      type: IsarType.string,
    ),
    r'notesAr': PropertySchema(
      id: 14,
      name: r'notesAr',
      type: IsarType.string,
    ),
    r'offlineId': PropertySchema(
      id: 15,
      name: r'offlineId',
      type: IsarType.string,
    ),
    r'plotId': PropertySchema(
      id: 16,
      name: r'plotId',
      type: IsarType.string,
    ),
    r'recordedBy': PropertySchema(
      id: 17,
      name: r'recordedBy',
      type: IsarType.string,
    ),
    r'serverId': PropertySchema(
      id: 18,
      name: r'serverId',
      type: IsarType.string,
    ),
    r'shouldRetrySync': PropertySchema(
      id: 19,
      name: r'shouldRetrySync',
      type: IsarType.bool,
    ),
    r'syncAttempts': PropertySchema(
      id: 20,
      name: r'syncAttempts',
      type: IsarType.long,
    ),
    r'syncError': PropertySchema(
      id: 21,
      name: r'syncError',
      type: IsarType.string,
    ),
    r'syncStatus': PropertySchema(
      id: 22,
      name: r'syncStatus',
      type: IsarType.string,
      enumMap: _LocalResearchLogsyncStatusEnumValueMap,
    ),
    r'title': PropertySchema(
      id: 23,
      name: r'title',
      type: IsarType.string,
    ),
    r'titleAr': PropertySchema(
      id: 24,
      name: r'titleAr',
      type: IsarType.string,
    ),
    r'treatmentId': PropertySchema(
      id: 25,
      name: r'treatmentId',
      type: IsarType.string,
    ),
    r'updatedAt': PropertySchema(
      id: 26,
      name: r'updatedAt',
      type: IsarType.dateTime,
    ),
    r'uploadedAttachmentUrls': PropertySchema(
      id: 27,
      name: r'uploadedAttachmentUrls',
      type: IsarType.stringList,
    ),
    r'uploadedPhotoUrls': PropertySchema(
      id: 28,
      name: r'uploadedPhotoUrls',
      type: IsarType.stringList,
    ),
    r'weatherConditionsJson': PropertySchema(
      id: 29,
      name: r'weatherConditionsJson',
      type: IsarType.string,
    )
  },
  estimateSize: _localResearchLogEstimateSize,
  serialize: _localResearchLogSerialize,
  deserialize: _localResearchLogDeserialize,
  deserializeProp: _localResearchLogDeserializeProp,
  idName: r'id',
  indexes: {
    r'offlineId': IndexSchema(
      id: 5429884731139810101,
      name: r'offlineId',
      unique: true,
      replace: false,
      properties: [
        IndexPropertySchema(
          name: r'offlineId',
          type: IndexType.hash,
          caseSensitive: true,
        )
      ],
    ),
    r'experimentId': IndexSchema(
      id: -2596400929068244875,
      name: r'experimentId',
      unique: false,
      replace: false,
      properties: [
        IndexPropertySchema(
          name: r'experimentId',
          type: IndexType.hash,
          caseSensitive: true,
        )
      ],
    ),
    r'logDate': IndexSchema(
      id: 8404824101822155242,
      name: r'logDate',
      unique: false,
      replace: false,
      properties: [
        IndexPropertySchema(
          name: r'logDate',
          type: IndexType.value,
          caseSensitive: false,
        )
      ],
    ),
    r'category': IndexSchema(
      id: -7560358558326323820,
      name: r'category',
      unique: false,
      replace: false,
      properties: [
        IndexPropertySchema(
          name: r'category',
          type: IndexType.hash,
          caseSensitive: true,
        )
      ],
    ),
    r'syncStatus': IndexSchema(
      id: 8239539375045684509,
      name: r'syncStatus',
      unique: false,
      replace: false,
      properties: [
        IndexPropertySchema(
          name: r'syncStatus',
          type: IndexType.hash,
          caseSensitive: true,
        )
      ],
    )
  },
  links: {},
  embeddedSchemas: {},
  getId: _localResearchLogGetId,
  getLinks: _localResearchLogGetLinks,
  attach: _localResearchLogAttach,
  version: '3.1.0+1',
);

int _localResearchLogEstimateSize(
  LocalResearchLog object,
  List<int> offsets,
  Map<Type, List<int>> allOffsets,
) {
  var bytesCount = offsets.last;
  bytesCount += 3 + object.category.length * 3;
  {
    final value = object.deviceId;
    if (value != null) {
      bytesCount += 3 + value.length * 3;
    }
  }
  bytesCount += 3 + object.experimentId.length * 3;
  {
    final value = object.hash;
    if (value != null) {
      bytesCount += 3 + value.length * 3;
    }
  }
  bytesCount += 3 + object.localAttachmentPaths.length * 3;
  {
    for (var i = 0; i < object.localAttachmentPaths.length; i++) {
      final value = object.localAttachmentPaths[i];
      bytesCount += value.length * 3;
    }
  }
  bytesCount += 3 + object.localPhotoPaths.length * 3;
  {
    for (var i = 0; i < object.localPhotoPaths.length; i++) {
      final value = object.localPhotoPaths[i];
      bytesCount += value.length * 3;
    }
  }
  {
    final value = object.logTime;
    if (value != null) {
      bytesCount += 3 + value.length * 3;
    }
  }
  {
    final value = object.measurementsJson;
    if (value != null) {
      bytesCount += 3 + value.length * 3;
    }
  }
  {
    final value = object.notes;
    if (value != null) {
      bytesCount += 3 + value.length * 3;
    }
  }
  {
    final value = object.notesAr;
    if (value != null) {
      bytesCount += 3 + value.length * 3;
    }
  }
  bytesCount += 3 + object.offlineId.length * 3;
  {
    final value = object.plotId;
    if (value != null) {
      bytesCount += 3 + value.length * 3;
    }
  }
  bytesCount += 3 + object.recordedBy.length * 3;
  {
    final value = object.serverId;
    if (value != null) {
      bytesCount += 3 + value.length * 3;
    }
  }
  {
    final value = object.syncError;
    if (value != null) {
      bytesCount += 3 + value.length * 3;
    }
  }
  bytesCount += 3 + object.syncStatus.name.length * 3;
  bytesCount += 3 + object.title.length * 3;
  {
    final value = object.titleAr;
    if (value != null) {
      bytesCount += 3 + value.length * 3;
    }
  }
  {
    final value = object.treatmentId;
    if (value != null) {
      bytesCount += 3 + value.length * 3;
    }
  }
  bytesCount += 3 + object.uploadedAttachmentUrls.length * 3;
  {
    for (var i = 0; i < object.uploadedAttachmentUrls.length; i++) {
      final value = object.uploadedAttachmentUrls[i];
      bytesCount += value.length * 3;
    }
  }
  bytesCount += 3 + object.uploadedPhotoUrls.length * 3;
  {
    for (var i = 0; i < object.uploadedPhotoUrls.length; i++) {
      final value = object.uploadedPhotoUrls[i];
      bytesCount += value.length * 3;
    }
  }
  {
    final value = object.weatherConditionsJson;
    if (value != null) {
      bytesCount += 3 + value.length * 3;
    }
  }
  return bytesCount;
}

void _localResearchLogSerialize(
  LocalResearchLog object,
  IsarWriter writer,
  List<int> offsets,
  Map<Type, List<int>> allOffsets,
) {
  writer.writeString(offsets[0], object.category);
  writer.writeDateTime(offsets[1], object.createdAt);
  writer.writeString(offsets[2], object.deviceId);
  writer.writeString(offsets[3], object.experimentId);
  writer.writeString(offsets[4], object.hash);
  writer.writeDateTime(offsets[5], object.lastSyncAttempt);
  writer.writeDouble(offsets[6], object.latitude);
  writer.writeStringList(offsets[7], object.localAttachmentPaths);
  writer.writeStringList(offsets[8], object.localPhotoPaths);
  writer.writeDateTime(offsets[9], object.logDate);
  writer.writeString(offsets[10], object.logTime);
  writer.writeDouble(offsets[11], object.longitude);
  writer.writeString(offsets[12], object.measurementsJson);
  writer.writeString(offsets[13], object.notes);
  writer.writeString(offsets[14], object.notesAr);
  writer.writeString(offsets[15], object.offlineId);
  writer.writeString(offsets[16], object.plotId);
  writer.writeString(offsets[17], object.recordedBy);
  writer.writeString(offsets[18], object.serverId);
  writer.writeBool(offsets[19], object.shouldRetrySync);
  writer.writeLong(offsets[20], object.syncAttempts);
  writer.writeString(offsets[21], object.syncError);
  writer.writeString(offsets[22], object.syncStatus.name);
  writer.writeString(offsets[23], object.title);
  writer.writeString(offsets[24], object.titleAr);
  writer.writeString(offsets[25], object.treatmentId);
  writer.writeDateTime(offsets[26], object.updatedAt);
  writer.writeStringList(offsets[27], object.uploadedAttachmentUrls);
  writer.writeStringList(offsets[28], object.uploadedPhotoUrls);
  writer.writeString(offsets[29], object.weatherConditionsJson);
}

LocalResearchLog _localResearchLogDeserialize(
  Id id,
  IsarReader reader,
  List<int> offsets,
  Map<Type, List<int>> allOffsets,
) {
  final object = LocalResearchLog();
  object.category = reader.readString(offsets[0]);
  object.createdAt = reader.readDateTime(offsets[1]);
  object.deviceId = reader.readStringOrNull(offsets[2]);
  object.experimentId = reader.readString(offsets[3]);
  object.hash = reader.readStringOrNull(offsets[4]);
  object.id = id;
  object.lastSyncAttempt = reader.readDateTimeOrNull(offsets[5]);
  object.latitude = reader.readDoubleOrNull(offsets[6]);
  object.localAttachmentPaths = reader.readStringList(offsets[7]) ?? [];
  object.localPhotoPaths = reader.readStringList(offsets[8]) ?? [];
  object.logDate = reader.readDateTime(offsets[9]);
  object.logTime = reader.readStringOrNull(offsets[10]);
  object.longitude = reader.readDoubleOrNull(offsets[11]);
  object.measurementsJson = reader.readStringOrNull(offsets[12]);
  object.notes = reader.readStringOrNull(offsets[13]);
  object.notesAr = reader.readStringOrNull(offsets[14]);
  object.offlineId = reader.readString(offsets[15]);
  object.plotId = reader.readStringOrNull(offsets[16]);
  object.recordedBy = reader.readString(offsets[17]);
  object.serverId = reader.readStringOrNull(offsets[18]);
  object.syncAttempts = reader.readLong(offsets[20]);
  object.syncError = reader.readStringOrNull(offsets[21]);
  object.syncStatus = _LocalResearchLogsyncStatusValueEnumMap[
          reader.readStringOrNull(offsets[22])] ??
      SyncStatus.pending;
  object.title = reader.readString(offsets[23]);
  object.titleAr = reader.readStringOrNull(offsets[24]);
  object.treatmentId = reader.readStringOrNull(offsets[25]);
  object.updatedAt = reader.readDateTime(offsets[26]);
  object.uploadedAttachmentUrls = reader.readStringList(offsets[27]) ?? [];
  object.uploadedPhotoUrls = reader.readStringList(offsets[28]) ?? [];
  object.weatherConditionsJson = reader.readStringOrNull(offsets[29]);
  return object;
}

P _localResearchLogDeserializeProp<P>(
  IsarReader reader,
  int propertyId,
  int offset,
  Map<Type, List<int>> allOffsets,
) {
  switch (propertyId) {
    case 0:
      return (reader.readString(offset)) as P;
    case 1:
      return (reader.readDateTime(offset)) as P;
    case 2:
      return (reader.readStringOrNull(offset)) as P;
    case 3:
      return (reader.readString(offset)) as P;
    case 4:
      return (reader.readStringOrNull(offset)) as P;
    case 5:
      return (reader.readDateTimeOrNull(offset)) as P;
    case 6:
      return (reader.readDoubleOrNull(offset)) as P;
    case 7:
      return (reader.readStringList(offset) ?? []) as P;
    case 8:
      return (reader.readStringList(offset) ?? []) as P;
    case 9:
      return (reader.readDateTime(offset)) as P;
    case 10:
      return (reader.readStringOrNull(offset)) as P;
    case 11:
      return (reader.readDoubleOrNull(offset)) as P;
    case 12:
      return (reader.readStringOrNull(offset)) as P;
    case 13:
      return (reader.readStringOrNull(offset)) as P;
    case 14:
      return (reader.readStringOrNull(offset)) as P;
    case 15:
      return (reader.readString(offset)) as P;
    case 16:
      return (reader.readStringOrNull(offset)) as P;
    case 17:
      return (reader.readString(offset)) as P;
    case 18:
      return (reader.readStringOrNull(offset)) as P;
    case 19:
      return (reader.readBool(offset)) as P;
    case 20:
      return (reader.readLong(offset)) as P;
    case 21:
      return (reader.readStringOrNull(offset)) as P;
    case 22:
      return (_LocalResearchLogsyncStatusValueEnumMap[
              reader.readStringOrNull(offset)] ??
          SyncStatus.pending) as P;
    case 23:
      return (reader.readString(offset)) as P;
    case 24:
      return (reader.readStringOrNull(offset)) as P;
    case 25:
      return (reader.readStringOrNull(offset)) as P;
    case 26:
      return (reader.readDateTime(offset)) as P;
    case 27:
      return (reader.readStringList(offset) ?? []) as P;
    case 28:
      return (reader.readStringList(offset) ?? []) as P;
    case 29:
      return (reader.readStringOrNull(offset)) as P;
    default:
      throw IsarError('Unknown property with id $propertyId');
  }
}

const _LocalResearchLogsyncStatusEnumValueMap = {
  r'pending': r'pending',
  r'syncing': r'syncing',
  r'synced': r'synced',
  r'failed': r'failed',
};
const _LocalResearchLogsyncStatusValueEnumMap = {
  r'pending': SyncStatus.pending,
  r'syncing': SyncStatus.syncing,
  r'synced': SyncStatus.synced,
  r'failed': SyncStatus.failed,
};

Id _localResearchLogGetId(LocalResearchLog object) {
  return object.id;
}

List<IsarLinkBase<dynamic>> _localResearchLogGetLinks(LocalResearchLog object) {
  return [];
}

void _localResearchLogAttach(
    IsarCollection<dynamic> col, Id id, LocalResearchLog object) {
  object.id = id;
}

extension LocalResearchLogByIndex on IsarCollection<LocalResearchLog> {
  Future<LocalResearchLog?> getByOfflineId(String offlineId) {
    return getByIndex(r'offlineId', [offlineId]);
  }

  LocalResearchLog? getByOfflineIdSync(String offlineId) {
    return getByIndexSync(r'offlineId', [offlineId]);
  }

  Future<bool> deleteByOfflineId(String offlineId) {
    return deleteByIndex(r'offlineId', [offlineId]);
  }

  bool deleteByOfflineIdSync(String offlineId) {
    return deleteByIndexSync(r'offlineId', [offlineId]);
  }

  Future<List<LocalResearchLog?>> getAllByOfflineId(
      List<String> offlineIdValues) {
    final values = offlineIdValues.map((e) => [e]).toList();
    return getAllByIndex(r'offlineId', values);
  }

  List<LocalResearchLog?> getAllByOfflineIdSync(List<String> offlineIdValues) {
    final values = offlineIdValues.map((e) => [e]).toList();
    return getAllByIndexSync(r'offlineId', values);
  }

  Future<int> deleteAllByOfflineId(List<String> offlineIdValues) {
    final values = offlineIdValues.map((e) => [e]).toList();
    return deleteAllByIndex(r'offlineId', values);
  }

  int deleteAllByOfflineIdSync(List<String> offlineIdValues) {
    final values = offlineIdValues.map((e) => [e]).toList();
    return deleteAllByIndexSync(r'offlineId', values);
  }

  Future<Id> putByOfflineId(LocalResearchLog object) {
    return putByIndex(r'offlineId', object);
  }

  Id putByOfflineIdSync(LocalResearchLog object, {bool saveLinks = true}) {
    return putByIndexSync(r'offlineId', object, saveLinks: saveLinks);
  }

  Future<List<Id>> putAllByOfflineId(List<LocalResearchLog> objects) {
    return putAllByIndex(r'offlineId', objects);
  }

  List<Id> putAllByOfflineIdSync(List<LocalResearchLog> objects,
      {bool saveLinks = true}) {
    return putAllByIndexSync(r'offlineId', objects, saveLinks: saveLinks);
  }
}

extension LocalResearchLogQueryWhereSort
    on QueryBuilder<LocalResearchLog, LocalResearchLog, QWhere> {
  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhere> anyId() {
    return QueryBuilder.apply(this, (query) {
      return query.addWhereClause(const IdWhereClause.any());
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhere> anyLogDate() {
    return QueryBuilder.apply(this, (query) {
      return query.addWhereClause(
        const IndexWhereClause.any(indexName: r'logDate'),
      );
    });
  }
}

extension LocalResearchLogQueryWhere
    on QueryBuilder<LocalResearchLog, LocalResearchLog, QWhereClause> {
  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause> idEqualTo(
      Id id) {
    return QueryBuilder.apply(this, (query) {
      return query.addWhereClause(IdWhereClause.between(
        lower: id,
        upper: id,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      idNotEqualTo(Id id) {
    return QueryBuilder.apply(this, (query) {
      if (query.whereSort == Sort.asc) {
        return query
            .addWhereClause(
              IdWhereClause.lessThan(upper: id, includeUpper: false),
            )
            .addWhereClause(
              IdWhereClause.greaterThan(lower: id, includeLower: false),
            );
      } else {
        return query
            .addWhereClause(
              IdWhereClause.greaterThan(lower: id, includeLower: false),
            )
            .addWhereClause(
              IdWhereClause.lessThan(upper: id, includeUpper: false),
            );
      }
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      idGreaterThan(Id id, {bool include = false}) {
    return QueryBuilder.apply(this, (query) {
      return query.addWhereClause(
        IdWhereClause.greaterThan(lower: id, includeLower: include),
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      idLessThan(Id id, {bool include = false}) {
    return QueryBuilder.apply(this, (query) {
      return query.addWhereClause(
        IdWhereClause.lessThan(upper: id, includeUpper: include),
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause> idBetween(
    Id lowerId,
    Id upperId, {
    bool includeLower = true,
    bool includeUpper = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addWhereClause(IdWhereClause.between(
        lower: lowerId,
        includeLower: includeLower,
        upper: upperId,
        includeUpper: includeUpper,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      offlineIdEqualTo(String offlineId) {
    return QueryBuilder.apply(this, (query) {
      return query.addWhereClause(IndexWhereClause.equalTo(
        indexName: r'offlineId',
        value: [offlineId],
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      offlineIdNotEqualTo(String offlineId) {
    return QueryBuilder.apply(this, (query) {
      if (query.whereSort == Sort.asc) {
        return query
            .addWhereClause(IndexWhereClause.between(
              indexName: r'offlineId',
              lower: [],
              upper: [offlineId],
              includeUpper: false,
            ))
            .addWhereClause(IndexWhereClause.between(
              indexName: r'offlineId',
              lower: [offlineId],
              includeLower: false,
              upper: [],
            ));
      } else {
        return query
            .addWhereClause(IndexWhereClause.between(
              indexName: r'offlineId',
              lower: [offlineId],
              includeLower: false,
              upper: [],
            ))
            .addWhereClause(IndexWhereClause.between(
              indexName: r'offlineId',
              lower: [],
              upper: [offlineId],
              includeUpper: false,
            ));
      }
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      experimentIdEqualTo(String experimentId) {
    return QueryBuilder.apply(this, (query) {
      return query.addWhereClause(IndexWhereClause.equalTo(
        indexName: r'experimentId',
        value: [experimentId],
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      experimentIdNotEqualTo(String experimentId) {
    return QueryBuilder.apply(this, (query) {
      if (query.whereSort == Sort.asc) {
        return query
            .addWhereClause(IndexWhereClause.between(
              indexName: r'experimentId',
              lower: [],
              upper: [experimentId],
              includeUpper: false,
            ))
            .addWhereClause(IndexWhereClause.between(
              indexName: r'experimentId',
              lower: [experimentId],
              includeLower: false,
              upper: [],
            ));
      } else {
        return query
            .addWhereClause(IndexWhereClause.between(
              indexName: r'experimentId',
              lower: [experimentId],
              includeLower: false,
              upper: [],
            ))
            .addWhereClause(IndexWhereClause.between(
              indexName: r'experimentId',
              lower: [],
              upper: [experimentId],
              includeUpper: false,
            ));
      }
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      logDateEqualTo(DateTime logDate) {
    return QueryBuilder.apply(this, (query) {
      return query.addWhereClause(IndexWhereClause.equalTo(
        indexName: r'logDate',
        value: [logDate],
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      logDateNotEqualTo(DateTime logDate) {
    return QueryBuilder.apply(this, (query) {
      if (query.whereSort == Sort.asc) {
        return query
            .addWhereClause(IndexWhereClause.between(
              indexName: r'logDate',
              lower: [],
              upper: [logDate],
              includeUpper: false,
            ))
            .addWhereClause(IndexWhereClause.between(
              indexName: r'logDate',
              lower: [logDate],
              includeLower: false,
              upper: [],
            ));
      } else {
        return query
            .addWhereClause(IndexWhereClause.between(
              indexName: r'logDate',
              lower: [logDate],
              includeLower: false,
              upper: [],
            ))
            .addWhereClause(IndexWhereClause.between(
              indexName: r'logDate',
              lower: [],
              upper: [logDate],
              includeUpper: false,
            ));
      }
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      logDateGreaterThan(
    DateTime logDate, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addWhereClause(IndexWhereClause.between(
        indexName: r'logDate',
        lower: [logDate],
        includeLower: include,
        upper: [],
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      logDateLessThan(
    DateTime logDate, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addWhereClause(IndexWhereClause.between(
        indexName: r'logDate',
        lower: [],
        upper: [logDate],
        includeUpper: include,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      logDateBetween(
    DateTime lowerLogDate,
    DateTime upperLogDate, {
    bool includeLower = true,
    bool includeUpper = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addWhereClause(IndexWhereClause.between(
        indexName: r'logDate',
        lower: [lowerLogDate],
        includeLower: includeLower,
        upper: [upperLogDate],
        includeUpper: includeUpper,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      categoryEqualTo(String category) {
    return QueryBuilder.apply(this, (query) {
      return query.addWhereClause(IndexWhereClause.equalTo(
        indexName: r'category',
        value: [category],
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      categoryNotEqualTo(String category) {
    return QueryBuilder.apply(this, (query) {
      if (query.whereSort == Sort.asc) {
        return query
            .addWhereClause(IndexWhereClause.between(
              indexName: r'category',
              lower: [],
              upper: [category],
              includeUpper: false,
            ))
            .addWhereClause(IndexWhereClause.between(
              indexName: r'category',
              lower: [category],
              includeLower: false,
              upper: [],
            ));
      } else {
        return query
            .addWhereClause(IndexWhereClause.between(
              indexName: r'category',
              lower: [category],
              includeLower: false,
              upper: [],
            ))
            .addWhereClause(IndexWhereClause.between(
              indexName: r'category',
              lower: [],
              upper: [category],
              includeUpper: false,
            ));
      }
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      syncStatusEqualTo(SyncStatus syncStatus) {
    return QueryBuilder.apply(this, (query) {
      return query.addWhereClause(IndexWhereClause.equalTo(
        indexName: r'syncStatus',
        value: [syncStatus],
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterWhereClause>
      syncStatusNotEqualTo(SyncStatus syncStatus) {
    return QueryBuilder.apply(this, (query) {
      if (query.whereSort == Sort.asc) {
        return query
            .addWhereClause(IndexWhereClause.between(
              indexName: r'syncStatus',
              lower: [],
              upper: [syncStatus],
              includeUpper: false,
            ))
            .addWhereClause(IndexWhereClause.between(
              indexName: r'syncStatus',
              lower: [syncStatus],
              includeLower: false,
              upper: [],
            ));
      } else {
        return query
            .addWhereClause(IndexWhereClause.between(
              indexName: r'syncStatus',
              lower: [syncStatus],
              includeLower: false,
              upper: [],
            ))
            .addWhereClause(IndexWhereClause.between(
              indexName: r'syncStatus',
              lower: [],
              upper: [syncStatus],
              includeUpper: false,
            ));
      }
    });
  }
}

extension LocalResearchLogQueryFilter
    on QueryBuilder<LocalResearchLog, LocalResearchLog, QFilterCondition> {
  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      categoryEqualTo(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'category',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      categoryGreaterThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'category',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      categoryLessThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'category',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      categoryBetween(
    String lower,
    String upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'category',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      categoryStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'category',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      categoryEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'category',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      categoryContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'category',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      categoryMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'category',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      categoryIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'category',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      categoryIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'category',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      createdAtEqualTo(DateTime value) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'createdAt',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      createdAtGreaterThan(
    DateTime value, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'createdAt',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      createdAtLessThan(
    DateTime value, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'createdAt',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      createdAtBetween(
    DateTime lower,
    DateTime upper, {
    bool includeLower = true,
    bool includeUpper = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'createdAt',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      deviceIdIsNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNull(
        property: r'deviceId',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      deviceIdIsNotNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNotNull(
        property: r'deviceId',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      deviceIdEqualTo(
    String? value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'deviceId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      deviceIdGreaterThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'deviceId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      deviceIdLessThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'deviceId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      deviceIdBetween(
    String? lower,
    String? upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'deviceId',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      deviceIdStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'deviceId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      deviceIdEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'deviceId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      deviceIdContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'deviceId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      deviceIdMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'deviceId',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      deviceIdIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'deviceId',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      deviceIdIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'deviceId',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      experimentIdEqualTo(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'experimentId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      experimentIdGreaterThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'experimentId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      experimentIdLessThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'experimentId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      experimentIdBetween(
    String lower,
    String upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'experimentId',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      experimentIdStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'experimentId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      experimentIdEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'experimentId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      experimentIdContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'experimentId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      experimentIdMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'experimentId',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      experimentIdIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'experimentId',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      experimentIdIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'experimentId',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      hashIsNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNull(
        property: r'hash',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      hashIsNotNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNotNull(
        property: r'hash',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      hashEqualTo(
    String? value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'hash',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      hashGreaterThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'hash',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      hashLessThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'hash',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      hashBetween(
    String? lower,
    String? upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'hash',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      hashStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'hash',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      hashEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'hash',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      hashContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'hash',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      hashMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'hash',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      hashIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'hash',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      hashIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'hash',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      idEqualTo(Id value) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'id',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      idGreaterThan(
    Id value, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'id',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      idLessThan(
    Id value, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'id',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      idBetween(
    Id lower,
    Id upper, {
    bool includeLower = true,
    bool includeUpper = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'id',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      lastSyncAttemptIsNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNull(
        property: r'lastSyncAttempt',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      lastSyncAttemptIsNotNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNotNull(
        property: r'lastSyncAttempt',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      lastSyncAttemptEqualTo(DateTime? value) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'lastSyncAttempt',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      lastSyncAttemptGreaterThan(
    DateTime? value, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'lastSyncAttempt',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      lastSyncAttemptLessThan(
    DateTime? value, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'lastSyncAttempt',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      lastSyncAttemptBetween(
    DateTime? lower,
    DateTime? upper, {
    bool includeLower = true,
    bool includeUpper = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'lastSyncAttempt',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      latitudeIsNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNull(
        property: r'latitude',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      latitudeIsNotNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNotNull(
        property: r'latitude',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      latitudeEqualTo(
    double? value, {
    double epsilon = Query.epsilon,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'latitude',
        value: value,
        epsilon: epsilon,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      latitudeGreaterThan(
    double? value, {
    bool include = false,
    double epsilon = Query.epsilon,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'latitude',
        value: value,
        epsilon: epsilon,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      latitudeLessThan(
    double? value, {
    bool include = false,
    double epsilon = Query.epsilon,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'latitude',
        value: value,
        epsilon: epsilon,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      latitudeBetween(
    double? lower,
    double? upper, {
    bool includeLower = true,
    bool includeUpper = true,
    double epsilon = Query.epsilon,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'latitude',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        epsilon: epsilon,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsElementEqualTo(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'localAttachmentPaths',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsElementGreaterThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'localAttachmentPaths',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsElementLessThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'localAttachmentPaths',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsElementBetween(
    String lower,
    String upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'localAttachmentPaths',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsElementStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'localAttachmentPaths',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsElementEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'localAttachmentPaths',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsElementContains(String value,
          {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'localAttachmentPaths',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsElementMatches(String pattern,
          {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'localAttachmentPaths',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsElementIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'localAttachmentPaths',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsElementIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'localAttachmentPaths',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsLengthEqualTo(int length) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'localAttachmentPaths',
        length,
        true,
        length,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'localAttachmentPaths',
        0,
        true,
        0,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'localAttachmentPaths',
        0,
        false,
        999999,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsLengthLessThan(
    int length, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'localAttachmentPaths',
        0,
        true,
        length,
        include,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsLengthGreaterThan(
    int length, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'localAttachmentPaths',
        length,
        include,
        999999,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localAttachmentPathsLengthBetween(
    int lower,
    int upper, {
    bool includeLower = true,
    bool includeUpper = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'localAttachmentPaths',
        lower,
        includeLower,
        upper,
        includeUpper,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsElementEqualTo(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'localPhotoPaths',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsElementGreaterThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'localPhotoPaths',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsElementLessThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'localPhotoPaths',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsElementBetween(
    String lower,
    String upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'localPhotoPaths',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsElementStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'localPhotoPaths',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsElementEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'localPhotoPaths',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsElementContains(String value,
          {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'localPhotoPaths',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsElementMatches(String pattern,
          {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'localPhotoPaths',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsElementIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'localPhotoPaths',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsElementIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'localPhotoPaths',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsLengthEqualTo(int length) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'localPhotoPaths',
        length,
        true,
        length,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'localPhotoPaths',
        0,
        true,
        0,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'localPhotoPaths',
        0,
        false,
        999999,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsLengthLessThan(
    int length, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'localPhotoPaths',
        0,
        true,
        length,
        include,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsLengthGreaterThan(
    int length, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'localPhotoPaths',
        length,
        include,
        999999,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      localPhotoPathsLengthBetween(
    int lower,
    int upper, {
    bool includeLower = true,
    bool includeUpper = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'localPhotoPaths',
        lower,
        includeLower,
        upper,
        includeUpper,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logDateEqualTo(DateTime value) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'logDate',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logDateGreaterThan(
    DateTime value, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'logDate',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logDateLessThan(
    DateTime value, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'logDate',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logDateBetween(
    DateTime lower,
    DateTime upper, {
    bool includeLower = true,
    bool includeUpper = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'logDate',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logTimeIsNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNull(
        property: r'logTime',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logTimeIsNotNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNotNull(
        property: r'logTime',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logTimeEqualTo(
    String? value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'logTime',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logTimeGreaterThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'logTime',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logTimeLessThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'logTime',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logTimeBetween(
    String? lower,
    String? upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'logTime',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logTimeStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'logTime',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logTimeEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'logTime',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logTimeContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'logTime',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logTimeMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'logTime',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logTimeIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'logTime',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      logTimeIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'logTime',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      longitudeIsNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNull(
        property: r'longitude',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      longitudeIsNotNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNotNull(
        property: r'longitude',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      longitudeEqualTo(
    double? value, {
    double epsilon = Query.epsilon,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'longitude',
        value: value,
        epsilon: epsilon,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      longitudeGreaterThan(
    double? value, {
    bool include = false,
    double epsilon = Query.epsilon,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'longitude',
        value: value,
        epsilon: epsilon,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      longitudeLessThan(
    double? value, {
    bool include = false,
    double epsilon = Query.epsilon,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'longitude',
        value: value,
        epsilon: epsilon,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      longitudeBetween(
    double? lower,
    double? upper, {
    bool includeLower = true,
    bool includeUpper = true,
    double epsilon = Query.epsilon,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'longitude',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        epsilon: epsilon,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      measurementsJsonIsNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNull(
        property: r'measurementsJson',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      measurementsJsonIsNotNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNotNull(
        property: r'measurementsJson',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      measurementsJsonEqualTo(
    String? value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'measurementsJson',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      measurementsJsonGreaterThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'measurementsJson',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      measurementsJsonLessThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'measurementsJson',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      measurementsJsonBetween(
    String? lower,
    String? upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'measurementsJson',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      measurementsJsonStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'measurementsJson',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      measurementsJsonEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'measurementsJson',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      measurementsJsonContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'measurementsJson',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      measurementsJsonMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'measurementsJson',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      measurementsJsonIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'measurementsJson',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      measurementsJsonIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'measurementsJson',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesIsNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNull(
        property: r'notes',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesIsNotNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNotNull(
        property: r'notes',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesEqualTo(
    String? value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'notes',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesGreaterThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'notes',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesLessThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'notes',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesBetween(
    String? lower,
    String? upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'notes',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'notes',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'notes',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'notes',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'notes',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'notes',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'notes',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesArIsNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNull(
        property: r'notesAr',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesArIsNotNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNotNull(
        property: r'notesAr',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesArEqualTo(
    String? value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'notesAr',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesArGreaterThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'notesAr',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesArLessThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'notesAr',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesArBetween(
    String? lower,
    String? upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'notesAr',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesArStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'notesAr',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesArEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'notesAr',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesArContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'notesAr',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesArMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'notesAr',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesArIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'notesAr',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      notesArIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'notesAr',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      offlineIdEqualTo(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'offlineId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      offlineIdGreaterThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'offlineId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      offlineIdLessThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'offlineId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      offlineIdBetween(
    String lower,
    String upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'offlineId',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      offlineIdStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'offlineId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      offlineIdEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'offlineId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      offlineIdContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'offlineId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      offlineIdMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'offlineId',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      offlineIdIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'offlineId',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      offlineIdIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'offlineId',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      plotIdIsNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNull(
        property: r'plotId',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      plotIdIsNotNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNotNull(
        property: r'plotId',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      plotIdEqualTo(
    String? value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'plotId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      plotIdGreaterThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'plotId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      plotIdLessThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'plotId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      plotIdBetween(
    String? lower,
    String? upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'plotId',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      plotIdStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'plotId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      plotIdEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'plotId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      plotIdContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'plotId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      plotIdMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'plotId',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      plotIdIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'plotId',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      plotIdIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'plotId',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      recordedByEqualTo(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'recordedBy',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      recordedByGreaterThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'recordedBy',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      recordedByLessThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'recordedBy',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      recordedByBetween(
    String lower,
    String upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'recordedBy',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      recordedByStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'recordedBy',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      recordedByEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'recordedBy',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      recordedByContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'recordedBy',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      recordedByMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'recordedBy',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      recordedByIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'recordedBy',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      recordedByIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'recordedBy',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      serverIdIsNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNull(
        property: r'serverId',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      serverIdIsNotNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNotNull(
        property: r'serverId',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      serverIdEqualTo(
    String? value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'serverId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      serverIdGreaterThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'serverId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      serverIdLessThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'serverId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      serverIdBetween(
    String? lower,
    String? upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'serverId',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      serverIdStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'serverId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      serverIdEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'serverId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      serverIdContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'serverId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      serverIdMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'serverId',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      serverIdIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'serverId',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      serverIdIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'serverId',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      shouldRetrySyncEqualTo(bool value) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'shouldRetrySync',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncAttemptsEqualTo(int value) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'syncAttempts',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncAttemptsGreaterThan(
    int value, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'syncAttempts',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncAttemptsLessThan(
    int value, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'syncAttempts',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncAttemptsBetween(
    int lower,
    int upper, {
    bool includeLower = true,
    bool includeUpper = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'syncAttempts',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncErrorIsNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNull(
        property: r'syncError',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncErrorIsNotNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNotNull(
        property: r'syncError',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncErrorEqualTo(
    String? value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'syncError',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncErrorGreaterThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'syncError',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncErrorLessThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'syncError',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncErrorBetween(
    String? lower,
    String? upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'syncError',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncErrorStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'syncError',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncErrorEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'syncError',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncErrorContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'syncError',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncErrorMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'syncError',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncErrorIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'syncError',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncErrorIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'syncError',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncStatusEqualTo(
    SyncStatus value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'syncStatus',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncStatusGreaterThan(
    SyncStatus value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'syncStatus',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncStatusLessThan(
    SyncStatus value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'syncStatus',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncStatusBetween(
    SyncStatus lower,
    SyncStatus upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'syncStatus',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncStatusStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'syncStatus',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncStatusEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'syncStatus',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncStatusContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'syncStatus',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncStatusMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'syncStatus',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncStatusIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'syncStatus',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      syncStatusIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'syncStatus',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleEqualTo(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'title',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleGreaterThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'title',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleLessThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'title',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleBetween(
    String lower,
    String upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'title',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'title',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'title',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'title',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'title',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'title',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'title',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleArIsNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNull(
        property: r'titleAr',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleArIsNotNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNotNull(
        property: r'titleAr',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleArEqualTo(
    String? value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'titleAr',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleArGreaterThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'titleAr',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleArLessThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'titleAr',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleArBetween(
    String? lower,
    String? upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'titleAr',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleArStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'titleAr',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleArEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'titleAr',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleArContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'titleAr',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleArMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'titleAr',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleArIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'titleAr',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      titleArIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'titleAr',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      treatmentIdIsNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNull(
        property: r'treatmentId',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      treatmentIdIsNotNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNotNull(
        property: r'treatmentId',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      treatmentIdEqualTo(
    String? value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'treatmentId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      treatmentIdGreaterThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'treatmentId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      treatmentIdLessThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'treatmentId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      treatmentIdBetween(
    String? lower,
    String? upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'treatmentId',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      treatmentIdStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'treatmentId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      treatmentIdEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'treatmentId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      treatmentIdContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'treatmentId',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      treatmentIdMatches(String pattern, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'treatmentId',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      treatmentIdIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'treatmentId',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      treatmentIdIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'treatmentId',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      updatedAtEqualTo(DateTime value) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'updatedAt',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      updatedAtGreaterThan(
    DateTime value, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'updatedAt',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      updatedAtLessThan(
    DateTime value, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'updatedAt',
        value: value,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      updatedAtBetween(
    DateTime lower,
    DateTime upper, {
    bool includeLower = true,
    bool includeUpper = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'updatedAt',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsElementEqualTo(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'uploadedAttachmentUrls',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsElementGreaterThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'uploadedAttachmentUrls',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsElementLessThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'uploadedAttachmentUrls',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsElementBetween(
    String lower,
    String upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'uploadedAttachmentUrls',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsElementStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'uploadedAttachmentUrls',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsElementEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'uploadedAttachmentUrls',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsElementContains(String value,
          {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'uploadedAttachmentUrls',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsElementMatches(String pattern,
          {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'uploadedAttachmentUrls',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsElementIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'uploadedAttachmentUrls',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsElementIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'uploadedAttachmentUrls',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsLengthEqualTo(int length) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'uploadedAttachmentUrls',
        length,
        true,
        length,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'uploadedAttachmentUrls',
        0,
        true,
        0,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'uploadedAttachmentUrls',
        0,
        false,
        999999,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsLengthLessThan(
    int length, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'uploadedAttachmentUrls',
        0,
        true,
        length,
        include,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsLengthGreaterThan(
    int length, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'uploadedAttachmentUrls',
        length,
        include,
        999999,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedAttachmentUrlsLengthBetween(
    int lower,
    int upper, {
    bool includeLower = true,
    bool includeUpper = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'uploadedAttachmentUrls',
        lower,
        includeLower,
        upper,
        includeUpper,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsElementEqualTo(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'uploadedPhotoUrls',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsElementGreaterThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'uploadedPhotoUrls',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsElementLessThan(
    String value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'uploadedPhotoUrls',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsElementBetween(
    String lower,
    String upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'uploadedPhotoUrls',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsElementStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'uploadedPhotoUrls',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsElementEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'uploadedPhotoUrls',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsElementContains(String value,
          {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'uploadedPhotoUrls',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsElementMatches(String pattern,
          {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'uploadedPhotoUrls',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsElementIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'uploadedPhotoUrls',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsElementIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'uploadedPhotoUrls',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsLengthEqualTo(int length) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'uploadedPhotoUrls',
        length,
        true,
        length,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'uploadedPhotoUrls',
        0,
        true,
        0,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'uploadedPhotoUrls',
        0,
        false,
        999999,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsLengthLessThan(
    int length, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'uploadedPhotoUrls',
        0,
        true,
        length,
        include,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsLengthGreaterThan(
    int length, {
    bool include = false,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'uploadedPhotoUrls',
        length,
        include,
        999999,
        true,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      uploadedPhotoUrlsLengthBetween(
    int lower,
    int upper, {
    bool includeLower = true,
    bool includeUpper = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.listLength(
        r'uploadedPhotoUrls',
        lower,
        includeLower,
        upper,
        includeUpper,
      );
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      weatherConditionsJsonIsNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNull(
        property: r'weatherConditionsJson',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      weatherConditionsJsonIsNotNull() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(const FilterCondition.isNotNull(
        property: r'weatherConditionsJson',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      weatherConditionsJsonEqualTo(
    String? value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'weatherConditionsJson',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      weatherConditionsJsonGreaterThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        include: include,
        property: r'weatherConditionsJson',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      weatherConditionsJsonLessThan(
    String? value, {
    bool include = false,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.lessThan(
        include: include,
        property: r'weatherConditionsJson',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      weatherConditionsJsonBetween(
    String? lower,
    String? upper, {
    bool includeLower = true,
    bool includeUpper = true,
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.between(
        property: r'weatherConditionsJson',
        lower: lower,
        includeLower: includeLower,
        upper: upper,
        includeUpper: includeUpper,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      weatherConditionsJsonStartsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.startsWith(
        property: r'weatherConditionsJson',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      weatherConditionsJsonEndsWith(
    String value, {
    bool caseSensitive = true,
  }) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.endsWith(
        property: r'weatherConditionsJson',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      weatherConditionsJsonContains(String value, {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.contains(
        property: r'weatherConditionsJson',
        value: value,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      weatherConditionsJsonMatches(String pattern,
          {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.matches(
        property: r'weatherConditionsJson',
        wildcard: pattern,
        caseSensitive: caseSensitive,
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      weatherConditionsJsonIsEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.equalTo(
        property: r'weatherConditionsJson',
        value: '',
      ));
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterFilterCondition>
      weatherConditionsJsonIsNotEmpty() {
    return QueryBuilder.apply(this, (query) {
      return query.addFilterCondition(FilterCondition.greaterThan(
        property: r'weatherConditionsJson',
        value: '',
      ));
    });
  }
}

extension LocalResearchLogQueryObject
    on QueryBuilder<LocalResearchLog, LocalResearchLog, QFilterCondition> {}

extension LocalResearchLogQueryLinks
    on QueryBuilder<LocalResearchLog, LocalResearchLog, QFilterCondition> {}

extension LocalResearchLogQuerySortBy
    on QueryBuilder<LocalResearchLog, LocalResearchLog, QSortBy> {
  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByCategory() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'category', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByCategoryDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'category', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByCreatedAt() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'createdAt', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByCreatedAtDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'createdAt', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByDeviceId() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'deviceId', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByDeviceIdDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'deviceId', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByExperimentId() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'experimentId', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByExperimentIdDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'experimentId', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy> sortByHash() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'hash', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByHashDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'hash', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByLastSyncAttempt() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'lastSyncAttempt', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByLastSyncAttemptDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'lastSyncAttempt', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByLatitude() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'latitude', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByLatitudeDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'latitude', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByLogDate() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'logDate', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByLogDateDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'logDate', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByLogTime() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'logTime', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByLogTimeDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'logTime', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByLongitude() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'longitude', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByLongitudeDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'longitude', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByMeasurementsJson() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'measurementsJson', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByMeasurementsJsonDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'measurementsJson', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy> sortByNotes() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'notes', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByNotesDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'notes', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByNotesAr() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'notesAr', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByNotesArDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'notesAr', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByOfflineId() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'offlineId', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByOfflineIdDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'offlineId', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByPlotId() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'plotId', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByPlotIdDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'plotId', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByRecordedBy() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'recordedBy', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByRecordedByDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'recordedBy', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByServerId() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'serverId', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByServerIdDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'serverId', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByShouldRetrySync() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'shouldRetrySync', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByShouldRetrySyncDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'shouldRetrySync', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortBySyncAttempts() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'syncAttempts', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortBySyncAttemptsDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'syncAttempts', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortBySyncError() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'syncError', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortBySyncErrorDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'syncError', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortBySyncStatus() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'syncStatus', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortBySyncStatusDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'syncStatus', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy> sortByTitle() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'title', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByTitleDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'title', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByTitleAr() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'titleAr', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByTitleArDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'titleAr', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByTreatmentId() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'treatmentId', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByTreatmentIdDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'treatmentId', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByUpdatedAt() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'updatedAt', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByUpdatedAtDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'updatedAt', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByWeatherConditionsJson() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'weatherConditionsJson', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      sortByWeatherConditionsJsonDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'weatherConditionsJson', Sort.desc);
    });
  }
}

extension LocalResearchLogQuerySortThenBy
    on QueryBuilder<LocalResearchLog, LocalResearchLog, QSortThenBy> {
  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByCategory() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'category', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByCategoryDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'category', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByCreatedAt() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'createdAt', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByCreatedAtDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'createdAt', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByDeviceId() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'deviceId', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByDeviceIdDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'deviceId', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByExperimentId() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'experimentId', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByExperimentIdDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'experimentId', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy> thenByHash() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'hash', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByHashDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'hash', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy> thenById() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'id', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByIdDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'id', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByLastSyncAttempt() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'lastSyncAttempt', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByLastSyncAttemptDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'lastSyncAttempt', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByLatitude() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'latitude', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByLatitudeDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'latitude', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByLogDate() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'logDate', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByLogDateDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'logDate', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByLogTime() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'logTime', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByLogTimeDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'logTime', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByLongitude() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'longitude', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByLongitudeDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'longitude', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByMeasurementsJson() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'measurementsJson', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByMeasurementsJsonDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'measurementsJson', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy> thenByNotes() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'notes', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByNotesDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'notes', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByNotesAr() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'notesAr', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByNotesArDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'notesAr', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByOfflineId() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'offlineId', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByOfflineIdDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'offlineId', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByPlotId() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'plotId', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByPlotIdDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'plotId', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByRecordedBy() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'recordedBy', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByRecordedByDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'recordedBy', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByServerId() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'serverId', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByServerIdDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'serverId', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByShouldRetrySync() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'shouldRetrySync', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByShouldRetrySyncDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'shouldRetrySync', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenBySyncAttempts() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'syncAttempts', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenBySyncAttemptsDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'syncAttempts', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenBySyncError() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'syncError', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenBySyncErrorDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'syncError', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenBySyncStatus() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'syncStatus', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenBySyncStatusDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'syncStatus', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy> thenByTitle() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'title', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByTitleDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'title', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByTitleAr() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'titleAr', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByTitleArDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'titleAr', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByTreatmentId() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'treatmentId', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByTreatmentIdDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'treatmentId', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByUpdatedAt() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'updatedAt', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByUpdatedAtDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'updatedAt', Sort.desc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByWeatherConditionsJson() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'weatherConditionsJson', Sort.asc);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QAfterSortBy>
      thenByWeatherConditionsJsonDesc() {
    return QueryBuilder.apply(this, (query) {
      return query.addSortBy(r'weatherConditionsJson', Sort.desc);
    });
  }
}

extension LocalResearchLogQueryWhereDistinct
    on QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct> {
  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByCategory({bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'category', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByCreatedAt() {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'createdAt');
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByDeviceId({bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'deviceId', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByExperimentId({bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'experimentId', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct> distinctByHash(
      {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'hash', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByLastSyncAttempt() {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'lastSyncAttempt');
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByLatitude() {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'latitude');
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByLocalAttachmentPaths() {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'localAttachmentPaths');
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByLocalPhotoPaths() {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'localPhotoPaths');
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByLogDate() {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'logDate');
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct> distinctByLogTime(
      {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'logTime', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByLongitude() {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'longitude');
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByMeasurementsJson({bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'measurementsJson',
          caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct> distinctByNotes(
      {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'notes', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct> distinctByNotesAr(
      {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'notesAr', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByOfflineId({bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'offlineId', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct> distinctByPlotId(
      {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'plotId', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByRecordedBy({bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'recordedBy', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByServerId({bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'serverId', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByShouldRetrySync() {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'shouldRetrySync');
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctBySyncAttempts() {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'syncAttempts');
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctBySyncError({bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'syncError', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctBySyncStatus({bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'syncStatus', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct> distinctByTitle(
      {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'title', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct> distinctByTitleAr(
      {bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'titleAr', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByTreatmentId({bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'treatmentId', caseSensitive: caseSensitive);
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByUpdatedAt() {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'updatedAt');
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByUploadedAttachmentUrls() {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'uploadedAttachmentUrls');
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByUploadedPhotoUrls() {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'uploadedPhotoUrls');
    });
  }

  QueryBuilder<LocalResearchLog, LocalResearchLog, QDistinct>
      distinctByWeatherConditionsJson({bool caseSensitive = true}) {
    return QueryBuilder.apply(this, (query) {
      return query.addDistinctBy(r'weatherConditionsJson',
          caseSensitive: caseSensitive);
    });
  }
}

extension LocalResearchLogQueryProperty
    on QueryBuilder<LocalResearchLog, LocalResearchLog, QQueryProperty> {
  QueryBuilder<LocalResearchLog, int, QQueryOperations> idProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'id');
    });
  }

  QueryBuilder<LocalResearchLog, String, QQueryOperations> categoryProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'category');
    });
  }

  QueryBuilder<LocalResearchLog, DateTime, QQueryOperations>
      createdAtProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'createdAt');
    });
  }

  QueryBuilder<LocalResearchLog, String?, QQueryOperations> deviceIdProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'deviceId');
    });
  }

  QueryBuilder<LocalResearchLog, String, QQueryOperations>
      experimentIdProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'experimentId');
    });
  }

  QueryBuilder<LocalResearchLog, String?, QQueryOperations> hashProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'hash');
    });
  }

  QueryBuilder<LocalResearchLog, DateTime?, QQueryOperations>
      lastSyncAttemptProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'lastSyncAttempt');
    });
  }

  QueryBuilder<LocalResearchLog, double?, QQueryOperations> latitudeProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'latitude');
    });
  }

  QueryBuilder<LocalResearchLog, List<String>, QQueryOperations>
      localAttachmentPathsProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'localAttachmentPaths');
    });
  }

  QueryBuilder<LocalResearchLog, List<String>, QQueryOperations>
      localPhotoPathsProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'localPhotoPaths');
    });
  }

  QueryBuilder<LocalResearchLog, DateTime, QQueryOperations> logDateProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'logDate');
    });
  }

  QueryBuilder<LocalResearchLog, String?, QQueryOperations> logTimeProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'logTime');
    });
  }

  QueryBuilder<LocalResearchLog, double?, QQueryOperations>
      longitudeProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'longitude');
    });
  }

  QueryBuilder<LocalResearchLog, String?, QQueryOperations>
      measurementsJsonProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'measurementsJson');
    });
  }

  QueryBuilder<LocalResearchLog, String?, QQueryOperations> notesProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'notes');
    });
  }

  QueryBuilder<LocalResearchLog, String?, QQueryOperations> notesArProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'notesAr');
    });
  }

  QueryBuilder<LocalResearchLog, String, QQueryOperations> offlineIdProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'offlineId');
    });
  }

  QueryBuilder<LocalResearchLog, String?, QQueryOperations> plotIdProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'plotId');
    });
  }

  QueryBuilder<LocalResearchLog, String, QQueryOperations>
      recordedByProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'recordedBy');
    });
  }

  QueryBuilder<LocalResearchLog, String?, QQueryOperations> serverIdProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'serverId');
    });
  }

  QueryBuilder<LocalResearchLog, bool, QQueryOperations>
      shouldRetrySyncProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'shouldRetrySync');
    });
  }

  QueryBuilder<LocalResearchLog, int, QQueryOperations> syncAttemptsProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'syncAttempts');
    });
  }

  QueryBuilder<LocalResearchLog, String?, QQueryOperations>
      syncErrorProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'syncError');
    });
  }

  QueryBuilder<LocalResearchLog, SyncStatus, QQueryOperations>
      syncStatusProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'syncStatus');
    });
  }

  QueryBuilder<LocalResearchLog, String, QQueryOperations> titleProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'title');
    });
  }

  QueryBuilder<LocalResearchLog, String?, QQueryOperations> titleArProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'titleAr');
    });
  }

  QueryBuilder<LocalResearchLog, String?, QQueryOperations>
      treatmentIdProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'treatmentId');
    });
  }

  QueryBuilder<LocalResearchLog, DateTime, QQueryOperations>
      updatedAtProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'updatedAt');
    });
  }

  QueryBuilder<LocalResearchLog, List<String>, QQueryOperations>
      uploadedAttachmentUrlsProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'uploadedAttachmentUrls');
    });
  }

  QueryBuilder<LocalResearchLog, List<String>, QQueryOperations>
      uploadedPhotoUrlsProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'uploadedPhotoUrls');
    });
  }

  QueryBuilder<LocalResearchLog, String?, QQueryOperations>
      weatherConditionsJsonProperty() {
    return QueryBuilder.apply(this, (query) {
      return query.addPropertyName(r'weatherConditionsJson');
    });
  }
}
