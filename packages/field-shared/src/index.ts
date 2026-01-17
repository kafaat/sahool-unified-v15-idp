// Re-export all shared functionality
export * from "./entity/Field";
export * from "./entity/FieldBoundaryHistory";
export * from "./entity/SyncStatus";
export * from "./middleware/etag";
export * from "./middleware/validation";
export * from "./middleware/logger";
export * from "./data-source";
export { createFieldApp, startFieldService } from "./app";

// Geospatial Module (PostGIS)
export { GeoService, geoService, geoRoutes } from "./geo";
export type {
  FieldInRadius,
  NearbyFarm,
  FieldInBBox,
  RegionStats,
  FieldAreaResult,
  PointInFieldResult,
  FieldsDistanceResult,
} from "./geo";
