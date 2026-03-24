import { describe, it, expect } from 'vitest';
import { getNDVIColor, getHealthLabel } from '../SatelliteMap';

describe('SatelliteMap getNDVIColor', () => {
  it('returns dark green for excellent NDVI (>= 0.7)', () => {
    expect(getNDVIColor(0.7)).toBe('#1B5E20');
    expect(getNDVIColor(0.85)).toBe('#1B5E20');
    expect(getNDVIColor(1.0)).toBe('#1B5E20');
  });

  it('returns green for good NDVI (0.5 - 0.7)', () => {
    expect(getNDVIColor(0.5)).toBe('#4CAF50');
    expect(getNDVIColor(0.6)).toBe('#4CAF50');
    expect(getNDVIColor(0.69)).toBe('#4CAF50');
  });

  it('returns yellow for moderate NDVI (0.3 - 0.5)', () => {
    expect(getNDVIColor(0.3)).toBe('#FDD835');
    expect(getNDVIColor(0.4)).toBe('#FDD835');
    expect(getNDVIColor(0.49)).toBe('#FDD835');
  });

  it('returns orange for poor NDVI (0.15 - 0.3)', () => {
    expect(getNDVIColor(0.15)).toBe('#FF9800');
    expect(getNDVIColor(0.2)).toBe('#FF9800');
    expect(getNDVIColor(0.29)).toBe('#FF9800');
  });

  it('returns red for critical NDVI (< 0.15)', () => {
    expect(getNDVIColor(0.0)).toBe('#F44336');
    expect(getNDVIColor(0.1)).toBe('#F44336');
    expect(getNDVIColor(0.14)).toBe('#F44336');
  });

  it('handles negative NDVI values', () => {
    expect(getNDVIColor(-0.5)).toBe('#F44336');
  });
});

describe('SatelliteMap getHealthLabel', () => {
  it('returns ممتاز for excellent NDVI (>= 0.7)', () => {
    expect(getHealthLabel(0.7)).toBe('ممتاز');
    expect(getHealthLabel(0.9)).toBe('ممتاز');
  });

  it('returns جيد for good NDVI (0.5 - 0.7)', () => {
    expect(getHealthLabel(0.5)).toBe('جيد');
    expect(getHealthLabel(0.65)).toBe('جيد');
  });

  it('returns متوسط for moderate NDVI (0.3 - 0.5)', () => {
    expect(getHealthLabel(0.3)).toBe('متوسط');
    expect(getHealthLabel(0.45)).toBe('متوسط');
  });

  it('returns ضعيف for poor NDVI (0.15 - 0.3)', () => {
    expect(getHealthLabel(0.15)).toBe('ضعيف');
    expect(getHealthLabel(0.25)).toBe('ضعيف');
  });

  it('returns حرج for critical NDVI (< 0.15)', () => {
    expect(getHealthLabel(0.0)).toBe('حرج');
    expect(getHealthLabel(0.1)).toBe('حرج');
  });
});
