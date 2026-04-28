/**
 * Polygon Geometry Validation Utilities
 * أدوات التحقق من صحة هندسة المضلعات
 *
 * Validates field boundary polygons before submission to prevent
 * corrupted geometries from reaching backend services.
 */

import type { FieldBoundary } from '@/features/satellite-monitor/types';

/** Minimum number of distinct vertices required to form a valid polygon */
export const MIN_POLYGON_VERTICES = 3;

/** Maximum number of vertices accepted (protects against degenerate inputs) */
export const MAX_POLYGON_VERTICES = 2000;

/**
 * Floating-point epsilon for orientation comparisons.
 * Cross-product values below this threshold are treated as zero (collinear)
 * to prevent false positive self-intersection reports for very small polygons
 * (e.g. field boundaries where adjacent vertices differ by < 1 mm in WGS84).
 *
 * Rationale: 1mm at the equator ≈ 9×10⁻⁶ degrees in both lat and lng.
 * A cross-product of two such vectors has magnitude ≈ (9e-6)² ≈ 8e-11, well
 * below 1e-9, so genuine 1mm-scale collinear points are correctly handled.
 * Genuine intersections of agricultural-scale edges (> 1cm apart) produce
 * cross-products many orders of magnitude larger and are unaffected.
 */
const EPS = 1e-9;

export interface PolygonValidationResult {
  valid: boolean;
  /** English error messages */
  errors: string[];
  /** Arabic error messages (parallel array, same order as `errors`) */
  errorsAr: string[];
}

// ---------------------------------------------------------------------------
// Segment–segment intersection (CLRS algorithm, orientation-based)
// ---------------------------------------------------------------------------

/**
 * Cross product of vectors (pj − pi) × (pk − pi).
 * Positive → counter-clockwise, negative → clockwise, near-zero → collinear.
 * Uses (lat, lng) as (y, x) — orientation is preserved for WGS84 coordinates
 * when the area is small enough that projection distortion is negligible.
 *
 * Values with |result| < EPS are treated as zero to handle floating-point
 * imprecision in small polygons.
 */
function crossProduct(
  pi: FieldBoundary,
  pj: FieldBoundary,
  pk: FieldBoundary,
): number {
  const val =
    (pj.lng - pi.lng) * (pk.lat - pi.lat) -
    (pj.lat - pi.lat) * (pk.lng - pi.lng);
  return Math.abs(val) < EPS ? 0 : val;
}

/** Returns true if q lies on segment p→r (all three collinear, assumed). */
function onSegment(p: FieldBoundary, q: FieldBoundary, r: FieldBoundary): boolean {
  return (
    q.lat <= Math.max(p.lat, r.lat) &&
    q.lat >= Math.min(p.lat, r.lat) &&
    q.lng <= Math.max(p.lng, r.lng) &&
    q.lng >= Math.min(p.lng, r.lng)
  );
}

/**
 * Returns true if segment (p1→p2) and segment (p3→p4) intersect.
 * Handles both proper intersections and degenerate collinear-overlap cases.
 */
function segmentsIntersect(
  p1: FieldBoundary,
  p2: FieldBoundary,
  p3: FieldBoundary,
  p4: FieldBoundary,
): boolean {
  const d1 = crossProduct(p3, p4, p1);
  const d2 = crossProduct(p3, p4, p2);
  const d3 = crossProduct(p1, p2, p3);
  const d4 = crossProduct(p1, p2, p4);

  if (
    ((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) &&
    ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))
  ) {
    return true; // proper intersection
  }

  // Collinear / degenerate cases (crossProduct returns exactly 0 after EPS clamp)
  if (d1 === 0 && onSegment(p3, p1, p4)) return true;
  if (d2 === 0 && onSegment(p3, p2, p4)) return true;
  if (d3 === 0 && onSegment(p1, p3, p2)) return true;
  if (d4 === 0 && onSegment(p1, p4, p2)) return true;

  return false;
}

/**
 * Returns an open-ring view of `points`, stripping the closing duplicate if the
 * first and last vertices are identical.  All internal geometry algorithms
 * (self-intersection, etc.) must operate on open rings; a closed ring would
 * introduce a degenerate zero-length edge (first → first) that can trigger
 * false collinear-path positives in the orientation test.
 */
function toOpenRing(points: FieldBoundary[]): FieldBoundary[] {
  if (points.length < 2) return points;
  const first = points[0]!;
  const last = points[points.length - 1]!;
  return first.lat === last.lat && first.lng === last.lng
    ? points.slice(0, -1)
    : points;
}

/**
 * O(n²) self-intersection check for a simple polygon.
 * Skips pairs of adjacent edges (they share a vertex by design).
 */
function hasSelfIntersection(points: FieldBoundary[]): boolean {
  const n = points.length;
  for (let i = 0; i < n; i++) {
    const p1 = points[i];
    const p2 = points[(i + 1) % n];
    if (!p1 || !p2) continue;
    for (let j = i + 2; j < n; j++) {
      // Skip the wrap-around edge (n−1 → 0) when i === 0, because it
      // is adjacent to edge (0 → 1).
      if (i === 0 && j === n - 1) continue;
      const p3 = points[j];
      const p4 = points[(j + 1) % n];
      if (!p3 || !p4) continue;
      if (segmentsIntersect(p1, p2, p3, p4)) return true;
    }
  }
  return false;
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Ensures a polygon ring is explicitly closed (first vertex === last vertex).
 * GeoJSON and PostGIS both require closed rings.
 *
 * If the polygon is already closed (first === last by coordinate value) it is
 * returned unchanged. Otherwise the first vertex is appended.
 *
 * Call this **after** `validatePolygon` — the validator works on open rings
 * (the closing edge is implicit). Pass the result to the API submission.
 *
 * @example
 * const closed = ensureClosedPolygon(boundaryPoints);
 * await api.createField({ boundary: closed });
 */
export function ensureClosedPolygon(points: FieldBoundary[]): FieldBoundary[] {
  if (points.length === 0) return points;
  const first = points[0]!;
  const last = points[points.length - 1]!;
  if (first.lat === last.lat && first.lng === last.lng) {
    return points; // already closed
  }
  return [...points, first];
}

/**
 * Validates a list of boundary points that define a field polygon.
 *
 * Checks performed (in order):
 * 1. Minimum vertex count (≥ 3)
 * 2. Maximum vertex count (≤ 2000)
 * 3. All coordinates within WGS84 bounds
 * 4. Self-intersection (no edges cross each other), using EPS-clamped
 *    orientation to handle floating-point imprecision
 *
 * The input is treated as an **open ring** (the closing edge is implicit).
 * After validation succeeds, call `ensureClosedPolygon()` before sending to
 * the backend.
 *
 * @example
 * const result = validatePolygon(boundaryPoints);
 * if (!result.valid) {
 *   setErrors(result.errorsAr); // show Arabic messages to users
 * }
 */
export function validatePolygon(points: FieldBoundary[]): PolygonValidationResult {
  const errors: string[] = [];
  const errorsAr: string[] = [];

  const addError = (en: string, ar: string) => {
    errors.push(en);
    errorsAr.push(ar);
  };

  if (points.length < MIN_POLYGON_VERTICES) {
    addError(
      `A polygon requires at least ${MIN_POLYGON_VERTICES} vertices (got ${points.length}).`,
      `يجب أن يحتوي المضلع على ${MIN_POLYGON_VERTICES} نقاط على الأقل (تم إدخال ${points.length}).`,
    );
    // Cannot check further without enough points
    return { valid: false, errors, errorsAr };
  }

  if (points.length > MAX_POLYGON_VERTICES) {
    addError(
      `Polygon has too many vertices (${points.length} > ${MAX_POLYGON_VERTICES}).`,
      `عدد نقاط المضلع كبير جداً (${points.length} > ${MAX_POLYGON_VERTICES}).`,
    );
  }

  // WGS84 coordinate bounds check
  for (let i = 0; i < points.length; i++) {
    const p = points[i]!;
    if (p.lat < -90 || p.lat > 90 || p.lng < -180 || p.lng > 180) {
      addError(
        `Vertex ${i + 1} has out-of-range coordinates (lat=${p.lat}, lng=${p.lng}).`,
        `النقطة ${i + 1} تحتوي على إحداثيات خارج النطاق (lat=${p.lat}, lng=${p.lng}).`,
      );
    }
  }

  // Only run the expensive self-intersection check when vertex count and
  // coordinates are valid.  Normalize to an open ring first so that a
  // pre-closed input (first vertex === last vertex) does not introduce a
  // degenerate zero-length edge that could produce false collinear positives.
  if (errors.length === 0) {
    const ring = toOpenRing(points);
    // A triangle (3 edges) cannot self-intersect — skip to avoid O(n²) for
    // the minimum-size case.
    if (ring.length >= 4 && hasSelfIntersection(ring)) {
      addError(
        'The polygon boundary crosses itself (self-intersection). Please redraw the boundary.',
        'حدود المضلع تتقاطع مع نفسها. يرجى إعادة رسم الحدود.',
      );
    }
  }

  return { valid: errors.length === 0, errors, errorsAr };
}

