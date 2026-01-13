/**
 * SAHOOL Geospatial Module
 * PostGIS-powered geospatial operations
 *
 * This module provides:
 * - GeoService: Service class for geospatial operations
 * - geoRoutes: Express routes for geospatial API endpoints
 * - Type definitions for geospatial data
 */

export { GeoService, geoService } from "./geo-service";
export { geoRoutes } from "./geo-routes";

export type {
  FieldInRadius,
  NearbyFarm,
  FieldInBBox,
  RegionStats,
  FieldAreaResult,
  PointInFieldResult,
  FieldsDistanceResult,
} from "./geo-service";
