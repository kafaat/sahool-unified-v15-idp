/**
 * Tests for polygon geometry validation utilities
 * اختبارات أدوات التحقق من صحة هندسة المضلعات
 */

import { describe, it, expect } from 'vitest';
import { validatePolygon, ensureClosedPolygon, MIN_POLYGON_VERTICES, MAX_POLYGON_VERTICES } from '../geometry';
import type { FieldBoundary } from '@/features/satellite-monitor/types';

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

const pt = (lat: number, lng: number): FieldBoundary => ({ lat, lng });

/** A simple axis-aligned square (no self-intersection) */
const SQUARE: FieldBoundary[] = [
  pt(24.7, 46.6),
  pt(24.7, 46.7),
  pt(24.8, 46.7),
  pt(24.8, 46.6),
];

/** A convex hexagon (valid polygon) */
const HEXAGON: FieldBoundary[] = [
  pt(24.70, 46.65),
  pt(24.73, 46.62),
  pt(24.76, 46.65),
  pt(24.76, 46.68),
  pt(24.73, 46.71),
  pt(24.70, 46.68),
];

/**
 * A "figure-eight" / self-intersecting polygon: the edges cross at the midpoint.
 *       (0,0) → (1,1) → (1,0) → (0,1) → back to (0,0)
 * Edge (0,0)→(1,1) crosses edge (1,0)→(0,1).
 */
const FIGURE_EIGHT: FieldBoundary[] = [
  pt(0, 0),
  pt(1, 1),
  pt(1, 0),
  pt(0, 1),
];

// ---------------------------------------------------------------------------
// validatePolygon tests
// ---------------------------------------------------------------------------

describe('validatePolygon', () => {
  // --- Minimum vertex count ---

  it('rejects empty array', () => {
    const result = validatePolygon([]);
    expect(result.valid).toBe(false);
    expect(result.errors[0]).toContain(`${MIN_POLYGON_VERTICES}`);
    expect(result.errorsAr[0]).toContain(`${MIN_POLYGON_VERTICES}`);
  });

  it('rejects one point', () => {
    const result = validatePolygon([pt(24.7, 46.6)]);
    expect(result.valid).toBe(false);
    expect(result.errors.length).toBe(1);
  });

  it('rejects two points', () => {
    const result = validatePolygon([pt(24.7, 46.6), pt(24.8, 46.7)]);
    expect(result.valid).toBe(false);
  });

  it('accepts exactly 3 points (triangle)', () => {
    const triangle: FieldBoundary[] = [pt(0, 0), pt(0, 1), pt(1, 0)];
    const result = validatePolygon(triangle);
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  // --- Maximum vertex count ---

  it('rejects polygons exceeding MAX_POLYGON_VERTICES', () => {
    const large = Array.from({ length: MAX_POLYGON_VERTICES + 1 }, (_, i) => pt(i * 0.0001, 0));
    const result = validatePolygon(large);
    expect(result.valid).toBe(false);
    expect(result.errors[0]).toContain(`${MAX_POLYGON_VERTICES}`);
  });

  it('accepts exactly MAX_POLYGON_VERTICES points', () => {
    // Use a circle-like shape to guarantee no self-intersections
    const n = MAX_POLYGON_VERTICES;
    const circle = Array.from({ length: n }, (_, i) => {
      const angle = (2 * Math.PI * i) / n;
      return pt(Math.sin(angle), Math.cos(angle)); // unit circle in (lat,lng) space
    });
    const result = validatePolygon(circle);
    expect(result.valid).toBe(true);
  });

  // --- WGS84 coordinate bounds ---

  it('rejects out-of-range latitude', () => {
    const pts = [pt(91, 0), pt(0, 0), pt(0, 1)];
    const result = validatePolygon(pts);
    expect(result.valid).toBe(false);
    expect(result.errors[0]).toContain('Vertex 1');
  });

  it('rejects out-of-range longitude', () => {
    const pts = [pt(0, -181), pt(0, 0), pt(1, 0)];
    const result = validatePolygon(pts);
    expect(result.valid).toBe(false);
    expect(result.errors[0]).toContain('Vertex 1');
  });

  it('reports error for every out-of-range vertex', () => {
    const pts = [pt(-91, 0), pt(0, 181), pt(1, 1)];
    const result = validatePolygon(pts);
    expect(result.valid).toBe(false);
    expect(result.errors).toHaveLength(2);
  });

  it('accepts boundary values exactly at WGS84 limits', () => {
    const pts = [pt(-90, -180), pt(90, -180), pt(90, 180)];
    const result = validatePolygon(pts);
    expect(result.valid).toBe(true);
  });

  // --- Valid polygons ---

  it('accepts an axis-aligned square', () => {
    const result = validatePolygon(SQUARE);
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
    expect(result.errorsAr).toHaveLength(0);
  });

  it('accepts a convex hexagon', () => {
    const result = validatePolygon(HEXAGON);
    expect(result.valid).toBe(true);
  });

  // --- Self-intersection ---

  it('detects a figure-eight (self-intersecting polygon)', () => {
    const result = validatePolygon(FIGURE_EIGHT);
    expect(result.valid).toBe(false);
    expect(result.errors[0]).toContain('self-intersection');
    expect(result.errorsAr[0]).toContain('تتقاطع');
  });

  it('does not flag a triangle as self-intersecting', () => {
    // Triangles (3 vertices) are always simple — no pair of non-adjacent edges.
    const triangle: FieldBoundary[] = [pt(0, 0), pt(0, 1), pt(1, 0)];
    const result = validatePolygon(triangle);
    expect(result.valid).toBe(true);
  });

  it('does not flag a square as self-intersecting', () => {
    const result = validatePolygon(SQUARE);
    expect(result.valid).toBe(true);
  });

  it('detects a bowtie shape (two diagonals crossing)', () => {
    // Vertices: top-left, bottom-right, top-right, bottom-left
    // This creates a crossing pattern like an hourglass.
    const bowtie: FieldBoundary[] = [
      pt(1, 0),  // top-left
      pt(0, 1),  // bottom-right
      pt(1, 1),  // top-right
      pt(0, 0),  // bottom-left
    ];
    const result = validatePolygon(bowtie);
    expect(result.valid).toBe(false);
    expect(result.errors[0]).toContain('self-intersection');
  });

  // --- Return shape ---

  it('always returns errors and errorsAr with the same length', () => {
    const result = validatePolygon(FIGURE_EIGHT);
    expect(result.errors.length).toBe(result.errorsAr.length);
  });

  it('returns empty error arrays for valid polygon', () => {
    const result = validatePolygon(SQUARE);
    expect(result.errors).toHaveLength(0);
    expect(result.errorsAr).toHaveLength(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// ensureClosedPolygon tests
// ═══════════════════════════════════════════════════════════════════════════

describe('ensureClosedPolygon', () => {
  it('returns empty array unchanged', () => {
    expect(ensureClosedPolygon([])).toEqual([]);
  });

  it('appends the first vertex when polygon is open', () => {
    const closed = ensureClosedPolygon(SQUARE);
    expect(closed).toHaveLength(SQUARE.length + 1);
    expect(closed[closed.length - 1]).toEqual(SQUARE[0]);
  });

  it('does not duplicate the closing vertex when polygon is already closed', () => {
    const alreadyClosed = [...SQUARE, SQUARE[0]!];
    const result = ensureClosedPolygon(alreadyClosed);
    expect(result).toHaveLength(alreadyClosed.length);
    expect(result).toBe(alreadyClosed); // same reference — no copy made
  });

  it('preserves the original array (no mutation)', () => {
    const original = [...SQUARE];
    ensureClosedPolygon(original);
    expect(original).toHaveLength(SQUARE.length);
  });

  it('closes a triangle correctly', () => {
    const triangle: FieldBoundary[] = [pt(0, 0), pt(0, 1), pt(1, 0)];
    const closed = ensureClosedPolygon(triangle);
    expect(closed).toHaveLength(4);
    expect(closed[3]).toEqual({ lat: 0, lng: 0 });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// EPS floating-point precision tests
// ═══════════════════════════════════════════════════════════════════════════

describe('validatePolygon (floating-point precision)', () => {
  it('does not falsely detect self-intersection in a tiny field (< 1mm coordinates)', () => {
    // A 1m × 1m square at lat≈24.7 in WGS84 degrees
    // 1m in lat ≈ 9e-6 degrees; construct a square at that scale.
    const delta = 9e-6;
    const tiny: FieldBoundary[] = [
      pt(24.700000, 46.600000),
      pt(24.700000, 46.600000 + delta),
      pt(24.700000 + delta, 46.600000 + delta),
      pt(24.700000 + delta, 46.600000),
    ];
    const result = validatePolygon(tiny);
    expect(result.valid).toBe(true);
  });

  it('still detects a genuine self-intersection in a tiny figure-eight', () => {
    // Scale the figure-eight down to sub-meter field size
    const s = 1e-5;
    const tiny: FieldBoundary[] = [
      pt(0, 0),
      pt(s, s),
      pt(s, 0),
      pt(0, s),
    ];
    const result = validatePolygon(tiny);
    expect(result.valid).toBe(false);
    expect(result.errors[0]).toContain('self-intersection');
  });
});
