/**
 * SAHOOL GeoJSON Types
 * Comprehensive geospatial type definitions following the GeoJSON specification (RFC 7946)
 *
 * These types are used for field boundaries, farm locations, and spatial analysis
 * across the SAHOOL platform.
 */

// ═══════════════════════════════════════════════════════════════════════════════
// Core GeoJSON Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * GeoJSON Position
 * A position is an array of numbers [longitude, latitude] or [longitude, latitude, altitude]
 *
 * @example
 * const position: GeoPosition = [46.7219, 24.6877]; // Riyadh coordinates
 */
export type GeoPosition = [number, number] | [number, number, number];

/**
 * GeoJSON Bounding Box
 * [west, south, east, north] or [west, south, minAlt, east, north, maxAlt]
 */
export type GeoBoundingBox =
  | [number, number, number, number]
  | [number, number, number, number, number, number];

// ═══════════════════════════════════════════════════════════════════════════════
// GeoJSON Geometry Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * GeoJSON Point
 * A single geographic point (e.g., farm center, sensor location)
 *
 * @example
 * const farmCenter: GeoPoint = {
 *   type: "Point",
 *   coordinates: [46.7219, 24.6877]
 * };
 */
export interface GeoPoint {
  readonly type: "Point";
  coordinates: GeoPosition;
}

/**
 * GeoJSON MultiPoint
 * Multiple unconnected points
 */
export interface GeoMultiPoint {
  readonly type: "MultiPoint";
  coordinates: GeoPosition[];
}

/**
 * GeoJSON LineString
 * A connected sequence of points (e.g., irrigation channel, road)
 */
export interface GeoLineString {
  readonly type: "LineString";
  coordinates: GeoPosition[];
}

/**
 * GeoJSON MultiLineString
 * Multiple line strings
 */
export interface GeoMultiLineString {
  readonly type: "MultiLineString";
  coordinates: GeoPosition[][];
}

/**
 * GeoJSON Polygon
 * A closed shape with optional holes (e.g., field boundary)
 * First ring is the exterior, subsequent rings are holes
 *
 * @example
 * const fieldBoundary: GeoPolygon = {
 *   type: "Polygon",
 *   coordinates: [[
 *     [46.72, 24.68],
 *     [46.73, 24.68],
 *     [46.73, 24.69],
 *     [46.72, 24.69],
 *     [46.72, 24.68]  // First and last point must be identical
 *   ]]
 * };
 */
export interface GeoPolygon {
  readonly type: "Polygon";
  coordinates: GeoPosition[][];
}

/**
 * GeoJSON MultiPolygon
 * Multiple polygons (e.g., non-contiguous fields)
 */
export interface GeoMultiPolygon {
  readonly type: "MultiPolygon";
  coordinates: GeoPosition[][][];
}

/**
 * GeoJSON GeometryCollection
 * A collection of heterogeneous geometries
 */
export interface GeoGeometryCollection {
  readonly type: "GeometryCollection";
  geometries: GeoGeometry[];
}

/**
 * Union of all GeoJSON geometry types
 */
export type GeoGeometry =
  | GeoPoint
  | GeoMultiPoint
  | GeoLineString
  | GeoMultiLineString
  | GeoPolygon
  | GeoMultiPolygon
  | GeoGeometryCollection;

// ═══════════════════════════════════════════════════════════════════════════════
// GeoJSON Feature Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * GeoJSON Feature
 * A geometry with associated properties
 *
 * @typeParam G - The geometry type (defaults to any GeoGeometry)
 * @typeParam P - The properties type (defaults to Record<string, unknown>)
 *
 * @example
 * interface FieldProperties {
 *   name: string;
 *   cropType: string;
 *   areaHa: number;
 * }
 *
 * const fieldFeature: GeoFeature<GeoPolygon, FieldProperties> = {
 *   type: "Feature",
 *   geometry: { type: "Polygon", coordinates: [...] },
 *   properties: { name: "North Field", cropType: "wheat", areaHa: 10.5 }
 * };
 */
export interface GeoFeature<
  G extends GeoGeometry = GeoGeometry,
  P = Record<string, unknown>,
> {
  readonly type: "Feature";
  geometry: G | null;
  properties: P | null;
  id?: string | number;
  bbox?: GeoBoundingBox;
}

/**
 * GeoJSON FeatureCollection
 * A collection of features
 *
 * @typeParam G - The geometry type for all features
 * @typeParam P - The properties type for all features
 */
export interface GeoFeatureCollection<
  G extends GeoGeometry = GeoGeometry,
  P = Record<string, unknown>,
> {
  readonly type: "FeatureCollection";
  features: GeoFeature<G, P>[];
  bbox?: GeoBoundingBox;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL-Specific Coordinate Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Simple latitude/longitude coordinates
 * Used for basic location data (non-GeoJSON format)
 */
export interface Coordinates {
  /** Latitude in decimal degrees (-90 to 90) */
  lat: number;
  /** Longitude in decimal degrees (-180 to 180) */
  lng: number;
}

/**
 * Alternative coordinate format with full names
 */
export interface GeoCoordinates {
  /** Latitude in decimal degrees */
  latitude: number;
  /** Longitude in decimal degrees */
  longitude: number;
  /** Optional altitude in meters */
  altitude?: number;
}

/**
 * Bounding box for spatial queries (non-GeoJSON format)
 */
export interface BoundingBox {
  /** Minimum latitude (south) */
  minLat: number;
  /** Minimum longitude (west) */
  minLon: number;
  /** Maximum latitude (north) */
  maxLat: number;
  /** Maximum longitude (east) */
  maxLon: number;
}

/**
 * Bounding box with alternative naming
 */
export interface SpatialExtent {
  /** Western boundary (minimum longitude) */
  west: number;
  /** Southern boundary (minimum latitude) */
  south: number;
  /** Eastern boundary (maximum longitude) */
  east: number;
  /** Northern boundary (maximum latitude) */
  north: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Field-Specific Geometry Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Properties for a field feature
 */
export interface FieldFeatureProperties {
  /** Field ID */
  id: string;
  /** Field name */
  name: string;
  /** Field name in Arabic */
  nameAr?: string;
  /** Parent farm ID */
  farmId: string;
  /** Area in hectares */
  areaHa: number;
  /** Current crop type */
  cropType?: string;
  /** Field status */
  status: string;
  /** Health score (0-100) */
  healthScore?: number;
  /** Current NDVI value */
  ndvi?: number;
}

/**
 * A field represented as a GeoJSON Feature
 */
export type FieldFeature = GeoFeature<GeoPolygon, FieldFeatureProperties>;

/**
 * Collection of field features
 */
export type FieldFeatureCollection = GeoFeatureCollection<
  GeoPolygon,
  FieldFeatureProperties
>;

/**
 * Properties for a sensor location feature
 */
export interface SensorFeatureProperties {
  /** Sensor ID */
  id: string;
  /** Sensor type */
  type: string;
  /** Associated field ID */
  fieldId?: string;
  /** Sensor status */
  status: "active" | "inactive" | "error";
  /** Last reading timestamp */
  lastReading?: string;
  /** Battery level (0-100) */
  batteryLevel?: number;
}

/**
 * A sensor represented as a GeoJSON Feature
 */
export type SensorFeature = GeoFeature<GeoPoint, SensorFeatureProperties>;

// ═══════════════════════════════════════════════════════════════════════════════
// Type Guards
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Type guard for GeoPoint
 */
export function isGeoPoint(geometry: unknown): geometry is GeoPoint {
  return (
    typeof geometry === "object" &&
    geometry !== null &&
    "type" in geometry &&
    (geometry as GeoPoint).type === "Point" &&
    "coordinates" in geometry &&
    Array.isArray((geometry as GeoPoint).coordinates)
  );
}

/**
 * Type guard for GeoPolygon
 */
export function isGeoPolygon(geometry: unknown): geometry is GeoPolygon {
  return (
    typeof geometry === "object" &&
    geometry !== null &&
    "type" in geometry &&
    (geometry as GeoPolygon).type === "Polygon" &&
    "coordinates" in geometry &&
    Array.isArray((geometry as GeoPolygon).coordinates)
  );
}

/**
 * Type guard for GeoLineString
 */
export function isGeoLineString(geometry: unknown): geometry is GeoLineString {
  return (
    typeof geometry === "object" &&
    geometry !== null &&
    "type" in geometry &&
    (geometry as GeoLineString).type === "LineString" &&
    "coordinates" in geometry &&
    Array.isArray((geometry as GeoLineString).coordinates)
  );
}

/**
 * Type guard for GeoMultiPolygon
 */
export function isGeoMultiPolygon(
  geometry: unknown
): geometry is GeoMultiPolygon {
  return (
    typeof geometry === "object" &&
    geometry !== null &&
    "type" in geometry &&
    (geometry as GeoMultiPolygon).type === "MultiPolygon" &&
    "coordinates" in geometry &&
    Array.isArray((geometry as GeoMultiPolygon).coordinates)
  );
}

/**
 * Type guard for GeoFeature
 */
export function isGeoFeature(obj: unknown): obj is GeoFeature {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "type" in obj &&
    (obj as GeoFeature).type === "Feature" &&
    "geometry" in obj &&
    "properties" in obj
  );
}

/**
 * Type guard for GeoFeatureCollection
 */
export function isGeoFeatureCollection(
  obj: unknown
): obj is GeoFeatureCollection {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "type" in obj &&
    (obj as GeoFeatureCollection).type === "FeatureCollection" &&
    "features" in obj &&
    Array.isArray((obj as GeoFeatureCollection).features)
  );
}

/**
 * Type guard for valid coordinates
 */
export function isValidCoordinates(coords: unknown): coords is Coordinates {
  return (
    typeof coords === "object" &&
    coords !== null &&
    "lat" in coords &&
    "lng" in coords &&
    typeof (coords as Coordinates).lat === "number" &&
    typeof (coords as Coordinates).lng === "number" &&
    (coords as Coordinates).lat >= -90 &&
    (coords as Coordinates).lat <= 90 &&
    (coords as Coordinates).lng >= -180 &&
    (coords as Coordinates).lng <= 180
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// Utility Functions
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Converts Coordinates to GeoPosition
 */
export function coordinatesToPosition(coords: Coordinates): GeoPosition {
  return [coords.lng, coords.lat];
}

/**
 * Converts GeoPosition to Coordinates
 */
export function positionToCoordinates(position: GeoPosition): Coordinates {
  return { lng: position[0], lat: position[1] };
}

/**
 * Creates a GeoPoint from Coordinates
 */
export function createGeoPoint(coords: Coordinates): GeoPoint {
  return {
    type: "Point",
    coordinates: coordinatesToPosition(coords),
  };
}

/**
 * Extracts center point from a BoundingBox
 */
export function getBoundingBoxCenter(bbox: BoundingBox): Coordinates {
  return {
    lat: (bbox.minLat + bbox.maxLat) / 2,
    lng: (bbox.minLon + bbox.maxLon) / 2,
  };
}
