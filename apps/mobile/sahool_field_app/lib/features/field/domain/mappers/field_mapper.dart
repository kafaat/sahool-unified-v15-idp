import 'package:latlong2/latlong.dart';

import '../entities/field.dart' as domain;
import '../../../fields/domain/entities/field_entity.dart';

/// Field Entity Mapper
/// Maps between domain.Field (from repository/database) and FieldEntity (for UI)
///
/// This mapper bridges the gap between the data layer (domain.Field)
/// and the presentation layer (FieldEntity) to ensure smooth data flow.
class FieldMapper {
  /// Convert domain.Field to FieldEntity for UI display
  static FieldEntity toFieldEntity(domain.Field field) {
    // Map boundary from LatLng to GeoLocation
    List<GeoLocation>? boundary;
    if (field.hasBoundary) {
      boundary = field.boundary
          .map((latLng) => GeoLocation(
                latitude: latLng.latitude,
                longitude: latLng.longitude,
              ))
          .toList();
    }

    // Map centroid to GeoLocation
    GeoLocation? center;
    if (field.centroid != null) {
      center = GeoLocation(
        latitude: field.centroid!.latitude,
        longitude: field.centroid!.longitude,
      );
    }

    // Map health status to field status
    FieldStatus status;
    switch (field.healthStatus) {
      case domain.FieldStatus.healthy:
        status = FieldStatus.active;
        break;
      case domain.FieldStatus.stressed:
        status = FieldStatus.active; // Still active, just needs attention
        break;
      case domain.FieldStatus.critical:
        status = FieldStatus.active; // Still active, critical needs attention
        break;
      case domain.FieldStatus.unknown:
      default:
        status = FieldStatus.fromString(field.status ?? 'active');
    }

    return FieldEntity(
      id: field.id,
      tenantId: field.tenantId,
      name: field.name,
      farmId: field.farmId,
      areaHectares: field.areaHectares,
      cropType: field.cropType ?? 'غير محدد',
      healthScore: field.ndvi, // Use NDVI as health score
      ndviValue: field.ndviCurrent,
      soilType: null, // Not in domain model
      irrigationType: null, // Not in domain model
      status: status,
      center: center,
      boundary: boundary,
      createdAt: field.createdAt,
      updatedAt: field.updatedAt,
    );
  }

  /// Convert FieldEntity to domain.Field
  static domain.Field fromFieldEntity(FieldEntity entity) {
    // Map boundary from GeoLocation to LatLng
    List<LatLng> boundary = [];
    if (entity.boundary != null && entity.boundary!.isNotEmpty) {
      boundary = entity.boundary!
          .map((geo) => LatLng(
                geo.latitude,
                geo.longitude,
              ))
          .toList();
    }

    // Map center to LatLng
    LatLng? centroid;
    if (entity.center != null) {
      centroid = LatLng(
        entity.center!.latitude,
        entity.center!.longitude,
      );
    }

    return domain.Field(
      id: entity.id,
      tenantId: entity.tenantId,
      farmId: entity.farmId,
      name: entity.name,
      cropType: entity.cropType,
      boundary: boundary,
      centroid: centroid,
      areaHectares: entity.areaHectares,
      status: entity.status.value,
      ndviCurrent: entity.ndviValue,
      synced: false, // New entities are not synced
      isDeleted: false,
      createdAt: entity.createdAt,
      updatedAt: entity.updatedAt,
    );
  }

  /// Convert list of domain.Field to list of FieldEntity
  static List<FieldEntity> toFieldEntities(List<domain.Field> fields) {
    return fields.map(toFieldEntity).toList();
  }

  /// Convert list of FieldEntity to list of domain.Field
  static List<domain.Field> fromFieldEntities(List<FieldEntity> entities) {
    return entities.map(fromFieldEntity).toList();
  }
}

/// Extension methods for easy conversion
extension DomainFieldExtension on domain.Field {
  /// Convert to FieldEntity for UI display
  FieldEntity toFieldEntity() => FieldMapper.toFieldEntity(this);
}

extension FieldEntityExtension on FieldEntity {
  /// Convert to domain.Field for repository operations
  domain.Field toDomainField() => FieldMapper.fromFieldEntity(this);
}

extension DomainFieldListExtension on List<domain.Field> {
  /// Convert to list of FieldEntity for UI display
  List<FieldEntity> toFieldEntities() => FieldMapper.toFieldEntities(this);
}

extension FieldEntityListExtension on List<FieldEntity> {
  /// Convert to list of domain.Field for repository operations
  List<domain.Field> toDomainFields() => FieldMapper.fromFieldEntities(this);
}
