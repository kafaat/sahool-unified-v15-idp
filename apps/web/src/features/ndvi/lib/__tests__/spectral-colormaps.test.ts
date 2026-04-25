/**
 * Tests for the unified spectral-index colormap module.
 * اختبارات الموديول الموحّد لخرائط ألوان المؤشرات الطيفية.
 */

import { describe, expect, it } from 'vitest';
import {
  SPECTRAL_INDEX_METADATA,
  SPECTRAL_INDEX_ORDER,
  buildCssGradient,
  buildInterpolateExpression,
  getIndexBand,
  getIndexColor,
  getIndexColorStops,
  getIndexHealthLabel,
  getIndexLegend,
  getIndexMetadata,
  type SpectralIndexId,
} from '../spectral-colormaps';

const ALL_INDICES: SpectralIndexId[] = ['ndvi', 'ndwi', 'evi', 'savi', 'ndre', 'lai'];

describe('SPECTRAL_INDEX_METADATA', () => {
  it('exposes metadata for every supported index', () => {
    for (const id of ALL_INDICES) {
      const meta = SPECTRAL_INDEX_METADATA[id];
      expect(meta.id).toBe(id);
      expect(meta.code).toBe(id.toUpperCase());
      expect(meta.nameEn.length).toBeGreaterThan(0);
      expect(meta.nameAr.length).toBeGreaterThan(0);
      expect(meta.descriptionEn.length).toBeGreaterThan(0);
      expect(meta.descriptionAr.length).toBeGreaterThan(0);
      expect(meta.minValue).toBeLessThan(meta.maxValue);
    }
  });

  it('SPECTRAL_INDEX_ORDER lists each index exactly once', () => {
    const seen = new Set(SPECTRAL_INDEX_ORDER);
    expect(seen.size).toBe(ALL_INDICES.length);
    for (const id of ALL_INDICES) expect(seen.has(id)).toBe(true);
  });
});

describe('getIndexColorStops', () => {
  it.each(ALL_INDICES)('returns ascending, non-empty stops for %s', (id) => {
    const stops = getIndexColorStops(id);
    expect(stops.length).toBeGreaterThanOrEqual(2);
    for (let i = 1; i < stops.length; i++) {
      expect(stops[i]!.value).toBeGreaterThan(stops[i - 1]!.value);
    }
    for (const stop of stops) {
      expect(stop.color).toMatch(/^#[0-9a-fA-F]{6}$/);
    }
  });

  it.each(ALL_INDICES)('first/last stops match metadata range for %s', (id) => {
    const meta = getIndexMetadata(id);
    const stops = getIndexColorStops(id);
    expect(stops[0]!.value).toBe(meta.minValue);
    expect(stops[stops.length - 1]!.value).toBe(meta.maxValue);
  });
});

describe('getIndexLegend', () => {
  it.each(ALL_INDICES)('legend bands for %s are contiguous and span full range', (id) => {
    const meta = getIndexMetadata(id);
    const legend = getIndexLegend(id);
    expect(legend.length).toBeGreaterThan(0);
    expect(legend[0]!.min).toBe(meta.minValue);
    expect(legend[legend.length - 1]!.max).toBe(meta.maxValue);
    for (let i = 1; i < legend.length; i++) {
      expect(legend[i]!.min).toBe(legend[i - 1]!.max);
    }
    for (const band of legend) {
      expect(band.labelEn).not.toBe('');
      expect(band.labelAr).not.toBe('');
    }
  });
});

describe('getIndexColor', () => {
  it('clamps below the minimum to the first stop colour', () => {
    const stops = getIndexColorStops('ndvi');
    expect(getIndexColor('ndvi', -10)).toBe(stops[0]!.color);
  });

  it('clamps above the maximum to the last stop colour', () => {
    const stops = getIndexColorStops('ndvi');
    expect(getIndexColor('ndvi', 99)).toBe(stops[stops.length - 1]!.color);
  });

  it('returns the exact stop colour at a stop value', () => {
    const stops = getIndexColorStops('ndvi');
    for (const stop of stops) {
      expect(getIndexColor('ndvi', stop.value)).toBe(stop.color);
    }
  });

  it('interpolates between adjacent stops', () => {
    const stops = getIndexColorStops('ndvi');
    const lo = stops[0]!;
    const hi = stops[1]!;
    const mid = (lo.value + hi.value) / 2;
    const c = getIndexColor('ndvi', mid);
    // Should be a valid hex and not exactly equal to either endpoint
    // (assuming the two endpoint colours differ — which is an invariant).
    expect(c).toMatch(/^#[0-9a-f]{6}$/);
    expect(c).not.toBe(lo.color);
    expect(c).not.toBe(hi.color);
  });

  it('LAI scale works on its 0..8 domain', () => {
    expect(getIndexColor('lai', 0)).toBe(getIndexColorStops('lai')[0]!.color);
    expect(getIndexColor('lai', 8)).toBe(
      getIndexColorStops('lai')[getIndexColorStops('lai').length - 1]!.color,
    );
  });
});

describe('getIndexBand & getIndexHealthLabel', () => {
  it('returns the matching band for an interior NDVI value', () => {
    const band = getIndexBand('ndvi', 0.55);
    expect(band.min).toBeLessThanOrEqual(0.55);
    expect(band.max).toBeGreaterThan(0.55);
  });

  it('returns final band for the upper-bound value (inclusive)', () => {
    const band = getIndexBand('ndvi', 1.0);
    const legend = getIndexLegend('ndvi');
    expect(band).toBe(legend[legend.length - 1]);
  });

  it('switches between Arabic and English labels', () => {
    const en = getIndexHealthLabel('ndvi', 0.65, 'en');
    const ar = getIndexHealthLabel('ndvi', 0.65, 'ar');
    expect(en).not.toBe('');
    expect(ar).not.toBe('');
    expect(en).not.toBe(ar);
  });
});

describe('buildInterpolateExpression', () => {
  it('produces a valid MapLibre interpolate expression header', () => {
    const expr = buildInterpolateExpression('ndvi', 'ndvi_value');
    expect(expr[0]).toBe('interpolate');
    expect(expr[1]).toEqual(['linear']);
    expect(expr[2]).toEqual(['to-number', ['get', 'ndvi_value']]);
    // After the header, the rest is value/colour pairs.
    const rest = expr.slice(3);
    expect(rest.length % 2).toBe(0);
    expect(rest.length / 2).toBe(getIndexColorStops('ndvi').length);
  });

  it('accepts a custom value-expression argument', () => {
    const expr = buildInterpolateExpression('lai', ['raster-value']);
    expect(expr[2]).toEqual(['raster-value']);
  });
});

describe('buildCssGradient', () => {
  it.each(ALL_INDICES)('produces a linear-gradient string for %s', (id) => {
    const css = buildCssGradient(id);
    expect(css.startsWith('linear-gradient(to right,')).toBe(true);
    for (const stop of getIndexColorStops(id)) {
      expect(css).toContain(stop.color);
    }
  });
});
