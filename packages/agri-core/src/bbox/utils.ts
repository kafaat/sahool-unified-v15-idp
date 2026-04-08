import type { BBoxArray } from "../types/field";

export function parseBBox(stored: string): BBoxArray {
  return JSON.parse(stored) as BBoxArray;
}

export function serializeBBox(bbox: BBoxArray): string {
  return JSON.stringify(bbox);
}

export function validateBBox(bbox: BBoxArray): { valid: boolean; error?: string } {
  const [w, s, e, n] = bbox;
  if (w < -180 || e > 180) return { valid: false, error: "Longitude out of range" };
  if (s < -90 || n > 90) return { valid: false, error: "Latitude out of range" };
  if (w >= e) return { valid: false, error: "West must be less than East" };
  if (s >= n) return { valid: false, error: "South must be less than North" };
  if ((e - w) < 0.001 || (n - s) < 0.001) return { valid: false, error: "Area too small (< ~100m)" };
  return { valid: true };
}

export function bboxCenter(bbox: BBoxArray): { lng: number; lat: number } {
  return { lng: (bbox[0] + bbox[2]) / 2, lat: (bbox[1] + bbox[3]) / 2 };
}

/** Rough area estimate in km² (equirectangular approximation) */
export function bboxAreaKm2(bbox: BBoxArray): number {
  const [w, s, e, n] = bbox;
  const latRad = ((s + n) / 2) * (Math.PI / 180);
  const widthKm = Math.abs(e - w) * 111.32 * Math.cos(latRad);
  const heightKm = Math.abs(n - s) * 110.574;
  return Math.round(widthKm * heightKm * 100) / 100;
}

/** Format bbox as Mapbox GL JS LngLatBoundsLike */
export function bboxToLngLatBounds(bbox: BBoxArray): [[number, number], [number, number]] {
  return [[bbox[0], bbox[1]], [bbox[2], bbox[3]]];
}

/**
 * Format bbox as Sentinel Hub Process API `bounds.bbox` array.
 * sentinelhub-py: BBox([W,S,E,N], CRS.WGS84) — same as BBoxArray ordering.
 */
export function bboxToSHArray(bbox: BBoxArray): [number, number, number, number] {
  return [bbox[0], bbox[1], bbox[2], bbox[3]];
}
