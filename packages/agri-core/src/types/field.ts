/** BBox in WGS84 — compatible with sentinelhub BBox([W,S,E,N], CRS.WGS84) */
export type BBoxArray = [number, number, number, number]; // [minLng, minLat, maxLng, maxLat]

export interface Field {
  id: string;
  userId: string;
  name: string;
  description?: string | null;
  bbox: BBoxArray;
  centerLng?: number | null;
  centerLat?: number | null;
  areaSqKm?: number | null;
  createdAt: string;
  updatedAt: string;
}

export type SentinelIndex = "NDVI" | "EVI" | "NDWI" | "TRUE_COLOR" | "FALSE_COLOR";
export type WeatherEndpoint = "current" | "forecast" | "history" | "agro";
